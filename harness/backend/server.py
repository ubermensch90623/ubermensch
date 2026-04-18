"""harness/ 정적·JSON API 서버 — stdlib http.server 기반.

경로:
- /                          → ui/index.html (리다이렉트)
- /ui/*                      → 정적 자산
- /api/score                 → restore_score.summary_for_ui
- /api/lineage               → source_lineage.jsonl 요약 (최근 200건)
- /api/claims/restored       → C-0 통과 claim (JSON Lines 전체)
- /api/claims/quarantined    → 격리 claim

보안: 로컬 전용 (127.0.0.1), CORS 미설정.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

import restore_score as rs
from schemas import read_lineage


HARNESS_ROOT = Path(__file__).resolve().parent.parent
UI_ROOT = HARNESS_ROOT / "ui"
DATA_ROOT = HARNESS_ROOT / "data"
DEFAULT_PORT = int(os.environ.get("HARNESS_PORT", "8765"))

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
}


def _jsonl_tail(path: Path, limit: int = 200) -> list:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fp:
        lines = [ln.strip() for ln in fp if ln.strip()]
    out = []
    for ln in lines[-limit:]:
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out


class HarnessHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, f"not found: {path.name}")
            return
        ct = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _api(self, path: str) -> Optional[object]:
        if path == "/api/score":
            recs = rs.load_restored(DATA_ROOT / "restored" / "c0_passed.jsonl")
            return rs.summary_for_ui(rs.build_matrix(recs))
        if path == "/api/lineage":
            return {"entries": _jsonl_tail(DATA_ROOT / "source_lineage.jsonl")}
        if path == "/api/claims/restored":
            return {"records": _jsonl_tail(DATA_ROOT / "restored" / "c0_passed.jsonl")}
        if path == "/api/claims/quarantined":
            return {"records": _jsonl_tail(DATA_ROOT / "low_confidence" / "c0_failed.jsonl")}
        if path == "/api/cards/catalog":
            catalog = DATA_ROOT / "study_notes" / "card_catalog.json"
            if catalog.exists():
                return json.loads(catalog.read_text(encoding="utf-8"))
            return {"cards": [], "total": 0, "error": "catalog not generated"}
        if path == "/api/predictions":
            # P9 리버스엔지니어링 예상문항 (있을 때만)
            pred = DATA_ROOT / "low_confidence" / "p9_predictions.json"
            if pred.exists():
                return json.loads(pred.read_text(encoding="utf-8"))
            return {"questions": [], "status": "P9 미실행 또는 대기 중"}
        return None

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        # API
        api_resp = self._api(path)
        if api_resp is not None:
            self._send_json(api_resp)
            return
        # Root → UI
        if path == "/" or path == "":
            index = UI_ROOT / "index.html"
            if index.exists():
                self._send_file(index)
                return
            self._send_json({"status": "harness UP", "ui": "미작성 (M3 마감 전)"})
            return
        # Static (UI)
        if path.startswith("/ui/"):
            rel = path[len("/ui/"):]
            candidate = UI_ROOT / rel
            candidate = candidate.resolve()
            if UI_ROOT.resolve() in candidate.parents or candidate == UI_ROOT.resolve():
                self._send_file(candidate)
                return
            self.send_error(403)
            return
        # 해설카드 직접 서빙 (읽기 전용)
        if path.startswith("/study/"):
            from urllib.parse import unquote
            fname = unquote(path[len("/study/"):])
            cards_dir = Path("C:/Users/윤상택/Desktop/Cowork_작업폴더/해설_카드")
            candidate = (cards_dir / fname).resolve()
            if cards_dir.resolve() in candidate.parents and candidate.suffix == ".html":
                self._send_file(candidate)
                return
            self.send_error(403)
            return
        self.send_error(404)

    def log_message(self, fmt, *args):  # 로그 억제
        return


def run(port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), HarnessHandler)
    print(f"harness up on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    run()
