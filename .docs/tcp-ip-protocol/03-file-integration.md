# 파일 기반 연동 사양

> **Version**: 1.1.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 JSON 파일을 통한 NeuroHub Client와의 연동 방식을 정의합니다.
네트워크 프로그래밍이 어려운 레거시 장비나 단순 연동이 필요한 경우에 적합합니다.

> **핵심 원칙**: 검사 장비 SW는 **WIP ID(serial_number)와 검사 결과만 전송**합니다.
> 작업자 ID, 공정 ID, 설비 ID는 NeuroHub Client에서 설정된 값을 사용합니다.

## 동작 원리

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   검사 장비     │     │ NeuroHub Client │     │  Backend API    │
│   (파일 생성)   │     │   (파일 감시)   │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │  1. JSON 파일 저장     │                       │
         │  (pending 폴더)       │                       │
         │──────────────────────>│                       │
         │                       │                       │
         │                       │  2. 파일 감지 (3초 주기)│
         │                       │                       │
         │                       │  3. JSON 파싱 & 검증   │
         │                       │                       │
         │                       │  4. API 전송          │
         │                       │──────────────────────>│
         │                       │                       │
         │                       │  5. 응답 수신          │
         │                       │<──────────────────────│
         │                       │                       │
         │                       │  6. 파일 이동          │
         │                       │  (completed/error)    │
         │                       │                       │
