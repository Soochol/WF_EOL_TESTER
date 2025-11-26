# TCP/IP 프로토콜 사양

> **Version**: 1.1.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 로컬 검사 장비 SW가 NeuroHub Client와 TCP/IP 소켓 통신을 수행하기 위한 프로토콜을 정의합니다.

> **핵심 원칙**: 검사 장비 SW는 **WIP ID(serial_number)와 검사 결과만 전송**합니다.
> 작업자 ID, 공정 ID, 설비 ID는 NeuroHub Client에서 설정된 값을 사용합니다.

## 연결 정보

| 항목 | 값 | 설명 |
|------|------|------|
| **Protocol** | TCP | Transmission Control Protocol |
| **Host** | `127.0.0.1` (기본값) | NeuroHub Client가 실행 중인 호스트 |
| **Port** | `9000` (기본값) | 설정에서 변경 가능 |
| **Encoding** | UTF-8 | 모든 문자열은 UTF-8로 인코딩 |
| **Data Format** | JSON | JavaScript Object Notation |

## 메시지 프레이밍

### 권장 방식: 길이 프리픽스 (Length-Prefixed)

데이터 무결성을 보장하기 위해 **길이 프리픽스 방식**을 권장합니다.

```
┌─────────────────┬─────────────────────────────────────┐
│  Length Header  │           JSON Payload              │
│   (4 bytes)     │         (Variable length)           │
├─────────────────┼─────────────────────────────────────┤
│ Big Endian      │ UTF-8 encoded JSON string           │
│ Unsigned Int    │                                     │
└─────────────────┴─────────────────────────────────────┘
```

**프레임 구조:**

| 오프셋 | 크기 | 타입 | 설명 |
|--------|------|------|------|
| 0 | 4 bytes | uint32 (Big Endian) | JSON 페이로드 길이 |
| 4 | N bytes | UTF-8 string | JSON 데이터 |

**예시 (바이트 레벨):**

JSON 데이터: `{"result":"PASS"}` (18 바이트)

```
Bytes: [0x00][0x00][0x00][0x12][0x7B][0x22][0x72][0x65]...
        |___________________|  |________________________
           Length = 18              JSON payload
```

### 대체 방식: 직접 전송 (Direct Mode)

길이 프리픽스 없이 JSON을 직접 전송할 수도 있습니다.    
이 경우 연결 종료 시점까지 데이터를 수신합니다.

```
┌─────────────────────────────────────┐
│           JSON Payload              │
│    (Connection close signals end)   │
└─────────────────────────────────────┘
```

> **주의**: 직접 전송 방식은 대용량 데이터에서 불안정할 수 있습니다.

## 통신 시퀀스

### 기본 통신 흐름

```
┌──────────────┐                    ┌──────────────────┐
│  검사 장비   │                    │  NeuroHub Client │
│  (Client)    │                    │    (Server)      │
└──────┬───────┘                    └────────┬─────────┘
       │                                     │
       │  1. TCP Connect (port 9000)         │
       │────────────────────────────────────>│
       │                                     │
       │  2. Connection Accepted             │
       │<────────────────────────────────────│
       │                                     │
       │  3. Send Length Header (4 bytes)    │
       │────────────────────────────────────>│
       │                                     │
       │  4. Send JSON Payload               │
       │────────────────────────────────────>│
       │                                     │
       │  5. Receive ACK Response            │
       │<────────────────────────────────────│
       │                                     │
       │  6. Close Connection                │
       │─────────────────────────────────────│
       │                                     │
```

### 상세 단계

#### Step 1: 연결 수립

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 9000))
```

#### Step 2: 데이터 준비

```python
# 착공 (START) 메시지 - WIP ID만 전송
start_data = {
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"  # WIP ID (필수)
}

# 완공 (COMPLETE) 메시지 - WIP ID + 검사 결과
complete_data = {
    "message_type": "COMPLETE",
    "serial_number": "WIP-KR01PSA2511-001",  # WIP ID (필수)
    "result": "PASS",
    "measurements": [...]
}

