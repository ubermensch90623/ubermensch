@echo off
chcp 65001 >nul
title AI 에이전트 팀 데모

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Python이 없습니다!
    echo   https://www.python.org 에서 설치하세요.
    echo   설치할 때 "Add Python to PATH" 꼭 체크!
    echo.
    pause
    exit /b
)

echo.
echo   ==========================================
echo     AI 에이전트 팀 데모  (설치 필요 없음)
echo   ==========================================
echo.

python -c "
import time

print('  [1단계] AI 에이전트 팀 구성')
print()
time.sleep(0.5)

agents = {
    '보안전문가': '코드 보안 취약점을 찾는 AI',
    '성능전문가': '성능 병목을 찾는 AI',
    '코드리뷰어': '코드 품질을 검사하는 AI',
}

for name, desc in agents.items():
    print(f'    + {name} 합류  ({desc})')
    time.sleep(0.3)

print()
print('  [2단계] 태스크 배정')
print()

tasks = ['보안 취약점 분석', '성능 병목 분석', '코드 품질 검사']
for i, t in enumerate(tasks, 1):
    print(f'    #{i} {t}')
    time.sleep(0.2)

print()
print('  [3단계] 에이전트들이 동시에 작업 중...')
print()
time.sleep(1)

results = {
    '보안전문가': [
        '동시성 제어 (asyncio.Lock) → 양호',
        '사용자 입력 검증 → 개선 필요',
        'LLM 응답 파싱 시 injection 방어 → 권장',
    ],
    '성능전문가': [
        'asyncio.gather 병렬 처리 → 양호',
        '태스크 폴링 0.5초 간격 → Event 기반 개선 가능',
        '메모리 제한 없는 큐 → maxsize 설정 권장',
    ],
    '코드리뷰어': [
        '추상 클래스 패턴 → 일관성 양호',
        'Hook 데코레이터 API → 직관적',
        '타입 힌트 → 잘 적용됨',
    ],
}

print('  ==========================================')
print('    분석 결과')
print('  ==========================================')
print()

for agent, findings in results.items():
    print(f'    [{agent}]')
    for f in findings:
        print(f'      - {f}')
        time.sleep(0.15)
    print()

print('  [4단계] 보안전문가 vs 반론전문가 토론')
print()
time.sleep(0.5)

debate = [
    ('보안전문가', '분석', '입력 검증 미흡으로 injection 공격 가능성 있음'),
    ('반론전문가', '반론', '입력 검증은 프레임워크가 아니라 사용자 책임 아닌가?'),
    ('보안전문가', '대응', '맞지만 기본 sanitization은 프레임워크가 제공해야 함'),
]

for speaker, role, content in debate:
    print(f'    [{role}] {speaker}:')
    print(f'      {content}')
    print()
    time.sleep(0.5)

print('    [합의]')
print('      기본 구조는 견고함.')
print('      입력 검증 가이드 + 메모리 제한 옵션 추가 권장.')
print()
print('  ==========================================')
print('    데모 완료!')
print()
print('    이게 Ubermensch 프레임워크입니다.')
print('    여러 AI가 팀으로 일하는 구조.')
print('  ==========================================')
print()
"

pause
