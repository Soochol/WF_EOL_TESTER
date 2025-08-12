# MCU 통신 비교 테스트

## 목적
시리얼 포트 모니터에서는 딜레이 없이 정상 동작하는데, 현재 프로젝트에서는 3초 대기가 필요한 이유를 분석합니다.

## 테스트 구조

### 1. `simple_serial_test.py`
- **목적**: 시리얼 포트 모니터와 동일한 방식으로 직접 통신
- **특징**: pyserial 직접 사용, 최소한의 오버헤드
- **예상 결과**: 딜레이 없이 정상 동작

### 2. `current_code_test.py` 
- **목적**: 현재 프로젝트의 LMAMCU 클래스로 동일한 시퀀스 테스트
- **특징**: 기존 코드 그대로 사용
- **예상 결과**: 3초 대기 필요성 확인

### 3. `timing_comparison.py`
- **목적**: 두 방식의 성능 차이 분석
- **특징**: 타이밍 비교, 병목 지점 식별
- **예상 결과**: 근본 원인 파악

## 테스트 시나리오
실제 로그에서 확인된 패킷 시퀀스:
```
1. CMD_ENTER_TEST_MODE (모드 1)
2. CMD_SET_UPPER_TEMP (52°C)
3. CMD_SET_FAN_SPEED (레벨 10) 
4. CMD_LMA_INIT (동작:52°C, 대기:35°C, 홀드:10초)
5. 온도 도달 대기 (STATUS_OPERATING_TEMP_REACHED)
6. CMD_STROKE_INIT_COMPLETE
7. 최종 완료 대기 (STATUS_STANDBY_TEMP_REACHED)
```

## 사용법
```bash
# 1. 단순 시리얼 테스트
python simple_serial_test.py

# 2. 현재 코드 테스트  
python current_code_test.py

# 3. 결과 비교 분석
python timing_comparison.py
```

## 연결 설정
MCU 연결 전 포트와 설정을 확인하세요:
- **포트**: COM4 (Windows) 또는 /dev/ttyUSB0 (Linux)
- **보드레이트**: 115200
- **데이터 비트**: 8
- **정지 비트**: 1
- **패리티**: None