json_bytes = json.dumps(start_data, ensure_ascii=False).encode('utf-8')
```

#### Step 3: 길이 헤더 전송

```python
length = len(json_bytes)
length_header = length.to_bytes(4, byteorder='big')
sock.sendall(length_header)
```

#### Step 4: JSON 페이로드 전송

```python
sock.sendall(json_bytes)
```

#### Step 5: ACK 수신

```python
response = sock.recv(4096)
ack = json.loads(response.decode('utf-8'))
```

#### Step 6: 연결 종료

```python
sock.close()
```

## ACK 응답 형식

서버는 데이터 수신 후 JSON 형식의 ACK를 반환합니다.

### 착공 성공 응답

```json
{
    "status": "OK",
    "message": "Start data received",
    "message_type": "START"
}
```

### 완공 성공 응답

```json
{
    "status": "OK",
    "message": "Complete data received",
    "message_type": "COMPLETE"
}
```

### 실패 응답

```json
{
    "status": "ERROR",
    "message": "JSON 파싱 오류: Expecting property name"
}
```

### 응답 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `status` | string | ✅ | `"OK"` 또는 `"ERROR"` |
| `message` | string | ✅ | 상태 설명 메시지 |
| `message_type` | string | ❌ | 처리된 메시지 타입 (`"START"` 또는 `"COMPLETE"`) |

## 타임아웃 및 재시도

### 권장 타임아웃 설정

| 항목 | 권장값 | 설명 |
|------|--------|------|
| **연결 타임아웃** | 5초 | 서버 연결 대기 시간 |
| **송신 타임아웃** | 10초 | 데이터 전송 대기 시간 |
| **수신 타임아웃** | 10초 | ACK 응답 대기 시간 |

### 재시도 정책

```python
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

for attempt in range(MAX_RETRIES):
    try:
        send_result(data)
        break
    except (socket.timeout, ConnectionRefusedError) as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
        else:
            raise
```

## 연결 관리

### Single Request per Connection (권장)

각 검사 결과마다 새로운 연결을 생성합니다.

```
[Connect] → [Send] → [Receive ACK] → [Close]
[Connect] → [Send] → [Receive ACK] → [Close]
...
```

**장점:**
- 구현 단순
- 연결 상태 관리 불필요
- 오류 복구 용이

### Keep-Alive (선택적)

연속적인 검사에서 연결을 유지할 수 있습니다.

```
[Connect] → [Send] → [ACK] → [Send] → [ACK] → ... → [Close]
```

> **주의**: 현재 서버는 연결당 단일 메시지 처리 후 대기 상태로 전환됩니다.
> Keep-Alive 사용 시 서버측 설정 확인이 필요합니다.

## 버퍼 크기

| 항목 | 크기 | 설명 |
|------|------|------|
| **서버 수신 버퍼** | 64KB (65536 bytes) | JSON 페이로드 최대 크기 |
| **ACK 응답 버퍼** | 4KB (4096 bytes) | 응답 수신 버퍼 |

> **주의**: JSON 페이로드가 64KB를 초과하면 분할 수신됩니다.
> 대용량 데이터 전송 시 반드시 길이 프리픽스 방식을 사용하세요.

## 네트워크 에러 처리

### 일반적인 에러 상황

| 에러 | 원인 | 대응 |
|------|------|------|
| `ConnectionRefusedError` | NeuroHub Client 미실행 | 클라이언트 실행 상태 확인 |
| `socket.timeout` | 서버 응답 지연 | 재시도 또는 타임아웃 증가 |
| `BrokenPipeError` | 연결 끊김 | 재연결 후 재전송 |
| `ConnectionResetError` | 서버측 연결 리셋 | 재연결 후 재전송 |

### 에러 복구 플로우

```
┌─────────────────┐
│   Send Data     │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ Success?│──Yes──> Done
    └────┬────┘
         │No
         ▼
    ┌─────────┐
    │ Retry?  │──No───> Log Error & Alert
    └────┬────┘
         │Yes
         ▼
    ┌─────────┐
    │  Wait   │
    │(backoff)│
    └────┬────┘
         │
         └──────> Reconnect & Retry
```

## 보안 고려사항

### 현재 지원

- 로컬호스트 통신 (127.0.0.1)
- 평문 JSON 전송

### 향후 지원 예정

- TLS/SSL 암호화 (wss://)
- 인증 토큰 기반 접근 제어

## 디버깅 및 테스트

### 연결 테스트

```bash
# telnet으로 연결 테스트
telnet 127.0.0.1 9000

# netcat으로 데이터 전송
echo '{"result":"PASS","measurements":[]}' | nc 127.0.0.1 9000
```

### 장비 시뮬레이터 사용

NeuroHub는 테스트용 장비 시뮬레이터를 제공합니다:

```bash
cd neurohub_client/tools
python equipment_simulator.py --result PASS
```

### Wireshark 분석

TCP 통신 디버깅 시 Wireshark 필터:
```
tcp.port == 9000
```

## 체크리스트

검사 장비 SW 개발 시 확인 사항:

- [ ] UTF-8 인코딩 사용
- [ ] JSON 유효성 검증
- [ ] 길이 프리픽스 Big Endian 형식
- [ ] 타임아웃 설정
- [ ] 재시도 로직 구현
- [ ] 에러 로깅
- [ ] ACK 응답 확인

---

*다음: [JSON 메시지 스키마](./02-json-schema.md)*