```

## 폴더 구조

### 기본 경로

```
C:/neurohub_work/
├── pending/          # 처리 대기 파일
├── completed/        # 처리 완료 파일
└── error/            # 처리 실패 파일
```

### 경로 설정

| 항목 | 기본값 | 설명 |
|------|--------|------|
| **기본 폴더** | `C:/neurohub_work` | 설정에서 변경 가능 |
| **대기 폴더** | `{base}/pending` | 새 파일 저장 위치 |
| **완료 폴더** | `{base}/completed` | 성공 처리 파일 이동 |
| **에러 폴더** | `{base}/error` | 실패 파일 이동 |

> **참고**: NeuroHub Client 설정에서 기본 폴더 경로를 변경할 수 있습니다.

---

## 파일 규칙

### 파일명 형식

```
result_{timestamp}_{identifier}.json
```

**예시:**
```
result_20250126_143052_001.json
result_20250126_143052_VOLTAGE.json
result_20250126_143052_a1b2c3d4.json
```

### 권장 명명 패턴

| 패턴 | 설명 | 예시 |
|------|------|------|
| `result_{YYYYMMDD}_{HHMMSS}_{seq}.json` | 날짜시간 + 순번 | `result_20250126_143052_001.json` |
| `result_{timestamp_ms}.json` | Unix 타임스탬프 | `result_1706252052123.json` |
| `result_{uuid}.json` | UUID | `result_a1b2c3d4-e5f6-7890.json` |

### 파일 확장자

- 반드시 `.json` 확장자 사용
- 대소문자 구분 없음 (`.JSON`, `.Json` 허용)

### 인코딩

- **UTF-8** (BOM 없음 권장)
- UTF-8 BOM (0xEF 0xBB 0xBF)도 허용

---

## JSON 파일 형식

### 전체 스키마

파일 기반 연동은 TCP 방식보다 확장된 스키마를 지원합니다.

```json
{
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS",
    "measurements": [...],
    "defect_data": [...],
    "process_data": {...}
}
```

### 필드 정의

| 필드 | 타입 | 필수 | 전송 주체 | 설명 |
|------|------|------|----------|------|
| `serial_number` | string | ✅ | 장비 | **WIP ID** (시리얼 번호) |
| `result` | string | ✅ | 장비 | 검사 결과 (`"PASS"` / `"FAIL"`) |
| `measurements` | array | ❌ | 장비 | 측정 항목 배열 |
| `defect_data` | array | ❌ | 장비 | 불량 항목 배열 |
| `process_data` | object | ❌ | 장비 | 추가 공정 데이터 (자유 형식) |

### Client에서 보충되는 정보 (장비에서 전송 불필요)

| 필드 | 설명 | Client 설정 위치 |
|------|------|-----------------|
| `worker_id` | 작업자 ID | 로그인한 사용자 |
| `process_id` | 공정 ID | 설정 화면 |
| `equipment_id` | 설비 ID | 설정 화면 |
| `lot_number` | LOT 번호 | WIP ID에서 추출 |

---

## 예제 파일

### 권장 예제 (WIP ID + 검사 결과)

```json
{
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS"
}
```

### 기본 예제 (측정 데이터 포함)

```json
{
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS",
    "measurements": [
        {
            "code": "VOLTAGE",
            "name": "전압",
            "value": 12.1,
            "unit": "V",
            "spec": {
                "min": 11.8,
                "max": 12.4,
                "target": 12.0
            },
            "result": "PASS"
        },
        {
            "code": "CURRENT",
            "name": "전류",
            "value": 2.5,
            "unit": "A",
            "spec": {
                "min": 2.0,
                "max": 3.0
            },
            "result": "PASS"
        }
    ]
}
```

### 전체 예제 (측정 데이터 포함)

```json
{
    "serial_number": "WIP-KR01PSA2511-001",
    "result": "PASS",
    "measurements": [
        {
            "code": "TEMP_SENSOR",
            "name": "온도 센서 측정",
            "value": 60.2,
            "unit": "°C",
            "spec": {
                "min": 55.0,
                "max": 65.0,
                "target": 60.0
            },
            "result": "PASS"
        },
        {
            "code": "HUMIDITY_SENSOR",
            "name": "습도 센서 측정",
            "value": 45.5,
            "unit": "%",
            "spec": {
                "min": 40.0,
                "max": 60.0
            },
            "result": "PASS"
        }
    ],
    "process_data": {
        "calibration_date": "2025-01-20",
        "firmware_version": "2.1.0",
        "test_cycle": 3
    }
}
```

### 불량 예제

```json
{
    "serial_number": "WIP-KR01PSA2511-002",
    "result": "FAIL",
    "measurements": [
        {
            "code": "TEMP_SENSOR",
            "name": "온도 센서 측정",
            "value": 72.5,
            "unit": "°C",
            "spec": {
                "min": 55.0,
                "max": 65.0,
                "target": 60.0
            },
            "result": "FAIL"
        }
    ],
    "defect_data": [
        {
            "code": "TEMP_SENSOR",
            "reason": "온도 상한 초과 (72.5°C > 65.0°C)"
        }
    ]
}
```

---

## 파일 처리 흐름

### 처리 상태 전이

```
                    ┌──────────────┐
                    │   pending/   │
                    │  (대기 중)   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  파일 감지   │
                    │  (3초 주기)  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  JSON 파싱   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │  성공   │  │공정불일치│  │파싱에러│
        └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │
             ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │completed│  │  error/ │  │  error/ │
        └─────────┘  └─────────┘  └─────────┘
```

### 파일 이동 규칙

| 상황 | 결과 | 대상 폴더 |
|------|------|-----------|
| JSON 파싱 성공 + API 전송 성공 | 성공 | `completed/` |
| JSON 파싱 성공 + API 전송 실패 | 실패 | `error/` |
| JSON 파싱 실패 | 실패 | `error/` |
| process_id 불일치 | 무시 | 원래 위치 유지 |

### 파일 잠금 및 충돌 방지

NeuroHub Client는 파일 처리 시:
1. 파일이 완전히 쓰여졌는지 확인 (파일 크기 안정화 대기)
2. 읽기 전용으로 파일 열기
3. 처리 완료 후 이동

**권장 사항 (검사 장비 측):**
- 임시 파일명으로 저장 후 `.json`으로 rename
- 파일 쓰기 완료 후 close 확실히 수행

```python
# 권장 패턴
import os
import tempfile

