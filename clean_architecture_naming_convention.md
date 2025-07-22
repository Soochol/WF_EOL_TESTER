# Clean Architecture 네이밍 컨벤션 정리

## 🏗️ 올바른 Clean Architecture 네이밍 규칙

### 📋 네이밍 매트릭스

| 레이어 | 컴포넌트 유형 | 네이밍 패턴 | 예시 | 위치 |
|--------|---------------|-------------|------|------|
| **Application** | Interface | `Service` | `PowerService` | `src/application/interfaces/` |
| **Application** | Use Case | `UseCase` | `ExecuteEOLTestUseCase` | `src/application/use_cases/` |
| **Application** | Command | `Command` | `ExecuteEOLTestCommand` | `src/application/commands/` |
| **Application** | Result | `Result` | `EOLTestResult` | `src/application/results/` |
| **Infrastructure** | Service 구현체 | `ServiceImpl` | `PowerServiceImpl` | `src/infrastructure/service_implementations/` |
| **Infrastructure** | 어댑터 | `Adapter` | `OdaPowerAdapter` | `src/infrastructure/hardware_adapters/` |
| **Infrastructure** | Repository 구현체 | `Repository` | `SQLiteTestRepository` | `src/infrastructure/repositories/` |
| **Infrastructure** | 기존 Controller | `Controller` | `OdaPowerSupply` | `src/infrastructure/controllers/` (보존) |
| **Presentation** | Controller | `Controller` | `TestExecutionController` | `src/presentation/controllers/` |
| **Presentation** | DTO | `DTO` | `EOLTestRequestDTO` | `src/presentation/dto/` |
| **Domain** | Entity | 명사 | `EOLTest` | `src/domain/entities/` |
| **Domain** | Value Object | 명사 | `ForceValue` | `src/domain/value_objects/` |
| **Domain** | Exception | `Exception` | `InvalidMeasurementException` | `src/domain/exceptions/` |

### 🔄 의존성 흐름 및 네이밍

#### 1. Application Layer 인터페이스
```python
# src/application/interfaces/power_service.py
class PowerService(ABC):
    """Application Layer에서 정의하는 Service 인터페이스"""
    
    @abstractmethod
    async def set_voltage(self, voltage: Voltage) -> None:
        pass
```

#### 2. Infrastructure Layer 구현체
```python
# src/infrastructure/service_implementations/power_service_impl.py
class PowerServiceImpl(PowerService):
    """PowerService 인터페이스의 Infrastructure 구현체"""
    
    def __init__(self, power_adapter: OdaPowerAdapter):
        self._adapter = power_adapter
```

#### 3. Hardware Adapter (어댑터 패턴)
```python
# src/infrastructure/hardware_adapters/oda_power_adapter.py
class OdaPowerAdapter:
    """기존 ODA Controller를 새로운 Service 인터페이스에 맞추는 어댑터"""
    
    def __init__(self, oda_controller: OdaPowerSupply):
        self._oda_controller = oda_controller  # 기존 Controller 재사용
```

#### 4. 기존 Controller (보존)
```python
# src/infrastructure/controllers/power_controller/oda/oda_power_supply.py
class OdaPowerSupply:
    """기존 ODA 전원공급기 Controller (그대로 보존)"""
    
    def __init__(self, connection_info: str):
        # 기존 구현 그대로 유지
        pass
```

### 🎯 핵심 원칙

#### 1. 인터페이스는 Application Layer에서 정의
```yaml
❌ 잘못된 방식: Infrastructure에서 Service 인터페이스 정의
✅ 올바른 방식: Application에서 Service 인터페이스 정의
```

#### 2. 구현체는 Infrastructure Layer에서 구현
```yaml
❌ 잘못된 이름: PowerControllerService
✅ 올바른 이름: PowerServiceImpl
```

#### 3. 어댑터는 기존 코드와 새 인터페이스 연결
```yaml
❌ 잘못된 방식: 기존 Controller 직접 수정
✅ 올바른 방식: Adapter로 기존 Controller 래핑
```

#### 4. 기존 Controller는 최대한 보존
```yaml
❌ 잘못된 방식: 기존 Controller 삭제하고 새로 작성
✅ 올바른 방식: 기존 Controller 보존하고 Adapter로 연결
```

### 🗂️ 디렉토리 구조 (최종)

```
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── exceptions/
├── application/
│   ├── interfaces/
│   │   ├── power_service.py              # PowerService 인터페이스
│   │   ├── loadcell_service.py           # LoadCellService 인터페이스
│   │   └── ...
│   ├── use_cases/
│   ├── commands/
│   └── results/
├── infrastructure/
│   ├── service_implementations/
│   │   ├── power_service_impl.py         # PowerService 구현체 (기존 Controller 직접 사용)
│   │   ├── loadcell_service_impl.py      # LoadCellService 구현체 (기존 Controller 직접 사용)
│   │   └── ...
│   ├── repositories/
│   │   ├── sqlite_test_repository.py     # Repository 구현체
│   │   └── ...
│   ├── external_services/
│   │   ├── console_notification_impl.py  # 외부 서비스 구현체
│   │   └── ...
│   └── controllers/ (기존 보존)
│       ├── power_controller/
│       ├── loadcell_controller/
│       └── ...
├── presentation/
│   ├── controllers/
│   ├── cli/
│   └── dto/
└── frameworks/
    ├── ajinextek/
    ├── serial/
    └── ...
```

### 💡 마이그레이션 전략

#### Phase 1: Application Layer 인터페이스 정의
```python
# 새로 생성: src/application/interfaces/power_service.py
class PowerService(ABC):
    pass
```

#### Phase 2: Infrastructure Layer Adapter 생성
```python
# 새로 생성: src/infrastructure/hardware_adapters/oda_power_adapter.py
class OdaPowerAdapter:
    def __init__(self, oda_controller: OdaPowerSupply):
        self._oda_controller = oda_controller  # 기존 Controller 재사용
```

#### Phase 3: Infrastructure Layer 구현체 생성
```python
# 새로 생성: src/infrastructure/service_implementations/power_service_impl.py
class PowerServiceImpl(PowerService):
    def __init__(self, power_adapter: OdaPowerAdapter):
        self._adapter = power_adapter
```

#### Phase 4: 기존 Controller는 그대로 보존
```python
# 보존: src/infrastructure/controllers/power_controller/oda/oda_power_supply.py
class OdaPowerSupply:
    # 기존 구현 그대로 유지
    pass
```

이 네이밍 컨벤션을 통해 Clean Architecture의 의존성 규칙을 준수하면서 기존 코드를 최대한 재활용할 수 있습니다.