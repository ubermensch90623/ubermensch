#!/usr/bin/env python3
"""
import-claude-code-sessions.py

~/.claude/projects/<프로젝트>/*.jsonl 형식의 Claude Code 세션 로그를
vault/Sessions/ 아래에 사람이 읽을 수 있는 마크다운 노트로 변환한다.

각 세션은 한 파일로 저장되고, 프론트매터에는 type/source/session-id/date 등
AI-first 규약 필드가 들어간다. 본문은 시간 순서로 사용자/어시스턴트 메시지를
나열하며, 도구 호출은 한 줄 요약으로 압축된다.

사용 예:
    python3 scripts/import-claude-code-sessions.py
    python3 scripts/import-claude-code-sessions.py --project -home-user-ubermensch
    python3 scripts/import-claude-code-sessions.py --skip-active 0

표준 라이브러리만 사용. 외부 의존성 없음.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Message:
    role: str
    timestamp: str
    text_blocks: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)


@dataclass
class Session:
    session_id: str
    source_path: Path
    cwd: str
    started: str
    ended: str
    messages: list[Message]

    @property
    def short_id(self) -> str:
        return self.session_id.split("-")[0]

    @property
    def message_count(self) -> int:
        return len(self.messages)


def summarize_tool_use(name: str, inp) -> str:
    """도구 호출 한 줄 요약."""
    if not isinstance(inp, dict):
        return f"[tool:{name}]"
    if "command" in inp:
        cmd = inp.get("command", "")
        desc = inp.get("description", "")
        cmd_short = cmd if len(cmd) <= 100 else cmd[:97] + "..."
        return f"[{name}] {desc}: `{cmd_short}`"
    if "file_path" in inp:
        return f"[{name}] {inp['file_path']}"
    if "url" in inp:
        return f"[{name}] {inp['url']}"
    if "query" in inp:
        return f"[{name}] {inp['query']!r}"
    if "prompt" in inp:
        p = inp["prompt"]
        return f"[{name}] {p[:120]}{'...' if len(p) > 120 else ''}"
    return f"[{name}] keys={sorted(inp.keys())}"


def extract_message(msg: dict) -> Message | None:
    role = msg.get("role")
    if role not in ("user", "assistant"):
        return None
    content = msg.get("content")
    text_blocks: list[str] = []
    tool_calls: list[str] = []

    if isinstance(content, str):
        text_blocks.append(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text_blocks.append(block.get("text", ""))
            elif btype == "tool_use":
                tool_calls.append(summarize_tool_use(block.get("name", "?"), block.get("input")))
            # tool_result, image 등은 본문에 포함하지 않음 (잡음)
    if not text_blocks and not tool_calls:
        return None
    return Message(role=role, timestamp="", text_blocks=text_blocks, tool_calls=tool_calls)


def parse_session(path: Path) -> Session | None:
    messages: list[Message] = []
    cwd = ""
    timestamps: list[str] = []
    session_id = path.stem

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            ts = d.get("timestamp", "")
            if not cwd and "cwd" in d:
                cwd = d["cwd"]
            if t in ("user", "assistant"):
                msg = d.get("message")
                if not isinstance(msg, dict):
                    continue
                m = extract_message(msg)
                if m is None:
                    continue
                # user 쪽이 도구 결과만 담고 있는 경우는 extract_message가 None을 반환했을 것
                m.timestamp = ts
                messages.append(m)
                if ts:
                    timestamps.append(ts)
    if not messages:
        return None
    started = min(timestamps) if timestamps else ""
    ended = max(timestamps) if timestamps else ""
    return Session(
        session_id=session_id,
        source_path=path,
        cwd=cwd or "(unknown)",
        started=started,
        ended=ended,
        messages=messages,
    )


def slugify_filename(s: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s.lower()[:40]


def render_session(sess: Session) -> tuple[str, str]:
    """(filename, markdown) 반환."""
    if sess.started:
        try:
            dt = datetime.fromisoformat(sess.started.replace("Z", "+00:00"))
            dt_local = dt.astimezone()
            date_str = dt_local.strftime("%Y-%m-%d")
            time_str = dt_local.strftime("%H-%M")
        except ValueError:
            date_str = "unknown-date"
            time_str = "00-00"
    else:
        date_str = "unknown-date"
        time_str = "00-00"

    fname = f"{date_str}_{time_str}_claude-code_{sess.short_id}.md"

    # 첫 사용자 메시지에서 제목 후보 추출
    title_seed = ""
    for m in sess.messages:
        if m.role == "user" and m.text_blocks:
            title_seed = m.text_blocks[0].splitlines()[0]
            break
    title_short = title_seed[:80] if title_seed else "(제목 없음)"

    # 프론트매터
    fm_lines = [
        "---",
        f'date: {date_str}',
        "type: session",
        f'source: claude-code',
        f'session-id: "{sess.session_id}"',
        f'started: "{sess.started}"',
        f'ended: "{sess.ended}"',
        f'cwd: "{sess.cwd}"',
        f"message-count: {sess.message_count}",
        "ai-first: true",
        "tags: [session, claude-code]",
        "---",
        "",
    ]
    body = [
        "## For future Claude",
        "",
        f"이 노트는 {date_str}에 진행된 Claude Code 세션 `{sess.short_id}`의 자동 임포트 기록이다. 작업 디렉터리는 `{sess.cwd}`였다.",
        "본문은 사용자/어시스턴트 메시지를 시간순으로 나열한다. 도구 호출은 한 줄 요약, 도구 결과는 생략됐다.",
        "",
        f"# {title_short}",
        "",
    ]

    for m in sess.messages:
        ts_short = ""
        if m.timestamp:
            try:
                dt = datetime.fromisoformat(m.timestamp.replace("Z", "+00:00"))
                ts_short = dt.astimezone().strftime("%H:%M:%S")
            except ValueError:
                ts_short = m.timestamp[:19]
        speaker = "사용자" if m.role == "user" else "Claude"
        body.append(f"## {speaker} · {ts_short}")
        body.append("")
        for tb in m.text_blocks:
            body.append(tb.rstrip())
            body.append("")
        for tc in m.tool_calls:
            body.append(f"- {tc}")
        if m.tool_calls:
            body.append("")

    return fname, "\n".join(fm_lines) + "\n".join(body) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=str(Path.home() / ".claude" / "projects"),
                    help="Claude Code 세션 루트 (기본: ~/.claude/projects)")
    ap.add_argument("--project", default=None,
                    help="특정 프로젝트만 (디렉터리 이름). 미지정이면 전체.")
    ap.add_argument("--vault-dir", default="vault",
                    help="볼트 루트 (기본: ./vault)")
    ap.add_argument("--out-subdir", default="Sessions",
                    help="볼트 내 출력 하위 폴더 (기본: Sessions)")
    ap.add_argument("--skip-active", type=int, default=120,
                    help="이 초 안에 수정된 파일은 활성 세션으로 보고 건너뜀 (기본: 120). 0이면 비활성화.")
    ap.add_argument("--overwrite", action="store_true",
                    help="기존 파일을 덮어씀")
    ap.add_argument("--dry-run", action="store_true",
                    help="실제 쓰지 않고 어떤 파일이 만들어질지 출력")
    args = ap.parse_args()

    src_root = Path(args.source_dir).expanduser()
    if not src_root.exists():
        print(f"ERROR: source-dir 없음: {src_root}", file=sys.stderr)
        return 1

    if args.project:
        project_dirs = [src_root / args.project]
    else:
        project_dirs = [p for p in src_root.iterdir() if p.is_dir()]

    out_dir = Path(args.vault_dir) / args.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).timestamp()
    written = 0
    skipped_active = 0
    skipped_existing = 0

    for pd in project_dirs:
        if not pd.exists():
            print(f"WARN: project 디렉터리 없음: {pd}", file=sys.stderr)
            continue
        for jsonl in sorted(pd.glob("*.jsonl")):
            mtime = jsonl.stat().st_mtime
            if args.skip_active > 0 and (now - mtime) < args.skip_active:
                skipped_active += 1
                print(f"[skip active] {jsonl.name}")
                continue
            sess = parse_session(jsonl)
            if sess is None:
                continue
            fname, content = render_session(sess)
            target = out_dir / fname
            if target.exists() and not args.overwrite:
                skipped_existing += 1
                print(f"[skip exists] {target}")
                continue
            if args.dry_run:
                print(f"[would write] {target}  ({sess.message_count} 메시지)")
            else:
                target.write_text(content, encoding="utf-8")
                print(f"[wrote] {target}  ({sess.message_count} 메시지)")
                written += 1

    print()
    print(f"완료. 작성: {written}, 활성 건너뜀: {skipped_active}, 기존 건너뜀: {skipped_existing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
