# Legacy Test Files

개발 과정에서 사용한 실험용/디버깅용 테스트 파일들

⚠️ **주의**: 이 파일들은 현재 프로덕션에서 사용되지 않으며, 참고용으로만 보관됩니다.

## 파일 목록

### WT1800E USB Connection Tests (개발 과정)

개발 초기에 PyVISA USB 연결을 검증하기 위해 작성된 여러 버전의 테스트들:

- **test_wt1800e_usb_minimal.py** - 최소한의 연결 테스트
- **test_wt1800e_usb_simple.py** - 단순 연결 및 *IDN? 조회
- **test_wt1800e_usb_improved.py** - 개선된 버전
- **test_wt1800e_usb_final.py** - 최종 작동 버전
- **test_wt1800e_usb_numeric.py** - NUMERIC 명령어 테스트
- **test_wt1800e_usb_fetch.py** - 데이터 fetch 테스트
- **test_wt1800e_usb_termination.py** - Termination character 테스트

### Command Tests

- **test_wt1800e_command_test.py** - 다양한 SCPI 명령어 테스트
- **test_wt1806_usb_success.py** - WT1806 USB 연결 성공 케이스

## 개발 히스토리

### Phase 1: USB 연결 수립 (초기)
- PyVISA-py 백엔드 사용
- USB 리소스 문자열 생성
- Timeout 설정 및 조정

### Phase 2: SCPI 명령어 테스트
- 다양한 명령어 조합 실험
- Termination character 검증
- 에러 처리 로직 개선

### Phase 3: Integration 구현 (완료)
최종 구현은 다음 파일들로 대체됨:
- `tests/integration/test_wt1806_integration_basic.py`
- `tests/integration/test_wt1806_integration_cycle.py`
- `src/infrastructure/implementation/hardware/power_analyzer/wt1800e/`

## 사용하지 않는 이유

1. **중복성**: 최종 통합 테스트에 모든 기능이 포함됨
2. **유지보수**: 구조화된 테스트 프레임워크로 이전
3. **일관성**: Clean Architecture 패턴에 맞지 않음

## 보관 이유

- 개발 과정 참고 자료
- 문제 해결 시 히스토리 추적
- USB 연결 디버깅 예제

## 삭제 가능 여부

✅ **안전하게 삭제 가능** - 모든 기능이 최신 코드에 구현됨

단, 삭제 전 권장사항:
1. git commit으로 보관
2. 주요 학습 내용을 문서화로 이전
3. 프로덕션 테스트가 안정적으로 작동하는지 확인

---

**마지막 업데이트**: 2025-11-07
**상태**: Archived (참고용 보관)
