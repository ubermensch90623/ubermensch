"""Utilities — date/time parsing, prompts with validation, table formatting."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Iterable, Sequence

from tabulate import tabulate


SOLVE_TIME_MIN_SEC = 1
SOLVE_TIME_MAX_SEC = 3600  # 1 hour cap; longer means data entry mistake
DATE_FUTURE_GRACE_DAYS = 1  # allow today + 1 day (for late-night logging)


def today_str() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(raw: str, default_today: bool = True) -> str:
    raw = (raw or "").strip()
    if not raw:
        if default_today:
            return today_str()
        raise ValueError("빈 날짜 입력")
    if not _DATE_RE.match(raw):
        raise ValueError(f"날짜 형식 오류 (YYYY-MM-DD, 0-padded): {raw}")
    try:
        d = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"날짜 형식 오류 (YYYY-MM-DD): {raw}") from e
    max_allowed = date.today() + timedelta(days=DATE_FUTURE_GRACE_DAYS)
    if d > max_allowed:
        raise ValueError(f"미래 날짜는 {max_allowed.isoformat()}까지만 허용: {raw}")
    return d.isoformat()


_SOLVE_TIME_RE = re.compile(
    r"""
    ^\s*
    (?:
        (?P<plain>\d+)                                  # "90"
        |
        (?P<min>\d+):(?P<sec>\d{1,2})                   # "1:30"
        |
        (?:(?P<m2>\d+)\s*m)\s*(?:(?P<s2>\d+)\s*s?)?     # "2m" or "1m30s"
        |
        (?:(?P<s3>\d+)\s*s)                             # "45s"
    )
    \s*$
    """,
    re.VERBOSE,
)


def parse_solve_time(raw: str) -> int:
    """Parse '90', '1:30', '2m', '1m30s', '45s' into seconds (int)."""
    raw = (raw or "").strip().lower()
    if not raw:
        raise ValueError("풀이 시간이 비어 있음")
    m = _SOLVE_TIME_RE.match(raw)
    if not m:
        raise ValueError(f"풀이 시간 형식 오류: {raw} (예: 90, 1:30, 2m, 1m30s)")
    if m.group("plain") is not None:
        secs = int(m.group("plain"))
    elif m.group("min") is not None:
        s = int(m.group("sec"))
        if s >= 60:
            raise ValueError(f"초 단위는 0~59 범위: {raw}")
        secs = int(m.group("min")) * 60 + s
    elif m.group("m2") is not None:
        s2 = int(m.group("s2")) if m.group("s2") else 0
        if s2 >= 60:
            raise ValueError(f"초 단위는 0~59 범위: {raw}")
        secs = int(m.group("m2")) * 60 + s2
    elif m.group("s3") is not None:
        secs = int(m.group("s3"))
    else:
        raise ValueError(f"풀이 시간 파싱 실패: {raw}")
    if not (SOLVE_TIME_MIN_SEC <= secs <= SOLVE_TIME_MAX_SEC):
        raise ValueError(
            f"풀이 시간 범위 초과 ({SOLVE_TIME_MIN_SEC}~{SOLVE_TIME_MAX_SEC}초): {secs}초"
        )
    return secs


def format_secs(seconds: int | float | None) -> str:
    if seconds is None or (isinstance(seconds, float) and seconds != seconds):  # NaN
        return "-"
    s = int(round(float(seconds)))
    if s < 60:
        return f"{s}초"
    m, r = divmod(s, 60)
    if r == 0:
        return f"{m}분"
    return f"{m}분 {r}초"


def format_pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "-"
    return f"{numerator / denominator * 100:.1f}%"


def prompt(msg: str) -> str:
    return input(msg).strip()


def prompt_yn(msg: str) -> bool:
    while True:
        v = prompt(msg).lower()
        if v in ("y", "yes", "ㅇ"):
            return True
        if v in ("n", "no", "ㄴ"):
            return False
        print("  → y 또는 n 으로 입력하세요.")


def prompt_int_range(msg: str, lo: int, hi: int) -> int:
    while True:
        v = prompt(msg)
        try:
            n = int(v)
        except ValueError:
            print(f"  → 정수를 입력하세요 ({lo}~{hi}).")
            continue
        if lo <= n <= hi:
            return n
        print(f"  → {lo}~{hi} 범위로 입력하세요.")


def prompt_choice(msg: str, options: Sequence[str]) -> str:
    print(msg)
    for i, opt in enumerate(options, start=1):
        print(f"  {i}) {opt}")
    while True:
        v = prompt("번호 선택: ")
        try:
            idx = int(v)
        except ValueError:
            print("  → 번호로 입력하세요.")
            continue
        if 1 <= idx <= len(options):
            return options[idx - 1]
        print(f"  → 1~{len(options)} 범위로 입력하세요.")


def prompt_required(msg: str) -> str:
    while True:
        v = prompt(msg)
        if v:
            return v
        print("  → 빈 값은 허용되지 않습니다.")


def prompt_optional(msg: str) -> str:
    return prompt(msg)


def prompt_date(msg: str) -> str:
    while True:
        try:
            return parse_date(prompt(msg), default_today=True)
        except ValueError as e:
            print(f"  → {e}")


def prompt_solve_time(msg: str) -> int:
    while True:
        try:
            return parse_solve_time(prompt(msg))
        except ValueError as e:
            print(f"  → {e}")


def print_table(rows: Iterable[Iterable], headers: Sequence[str]) -> None:
    rows = list(rows)
    if not rows:
        print("  (데이터 없음)")
        return
    print(tabulate(rows, headers=list(headers), tablefmt="github"))
