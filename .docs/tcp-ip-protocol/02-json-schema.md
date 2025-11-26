# JSON 메시지 스키마 사양

> **Version**: 1.2.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 검사 장비 SW가 NeuroHub Client로 전송하는 JSON 메시지의 구조와 필드를 정의합니다.

> **핵심 원칙**: 검사 장비 SW는 **WIP ID(serial_number)와 검사 결과만 전송**합니다.
> 작업자 ID, 공정 ID, 설비 ID는 NeuroHub Client에서 설정된 값을 사용합니다.

## 메시지 타입

NeuroHub는 **두 가지 메시지 타입**을 지원합니다:

| 타입 | `message_type` | 용도 | 전송 방향 |
|------|----------------|------|----------|
| **StartData** | `"START"` | 착공 (작업 시작) 알림 | 장비 → NeuroHub |
| **EquipmentData** | `"COMPLETE"` | 완공 (검사/측정 결과) 데이터 | 장비 → NeuroHub |
| **AckResponse** | - | 수신 확인 응답 | NeuroHub → 장비 |

> **참고**: `message_type`이 없으면 기본값 `"COMPLETE"`로 처리됩니다 (하위 호환성).

---

## 1. StartData (착공 알림)

검사 장비가 작업 시작 시 NeuroHub Client로 전송하는 메시지입니다.

> **중요**: 검사 장비 SW는 **WIP ID(serial_number)만 전송**하면 됩니다.

### 스키마 개요

```json
{
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"
}
```

### StartData 필드 정의

| 필드 | 타입 | 필수 | 전송 주체 | 설명 | 예시 |
|------|------|------|----------|------|------|
| `message_type` | string | ✅ | 장비 | 메시지 타입 (반드시 `"START"`) | `"START"` |
| `serial_number` | string | ✅ | 장비 | **WIP ID** (시리얼 번호) | `"WIP-KR01PSA2511-001"` |

### Client에서 보충되는 정보 (장비에서 전송 불필요)

| 필드 | 설명 | Client 설정 위치 |
|------|------|-----------------|
| `worker_id` | 작업자 ID | 로그인한 사용자 |
| `process_id` | 공정 ID | 설정 화면 |
| `equipment_id` | 설비 ID | 설정 화면 |

### StartData 예제

#### 권장 예제 (장비에서 전송)

```json
{
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"
}
```

---

## 2. EquipmentData (완공 결과 데이터)

검사 장비가 작업 완료 시 NeuroHub Client로 전송하는 메시지입니다.

> **중요**: 검사 장비 SW는 **WIP ID와 검사 결과만 전송**하면 됩니다.

### 스키마 개요

```json
{
    "message_type": "COMPLETE",
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS",
    "measurements": [...]
}
```

### EquipmentData 필드 정의

| 필드 | 타입 | 필수 | 전송 주체 | 설명 |
|------|------|------|----------|------|
| `message_type` | string | ✅ | 장비 | 메시지 타입 (`"COMPLETE"`) |
| `serial_number` | string | ✅ | 장비 | **WIP ID** (시리얼 번호) |
| `result` | string | ✅ | 장비 | 전체 검사 결과 (`"PASS"` 또는 `"FAIL"`) |
| `measurements` | array | ❌ | 장비 | 측정 항목 배열 |
| `defects` | array | ❌ | 장비 | 불량 항목 배열 |

### Client에서 보충되는 정보 (장비에서 전송 불필요)

| 필드 | 설명 | Client 설정 위치 |
|------|------|-----------------|
| `worker_id` | 작업자 ID | 로그인한 사용자 |
| `process_id` | 공정 ID | 설정 화면 |
| `equipment_id` | 설비 ID | 설정 화면 |

### MeasurementItem (측정 항목)

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `code` | string | ✅ | 측정 항목 코드 | `"VOLTAGE"` |
| `name` | string | ❌ | 측정 항목 표시명 | `"전압 측정"` |
| `value` | number | ✅ | 측정값 | `12.1` |
| `unit` | string | ❌ | 측정 단위 | `"V"` |
| `spec` | object | ❌ | 스펙 한계값 | `{"min":11.8,"max":12.4}` |
| `result` | string | ✅ | 판정 결과 | `"PASS"` |

### DefectItem (불량 항목)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `code` | string | ✅ | 불량 코드 |
| `reason` | string | ❌ | 불량 사유 |

---

## 3. 예제 메시지

### 착공 (START)

```json
{
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"
}
```

### 완공 - PASS

```json
{
    "message_type": "COMPLETE",
    "serial_number": "WIP-KR01PSA2511-001",
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
```

### 완공 - FAIL

```json
{
    "message_type": "COMPLETE",
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "FAIL",
    "measurements": [
        {
            "code": "VOLTAGE",
            "value": 12.8,
            "result": "FAIL"
        }
    ],
    "defects": [
        {"code": "VOLTAGE", "reason": "상한 초과"}
    ]
}
```

### 하위 호환 (message_type 생략)

```json
{
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS",
    "measurements": [...]
}
```

---

## 4. 착공-완공 시퀀스

```
[검사 장비]                    [NeuroHub Client]                [Backend]
     │                               │                              │
     │  (사전) Client: 작업자 로그인, 공정/설비 설정                   │
     │                               │                              │
     │  1. START + WIP ID            │                              │
     │──────────────────────────────>│  2. 착공 요청                 │
     │                               │    (WIP ID + 작업자/공정/설비) │
     │                               │─────────────────────────────>│
     │                               │  3. 착공 확인                 │
     │  4. ACK                       │<─────────────────────────────│
     │<──────────────────────────────│                              │
     │                               │                              │
     │  ~~~~ 검사 수행 ~~~~          │                              │
     │                               │                              │
     │  5. COMPLETE + 결과           │                              │
     │──────────────────────────────>│  6. 완공 요청                 │
     │                               │    (WIP ID + 검사결과)        │
     │                               │─────────────────────────────>│
     │                               │  7. 완공 확인                 │
     │  8. ACK                       │<─────────────────────────────│
     │<──────────────────────────────│                              │
```

---

## 5. ACK 응답

### 착공 성공

```json
{
    "status": "OK",
    "message": "Start data received",
    "message_type": "START"
}
```

### 완공 성공

```json
{
    "status": "OK",
    "message": "Complete data received",
    "message_type": "COMPLETE"
}
```

### 실패

```json
{
    "status": "ERROR",
    "message": "JSON 파싱 오류: ..."
}
```

---

## 6. 측정 코드 표준 (권장)

| 코드 | 설명 | 단위 |
|------|------|------|
| `VOLTAGE` | 전압 | V |
| `CURRENT` | 전류 | A |
| `RESISTANCE` | 저항 | Ω |
| `TEMP` | 온도 | °C |
| `TORQUE` | 토크 | N·m |
| `PRESS_FORCE` | 압입력 | kgf |

---

*다음: [파일 기반 연동](./03-file-integration.md)*
