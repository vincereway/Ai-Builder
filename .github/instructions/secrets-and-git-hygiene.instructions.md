---
applyTo: "**/*.py"
description: "Secret handling, public-repo hygiene, and git safety rules for Ai-Builder."
---

# Secrets And Git Hygiene

## 1. 핵심 원칙

절대 하지 말 것:

- 실제 API 키를 추적 파일에 저장
- 개인 이름, 개인 이메일, 회사 실명, 내부 서버 정보를 코드나 문서에 남김
- `data/settings.sqlite3` 같은 로컬 DB를 git에 추가
- 과거에 제거한 식별 정보를 다시 커밋

반드시 지킬 것:

- 비밀정보는 로컬 저장소에만 둡니다.
- 문서 예시는 더미 값만 사용합니다.
- 작업 전후에 git 추적 상태를 확인합니다.

## 2. 민감정보 저장 위치

주요 로컬 저장소:

- `data/settings.sqlite3`

민감 데이터 예시:

- Sigma / Gemini / OpenAI / Claude API Key
- 내부 Sigma 서버 IP
- System Prompt 본문
- 진료별 Enhance 결과 캐시

## 3. git 안전성

중요 규칙:

- `.gitignore`의 `*.sqlite3`, `data/`, `logs/`, `certs/`, `conf/conf.yml` 규칙을 유지합니다.
- 커밋 전 `git status --short`와 `git check-ignore -v data/settings.sqlite3`를 확인합니다.
- 실제 키 패턴과 식별 정보가 파일이나 문서에 들어갔는지 검색합니다.

## 4. Claude 관련 추가 주의

- Claude 키는 SQLite에만 저장합니다.
- `sk-ant` 패턴이 코드, 문서, 커밋 메시지에 직접 남지 않게 확인합니다.

## 5. 사고 대응 원칙

- 민감정보가 커밋되면 단순 revert 전에 노출 범위를 먼저 파악합니다.
- 공개 저장소에 push된 상태면 history rewrite 필요성을 즉시 판단합니다.
- 사용자 승인 없이 파괴적 git 명령은 실행하지 않습니다.
