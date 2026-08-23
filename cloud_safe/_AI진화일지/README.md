# v1 호환 착륙장 (landing zone)

구 routine 프롬프트가 쓰는 경로 `cloud_safe/_AI진화일지/`.
**정본은 `cloud_safe/_SSOT/_AI진화일지/`** 이며, 여기 쌓인 파일은
`append_result.sh` 실행 시 정본으로 자동 이관된다.

심링크로는 안 되는 이유: `git add` 가 심링크를 통과하지 못함
(`fatal: pathspec ... is beyond a symbolic link`) → v1 의 push 가 계속 실패.
따라서 실제 디렉토리로 둔다. 종환이 프롬프트를 v2 로 교체하면 이 폴더는 비게 된다.
