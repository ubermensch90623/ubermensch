from ncs_pdf_extractor.parser import extract_problems_from_pages, infer_category, regroup_by_category


def test_extract_problems_from_pages_splits_and_classifies_questions() -> None:
    pages = [
        {
            "page": 1,
            "text": """
1. 다음 보고서 작성 원칙으로 가장 적절한 것은?
① 핵심 없이 길게 작성한다
② 수신자를 고려해 명확하게 작성한다
③ 수치는 생략한다
④ 제목은 불필요하다
정답: ②
해설: 보고서는 목적과 수신자를 반영해야 한다.

2. 표를 보고 생산량 증가율을 계산하시오.
① 5%
② 10%
③ 15%
④ 20%
정답: ③
            """,
        }
    ]

    document = extract_problems_from_pages(pages, source_file="sample.pdf")

    assert len(document.problems) == 2
    assert document.problems[0].category == "의사소통"
    assert document.problems[0].answer == "②"
    assert document.problems[1].category == "수리"
    assert document.problems[1].choices == ["5%", "10%", "15%", "20%"]


def test_regroup_by_category_returns_bucketed_payload() -> None:
    pages = [
        {"page": 3, "text": "1. 예산 집행 우선순위를 정하시오.\n① 인건비\n② 홍보비"}
    ]
    document = extract_problems_from_pages(pages, source_file="budget.pdf")

    grouped = regroup_by_category(document)

    assert list(grouped) == ["자원관리"]
    assert grouped["자원관리"][0]["page"] == 3


def test_infer_category_defaults_to_unknown() -> None:
    assert infer_category("철학적인 사고 실험 문제") == "미분류"
