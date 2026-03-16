---
applyTo: "scripts/**"
description: "Verification commands and regression checks for build, Sigma API, Claude, cache, and git safety."
---

# Verification Runbook

## 1. 목적

핵심 기능 회귀를 빠르게 확인할 때 쓰는 검증 절차 모음입니다.

## 2. 권장 순서

1. Sigma 헬스체크
2. Sigma 목록/상세 API 확인
3. 앱 내부 `SigmaApiClient` 확인
4. Claude 실호출 확인
5. UI 실행 확인
6. 빌드 확인
7. git 추적 안전성 확인

## 3. 자주 쓰는 검증 명령

Sigma 헬스체크:

```powershell
try {
    (Invoke-WebRequest -Uri "https://127.0.0.1:57443/health/simple/" -UseBasicParsing -SkipCertificateCheck -TimeoutSec 3).Content
} catch {
    $_.Exception.Message
}
```

앱 내부 SigmaApiClient 확인:

```powershell
d:/Github/Ai-Builder/.venv/Scripts/python.exe -c "import sys, json; sys.path.insert(0, 'src'); from ai_builder.services.sigma_api import SigmaApiClient; client=SigmaApiClient('192.168.0.11', 'sigma_your_key'); out={}; out['health_check']=client.health_check(); enc=client.get_encounters('2026-02-14'); out['encounter_count']=len(enc.get('results', [])) if isinstance(enc, dict) else None; out['first_encounter_uuid']=(enc.get('results') or [{}])[0].get('encounter_uuid') if enc.get('results') else None; print(json.dumps(out, ensure_ascii=False))"
```

Claude 실호출 확인:

```powershell
d:/Github/Ai-Builder/.venv/Scripts/python.exe -c "import sys, json; sys.path.insert(0, 'src'); from conf.nnconf.nnconfig import nn_conf; from ai_builder.services.ai_service import AiService; prompt='You are a medical documentation extraction assistant. Return ONLY a single valid JSON object with keys chief_complaint, onset, subjective, objective, assessment, plan, metadata. metadata must include primary_diagnosis as string and follow_up_needed as boolean. Use empty strings when information is not present and do not infer unsupported facts.'; note='환자가 3일 전부터 목 통증과 두통을 호소함. 발열은 없고, 경부 압통이 약간 있음. 근육 긴장 의심. 추가 진통제 복용 여부는 말하지 않음.'; text = AiService.enhance_with_claude(prompt, note); parsed = json.loads(text); print(json.dumps({'selected_model': nn_conf.claude_model_id, 'json_parse_ok': isinstance(parsed, dict), 'keys': sorted(parsed.keys())}, ensure_ascii=False))"
```

빌드 확인:

```powershell
Set-Location "d:/Github/Ai-Builder"
$env:Path = "d:/Github/Ai-Builder/.venv/Scripts;" + $env:Path
cmd /c build.bat
```

git 추적 안전성:

```powershell
Set-Location "d:/Github/Ai-Builder"
git check-ignore -v data/settings.sqlite3
git status --short
```

## 4. 체크 포인트

- 진료 목록 헤더가 `No.` / `Name`인지 확인합니다.
- 환자 선택 시 우측 원문이 갱신되는지 확인합니다.
- 서버 `external_note`가 없을 때 로컬 캐시가 복원되는지 확인합니다.
- 결과가 있으면 복사 버튼이 의미 있게 동작하는지 확인합니다.
- Claude 응답이 코드펜스 없이 JSON으로 파싱되는지 확인합니다.
- `dist/AiBuilder.exe`가 생성되고 기동 가능한지 확인합니다.

## 5. 실패 시 우선 조사 순서

1. 네트워크/서버 상태
2. SSL/인증서 신뢰 문제
3. Sigma API Key
4. AI Key 및 모델 ID
5. `data/settings.sqlite3` 설정값
6. Claude 정규화 및 JSON 검증 로직
7. `.ui` 파일과 generated UI 불일치