def save_result_safely(data, folder):
    # 임시 파일에 먼저 저장
    fd, temp_path = tempfile.mkstemp(suffix='.tmp', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 최종 파일명으로 rename (atomic operation)
        final_path = os.path.join(folder, f"result_{timestamp()}.json")
        os.rename(temp_path, final_path)
        return final_path
    except:
        os.unlink(temp_path)
        raise
```

---

## 폴더 감시 설정

### 감시 주기

| 항목 | 값 | 설명 |
|------|------|------|
| **스캔 간격** | 3초 | 파일 스캔 주기 |
| **파일 패턴** | `*.json` | 감시 대상 파일 |
| **최대 동시 처리** | 1개 | 파일당 순차 처리 |

### 성능 고려사항

- 대량 파일 발생 시 순차 처리로 인한 지연 가능
- 실시간 처리가 필요하면 TCP/IP 방식 권장
- 감시 폴더에 과도한 파일 축적 방지

---

## 에러 처리

### 에러 폴더 파일 형식

처리 실패한 파일은 `error/` 폴더로 이동되며, 에러 정보 파일이 함께 생성됩니다.

```
error/
├── result_20250126_143052_001.json           # 원본 파일
└── result_20250126_143052_001.json.error     # 에러 정보
```

### 에러 정보 파일 예시

```json
{
    "original_file": "result_20250126_143052_001.json",
    "error_time": "2025-01-26T14:31:00+09:00",
    "error_type": "JSONDecodeError",
    "error_message": "Expecting property name: line 5 column 1",
    "stack_trace": "..."
}
```

### 에러 복구

1. `error/` 폴더의 파일 확인
2. JSON 오류 수정
3. 수정된 파일을 `pending/` 폴더로 이동
4. 자동 재처리

---

## 모니터링 및 디버깅

### 폴더 상태 확인

```bash
# pending 폴더 파일 수 확인
dir C:\neurohub_work\pending\*.json | find /c ".json"

# error 폴더 확인
dir C:\neurohub_work\error\

# 실시간 모니터링 (PowerShell)
Get-ChildItem C:\neurohub_work\pending -Filter *.json |
    Select-Object Name, LastWriteTime, Length
```

### 테스트 파일 생성

```python
import json
from datetime import datetime

# 테스트 데이터 생성
test_data = {
    "result": "PASS",
    "measurements": [
        {
            "code": "TEST",
            "name": "테스트 측정",
            "value": 100.0,
            "unit": "unit",
            "result": "PASS"
        }
    ]
}

# 파일 저장
filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}_test.json"
filepath = f"C:/neurohub_work/pending/{filename}"

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print(f"테스트 파일 생성: {filepath}")
```

---

## 체크리스트

파일 기반 연동 구현 시 확인 사항:

- [ ] 폴더 경로 확인 (`C:/neurohub_work/pending`)
- [ ] 폴더 쓰기 권한 확인
- [ ] UTF-8 인코딩 사용
- [ ] `.json` 확장자 사용
- [ ] JSON 유효성 검증
- [ ] 임시 파일 → rename 패턴 적용
- [ ] 에러 폴더 모니터링 프로세스 구축
- [ ] 파일 정리 정책 수립 (completed 폴더)

---

## TCP vs 파일 비교

| 항목 | TCP/IP | 파일 기반 |
|------|--------|-----------|
| **실시간성** | ✅ 즉시 | ⚠️ 3초 지연 |
| **구현 난이도** | 중간 | 쉬움 |
| **응답 확인** | ✅ ACK 수신 | ❌ 파일 이동 확인 |
| **대용량 데이터** | ✅ 스트리밍 | ⚠️ 파일 크기 제한 |
| **네트워크 필요** | ✅ | ❌ |
| **디버깅** | 중간 | 쉬움 (파일 확인) |

---

*다음: [에러 처리](./04-error-handling.md)*
