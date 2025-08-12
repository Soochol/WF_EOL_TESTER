# DIOMonitoringService 검증 가이드

이 가이드는 DIOMonitoringService의 버튼 콜백 flow가 올바르게 동작하는지 검증하는 방법을 설명합니다.

## 개요

DIOMonitoringService는 다음과 같은 flow로 동작합니다:

1. **초기화**: Digital I/O 서비스 연결, 하드웨어 설정 로드, 콜백 함수 설정
2. **모니터링**: 0.1초마다 모든 입력 채널 읽기 및 edge detection
3. **버튼 처리**: 이중 버튼 press 감지 및 안전 센서 확인
4. **콜백 실행**: 모든 조건 충족 시 start_button_callback 실행
5. **Debounce**: 2초 대기 후 다음 입력 허용

## 하드웨어 설정 (기본값)

- **왼쪽 버튼**: 채널 8, B-contact (Normally Closed), falling edge
- **오른쪽 버튼**: 채널 9, B-contact (Normally Closed), falling edge
- **Emergency Stop**: 채널 3, A-contact (Normally Open), rising edge
- **안전 센서들**:
  - Door sensor: 채널 10, B-contact, rising edge
  - Clamp sensor: 채널 14, A-contact, rising edge
  - Chain sensor: 채널 15, A-contact, rising edge

## 검증 방법

### 1. 자동 검증 도구 사용

가장 간단한 방법은 제공된 검증 도구를 사용하는 것입니다:

```bash
# 기본 검증 테스트 실행
./verify_dio.sh test

# 연속 모니터링 (60초)
./verify_dio.sh monitor 60

# 도움말
./verify_dio.sh help
```

### 2. 메인 애플리케이션에서 확인

메인 애플리케이션을 실행하면 자동으로 검증 로그가 출력됩니다:

```bash
python main.py
```

로그에서 다음 키워드들을 확인하세요:

- `🔧 VERIFICATION`: 초기화 검증
- `🔧 DIO_INIT`: DIOMonitoringService 초기화
- `🔧 DIO_START`: 모니터링 시작
- `🎯 DIO_CYCLE`: 버튼 감지 및 처리
- `🚀 DIO_CALLBACK`: 콜백 실행
- `📋 VERIFICATION_REPORT`: 종합 상태 보고서

### 3. 수동 버튼 테스트

다음 시나리오들을 테스트해보세요:

#### 시나리오 1: 단일 버튼 Press
- 왼쪽 또는 오른쪽 버튼만 누름
- **예상 결과**: Edge 감지되지만 콜백 실행되지 않음
- **로그**: `Single button press detected` 메시지

#### 시나리오 2: 이중 버튼 Press (안전 센서 미충족)
- 양쪽 버튼 동시에 누르지만 안전 센서 조건 불충족
- **예상 결과**: 이중 press 감지되지만 안전 조건으로 인해 차단
- **로그**: `❌ DIO_SAFETY: Safety sensors not satisfied`

#### 시나리오 3: 이중 버튼 Press (모든 조건 충족)
- 양쪽 버튼 동시에 누르고 모든 안전 센서 조건 충족
- **예상 결과**: 콜백 함수 실행, EOL 테스트 시작
- **로그**: `🎯 VERIFICATION: Button press callback triggered`

#### 시나리오 4: Emergency Stop
- Emergency stop 버튼 press
- **예상 결과**: 즉시 emergency stop 콜백 실행
- **로그**: `🚨 VERIFICATION: Emergency stop callback triggered`

## 로그 분석

### 정상 동작 로그 예시

```
🔧 VERIFICATION: Digital I/O service connection status: True
🔧 VERIFICATION: Hardware config loaded successfully
🔧 DIO_INIT: Channel configuration built - 6 channels configured
✅ DIOMonitoringService initialized
🔧 DIO_START: Button monitoring service started successfully
📋 VERIFICATION_REPORT: Starting comprehensive verification report...
🎯 DIO_CYCLE: Edge detected on channels: [8]
🎯 DIO_BUTTON: Processing button press on channel 8
🎯 DIO_BUTTON: ✅ DUAL BUTTON PRESS DETECTED!
✅ DIO_SAFETY: All safety sensors satisfied!
🚀 DIO_CALLBACK: Starting dual button press handler...
🎯 VERIFICATION: Button press callback triggered - Starting EOL test...
✅ CALLBACK_EXEC: Button press callback executed successfully
```

### 문제 발생 시 로그 예시

```
❌ VERIFICATION: Failed to connect Digital I/O service: Connection refused
⚠️ DIO_CYCLE: Digital I/O service not connected, waiting...
❌ DIO_SAFETY: Safety sensors not satisfied - Clamp: False, Chain: True, Door: True
❌ CALLBACK_EXEC: Error executing button press callback: EOL test already running
```

## 문제 해결

### 1. Digital I/O 연결 실패
- 하드웨어 연결 확인
- AJINEXTEK 드라이버 설치 확인
- Mock 모드로 테스트 (`AXL_MOCK_MODE=true`)

### 2. 버튼이 감지되지 않음
- 하드웨어 채널 번호 확인
- Contact type 설정 확인 (A-contact vs B-contact)
- Edge type 설정 확인 (rising vs falling)

### 3. 안전 센서 문제
- 각 안전 센서의 연결 상태 확인
- 센서 논리 상태 확인 (A-contact/B-contact)
- Verification report에서 현재 센서 상태 확인

### 4. 콜백이 실행되지 않음
- 콜백 함수가 올바르게 설정되었는지 확인
- EOL 테스트가 이미 실행 중인지 확인
- Debounce 시간 대기 후 재시도

## 고급 디버깅

### 상세 상태 확인

검증 도구의 `get_detailed_status()` 메서드를 사용하여 모든 상태를 확인할 수 있습니다:

```python
status = await dio_monitoring_service.get_detailed_status()
print(json.dumps(status, indent=2))
```

### 로그 레벨 조정

더 상세한 로그를 보려면 로그 레벨을 DEBUG로 설정:

```python
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```

### 타이밍 파라미터 조정

필요에 따라 타이밍 파라미터 조정:

```python
dio_monitoring_service.set_polling_interval(0.05)  # 50ms
dio_monitoring_service.set_debounce_time(1.0)      # 1초
```

## 결론

이 검증 프로세스를 통해 DIOMonitoringService의 전체 flow가 올바르게 동작하는지 확인할 수 있습니다. 문제가 발생하면 로그를 주의 깊게 분석하고 위의 문제 해결 가이드를 참조하세요.