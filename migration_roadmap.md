# WF_EOL_TESTER → Clean Architecture 마이그레이션 로드맵

## 🗺️ 전체 마이그레이션 전략

### 핵심 원칙
1. **Zero Downtime**: 기존 기능 중단 없이 점진적 마이그레이션
2. **Backward Compatibility**: 기존 인터페이스 유지하며 내부 구조 변경
3. **Risk Mitigation**: 단계별 검증으로 위험 최소화
4. **Testability**: 각 단계마다 충분한 테스트 적용

### 마이그레이션 단계 (6 Phase)

## 📋 Phase 1: Domain Layer 구축 (1-2주)

### 목표
순수한 비즈니스 로직과 도메인 엔티티 구축

### 작업 항목

#### 1.1 도메인 엔티티 생성
```bash
mkdir -p src/domain/entities
mkdir -p src/domain/value_objects  
mkdir -p src/domain/exceptions
mkdir -p src/domain/enums
```

#### 생성할 파일들
```yaml
src/domain/
├── entities/
│   ├── __init__.py
│   ├── eol_test.py              # EOL 테스트 엔티티
│   ├── dut.py                   # Device Under Test 엔티티
│   ├── measurement.py           # 측정값 엔티티
│   ├── test_result.py           # 테스트 결과 엔티티
│   └── hardware_device.py       # 하드웨어 장치 엔티티
├── value_objects/
│   ├── __init__.py
│   ├── identifiers.py           # 각종 ID 값 객체
│   ├── measurements.py          # 측정값 관련 값 객체
│   ├── forces.py                # 힘 관련 값 객체
│   ├── voltages.py              # 전압 관련 값 객체
│   └── time_values.py           # 시간 관련 값 객체
├── enums/
│   ├── __init__.py
│   ├── test_types.py            # 테스트 타입 열거형
│   ├── hardware_types.py        # 하드웨어 타입 열거형
│   ├── measurement_units.py     # 측정 단위 열거형
│   └── status_enums.py          # 각종 상태 열거형
└── exceptions/
    ├── __init__.py
    ├── domain_exceptions.py     # 도메인 예외
    ├── validation_exceptions.py # 검증 예외
    └── business_rule_exceptions.py # 비즈니스 룰 예외
```

#### 1.2 기존 코드에서 도메인 로직 추출
```python
# 현재: src/infrastructure/controllers/base.py의 HardwareStatus
# 이동: src/domain/enums/hardware_status.py

# 현재: src/infrastructure/controllers/loadcell_controller/base.py의 LoadcellStatus  
# 이동: src/domain/enums/loadcell_status.py

# 현재: 각 Controller의 비즈니스 로직
# 추출: Domain Entity 메서드로 이동
```

#### 1.3 도메인 검증 규칙 구현
```python
# 예시: src/domain/entities/measurement.py
class Measurement:
    def validate_measurement_range(self) -> None:
        """측정값 범위 검증 - 순수 비즈니스 룰"""
        if self.force_value.value < 0:
            raise InvalidMeasurementError("Force cannot be negative")
        
        if self.force_value.value > MAX_SAFE_FORCE:
            raise UnsafeMeasurementError("Force exceeds safety limit")
```

### 완료 기준
- [ ] 모든 도메인 엔티티 구현 완료
- [ ] 도메인 로직 단위 테스트 100% 통과
- [ ] 순환 의존성 없음 검증
- [ ] 외부 의존성 없음 검증

---

## 💼 Phase 2: Application Layer 구축 (2-3주)

### 목표
Use Cases와 Service 인터페이스 구현

### 작업 항목

#### 2.1 Application 구조 생성
```bash
mkdir -p src/application/use_cases
mkdir -p src/application/interfaces
mkdir -p src/application/commands
mkdir -p src/application/results
mkdir -p src/application/services
```

#### 2.2 Use Cases 구현
```yaml
src/application/use_cases/
├── __init__.py
├── execute_eol_test_use_case.py     # 메인 EOL 테스트 실행
├── control_hardware_use_case.py     # 하드웨어 제어
├── generate_report_use_case.py      # 보고서 생성
└── calibrate_hardware_use_case.py   # 하드웨어 캘리브레이션
```

