# Integration Tests

통합 테스트 디렉토리 - 실제 하드웨어와의 통합 테스트 스크립트

## 파일 목록

### WT1806 Integration Tests (Production)

- **test_wt1806_integration_basic.py** - 기본 10초 통합 테스트
  - 빠른 검증용 (10초 사이클)
  - WH, AH, TIME 측정 확인
  ```bash
  uv run python tests/integration/test_wt1806_integration_basic.py
  ```

- **test_wt1806_integration_cycle.py** - 멀티 사이클 통합 테스트
  - 3 사이클 × 10초 = ~50초
  - 통계 분석 (min, max, average)
  ```bash
  uv run python tests/integration/test_wt1806_integration_cycle.py
  ```

- **test_wt1806_production_integration.py** - 프로덕션 통합 테스트
  - 실제 제품 테스트용 긴 사이클
  ```bash
  uv run python tests/integration/test_wt1806_production_integration.py
  ```

### Mock Hardware Tests

- **test_mock_power_integration.py** - Mock Power Analyzer 통합 테스트
- **test_robot_integration.py** - Robot 통합 테스트

## 사용법

### 전제 조건
- WT1806 Power Analyzer가 USB로 연결되어 있어야 함
- PyVISA 및 드라이버 설치 완료

### 빠른 검증
```bash
# 기본 테스트 (10초)
uv run python tests/integration/test_wt1806_integration_basic.py

# 사이클 테스트 (50초)
uv run python tests/integration/test_wt1806_integration_cycle.py
```

### 주의사항
- 테스트 중 WT1806의 전면 패널이 잠김 (Remote Mode)
- 에러 844는 TIMER 모드에서 정상적인 동작
- 테스트 완료 후 자동으로 연결 해제됨

## 개발 히스토리

### 2025-11-07
- ✅ WT1806 integration 기능 구현 완료
- ✅ 에러 처리 개선 (844, 813, 85 필터링)
- ✅ :STATUS:ERROR? 명령어로 변경 (SCPI 표준)
- ✅ 통합 상태 리셋 로직 추가
