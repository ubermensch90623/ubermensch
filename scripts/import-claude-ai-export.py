#!/usr/bin/env python3
"""
import-claude-ai-export.py

claude.ai 웹의 공식 데이터 export(zip)를 vault/Sessions/claude-ai/ 아래의
마크다운 노트로 변환한다.

export 받기:
    claude.ai → 좌측 하단 프로필 → Settings → Privacy → Export data
    24시간 이내에 이메일로 다운로드 링크 도착. 24시간 후 만료.

사용 예:
    python3 scripts/import-claude-ai-export.py path/to/data-export.zip
    python3 scripts/import-claude-ai-export.py path/to/extracted/dir
    python3 scripts/import-claude-ai-export.py --vault-dir vault data-export.zip

지원하는 입력:
    1) zip 파일 (직접 읽음)
    2) 압축 해제된 디렉터리

기대하는 export 구조 (Anthropic이 제공하는 공식 포맷, 변경 가능성 있음):
    conversations.json  — 모든 대화의 배열
    각 대화 객체:
        {
          "uuid": "...",
          "name": "Title",
          "created_at": "ISO",
          "updated_at": "ISO",
          "chat_messages": [
            {
              "uuid": "...",
              "text": "...",        # 또는 "content": [...]
              "sender": "human"|"assistant",
              "created_at": "ISO"
            }, ...
          ]
        }

스키마가 다르면 가능한 한 유연하게 추출하려 시도한다 (heuristic).
표준 라이브러리만 사용.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable


def slugify(s: str, maxlen: int = 60) -> str:
    s = re.sub(r"[\s/]+", "-", s.strip())
    s = re.sub(r"[^\w\-가-힣]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen] or "untitled"


def find_conversations_file(root: Path) -> Path | None:
    candidates = ["conversations.json", "data/conversations.json"]
    for c in candidates:
        p = root / c
        if p.exists():
            return p
    # 임의 깊이로 탐색
    for p in root.rglob("conversations.json"):
        return p
    return None


def load_conversations_from_zip(zip_path: Path) -> list[dict]:
    with zipfile.ZipFile(zip_path) as z:
        # 후보 우선순위
        target = None
        for name in z.namelist():
            if name.endswith("conversations.json"):
                target = name
                break
        if target is None:
            raise FileNotFoundError(f"{zip_path} 안에 conversations.json을 찾지 못했습니다.")
        with z.open(target) as f:
            return json.load(f)


def load_conversations_from_dir(dir_path: Path) -> list[dict]:
    p = find_conversations_file(dir_path)
    if p is None:
        raise FileNotFoundError(f"{dir_path} 안에 conversations.json을 찾지 못했습니다.")
    with p.open() as f:
        return json.load(f)


def extract_message_text(msg: dict) -> str:
    """공식 포맷이 'text' 또는 'content'(블록 리스트) 둘 다일 수 있어 둘 다 대응."""
    txt = msg.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif "text" in block:
                    parts.append(block.get("text", ""))
        if parts:
            return "\n\n".join(p for p in parts if p)
    # message 안에 input/output 같은 구조가 있는 경우
    if "message" in msg and isinstance(msg["message"], dict):
        return extract_message_text(msg["message"])
    return ""


def render_conversation(conv: dict) -> tuple[str, str] | None:
    uuid = conv.get("uuid") or conv.get("id") or ""
    title = conv.get("name") or conv.get("title") or "(제목 없음)"
    created = conv.get("created_at", "")
    updated = conv.get("updated_at", "")

    messages: Iterable[dict] = (
        conv.get("chat_messages")
        or conv.get("messages")
        or []
    )

    rendered: list[tuple[str, str, str]] = []  # (role, ts, text)
    for m in messages:
        if not isinstance(m, dict):
            continue
        sender = m.get("sender") or m.get("role") or ""
        text = extract_message_text(m)
        ts = m.get("created_at", "")
        if not text.strip():
            continue
        if sender in ("human", "user"):
            role = "user"
        elif sender == "assistant":
            role = "assistant"
        else:
            role = sender or "unknown"
        rendered.append((role, ts, text))

    if not rendered:
        return None

    # 시작/종료 시각
    timestamps = [r[1] for r in rendered if r[1]]
    started = created or (min(timestamps) if timestamps else "")
    ended = updated or (max(timestamps) if timestamps else "")

    # 파일명
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
        "ai-first: true",
        "tags: [chat, claude-ai]",
        "---",
        "",
    ]
    body = [
        "## For future Claude",
        "",
        f"이 노트는 claude.ai 웹 채팅 `{title}` ({date_str})의 자동 임포트 기록이다.",
        f"공식 Settings → Privacy → Export data로 받은 zip에서 추출됐다. 메시지 수: {len(rendered)}.",
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
    ap.add_argument("input", help="export zip 파일 또는 압축 해제된 디렉터리")
    ap.add_argument("--vault-dir", default="vault", help="볼트 루트 (기본: ./vault)")
    ap.add_argument("--out-subdir", default="Sessions/claude-ai",
                    help="볼트 내 출력 하위 폴더 (기본: Sessions/claude-ai)")
    ap.add_argument("--overwrite", action="store_true", help="기존 파일을 덮어씀")
    ap.add_argument("--dry-run", action="store_true", help="실제 쓰지 않고 미리 보기")
    args = ap.parse_args()

    src = Path(args.input).expanduser()
    if not src.exists():
        print(f"ERROR: 입력 경로가 없음: {src}", file=sys.stderr)
        return 1

    try:
        if src.is_file() and src.suffix.lower() == ".zip":
            conversations = load_conversations_from_zip(src)
        elif src.is_dir():
            conversations = load_conversations_from_dir(src)
        else:
            print(f"ERROR: zip 또는 디렉터리가 필요합니다: {src}", file=sys.stderr)
            return 1
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: export 파싱 실패: {e}", file=sys.stderr)
        return 1

    out_dir = Path(args.vault_dir) / args.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    empty = 0
    for conv in conversations:
        if not isinstance(conv, dict):
            continue
        result = render_conversation(conv)
        if result is None:
            empty += 1
            continue
        fname, content = result
        target = out_dir / fname
        if target.exists() and not args.overwrite:
            skipped += 1
            print(f"[skip exists] {target}")
            continue
        if args.dry_run:
            print(f"[would write] {target}")
        else:
            target.write_text(content, encoding="utf-8")
            print(f"[wrote] {target}")
            written += 1

    print()
    print(f"완료. 작성: {written}, 기존 건너뜀: {skipped}, 빈 대화: {empty}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