#### 2.3 Service 인터페이스 정의 (올바른 네이밍)
```yaml
src/application/interfaces/
├── __init__.py
├── power_service.py                 # PowerService 인터페이스
├── loadcell_service.py              # LoadCellService 인터페이스
├── dio_service.py                   # DIOService 인터페이스
├── mcu_service.py                   # MCUService 인터페이스
├── robot_service.py                 # RobotService 인터페이스
├── test_repository.py               # TestRepository 인터페이스
├── measurement_repository.py        # MeasurementRepository 인터페이스
├── notification_service.py          # NotificationService 인터페이스
└── report_generator_service.py      # ReportGeneratorService 인터페이스
```

#### 2.4 Command/Result 객체 구현
```python
# src/application/commands/execute_eol_test_command.py
@dataclass
class ExecuteEOLTestCommand:
    dut_id: DUTId
    test_type: TestType
    operator_id: OperatorId
    
    def validate(self) -> None:
        """명령 유효성 검증"""
```

### 완료 기준
- [ ] 모든 Use Cases 구현 완료
- [ ] 모든 Service 인터페이스 정의 완료
- [ ] Command/Result 객체 완성
- [ ] Use Case 단위 테스트 90% 이상

---

## 🔌 Phase 3: Infrastructure Adapter 구축 (2-3주)

### 목표
기존 Controller 코드를 Service 인터페이스에 어댑팅

### 작업 항목

#### 3.1 Infrastructure Layer 구조 생성 (올바른 네이밍)
```bash
mkdir -p src/infrastructure/service_implementations
mkdir -p src/infrastructure/hardware_adapters
mkdir -p src/infrastructure/repositories  
mkdir -p src/infrastructure/external_services
# 기존 controllers 디렉토리는 보존
# src/infrastructure/controllers/ (그대로 유지)
```

#### 3.2 Service 구현체 구현 (단순화된 2단계 구조)
```python
# 1단계: Application Interface (이미 Phase 2에서 생성)
# src/application/interfaces/loadcell_service.py
class LoadCellService(ABC):
    @abstractmethod
    async def read_force_value(self) -> ForceValue:
        pass

# 2단계: Infrastructure ServiceImpl (기존 Controller 직접 사용)
# src/infrastructure/service_implementations/loadcell_service_impl.py
class LoadCellServiceImpl(LoadCellService):
    """LoadCellService 인터페이스의 Infrastructure 구현체 - 기존 Controller 직접 사용"""
    
    def __init__(self, bs205_controller: BS205Controller, serial_manager: SerialManager):
        self._controller = bs205_controller  # 기존 Controller 직접 주입
        self._serial_manager = serial_manager  # 통합 시리얼 사용
    
    async def read_force_value(self) -> ForceValue:
        """Domain 객체 변환 + 기존 Controller 직접 호출"""
        # 기존 Controller로 명령 생성 및 시리얼 통신
        command = self._controller.build_read_command()
        response = await self._serial_manager.send_command_and_wait_response(command)
        raw_data = self._controller.parse_response(response)
        
        # Domain 객체로 변환
        return ForceValue.from_raw_data(raw_data)

# 기존 Controller는 그대로 보존
# src/infrastructure/controllers/loadcell_controller/bs205/bs205_controller.py
class BS205Controller:
    # 기존 구현 그대로 유지
    pass
```

#### 3.3 Repository 구현체 구축
```python
# src/infrastructure/repositories/sqlite_test_repository.py
class SQLiteTestRepository(TestRepository):
    """TestRepository 인터페이스의 SQLite 구현체"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self._db = db_connection
    
    async def save(self, test: EOLTest) -> EOLTest:
        # Domain 객체 → DB 레코드 변환
        test_record = {
            'test_id': test.test_id.value,
            'dut_id': test.dut_id.value,
            'test_type': test.test_type.value,
            'created_at': test.created_at.isoformat(),
            'operator_id': test.operator_id.value
        }
        
        async with self._db.transaction() as tx:
            await tx.execute(
                "INSERT INTO eol_tests (...) VALUES (...)",
                test_record
            )
        
        return test

# src/infrastructure/repositories/sqlite_measurement_repository.py
class SQLiteMeasurementRepository(MeasurementRepository):
    """MeasurementRepository 인터페이스의 SQLite 구현체"""
    
    async def save(self, measurement: Measurement) -> Measurement:
        # Domain 객체를 DB에 저장
        pass
    
    async def find_by_test_id(self, test_id: TestId) -> List[Measurement]:
        # 테스트별 측정값 조회
        pass
```

