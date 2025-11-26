# NeuroHub 로컬 검사 장비 연동 사양서

> **Version**: 1.0.0
> **Last Updated**: 2025-01-26
> **Status**: Draft

## 개요

이 문서는 NeuroHub Client(`neurohub_client`)와 로컬 검사/조립 장비 간의 통신 인터페이스 사양을 정의합니다.
로컬 검사 SW 개발자는 이 사양에 따라 NeuroHub 시스템과 연동할 수 있습니다.

## 문서 구조

| 문서 | 설명 |
|------|------|
| [TCP/IP 프로토콜 사양](./01-tcp-protocol.md) | 소켓 통신 프로토콜 상세 |
| [JSON 메시지 스키마](./02-json-schema.md) | 데이터 구조 및 필드 정의 |
| [파일 기반 연동](./03-file-integration.md) | JSON 파일 모니터링 방식 |
| [에러 처리](./04-error-handling.md) | 에러 코드 및 처리 방법 |
| [예제 코드](./05-examples.md) | 언어별 구현 예제 |

## 연동 방식 선택 가이드

NeuroHub는 두 가지 연동 방식을 지원합니다:

### 1. TCP/IP 소켓 통신 (권장)

```
[검사 장비 SW] ---(TCP/JSON)---> [NeuroHub Client:9000] ---(REST API)---> [Backend]
```

**장점:**
- 실시간 데이터 전송
- 즉시 응답 확인 (ACK/NACK)
- 양방향 통신 가능

**적합한 경우:**
- 실시간 결과 반영이 필요한 경우
- 검사 장비가 네트워크 프로그래밍을 지원하는 경우
- 즉시 결과 확인이 필요한 경우

### 2. 파일 기반 연동

```
[검사 장비 SW] ---(JSON 파일 저장)---> [감시 폴더] ---(파일 감지)---> [NeuroHub Client]
```

**장점:**
- 구현이 단순 (파일 저장만 하면 됨)
- 네트워크 프로그래밍 불필요
- 검사 장비 SW 수정 최소화

**적합한 경우:**
- 레거시 장비 연동
- 네트워크 프로그래밍이 어려운 경우
- 배치 처리가 가능한 경우

## 통신 흐름도

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  로컬 검사 SW   │     │ NeuroHub Client │     │  Backend API    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │  (사전) Client에서 작업자 로그인, 공정/설비 설정  │
         │                       │                       │
         │  1. START + WIP ID    │                       │
         │──────────────────────>│  2. 착공 요청          │
         │                       │   (WIP ID + 작업자/공정/설비)
         │                       │──────────────────────>│
         │                       │  3. 착공 확인          │
         │  4. ACK               │<──────────────────────│
         │<──────────────────────│                       │
         │                       │                       │
         │  ~~~~ 검사 수행 ~~~~   │                       │
         │                       │                       │
         │  5. COMPLETE + 결과   │                       │
         │──────────────────────>│  6. 완공 요청          │
         │                       │   (WIP ID + 검사결과)   │
         │                       │──────────────────────>│
         │                       │  7. 완공 확인          │
         │  8. ACK               │<──────────────────────│
         │<──────────────────────│                       │
         │                       │                       │
```

> **중요**: 검사 장비 SW는 WIP ID(시리얼 번호)와 검사 결과만 전송합니다.
> 작업자 ID, 공정 ID, 설비 ID는 NeuroHub Client에서 설정된 값을 사용합니다.

## 빠른 시작

### TCP/IP 연동 (Python 예제)

```python
import socket
import json

def send_to_neurohub(data: dict, host="127.0.0.1", port=9000):
    """메시지를 NeuroHub Client로 전송"""
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        # 길이 프리픽스 전송 (4바이트, Big Endian)
        length = len(json_data)
        sock.sendall(length.to_bytes(4, byteorder='big'))

        # JSON 데이터 전송
        sock.sendall(json_data)

        # ACK 수신
        response = sock.recv(4096)
        return json.loads(response.decode('utf-8'))

# 착공 (START) - WIP ID만 전송
start_msg = {
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"  # WIP ID (필수)
}
ack = send_to_neurohub(start_msg)
print(f"착공 응답: {ack}")

# ... 검사 수행 ...

# 완공 (COMPLETE) - WIP ID + 검사 결과 전송
complete_msg = {
    "message_type": "COMPLETE",
    "serial_number": "WIP-KR01PSA2511-001",  # WIP ID (필수)
    "result": "PASS",
    "measurements": [
        {
            "code": "VOLTAGE",
            "name": "전압 측정",
            "value": 12.1,
            "unit": "V",
            "spec": {"min": 11.8, "max": 12.4, "target": 12.0},
            "result": "PASS"
        }
    ]
}
ack = send_to_neurohub(complete_msg)
print(f"완공 응답: {ack}")
```

### 파일 기반 연동

```python
import json
from datetime import datetime

def save_result_file(data: dict, folder="C:/neurohub_work/pending"):
    """검사 결과를 JSON 파일로 저장"""
    filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    filepath = f"{folder}/{filename}"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath
```

## 연락처

기술 지원 문의:
- Email: support@f2x.co.kr
- 담당자: 개발팀

---

*이 문서는 NeuroHub 프로젝트의 일부입니다.*
