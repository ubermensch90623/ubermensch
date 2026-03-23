# NCS PDF 문제 추출기

PDF 형태의 NCS 문제집/기출 자료에서 텍스트를 읽어 문항 단위로 분리하고, 카테고리별로 정리된 JSON/Markdown 결과물을 만드는 CLI 시스템입니다.

## 주요 기능
- PDF 파일 또는 디렉터리 단위 입력 지원
- 문항 번호 패턴(`1.`, `2)`, `문제 3.` 등)을 기준으로 자동 분리
- 선택지, 정답, 해설을 최대한 구조화해서 추출
- 키워드 기반으로 NCS 영역(의사소통, 수리, 문제해결, 자원관리, 정보, 기술)을 자동 분류
- 결과물을 JSON + Markdown 동시 생성

## 설치
```bash
python -m pip install -e .
```

개발용 테스트까지 설치하려면:

```bash
python -m pip install -e .[dev]
```

## 사용 방법
```bash
ncs-extract ./pdfs --output-dir ./output
```

또는 단일 파일:

```bash
ncs-extract ./pdfs/sample.pdf
```

실행 결과:
- `output/sample.json`: 원본 문항 + 카테고리별 정리 JSON
- `output/sample.md`: 사람이 검토하기 쉬운 Markdown 리포트

## JSON 출력 예시
```json
{
  "document": {
    "source_file": "sample.pdf",
    "problem_count": 2,
    "problems": [
      {
        "number": "1.",
        "page": 1,
        "category": "의사소통",
        "question": "1. 다음 보고서 작성 원칙으로 가장 적절한 것은?",
        "choices": [
          "핵심 없이 길게 작성한다",
          "수신자를 고려해 명확하게 작성한다"
        ],
        "answer": "②",
        "explanation": "보고서는 목적과 수신자를 반영해야 한다.",
        "source_file": "sample.pdf"
      }
    ]
  },
  "by_category": {
    "의사소통": [
      {
        "number": "1.",
        "page": 1
      }
    ]
  }
}
```

## 동작 방식
1. `pypdf`로 각 페이지 텍스트를 추출합니다.
2. 정규식으로 문항 시작점을 찾아 페이지별 문항 블록을 분리합니다.
3. 선택지/정답/해설을 후처리해서 구조화합니다.
4. 키워드 규칙으로 카테고리를 추정합니다.
5. JSON/Markdown 파일로 저장합니다.

## 한계와 확장 아이디어
- 스캔본 PDF처럼 텍스트 레이어가 없는 파일은 OCR 연동이 추가로 필요합니다.
- 표/도형 중심 문제는 텍스트만으로 완전 복원되지 않을 수 있습니다.
- 카테고리 분류는 현재 휴리스틱 기반이므로, 향후 LLM 또는 분류 모델로 고도화할 수 있습니다.
- 정답이 별도 페이지에 모여 있는 PDF는 추가 매칭 로직이 필요할 수 있습니다.