#### 3.4 기존 Controller 보존 및 3단계 구조 적용
```yaml
전략: 기존 Controller 코드 완전 보존 + Clean Architecture 3단계 구조

의존성 흐름:
Application Interface → ServiceImpl → Adapter → 기존 Controller

구체적 매핑:
- PowerService → PowerServiceImpl → OdaPowerAdapter → OdaPowerSupply (기존)
- LoadCellService → LoadCellServiceImpl → BS205LoadCellAdapter → BS205Controller (기존)
- DIOService → DIOServiceImpl → AjinextekDIOAdapter → AjinextekDIOController (기존)
- MCUService → MCUServiceImpl → LMAMCUAdapter → LMAController (기존)
- RobotService → RobotServiceImpl → AjinextekRobotAdapter → AjinextekRobotController (기존)

시리얼 통신 통합:
- 각 Adapter에서 통합 SerialManager 사용
- 기존 개별 serial_communication.py 제거
- src/driver/serial/ → src/frameworks/serial/ 통합 사용
```

### 완료 기준
- [ ] 모든 Service 인터페이스 → ServiceImpl → Adapter → Controller 체인 구현
- [ ] Repository 구현체 완성 (SQLite 기반)
- [ ] 시리얼 통신 통합 완료 (중복 제거)
- [ ] 기존 기능 100% 동작 보장 (어댑터 패턴 적용)
- [ ] 통합 테스트 통과 (새 구조 검증)
- [ ] Clean Architecture 의존성 규칙 준수 검증

---

## 🌐 Phase 4: Frameworks Layer 정리 (1주)

### 목표
외부 라이브러리 의존성 정리 및 래핑

### 작업 항목

#### 4.1 외부 라이브러리 래퍼 생성
```bash
mkdir -p src/frameworks/ajinextek
mkdir -p src/frameworks/serial
mkdir -p src/frameworks/database
mkdir -p src/frameworks/logging
```

#### 4.2 AXL 라이브러리 래퍼 (기존 위치 정리)
```python
# 현재: src/driver/ajinextek/AXL(Library)/ 
# 이동: src/frameworks/ajinextek/AXL(Library)/
# 목적: Clean Architecture Frameworks Layer로 분류

# src/frameworks/ajinextek/axl_wrapper.py
class AXLLibraryWrapper:
    """AJINEXTEK AXL 라이브러리 래퍼"""
    
    def __init__(self, library_path: str):
        self._axl = ctypes.CDLL(library_path)
    
    def open_device(self, irq_no: int) -> bool:
        """라이브러리 초기화"""
        return self._axl.AxlOpen(irq_no) == 1
    
    def close_device(self) -> None:
        """라이브러리 종료"""
        self._axl.AxlClose()
```

#### 4.3 시리얼 통신 통합 정리
```python
# 현재: src/driver/serial/ → src/frameworks/serial/
# 용도: pyserial 라이브러리 래핑 및 통합 시리얼 관리

# 통합 대상:
# - src/infrastructure/controllers/loadcell_controller/bs205/serial_communication.py (제거)
# - 기타 개별 시리얼 통신 로직들

# src/frameworks/serial/serial_manager.py
class SerialManager:
    """통합 시리얼 통신 매니저"""
    
    def __init__(self, port: str, baudrate: int):
        self._serial = serial.Serial(port, baudrate)
    
    async def send_command_and_wait_response(self, command: bytes) -> bytes:
        """명령 전송 및 응답 대기"""
        self._serial.write(command)
        return self._serial.read_until(b'\r\n')
```

### 완료 기준
- [ ] 외부 라이브러리 래퍼 완성
- [ ] 의존성 격리 검증
- [ ] 라이브러리 버전 업그레이드 용이성 확인

---

## 🎯 Phase 5: Presentation Layer 구축 (1-2주)

### 목표
사용자 인터페이스 계층 구축

### 작업 항목

