#!/usr/bin/env python3
"""
fetch-claude-ai.py

claude.ai의 내부 REST API를 사용자분의 sessionKey 쿠키로 호출해
모든 대화를 끌어와 vault/Sessions/claude-ai/ 아래에 마크다운으로 저장한다.

사용:
    1) https://claude.ai 로그인 후 DevTools 열기 (F12)
    2) Application(or Storage) → Cookies → https://claude.ai
    3) "sessionKey" 값 복사 (sk-ant-sid01-... 로 시작하는 긴 문자열)
    4) .env 또는 환경변수에 설정:
         CLAUDE_AI_SESSION_KEY=sk-ant-sid01-...
    5) python3 scripts/fetch-claude-ai.py

옵션:
    --org-uuid <uuid>     특정 조직만 (미지정시 첫 번째 조직)
    --limit N             가장 최근 N개만
    --since YYYY-MM-DD    이 날짜 이후 갱신된 것만
    --vault-dir PATH      볼트 위치 (기본 ./vault)
    --overwrite           기존 노트 덮어씀
    --dry-run             목록만 출력

주의:
    - sessionKey는 비밀번호와 같은 효력이 있음. 절대 git에 커밋하거나 공유하지 말 것.
    - 비공식 API라 언제 깨질지 모름. 깨지면 공식 Export 경로 사용.
    - 표준 라이브러리만 사용 (urllib).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "https://claude.ai/api"


def http_get(url: str, session_key: str) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "Cookie": f"sessionKey={session_key}",
            "User-Agent": "Mozilla/5.0 (compatible; ubermensch-fetcher/1.0)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code} on {url}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"네트워크 오류 ({url}): {e}") from e


def load_session_key() -> str:
    # .env 우선
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("CLAUDE_AI_SESSION_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("CLAUDE_AI_SESSION_KEY", "")


def slugify(s: str, maxlen: int = 60) -> str:
    s = re.sub(r"[\s/]+", "-", s.strip())
    s = re.sub(r"[^\w\-가-힣]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen] or "untitled"


def extract_text(msg: dict) -> str:
    for key in ("text", "content"):
        v = msg.get(key)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, list):
            parts = []
            for block in v:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
                    elif "text" in block:
                        parts.append(block["text"])
            if parts:
                return "\n\n".join(p for p in parts if p)
    return ""


def render_markdown(conv: dict) -> tuple[str, str] | None:
    uuid = conv.get("uuid", "")
    title = conv.get("name") or "(제목 없음)"
    created = conv.get("created_at", "")
    updated = conv.get("updated_at", "")
    messages = conv.get("chat_messages") or conv.get("messages") or []

    rendered = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        sender = m.get("sender") or m.get("role") or ""
        text = extract_text(m)
        ts = m.get("created_at", "")
        if not text.strip():
            continue
        role = "user" if sender in ("human", "user") else (
            "assistant" if sender == "assistant" else sender
        )
        rendered.append((role, ts, text))

    if not rendered:
        return None

    timestamps = [r[1] for r in rendered if r[1]]
    started = created or (min(timestamps) if timestamps else "")
    ended = updated or (max(timestamps) if timestamps else "")

    if started:
        try:
            dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
            date_str = dt.astimezone().strftime("%Y-%m-%d")
        except ValueError:
            date_str = "unknown-date"
    else:
        date_str = "unknown-date"

    short_id = (uuid.split("-")[0] if uuid else "noid")[:8]
    fname = f"{date_str}_{slugify(title)}_{short_id}.md"

    fm = [
        "---",
        f"date: {date_str}",
        "type: chat",
        "source: claude-ai-web",
        f'chat-id: "{uuid}"',
        f'title: "{title.replace(chr(34), chr(39))}"',
        f'started: "{started}"',
        f'ended: "{ended}"',
        f"message-count: {len(rendered)}",
        "fetched-via: claude-ai-internal-api",
        "ai-first: true",
        "tags: [chat, claude-ai]",
        "---",
        "",
    ]
    body = [
        "## For future Claude",
        "",
        f"이 노트는 claude.ai 웹 채팅 `{title}` ({date_str})의 자동 임포트 기록이다.",
        f"sessionKey 쿠키로 claude.ai 내부 API를 호출해 가져왔다. 메시지 수: {len(rendered)}.",
        "",
        f"# {title}",
        "",
    ]
    for role, ts, text in rendered:
        ts_short = ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                ts_short = dt.astimezone().strftime("%Y-%m-%d %H:%M")
            except ValueError:
                ts_short = ts[:19]
        speaker = "사용자" if role == "user" else "Claude" if role == "assistant" else role
        body.append(f"## {speaker} · {ts_short}")
        body.append("")
        body.append(text.rstrip())
        body.append("")
    return fname, "\n".join(fm) + "\n".join(body) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault-dir", default="vault")
    ap.add_argument("--out-subdir", default="Sessions/claude-ai")
    ap.add_argument("--org-uuid", default=None,
                    help="특정 조직만. 미지정 시 첫 번째 조직 자동 선택.")
    ap.add_argument("--limit", type=int, default=0,
                    help="가장 최근 N개만 (0 = 무제한)")
    ap.add_argument("--since", default=None,
                    help="이 날짜(YYYY-MM-DD) 이후 updated_at만 처리")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="목록만 받아서 어떤 게 임포트될지 출력")
    ap.add_argument("--sleep", type=float, default=0.3,
                    help="대화 간 요청 간격 (초). 너무 빠르면 rate limit.")
    args = ap.parse_args()

    session_key = load_session_key()
    if not session_key:
        print("ERROR: CLAUDE_AI_SESSION_KEY 가 .env 또는 환경변수에 설정되어 있지 않습니다.", file=sys.stderr)
        print("  .env에 CLAUDE_AI_SESSION_KEY=sk-ant-sid01-... 추가", file=sys.stderr)
        return 1

    print("[1/3] 조직 목록 조회...")
    orgs = http_get(f"{BASE}/organizations", session_key)
    if not isinstance(orgs, list) or not orgs:
        print("ERROR: 조직을 찾지 못함. sessionKey가 만료됐거나 잘못됐을 수 있음.", file=sys.stderr)
        return 1

    if args.org_uuid:
        org_uuid = args.org_uuid
    else:
        org_uuid = orgs[0].get("uuid")
        names = [(o.get("name", "?"), o.get("uuid", "?")) for o in orgs]
        print(f"      {len(orgs)}개 조직: {names}")
        print(f"      첫 번째 사용: {orgs[0].get('name')} ({org_uuid})")

    print(f"[2/3] 대화 목록 조회 (org={org_uuid})...")
    convs = http_get(
        f"{BASE}/organizations/{org_uuid}/chat_conversations",
        session_key,
    )
    if not isinstance(convs, list):
        print(f"ERROR: 예상치 못한 응답: {type(convs)}", file=sys.stderr)
        return 1
    print(f"      총 {len(convs)}개 대화")

    # 정렬 + 필터
    convs.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
    if args.since:
        convs = [c for c in convs if c.get("updated_at", "") >= args.since]
        print(f"      --since {args.since} 필터 후: {len(convs)}개")
    if args.limit > 0:
        convs = convs[: args.limit]
        print(f"      --limit {args.limit} 적용: {len(convs)}개")

    out_dir = Path(args.vault_dir) / args.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[3/3] 각 대화 상세 가져와 마크다운 작성 → {out_dir}")
    written = 0
    skipped = 0
    failed = 0
    for i, conv_meta in enumerate(convs, 1):
        conv_uuid = conv_meta.get("uuid")
        title = conv_meta.get("name") or "(no title)"
        if args.dry_run:
            print(f"  [{i}/{len(convs)}] {title}  ({conv_uuid})")
            continue

        try:
            full = http_get(
                f"{BASE}/organizations/{org_uuid}/chat_conversations/{conv_uuid}"
                "?tree=True&rendering_mode=messages",
                session_key,
            )
        except RuntimeError as e:
            print(f"  [{i}/{len(convs)}] FAIL  {title}: {e}", file=sys.stderr)
            failed += 1
            continue

        result = render_markdown(full)
        if result is None:
            print(f"  [{i}/{len(convs)}] empty  {title}")
            continue
        fname, content = result
        target = out_dir / fname
        if target.exists() and not args.overwrite:
            skipped += 1
            print(f"  [{i}/{len(convs)}] skip   {fname}")
        else:
            target.write_text(content, encoding="utf-8")
            written += 1
            print(f"  [{i}/{len(convs)}] wrote  {fname}")

        if args.sleep > 0 and i < len(convs):
            time.sleep(args.sleep)

    print()
    print(f"완료. 작성: {written}, 건너뜀: {skipped}, 실패: {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
