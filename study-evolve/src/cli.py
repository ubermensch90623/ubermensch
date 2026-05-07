"""Interactive CLI flows — add (record), done-review (mark complete)."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .constants import (
    AREAS_BY_SUBJECT,
    FAIL_TAGS,
    SUBJECTS,
)
from .models import StudyRecord
from .storage import (
    append_record_with_id,
    append_schedules,
    load_records,
    load_schedule,
    mark_review_done,
)
from .utils import (
    prompt,
    prompt_choice,
    prompt_date,
    prompt_int_range,
    prompt_optional,
    prompt_required,
    prompt_solve_time,
    prompt_yn,
)


def add_interactive() -> None:
    print("[학습 기록 추가]")
    print("---")

    print("1) 날짜를 입력하세요. Enter를 누르면 오늘 날짜 사용.")
    rec_date = prompt_date("   날짜 (YYYY-MM-DD): ")

    print("2) 과목을 선택하세요:")
    subject = prompt_choice("", SUBJECTS)

    if subject == "기타":
        print("3) 영역을 직접 입력하세요.")
        area = prompt_required("   영역: ")
    else:
        areas = AREAS_BY_SUBJECT[subject]
        print("3) 영역을 선택하세요:")
        # Allow choosing from list or typing a new one (free input fallback)
        choice_options = areas + ["(직접 입력)"]
        chosen = prompt_choice("", choice_options)
        if chosen == "(직접 입력)":
            area = prompt_required("   영역: ")
        else:
            area = chosen

    print("4) 문제 출처를 입력하세요. 예: 민경채 PSAT, 봉투모의고사, 전공기출, 공기업단기, 해커스 등")
    source = prompt_required("   출처: ")

    print("5) 문제 번호를 입력하세요. 예: 2024-민경채-자료해석-12")
    problem_no = prompt_required("   문제 번호: ")

    print("6) 정답인가요?")
    is_correct = prompt_yn("   y/n: ")

    print("7) 풀이 시간을 입력하세요. 예: 90 / 1:30 / 2m / 1m30s")
    solve_time_sec = prompt_solve_time("   풀이 시간: ")

    print("8) 체감 난이도 1~5")
    difficulty = prompt_int_range("   난이도: ", 1, 5)

    fail_tag = ""
    if not is_correct:
        print("9) 실패 태그를 선택하세요:")
        chosen_tag = prompt_choice("", FAIL_TAGS)
        if chosen_tag == "기타":
            fail_tag = prompt_required("   직접 입력: ")
        else:
            fail_tag = chosen_tag

    print("10) 짧은 메모 (한 줄, Enter로 건너뛰기)")
    memo = prompt_optional("   메모: ")

    def _build(new_id: int) -> StudyRecord:
        return StudyRecord(
            id=new_id,
            date=rec_date,
            subject=subject,
            area=area,
            source=source,
            problem_no=problem_no,
            is_correct=is_correct,
            solve_time_sec=solve_time_sec,
            difficulty=difficulty,
            fail_tag=fail_tag,
            memo=memo,
        )

    # ID allocation + write happen atomically inside one exclusive lock.
    record = append_record_with_id(_build)
    append_schedules(record)

    print()
    print("[기록 저장 완료]")
    print(f"날짜: {record.date}")
    print(f"과목: {record.subject}")
    print(f"영역: {record.area}")
    print(f"문제: {record.problem_no}")
    print(f"결과: {'정답' if record.is_correct else '오답'}")
    if not record.is_correct:
        print(f"실패 태그: {record.fail_tag}")
        print("복습 예정:")
        print(f"- 1일 후: {record.review_1d}")
        print(f"- 3일 후: {record.review_3d}")
        print(f"- 7일 후: {record.review_7d}")


def done_review_interactive() -> None:
    schedule_df = load_schedule()
    records_df = load_records()
    if schedule_df.empty:
        print("복습 스케줄이 비어 있습니다. python main.py add 로 먼저 기록하세요.")
        return

    today_ts = pd.Timestamp(date.today())
    due = schedule_df[(schedule_df["review_date_dt"] <= today_ts) & (~schedule_df["is_done"])]
    if due.empty:
        print("오늘 복습할 항목이 없습니다.")
        return

    if not records_df.empty:
        merged = due.merge(
            records_df[["id", "subject", "area", "problem_no"]],
            left_on="record_id", right_on="id", how="left",
        )
    else:
        merged = due.assign(subject="?", area="?", problem_no="?")
    merged = merged.sort_values("review_date_dt").reset_index(drop=True)

    print("오늘 복습 대상:")
    for i, row in merged.iterrows():
        print(f"  {i+1}) {row['subject']} / {row['area']} / {row['problem_no']} / {row['review_type']}")

    print()
    raw = prompt("완료한 번호를 입력하세요. 예: 1,2 또는 all : ")
    raw_norm = raw.strip().lower()

    if raw_norm in ("all", "전체"):
        selected_idx = list(range(len(merged)))
    else:
        try:
            selected_idx = [int(x.strip()) - 1 for x in raw.split(",") if x.strip()]
        except ValueError:
            print("입력 형식 오류. 처리하지 않았습니다.")
            return
        if not selected_idx:
            print("선택된 항목이 없습니다.")
            return
        invalid = [i + 1 for i in selected_idx if i < 0 or i >= len(merged)]
        if invalid:
            print(f"범위 밖 번호: {invalid}. 처리하지 않았습니다.")
            return
        # dedupe while preserving order — '1,1,2' → '1,2'
        selected_idx = list(dict.fromkeys(selected_idx))

    updated = 0
    for i in selected_idx:
        row = merged.iloc[i]
        if mark_review_done(int(row["record_id"]), row["review_type"]):
            updated += 1

    print(f"[완료 처리됨: {updated}건]")