#### 5.1 Controller 계층 생성
```bash
mkdir -p src/presentation/controllers
mkdir -p src/presentation/cli
mkdir -p src/presentation/dto
mkdir -p src/presentation/validators
```

#### 5.2 Controller 및 CLI 인터페이스 구현
```python
# src/presentation/controllers/test_execution_controller.py
class TestExecutionController:
    """EOL 테스트 실행 전용 Controller (단일 책임)"""
    
    def __init__(self,
                 execute_eol_test_use_case: ExecuteEOLTestUseCase,
                 generate_report_use_case: GenerateTestReportUseCase):
        self._execute_test_use_case = execute_eol_test_use_case
        self._generate_report_use_case = generate_report_use_case
    
    async def start_eol_test(self, request: EOLTestRequestDTO) -> EOLTestResponseDTO:
        # DTO → Command 변환 → Use Case 실행 → Result → DTO 변환
        pass

# src/presentation/controllers/hardware_status_controller.py
class HardwareStatusController:
    """하드웨어 상태 모니터링 및 개별 제어 전용 Controller (단일 책임)"""
    
    def __init__(self,
                 control_hardware_use_case: ControlHardwareUseCase,
                 measure_loadcell_use_case: MeasureLoadCellUseCase):
        self._control_hardware_use_case = control_hardware_use_case
        self._measure_loadcell_use_case = measure_loadcell_use_case
    
    async def get_all_hardware_status(self) -> List[HardwareStatusDTO]:
        # 하드웨어 상태 조회
        pass
    
    async def connect_hardware(self, hardware_type: str) -> HardwareControlResponseDTO:
        # 개별 하드웨어 연결
        pass

# src/presentation/cli/eol_test_cli.py
class EOLTestCLI:
    """EOL 테스트 CLI 인터페이스"""
    
    def __init__(self, 
                 test_controller: TestExecutionController,
                 hardware_controller: HardwareStatusController):
        self._test_controller = test_controller
        self._hardware_controller = hardware_controller
    
    async def run_test(self, dut_serial: str, test_type: str) -> None:
        # Controller를 통한 테스트 실행
        request = EOLTestRequestDTO(
            dut_serial=dut_serial,
            test_type=test_type,
            operator="CLI_USER"
        )
        
        result = await self._test_controller.start_eol_test(request)
        self._display_result(result)
```

#### 5.3 DTO 객체 구현
```python
# src/presentation/dto/test_request_dto.py
@dataclass
class TestRequestDTO:
    """외부 요청을 위한 DTO"""
    dut_serial: str
    test_type: str
    operator: str
    
    def to_command(self) -> ExecuteEOLTestCommand:
        """DTO → Command 변환"""
        return ExecuteEOLTestCommand(
            dut_id=DUTId(self.dut_serial),
            test_type=TestType(self.test_type),
            operator_id=OperatorId(self.operator)
        )
```

### 완료 기준
- [ ] CLI 인터페이스 구현 완료
- [ ] DTO 변환 로직 완성
- [ ] 사용자 입력 검증 구현
- [ ] E2E 테스트 통과

---

## 🔄 Phase 6: 통합 및 최적화 (1-2주)

### 목표
전체 시스템 통합 및 성능 최적화

### 작업 항목

