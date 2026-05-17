# ubermensch

이 레포는 [gbrain](https://github.com/garrytan/gbrain) (AI 에이전트용 영구 메모리)을
Claude Code와 함께 쓰기 위한 setup을 포함합니다.

## 빠른 시작

1) gbrain 설치 (최초 1회):

   ```bash
   ./scripts/setup-gbrain.sh
   gbrain init          # API 키 입력 등 대화형 초기화
   ```

2) 노트/문서 인덱싱:

   ```bash
   gbrain import ~/notes/
   ```

3) 동작 확인:

   ```bash
   gbrain query "무슨 주제가 자주 나오지?"
   ```

4) Claude Code에서 사용:

   - 이 레포 루트에 `.mcp.json` 이 있어서 Claude Code를 이 디렉터리에서 열면
     `gbrain` MCP 서버에 자동 연결됩니다.
   - 세션 안에서 `/mcp` 로 연결 상태 확인.

## 파일 구성

- `.mcp.json` — Claude Code용 MCP 서버 설정 (gbrain stdio)
- `scripts/setup-gbrain.sh` — clone + bun install + bun link 자동화
- `.gitignore` — 로컬 gbrain 데이터 제외

## 참고

- gbrain은 `bun link` 방식의 전역 설치를 권장합니다 (npm/bun global은
  postinstall 훅 문제로 실패할 수 있음).
- 정확한 최신 설치 가이드는 항상 [상위 레포](https://github.com/garrytan/gbrain)
  README를 확인하세요.
