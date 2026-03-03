# Ubermensch Project

## Auto Memory
- Auto memory is enabled for this project
- Claude will automatically save learnings and patterns to `~/.claude/projects/<project>/memory/`
- Memory persists across sessions and is loaded at the start of each conversation

## Skills

### /simplify - 코드 자동 정리
- 기능 구현이나 버그 수정 후 `/simplify`를 실행하면 코드를 자동으로 정리
- 3개 리뷰 에이전트를 병렬 실행:
  1. **코드 재사용 검토**: 기존 유틸리티/헬퍼와 중복되는 코드 탐지
  2. **코드 품질 검토**: 중복 상태, 복붙 코드, 추상화 누수 등 검토
  3. **효율성 검토**: 불필요한 연산, 병렬화 누락, 메모리 누수 등 검토
- 사용법: `/simplify` 또는 `/simplify src/specific-file.ts`

### /batch - 대규모 병렬 코드 변경
- 대규모 변경을 독립적인 작업 단위(5~30개)로 분해 후 병렬 실행
- 각 에이전트가 격리된 git worktree에서 독립적으로 작업
- 작업 완료 후 자동으로 테스트 실행 및 PR 생성
- 사용법: `/batch migrate src/ from Solid to React`