#### 6.1 의존성 주입 설정
```python
# src/main.py
class ApplicationBootstrap:
    """애플리케이션 부트스트랩"""
    
    def configure_dependencies(self) -> DIContainer:
        container = DIContainer()
        
        # Domain (의존성 없음)
        
        # Application (Use Cases)
        container.register(ExecuteEOLTestUseCase, self._create_eol_test_use_case)
        container.register(ControlHardwareUseCase, self._create_control_hardware_use_case)
        container.register(GenerateTestReportUseCase, self._create_generate_report_use_case)
        container.register(CalibrateHardwareUseCase, self._create_calibrate_hardware_use_case)
        
        # Infrastructure (Service 구현체 → Adapter → Controller 체인)
        # Service 구현체
        container.register(LoadCellService, lambda: LoadCellServiceImpl(
            self.resolve(BS205LoadCellAdapter)
        ))
        container.register(PowerService, lambda: PowerServiceImpl(
            self.resolve(OdaPowerAdapter)
        ))
        
        # Service 구현체 (기존 Controller 직접 주입)
        container.register(LoadCellService, lambda: LoadCellServiceImpl(
            self.resolve(BS205Controller),
            self.resolve(SerialManager)
        ))
        container.register(PowerService, lambda: PowerServiceImpl(
            self.resolve(OdaPowerSupply)
        ))
        
        # 기존 Controllers (보존)
        container.register(BS205Controller, self._create_bs205_controller)
        container.register(OdaPowerSupply, self._create_oda_power_supply)
        
        # Repositories
        container.register(TestRepository, lambda: SQLiteTestRepository(
            self.resolve(DatabaseConnection)
        ))
        
        # Presentation (Controllers 분리)
        container.register(TestExecutionController, lambda: TestExecutionController(
            self.resolve(ExecuteEOLTestUseCase),
            self.resolve(GenerateTestReportUseCase)
        ))
        container.register(HardwareStatusController, lambda: HardwareStatusController(
            self.resolve(ControlHardwareUseCase),
            self.resolve(CalibrateHardwareUseCase),
            self.resolve(LoadCellService)
        ))
        container.register(EOLTestCLI, lambda: EOLTestCLI(
            self.resolve(TestExecutionController),
            self.resolve(HardwareStatusController)
        ))
        
        return container
```

#### 6.2 통합 테스트 구축
```python
# tests/integration/test_eol_workflow.py
class TestEOLWorkflow:
    """전체 EOL 워크플로우 통합 테스트"""
    
    async def test_complete_eol_test_execution(self):
        # Given: 테스트 설정
        # When: EOL 테스트 실행
        # Then: 올바른 결과 생성
```

#### 6.3 성능 최적화
```yaml
최적화 영역:
- 비동기 처리 최적화
- 메모리 사용량 최적화  
- 하드웨어 통신 최적화
- 데이터베이스 쿼리 최적화
```

#### 6.4 레거시 코드 제거
```yaml
제거 대상:
- 사용되지 않는 Controller 메서드
- 중복된 예외 처리 로직
- 불필요한 래퍼 클래스
- 사용되지 않는 설정 파일
```

### 완료 기준
- [ ] 전체 시스템 통합 완료
- [ ] 성능 벤치마크 통과
- [ ] 메모리 누수 없음 확인
- [ ] 레거시 코드 정리 완료

---

## 🎯 마이그레이션 검증 기준

### 기능적 검증
```yaml
✅ 기존 기능 100% 동작
✅ 새로운 아키텍처로 동일한 결과 생성
✅ 하드웨어 제어 정확성 유지
✅ 데이터 일관성 보장
```

### 비기능적 검증  
```yaml
✅ 성능 저하 5% 이내
✅ 메모리 사용량 증가 10% 이내
✅ 코드 커버리지 90% 이상
✅ 순환 의존성 0개
```

### 유지보수성 검증
```yaml
✅ 새로운 하드웨어 추가 용이성
✅ 비즈니스 로직 변경 용이성
✅ 테스트 작성 용이성
✅ 문서화 완성도
```

---

## 🚨 위험 관리 및 롤백 계획

### 위험 요소
1. **하드웨어 호환성**: 기존 하드웨어 제어 로직 변경으로 인한 호환성 문제
2. **성능 저하**: 새로운 추상화 계층으로 인한 성능 영향
3. **데이터 손실**: 마이그레이션 과정에서 기존 데이터 손실 위험

### 롤백 계획
```yaml
Phase별 롤백:
- 각 Phase 완료 시 Git 태그 생성
- 문제 발생 시 이전 태그로 즉시 롤백
- 데이터 백업 및 복구 절차 준비

핫픽스 계획:
- 운영 중 문제 발생 시 임시 패치 적용
- 근본적 해결책은 다음 Phase에서 적용
```

### 성공 지표
```yaml
기술적 지표:
- 코드 복잡도 감소 30%
- 테스트 커버리지 90% 이상
- 빌드 시간 증가 10% 이내

비즈니스 지표:
- 새로운 기능 개발 시간 단축 40%
- 버그 발생률 감소 50%
- 하드웨어 추가 시간 단축 60%
```

이 로드맵을 통해 기존 WF_EOL_TESTER를 안전하고 체계적으로 Clean Architecture로 마이그레이션할 수 있습니다.