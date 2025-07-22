# WF_EOL_TESTER Clean Architecture 설계

## 🎯 Domain Layer (1층) - 핵심 비즈니스 로직

### 도메인 엔티티 (Entities)

#### 1. EOL_Test (End-of-Line 테스트)
```python
@dataclass
class EOLTest:
    test_id: TestId
    dut_id: DUTId  # Device Under Test ID
    test_type: TestType
    test_specification: TestSpecification
    created_at: datetime
    operator_id: OperatorId
    
    def start_test(self) -> None:
        """테스트 시작"""
        
    def complete_test(self, measurements: List[Measurement]) -> TestResult:
        """테스트 완료 및 결과 생성"""
        
    def is_valid_for_execution(self) -> bool:
        """테스트 실행 가능 여부 검증"""
```

#### 2. DUT (Device Under Test)
```python
@dataclass  
class DUT:
    dut_id: DUTId
    serial_number: str
    model_number: str
    firmware_version: str
    hardware_revision: str
    
    def get_test_configuration(self) -> TestConfiguration:
        """DUT별 테스트 설정 반환"""
```

#### 3. Measurement (측정값)
```python
@dataclass
class Measurement:
    measurement_id: MeasurementId
    test_id: TestId
    measurement_type: MeasurementType
    value: MeasurementValue
    unit: MeasurementUnit
    timestamp: datetime
    hardware_source: HardwareSource
    
    def is_within_tolerance(self, specification: TestSpecification) -> bool:
        """허용 오차 범위 내 여부 확인"""
        
    def to_engineering_units(self) -> str:
        """공학 단위로 변환"""
```

#### 4. TestResult (테스트 결과)
```python
@dataclass
class TestResult:
    result_id: TestResultId
    test_id: TestId
    measurements: List[Measurement]
    pass_fail_status: PassFailStatus
    test_duration: timedelta
    completed_at: datetime
    failure_reasons: List[FailureReason]
    
    @classmethod
    def evaluate(cls, test: EOLTest, measurements: List[Measurement]) -> 'TestResult':
        """측정값들을 기반으로 Pass/Fail 판정"""
```

#### 5. HardwareDevice (하드웨어 장치)
```python
@dataclass
class HardwareDevice:
    device_id: DeviceId
    device_type: HardwareType
    vendor: str
    model: str
    connection_info: ConnectionInfo
    status: HardwareStatus
    capabilities: List[HardwareCapability]
    
    def can_perform_measurement(self, measurement_type: MeasurementType) -> bool:
        """특정 측정 수행 가능 여부"""
```

### 값 객체 (Value Objects)

#### 측정값 관련
```python
@dataclass(frozen=True)
class MeasurementValue:
    value: float
    precision: int
    
    def __post_init__(self):
        """값 유효성 검증"""
        
@dataclass(frozen=True)
class Force(MeasurementValue):
    unit: ForceUnit = ForceUnit.NEWTON
    
@dataclass(frozen=True)
class Weight(MeasurementValue):
    unit: WeightUnit = WeightUnit.KILOGRAM
    
@dataclass(frozen=True)
class Voltage(MeasurementValue):
    unit: VoltageUnit = VoltageUnit.VOLT
```

#### 식별자
```python
@dataclass(frozen=True)
class TestId:
    value: str
    
    @classmethod
    def generate(cls) -> 'TestId':
        """새로운 테스트 ID 생성"""
        
@dataclass(frozen=True)
class DUTId:
    value: str
    
@dataclass(frozen=True)  
class MeasurementId:
    value: str
```

## 💼 Application Layer (2층) - Use Cases

### Use Cases

#### 1. ExecuteEOLTestUseCase
```python
class ExecuteEOLTestUseCase:
    def __init__(self,
                 # Hardware Services (Application Interface → Infrastructure 구현체)
                 power_service: PowerService,
                 loadcell_service: LoadCellService,
                 dio_service: DIOService,
                 mcu_service: MCUService,
                 robot_service: RobotService,
                 # Repository Services
                 test_repository: TestRepository,
                 measurement_repository: MeasurementRepository,
                 # External Services
                 notification_service: NotificationService,
                 report_generator_service: ReportGeneratorService):
        self._power_service = power_service
        self._loadcell_service = loadcell_service
        self._dio_service = dio_service
        self._mcu_service = mcu_service
        self._robot_service = robot_service
        self._test_repository = test_repository
        self._measurement_repository = measurement_repository
        self._notification_service = notification_service
        self._report_generator_service = report_generator_service
    
    async def execute(self, command: ExecuteEOLTestCommand) -> EOLTestResult:
        """EOL 테스트 실행 시나리오"""
        
        # 1. 테스트 생성 및 검증
        test = EOLTest.create(
            dut_id=command.dut_id,
            test_type=command.test_type,
            operator_id=command.operator_id
        )
        
        # 2. 하드웨어 초기화
        hardware_controllers = await self._initialize_hardware(test)
        
        try:
            # 3. 측정 시퀀스 실행
            measurements = await self._execute_measurement_sequence(
                test, hardware_controllers
            )
            
            # 4. 결과 평가
            test_result = TestResult.evaluate(test, measurements)
            
            # 5. 데이터 저장
            await self._save_test_data(test, measurements, test_result)
            
            # 6. 알림 발송
            await self._send_notifications(test_result)
            
            return EOLTestResult.from_domain(test_result)
            
        finally:
            # 7. 하드웨어 정리
            await self._cleanup_hardware(hardware_controllers)
```


### 인터페이스 정의 (Dependency Inversion)

