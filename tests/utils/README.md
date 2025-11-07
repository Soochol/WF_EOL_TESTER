# Test Utilities

진단 및 유틸리티 도구 - 하드웨어 문제 해결 및 디버깅용 스크립트

## 파일 목록

### WT1806 Diagnostic Tools

- **test_wt1806_reset.py** - WT1806 상태 리셋 도구
  - 용도: WT1806이 TIM 상태에 갇혔을 때 복구
  - 실행: `:INTEGrate:STOP` + `:INTEGrate:RESet` + `*CLS`
  ```bash
  uv run python tests/utils/test_wt1806_reset.py
  ```

  **증상**: 에러 813 "Cannot be set while integration is running" 발생 시 사용

- **test_wt1806_error_command.py** - SCPI 에러 명령어 테스트
  - `:STATUS:ERROR?` vs `:SYSTem:ERRor?` 비교 테스트
  - WT1806 호환성 검증
  ```bash
  uv run python tests/utils/test_wt1806_error_command.py
  ```

  **결과**:
  - ✅ `:STATUS:ERROR?` - 작동 (SCPI 표준)
  - ❌ `:SYSTem:ERRor?` - 타임아웃 (비표준)

### Connection Tools

- **test_visa_usb_connection.py** - VISA USB 연결 테스트
  - PyVISA 설치 확인
  - USB 연결 상태 확인
  - 장치 ID 조회
  ```bash
  uv run python tests/utils/test_visa_usb_connection.py
  ```

## 사용 시나리오

### 시나리오 1: WT1806이 응답하지 않음
```bash
# 1. 연결 상태 확인
uv run python tests/utils/test_visa_usb_connection.py

# 2. 상태 리셋
uv run python tests/utils/test_wt1806_reset.py

# 3. 통합 테스트 재실행
uv run python tests/integration/test_wt1806_integration_basic.py
```

### 시나리오 2: 에러 813 발생
```bash
# WT1806 상태 리셋
uv run python tests/utils/test_wt1806_reset.py
```

### 시나리오 3: 타임아웃 발생
```bash
# 에러 명령어 호환성 확인
uv run python tests/utils/test_wt1806_error_command.py
```

## 문제 해결 가이드

### Error 813: "Cannot be set while integration is running"
**원인**: WT1806이 이전 테스트에서 TIM 상태로 남아있음
**해결**: `test_wt1806_reset.py` 실행

### Error 844: "Attempted to stop integration..."
**원인**: TIMER 모드에서 타이머가 만료되어 자동 중지됨
**해결**: 정상 동작 - 에러 아님

### Timeout on :SYSTem:ERRor?
**원인**: WT1806은 :SYSTem:ERRor? 명령어 미지원
**해결**: :STATUS:ERROR? 사용 (이미 구현됨)

## 개발 참고사항

### WT1806 Integration States
- **RES** - Reset (리셋 완료)
- **STAR** - Start (적산 진행 중)
- **TIM** - Time Up (타이머 만료)
- **STOP** - Stopped (수동 정지)

### 에러 코드
- **85** - Remote mode button lock (무시 가능)
- **813** - Integration running (리셋 필요)
- **844** - Already stopped (TIMER 모드 정상)
