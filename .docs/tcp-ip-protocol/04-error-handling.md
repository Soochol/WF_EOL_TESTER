# 에러 처리 사양

> **Version**: 1.0.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 NeuroHub Client와의 연동 시 발생할 수 있는 에러 유형과 처리 방법을 정의합니다.

## 에러 분류

```
┌─────────────────────────────────────────────────────────────┐
│                        에러 유형                            │
├─────────────────┬─────────────────┬─────────────────────────┤
│   연결 에러     │   데이터 에러   │      비즈니스 에러      │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • 연결 거부     │ • JSON 파싱     │ • 공정 불일치           │
│ • 타임아웃      │ • 필수 필드 누락│ • 인증 만료             │
│ • 네트워크 단절 │ • 데이터 타입   │ • 중복 처리             │
│ • 포트 사용 중  │ • 값 범위 초과  │ • 권한 없음             │
└─────────────────┴─────────────────┴─────────────────────────┘
```

---

## 1. 연결 에러 (Connection Errors)

### 1.1 ConnectionRefusedError

**원인**: NeuroHub Client가 실행되지 않았거나 TCP 서버가 비활성화됨

**에러 메시지**:
```
[WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다.
```

**대응 방법**:
```python
import socket
import time

def connect_with_retry(host, port, max_retries=3, delay=2):
    """재시도 로직이 포함된 연결"""
    last_error = None

    for attempt in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            return sock
        except ConnectionRefusedError as e:
            last_error = e
            print(f"연결 실패 (시도 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff

    raise ConnectionError(f"연결 실패: {last_error}")
```

**사용자 알림**:
```
NeuroHub Client가 실행 중인지 확인하세요.
- 프로그램 실행 상태 확인
- TCP 서버 포트 설정 확인 (기본: 9000)
```

### 1.2 socket.timeout

**원인**: 서버 응답 지연 또는 네트워크 지연

**에러 메시지**:
```
timed out
```

**대응 방법**:
```python
def send_with_timeout(sock, data, timeout=10):
    """타임아웃 처리가 포함된 전송"""
    sock.settimeout(timeout)

    try:
        sock.sendall(data)
        response = sock.recv(4096)
        return response
    except socket.timeout:
        # 타임아웃 시 연결 상태 확인
        try:
            sock.getpeername()  # 연결 확인
            # 연결은 유지 중 - 재시도 가능
            raise TimeoutError("서버 응답 타임아웃 - 재시도 필요")
        except:
            # 연결 끊김
            raise ConnectionError("서버 연결 끊김")
```

### 1.3 네트워크 단절

**에러 유형**:
- `BrokenPipeError`: 파이프가 끊어짐
- `ConnectionResetError`: 연결이 리셋됨
- `OSError: [Errno 10054]`: 기존 연결이 원격 호스트에 의해 강제로 끊김

**대응 방법**:
```python
def safe_send(sock, data):
    """안전한 데이터 전송"""
    try:
        sock.sendall(data)
    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        # 연결 재수립 필요
        raise ConnectionError(f"연결 끊김: {e}")
```

---

## 2. 데이터 에러 (Data Errors)

### 2.1 JSON 파싱 에러

**에러 유형**:
- `json.JSONDecodeError`: 잘못된 JSON 형식
- `UnicodeDecodeError`: 인코딩 문제

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "JSON 파싱 오류: Expecting property name: line 3 column 5 (char 25)"
}
```

**검증 코드**:
```python
import json

def validate_json(data_bytes):
    """JSON 유효성 검증"""
    try:
        # UTF-8 디코딩
        text = data_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        return False, f"인코딩 오류: UTF-8 형식이 아님 ({e})"

    try:
        # JSON 파싱
        data = json.loads(text)
        return True, data
    except json.JSONDecodeError as e:
        return False, f"JSON 파싱 오류: {e.msg} (line {e.lineno} column {e.colno})"