#### Hardware Service Interfaces
```python
# src/application/interfaces/power_service.py
class PowerService(ABC):
    @abstractmethod
    async def set_voltage(self, voltage: Voltage) -> None:
        pass
    
    @abstractmethod
    async def enable_output(self) -> None:
        pass
    
    @abstractmethod
    async def measure_current_consumption(self) -> Current:
        pass

# src/application/interfaces/loadcell_service.py
class LoadCellService(ABC):
    @abstractmethod
    async def read_force_value(self) -> ForceValue:
        pass
    
    @abstractmethod
    async def perform_zero_calibration(self) -> CalibrationResult:
        pass

# src/application/interfaces/dio_service.py
class DIOService(ABC):
    @abstractmethod
    async def read_input_port(self, port: int) -> bool:
        pass
    
    @abstractmethod
    async def write_output_port(self, port: int, value: bool) -> None:
        pass

# src/application/interfaces/mcu_service.py
class MCUService(ABC):
    @abstractmethod
    async def send_command(self, command: MCUCommand) -> MCUResponse:
        pass

# src/application/interfaces/robot_service.py
class RobotService(ABC):
    @abstractmethod
    async def move_to_position(self, position: Position) -> None:
        pass
```

#### Repository Interfaces
```python
# src/application/interfaces/test_repository.py
class TestRepository(ABC):
    @abstractmethod
    async def save(self, test: EOLTest) -> EOLTest:
        pass
    
    @abstractmethod
    async def find_by_id(self, test_id: TestId) -> Optional[EOLTest]:
        pass

# src/application/interfaces/measurement_repository.py
class MeasurementRepository(ABC):
    @abstractmethod
    async def save(self, measurement: Measurement) -> Measurement:
        pass
    
    @abstractmethod
    async def find_by_test_id(self, test_id: TestId) -> List[Measurement]:
        pass
```

#### External Service Interfaces
```python
# src/application/interfaces/notification_service.py
class NotificationService(ABC):
    @abstractmethod
    async def send_test_completion_notification(self, result: TestResult) -> None:
        pass

# src/application/interfaces/report_generator_service.py
class ReportGeneratorService(ABC):
    @abstractmethod
    async def generate_report(self, test_result: TestResult, format: ReportFormat) -> Report:
        pass
```

## 🔌 Infrastructure Layer (3층) - 구현체

### Hardware Controller 구현체 (현재 위치 유지)
```
src/infrastructure/controllers/
├── loadcell_controller/
│   ├── bs205/
│   │   └── bs205_controller.py  → LoadCellService 구현
│   └── mock/
├── power_controller/
│   ├── oda/
│   │   └── oda_power_supply.py  → PowerControllerService 구현
│   └── mock/
├── dio_controller/
├── mcu_controller/
└── robot_controller/
```

### Service 구현체 (신규 생성 - 기존 Controller 직접 사용)
```
src/infrastructure/service_implementations/
├── power_service_impl.py           # PowerService 구현체 (기존 OdaPowerSupply 직접 사용)
├── loadcell_service_impl.py        # LoadCellService 구현체 (기존 BS205Controller 직접 사용)
├── dio_service_impl.py             # DIOService 구현체 (기존 AjinextekDIOController 직접 사용)
├── mcu_service_impl.py             # MCUService 구현체 (기존 LMAController 직접 사용)
└── robot_service_impl.py           # RobotService 구현체 (기존 AjinextekRobotController 직접 사용)
```

### Repository 구현체 (신규 생성)
```
src/infrastructure/repositories/
├── sqlite_test_repository.py
├── sqlite_measurement_repository.py
└── file_based_test_repository.py
```

### External Services (신규 생성)
```
src/infrastructure/external_services/
├── console_notification_impl.py
├── database_connection_manager.py
└── file_export_service.py
```

## 🌐 Frameworks Layer (4층) - 외부 라이브러리

### 현재 위치 유지
```
src/frameworks/  # 정리 후 위치
├── ajinextek/AXL(Library)/  → AJINEXTEK 하드웨어 SDK
├── serial/                  → 시리얼 통신 라이브러리 래퍼
└── external_libs/           → 기타 외부 라이브러리
```

## 🔌 Presentation Layer (3층) - 인터페이스 어댑터

### Controllers (신규 생성)
```
src/presentation/controllers/
├── test_execution_controller.py       # 핵심 EOL 테스트 실행 전용
└── hardware_status_controller.py      # 하드웨어 상태 모니터링 및 개별 제어 전용
```

### CLI Interface (신규 생성)
```
src/presentation/cli/
├── eol_test_cli.py
└── hardware_control_cli.py
```

### GUI Interface (선택적)
```
src/presentation/gui/
├── test_execution_gui.py
└── result_viewer_gui.py
```

## 🔄 의존성 방향 (단순화된 2단계 구조)

```
Frameworks ← Infrastructure ← Application ← Domain
    ↓              ↓              ↓           ↓
외부 라이브러리  →  ServiceImpl   →   Use Cases  →  엔티티
(AXL, Serial)    → Controllers   (비즈니스)    (순수 로직)
                 (직접 사용)
```

### 핵심 원칙 (단순화된 구조)
1. **Domain**: 다른 레이어를 모름 (순수 비즈니스 로직)
2. **Application**: Domain만 알고 Infrastructure는 인터페이스로만
3. **Infrastructure**: ServiceImpl이 Application 인터페이스를 구현하고 기존 Controllers 직접 사용
4. **Frameworks**: 최외곽 레이어, 실제 라이브러리/SDK

### 마이그레이션 전략 (단순화된 방식)
1. **Phase 1**: Domain Layer 구축 (엔티티, 값 객체)
2. **Phase 2**: Application Layer 구축 (Use Cases, 인터페이스)
3. **Phase 3**: ServiceImpl이 기존 Controllers 직접 사용하도록 구현
4. **Phase 4**: Presentation Layer 추가
5. **Phase 5**: 점진적 리팩토링 및 최적화