```

**일반적인 JSON 오류**:

| 오류 | 원인 | 해결 |
|------|------|------|
| `Expecting property name` | 후행 쉼표 | 마지막 항목 뒤 쉼표 제거 |
| `Expecting ',' delimiter` | 쉼표 누락 | 항목 사이 쉼표 추가 |
| `Expecting value` | 빈 값 | 값 입력 또는 null 사용 |
| `Invalid \escape` | 이스케이프 오류 | 백슬래시 이스케이프 (`\\`) |
| `Unexpected UTF-8 BOM` | BOM 포함 | UTF-8 without BOM 사용 |

### 2.2 필수 필드 누락

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "필수 필드 누락: 'result'"
}
```

**검증 코드**:
```python
def validate_required_fields(data):
    """필수 필드 검증"""
    errors = []

    # 루트 필수 필드
    if 'result' not in data:
        errors.append("필수 필드 누락: 'result'")

    # result 값 검증
    if 'result' in data and data['result'] not in ('PASS', 'FAIL'):
        errors.append(f"잘못된 result 값: '{data['result']}' (PASS 또는 FAIL)")

    # measurements 검증
    if 'measurements' in data:
        for i, item in enumerate(data['measurements']):
            if 'code' not in item:
                errors.append(f"measurements[{i}]: 필수 필드 누락 'code'")
            if 'value' not in item:
                errors.append(f"measurements[{i}]: 필수 필드 누락 'value'")
            if 'result' not in item:
                errors.append(f"measurements[{i}]: 필수 필드 누락 'result'")

    return errors
```

### 2.3 데이터 타입 오류

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "데이터 타입 오류: measurements[0].value는 숫자여야 합니다"
}
```

**잘못된 예시**:
```json
{
    "result": "PASS",
    "measurements": [
        {
            "code": "VOLTAGE",
            "value": "12.1",  // ❌ 문자열 대신 숫자 사용
            "result": "PASS"
        }
    ]
}
```

**올바른 예시**:
```json
{
    "result": "PASS",
    "measurements": [
        {
            "code": "VOLTAGE",
            "value": 12.1,  // ✅ 숫자 타입
            "result": "PASS"
        }
    ]
}
```

---

## 3. 비즈니스 에러 (Business Errors)

### 3.1 공정 불일치

**상황**: 파일의 `process_id`와 현재 선택된 공정이 다름

**처리**:
- 파일은 `pending/` 폴더에 유지됨 (이동 안 함)
- 다른 공정으로 전환 시 자동 처리

**확인 방법**:
```python
def check_process_match(file_data, current_process_id):
    """공정 ID 매칭 확인"""
    file_process = file_data.get('process_id')

    if file_process and file_process != current_process_id:
        return False, f"공정 불일치: 파일({file_process}) != 현재({current_process_id})"

    return True, None
```

### 3.2 인증 만료

**Backend API 응답**: `401 Unauthorized`

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "인증이 만료되었습니다. 다시 로그인해주세요."
}
```

**대응**:
- NeuroHub Client에서 재로그인 필요
- 자동 재시도하지 않음 (사용자 개입 필요)

### 3.3 중복 처리

**Backend API 응답**: `409 Conflict`

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "이미 처리된 작업입니다"
}
```

**처리**:
- 파일은 `completed/` 폴더로 이동 (중복이지만 정상 종료)
- 로그에 경고 기록

### 3.4 서버 오류

**Backend API 응답**: `500 Internal Server Error`

**ACK 응답**:
```json
{
    "status": "ERROR",
    "message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
}
```

**대응**:
- 자동 재시도 (최대 3회)
- Exponential backoff 적용

---

## 4. ACK 응답 코드 정리

### 성공 응답

| 상태 | 메시지 | 설명 |
|------|--------|------|
| `OK` | `Data received successfully` | 데이터 정상 수신 및 처리 |

### 에러 응답

| 상태 | 메시지 패턴 | 원인 | 대응 |
|------|------------|------|------|
| `ERROR` | `JSON 파싱 오류: ...` | JSON 형식 오류 | JSON 수정 후 재전송 |
| `ERROR` | `필수 필드 누락: ...` | 필수 필드 없음 | 필드 추가 후 재전송 |
| `ERROR` | `데이터 타입 오류: ...` | 타입 불일치 | 타입 수정 후 재전송 |
| `ERROR` | `인증이 만료되었습니다` | 토큰 만료 | 재로그인 후 재시도 |
| `ERROR` | `이미 처리된 작업입니다` | 중복 요청 | 무시 가능 |
| `ERROR` | `서버 오류가 발생했습니다` | 서버 장애 | 재시도 |

---

## 5. 에러 처리 플로우차트

```
                        ┌────────────────┐
                        │  데이터 전송   │
                        └───────┬────────┘
                                │
                        ┌───────▼────────┐
                        │  연결 성공?    │
                        └───────┬────────┘
                                │
                    ┌───────────┼───────────┐
                    │No                     │Yes
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │ 재시도 가능?  │       │  ACK 수신?    │
            └───────┬───────┘       └───────┬───────┘
                    │                       │
        ┌───────────┼───────┐   ┌───────────┼───────────┐
        │Yes                │No │No                     │Yes
        ▼                   ▼   ▼                       ▼
┌───────────────┐   ┌─────────────┐   ┌─────────┐  ┌─────────────┐
│ 대기 후 재시도│   │ 에러 기록   │   │타임아웃 │  │ status=OK?  │
│               │   │ 사용자 알림 │   │ 재시도  │  └──────┬──────┘
└───────────────┘   └─────────────┘   └─────────┘         │
                                              ┌───────────┼───────────┐
                                              │Yes                    │No
                                              ▼                       ▼
                                        ┌─────────┐           ┌─────────────┐
                                        │  완료   │           │ 에러 메시지 │
                                        └─────────┘           │ 파싱 & 처리 │
                                                              └─────────────┘
```

---

## 6. 권장 에러 처리 구현

### 6.1 완전한 에러 처리 예제

```python
import socket
import json
import time
import logging
from enum import Enum
from typing import Tuple, Optional, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    JSON_PARSE = "json_parse"
    VALIDATION = "validation"
    AUTH = "auth"
    SERVER = "server"
    UNKNOWN = "unknown"


class NeuroHubError(Exception):
    """NeuroHub 통신 에러"""
    def __init__(self, error_type: ErrorType, message: str, retryable: bool = False):
        self.error_type = error_type
        self.message = message
        self.retryable = retryable
        super().__init__(message)


class NeuroHubClient:
    """NeuroHub 통신 클라이언트"""

    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        self.host = host
        self.port = port
        self.max_retries = 3
        self.base_delay = 2

    def send_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """검사 결과 전송 (재시도 로직 포함)"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return self._send_once(data)
            except NeuroHubError as e:
                last_error = e
                logger.warning(f"전송 실패 (시도 {attempt + 1}/{self.max_retries}): {e.message}")

                if not e.retryable:
                    raise

                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)

        raise last_error

    def _send_once(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """단일 전송 시도"""
        # 1. 데이터 검증
        self._validate_data(data)

        # 2. JSON 직렬화
        try:
            json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        except (TypeError, ValueError) as e:
            raise NeuroHubError(
                ErrorType.JSON_PARSE,
                f"JSON 직렬화 오류: {e}",
                retryable=False
            )

        # 3. 연결
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            raise NeuroHubError(
                ErrorType.CONNECTION,
                "NeuroHub Client에 연결할 수 없습니다",
                retryable=True
            )
        except socket.timeout:
            raise NeuroHubError(
                ErrorType.TIMEOUT,
                "연결 타임아웃",
                retryable=True
            )

        try:
            # 4. 길이 헤더 + 데이터 전송
            length_header = len(json_bytes).to_bytes(4, byteorder='big')
            sock.settimeout(10)
            sock.sendall(length_header)
            sock.sendall(json_bytes)

            # 5. ACK 수신
            response = sock.recv(4096)
            if not response:
                raise NeuroHubError(
                    ErrorType.CONNECTION,
                    "서버 응답 없음",
                    retryable=True
                )

            # 6. ACK 파싱
            ack = json.loads(response.decode('utf-8'))
            return self._handle_ack(ack)

        except socket.timeout:
            raise NeuroHubError(
                ErrorType.TIMEOUT,
                "응답 타임아웃",
                retryable=True
            )
        except (BrokenPipeError, ConnectionResetError) as e:
            raise NeuroHubError(
                ErrorType.CONNECTION,
                f"연결 끊김: {e}",
                retryable=True
            )
        finally:
            if sock:
                sock.close()

    def _validate_data(self, data: Dict[str, Any]):
        """데이터 유효성 사전 검증"""
        if 'result' not in data:
            raise NeuroHubError(
                ErrorType.VALIDATION,
                "필수 필드 누락: 'result'",
                retryable=False
            )

        if data['result'] not in ('PASS', 'FAIL'):
            raise NeuroHubError(
                ErrorType.VALIDATION,
                f"잘못된 result 값: '{data['result']}'",
                retryable=False
            )

    def _handle_ack(self, ack: Dict[str, Any]) -> Dict[str, Any]:
        """ACK 응답 처리"""
        status = ack.get('status')
        message = ack.get('message', '')

        if status == 'OK':
            logger.info(f"전송 성공: {message}")
            return ack

        # 에러 유형 판별
        if '인증' in message or 'auth' in message.lower():
            raise NeuroHubError(ErrorType.AUTH, message, retryable=False)
        elif '서버 오류' in message or 'server' in message.lower():
            raise NeuroHubError(ErrorType.SERVER, message, retryable=True)
        elif 'JSON' in message or '파싱' in message:
            raise NeuroHubError(ErrorType.JSON_PARSE, message, retryable=False)
        elif '필드' in message or '타입' in message:
            raise NeuroHubError(ErrorType.VALIDATION, message, retryable=False)
        else:
            raise NeuroHubError(ErrorType.UNKNOWN, message, retryable=False)


# 사용 예시
if __name__ == "__main__":
    client = NeuroHubClient()

    data = {
        "result": "PASS",
        "measurements": [
            {
                "code": "VOLTAGE",
                "value": 12.1,
                "result": "PASS"
            }
        ]
    }

    try:
        result = client.send_result(data)
        print(f"성공: {result}")
    except NeuroHubError as e:
        print(f"실패 [{e.error_type.value}]: {e.message}")
        if e.retryable:
            print("  → 재시도 가능한 에러입니다")
        else:
            print("  → 데이터 수정 후 재시도하세요")
```

---

## 7. 로깅 권장사항

### 로그 레벨

| 레벨 | 용도 |
|------|------|
| `DEBUG` | 상세 통신 내용 (개발용) |
| `INFO` | 정상 처리 완료 |
| `WARNING` | 재시도 발생, 경고 |
| `ERROR` | 처리 실패 |
| `CRITICAL` | 시스템 장애 |

### 로그 포맷 권장

```python
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
```

### 로그 예시

```
2025-01-26 14:30:15 [INFO] neurohub: 검사 결과 전송 시작
2025-01-26 14:30:15 [DEBUG] neurohub: 연결 시도 127.0.0.1:9000
2025-01-26 14:30:15 [DEBUG] neurohub: 데이터 전송 (256 bytes)
2025-01-26 14:30:15 [INFO] neurohub: 전송 성공: Data received successfully
2025-01-26 14:30:20 [WARNING] neurohub: 연결 실패 (시도 1/3): 연결 거부
2025-01-26 14:30:22 [INFO] neurohub: 2초 후 재시도...
2025-01-26 14:30:24 [INFO] neurohub: 전송 성공: Data received successfully
```

---

## 8. 체크리스트

에러 처리 구현 시 확인 사항:

- [ ] 연결 에러 처리 (ConnectionRefusedError)
- [ ] 타임아웃 처리 (socket.timeout)
- [ ] 재시도 로직 구현 (exponential backoff)
- [ ] JSON 사전 검증
- [ ] ACK 응답 파싱 및 처리
- [ ] 로깅 구현
- [ ] 사용자 알림 UI 연동

---

*다음: [예제 코드](./05-examples.md)*
