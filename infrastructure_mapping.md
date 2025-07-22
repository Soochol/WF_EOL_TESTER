# WF_EOL_TESTER Infrastructure Layer 재분류

## 🔌 Infrastructure Layer (3층) - 구현체 매핑

### 현재 → Clean Architecture 매핑

## 1. Hardware Service 구현체

### 🔋 PowerService 구현체
```yaml
현재 위치: src/infrastructure/controllers/power_controller/
매핑 결과:
  ✅ oda/oda_power_supply.py → OdaPowerSupply (기존 Controller 보존)
  ✅ mock/mock_oda_power_supply.py → MockOdaPowerSupply (기존 Mock 보존)
  
새로운 구조 (단순화된 2단계):
src/infrastructure/
├── service_implementations/
│   ├── power_service_impl.py          # PowerService 구현체 (기존 Controller 직접 사용)
│   └── mock_power_service_impl.py     # 테스트용 Mock 구현체
└── controllers/ (기존 보존)
    └── power_controller/
        ├── oda/oda_power_supply.py    # 기존 Controller (그대로 보존)
        └── mock/mock_oda_power_supply.py # 기존 Mock (그대로 보존)
```

#### 구현 예시: PowerServiceImpl (단순화된 2단계 구조)
```python
class PowerServiceImpl(PowerService):
    """PowerService 인터페이스의 Infrastructure 구현체 - 기존 Controller 직접 사용"""
    
    def __init__(self, oda_controller: OdaPowerSupply):
        self._oda_controller = oda_controller  # 기존 Controller 직접 주입
    
    async def set_voltage(self, voltage: Voltage) -> None:
        """전압 설정 - Domain 객체를 Hardware 명령으로 변환하여 기존 Controller 직접 호출"""
        voltage_volts = voltage.to_volts()  # Domain 객체 변환
        await self._oda_controller.set_voltage(voltage_volts)  # 기존 Controller 직접 호출
    
    async def enable_output(self) -> None:
        """출력 활성화 - 기존 Controller 직접 호출"""
        await self._oda_controller.enable_output()
    
    async def measure_current_consumption(self) -> Current:
        """전류 측정 - 기존 Controller 호출 후 Domain 객체로 변환"""
        raw_current = await self._oda_controller.read_current()  # 기존 Controller 직접 호출
        return Current(value=raw_current, unit=CurrentUnit.AMPERE)  # Domain 객체 변환
```

### ⚖️ LoadCellService 구현체
```yaml
현재 위치: src/infrastructure/controllers/loadcell_controller/
매핑 결과:
  ✅ bs205/bs205_controller.py → BS205Controller (기존 Controller 보존)
  ✅ mock/mock_bs205_controller.py → MockBS205Controller (기존 Mock 보존)
  ❌ bs205/serial_communication.py → 제거 (중복 시리얼 로직)

새로운 구조 (단순화된 2단계):
src/infrastructure/
├── service_implementations/
│   ├── loadcell_service_impl.py      # LoadCellService 구현체 (기존 Controller 직접 사용)
│   └── mock_loadcell_service_impl.py # 테스트용 Mock 구현체
└── controllers/ (기존 보존)
    └── loadcell_controller/
        ├── bs205/bs205_controller.py # 기존 Controller (그대로 보존)
        └── mock/mock_bs205_controller.py # 기존 Mock (그대로 보존)

시리얼 통신 통합:
- BS205Controller에서 독립적인 시리얼 로직 제거
- src/driver/serial/manager.py 통합 사용
- 중복 코드 제거 및 일관성 확보
```

#### 구현 예시: LoadCellServiceImpl (단순화된 2단계 구조 + 시리얼 통합)
```python
class LoadCellServiceImpl(LoadCellService):
    """LoadCellService 인터페이스의 Infrastructure 구현체 - 기존 Controller 직접 사용"""
    
    def __init__(self, bs205_controller: BS205Controller, serial_manager: SerialManager):
        self._bs205_controller = bs205_controller  # 기존 Controller 직접 주입
        self._serial_manager = serial_manager      # 통합 시리얼 매니저 사용
    
    async def read_force_value(self) -> ForceValue:
        """힘 측정값 읽기 - 기존 Controller 직접 사용 + 통합 시리얼"""
        
        # 기존 Controller로 명령 생성
        command = self._bs205_controller.build_read_command()
        
        # 통합 시리얼 매니저로 통신
        response = await self._serial_manager.send_command_and_wait_response(command)
        
        # 기존 Controller로 파싱
        raw_force = self._bs205_controller.parse_response(response)
        
        # Domain 객체로 변환
        return ForceValue(
            value=raw_force.value,
            unit=ForceUnit.NEWTON,
            precision=3,
            timestamp=datetime.now()
        )
    
    async def perform_zero_calibration(self) -> CalibrationResult:
        """영점 보정 수행 - 기존 Controller 직접 사용 + 통합 시리얼"""
        
        # 기존 Controller로 캘리브레이션 명령 생성
        calibration_command = self._bs205_controller.build_zero_calibration_command()
        
        # 통합 시리얼 매니저로 통신
        response = await self._serial_manager.send_command_and_wait_response(calibration_command)
        
        # 기존 Controller로 결과 파싱
        raw_result = self._bs205_controller.parse_calibration_response(response)
        
        # Domain 객체로 변환
        return CalibrationResult(
            calibration_type=CalibrationType.ZERO_POINT,
            success=raw_result.success,
            offset_value=raw_result.offset,
            performed_at=datetime.now()
        )
```

### 🔌 DIOControllerService 구현체
```yaml
현재 위치: src/infrastructure/controllers/dio_controller/
매핑 결과:
  ✅ ajinextek/dio_controller.py → AjinextekDIOService
  ✅ mock/mock_ajinextek_dio_controller.py → MockDIOService

새로운 구조 (단순화된 2단계):
src/infrastructure/service_implementations/
├── dio_service_impl.py               # DIOService 구현체 (기존 Controller 직접 사용)
└── mock_dio_service_impl.py          # 테스트용 Mock 구현체
```

### 🤖 RobotControllerService 구현체
```yaml
현재 위치: src/infrastructure/controllers/robot_controller/
매핑 결과:
  ✅ ajinextek/motion.py → AjinextekRobotService
  ✅ mock/mock_ajinextek_robot_controller.py → MockRobotService

새로운 구조 (단순화된 2단계):
src/infrastructure/service_implementations/
├── robot_service_impl.py             # RobotService 구현체 (기존 Controller 직접 사용)
└── mock_robot_service_impl.py        # 테스트용 Mock 구현체
```

### 🔧 MCUControllerService 구현체
```yaml
현재 위치: src/infrastructure/controllers/mcu_controller/
매핑 결과:
  ✅ lma/lma_controller.py → LMAMCUService
  ✅ mock/mock_lma_controller.py → MockMCUService

새로운 구조 (단순화된 2단계):
src/infrastructure/service_implementations/
├── mcu_service_impl.py               # MCUService 구현체 (기존 Controller 직접 사용)
└── mock_mcu_service_impl.py          # 테스트용 Mock 구현체
```

## 2. Repository 구현체 (신규 생성)

### 📊 Data Repository 구현체
```yaml
새로운 위치: src/infrastructure/repositories/
구조:
├── sqlite_test_repository.py         # SQLite 기반 테스트 데이터 저장
├── sqlite_measurement_repository.py  # SQLite 기반 측정 데이터 저장
├── file_test_repository.py           # 파일 기반 테스트 데이터 저장
└── memory_test_repository.py         # 메모리 기반 테스트 저장 (개발용)
```

#### 구현 예시: SQLiteTestRepository
```python
class SQLiteTestRepository(TestRepository):
    """SQLite 기반 테스트 Repository 구현체"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self._db = db_connection
    
    async def save(self, test: EOLTest) -> EOLTest:
        """테스트 저장 - Domain 객체를 DB 레코드로 변환"""
        
        test_record = {
            'test_id': test.test_id.value,
            'dut_id': test.dut_id.value,
            'test_type': test.test_type.value,
            'created_at': test.created_at.isoformat(),
            'operator_id': test.operator_id.value
        }
        
        async with self._db.transaction() as tx:
            await tx.execute(
                "INSERT INTO eol_tests (test_id, dut_id, test_type, created_at, operator_id) "
                "VALUES (:test_id, :dut_id, :test_type, :created_at, :operator_id)",
                test_record
            )
        
        return test
    
    async def find_by_id(self, test_id: TestId) -> Optional[EOLTest]:
        """테스트 조회 - DB 레코드를 Domain 객체로 변환"""
        
        record = await self._db.fetch_one(
            "SELECT * FROM eol_tests WHERE test_id = :test_id",
            {'test_id': test_id.value}
        )
        
        if not record:
            return None
        
        # DB 레코드 → Domain 객체 변환
        return EOLTest(
            test_id=TestId(record['test_id']),
            dut_id=DUTId(record['dut_id']),
            test_type=TestType(record['test_type']),
            created_at=datetime.fromisoformat(record['created_at']),
            operator_id=OperatorId(record['operator_id'])
        )
```

### 📈 MeasurementRepository 구현체
```python
class SQLiteMeasurementRepository(MeasurementRepository):
    """SQLite 기반 측정값 Repository 구현체"""
    
    async def save(self, measurement: Measurement) -> Measurement:
        """측정값 저장"""
        
        measurement_record = {
            'measurement_id': measurement.measurement_id.value,
            'test_id': measurement.test_id.value,
            'measurement_type': measurement.measurement_type.value,
            'value': measurement.value.value,
            'unit': measurement.unit.value,
            'timestamp': measurement.timestamp.isoformat(),
            'hardware_source': measurement.hardware_source.value
        }
        
        async with self._db.transaction() as tx:
            await tx.execute(
                "INSERT INTO measurements (...) VALUES (...)",
                measurement_record
            )
        
        return measurement
    
    async def find_by_test_id(self, test_id: TestId) -> List[Measurement]:
        """테스트별 측정값 조회"""
        
        records = await self._db.fetch_all(
            "SELECT * FROM measurements WHERE test_id = :test_id",
            {'test_id': test_id.value}
        )
        
        return [self._record_to_domain(record) for record in records]
```

## 3. External Services 구현체 (신규 생성)

### 📧 NotificationService 구현체
```yaml
새로운 위치: src/infrastructure/external_services/
구조:
├── slack_notification_service.py     # Slack 알림
├── console_notification_service.py   # 콘솔 출력 (개발용)
└── composite_notification_service.py # 복합 알림 서비스
```

#### 구현 예시: ConsoleNotificationService
```python
class ConsoleNotificationService(NotificationService):
    """콘솔 기반 알림 Service 구현체"""
    
    async def send_test_completion_notification(self, result: TestResult) -> None:
        """테스트 완료 알림 콘솔 출력"""
        
        console_message = self._generate_console_message(result)
        print(console_message)
        
        # 로깅도 함께 수행
        logger.info(f"EOL Test Completed: {result.test_id.value} - {result.pass_fail_status.value}")
    
    def _generate_console_message(self, result: TestResult) -> str:
        """콘솔 메시지 생성"""
        return f"""
        ================================
        EOL 테스트 완료
        ================================
        테스트 ID: {result.test_id.value}
        결과: {result.pass_fail_status.value}
        완료 시간: {result.completed_at.isoformat()}
        테스트 시간: {result.test_duration.total_seconds()}초
        측정값 개수: {len(result.measurements)}
        ================================
        """
```

### 📄 ReportGeneratorService 구현체
```yaml
새로운 위치: src/infrastructure/external_services/
구조:
├── excel_report_generator.py         # Excel 보고서 생성
├── pdf_report_generator.py           # PDF 보고서 생성
├── csv_report_generator.py           # CSV 보고서 생성
└── composite_report_generator.py     # 복합 보고서 생성
```

## 4. 단순화된 2단계 구조 적용

### ServiceImpl이 기존 Controller 직접 사용
```python
class LoadCellServiceImpl(LoadCellService):
    """
    LoadCellService 인터페이스의 구현체
    
    기존 BS205Controller를 직접 사용하여 불필요한 중간 계층을 제거하고
    Clean Architecture의 Service 인터페이스를 귀처하게 구현합니다.
    """
    
    def __init__(self, bs205_controller: BS205Controller, serial_manager: SerialManager):
        self._controller = bs205_controller  # 기존 Controller 직접 주입
        self._serial_manager = serial_manager
    
    async def read_force_value(self) -> ForceValue:
        """기존 Controller 직접 사용 + Domain 객체 변환"""
        
        # 기존 Controller로 명령 생성 및 통신 처리
        command = self._controller.build_read_command()
        response = await self._serial_manager.send_command_and_wait_response(command)
        raw_measurement = self._controller.parse_response(response)
        
        # Domain 객체로 변환
        return ForceValue(
            value=raw_measurement.value,
            unit=ForceUnit.NEWTON,
            precision=3,
            timestamp=datetime.now()
        )
```

## 5. 의존성 주입 설정

### DI Container 구성
```python
class DIContainer:
    """의존성 주입 컨테이너"""
    
    def configure_hardware_services(self) -> None:
        """하드웨어 서비스 의존성 구성"""
        
        # Hardware Controllers (기존 코드)
        self.register(BS205Controller, self._create_bs205_controller)
        self.register(OdaPowerSupply, self._create_oda_power_supply)
        
        # Service 구현체 (기존 Controller 직접 사용)
        self.register(LoadCellService, lambda: LoadCellServiceImpl(
            self.resolve(BS205Controller),
            self.resolve(SerialManager)
        ))
        self.register(PowerService, lambda: PowerServiceImpl(
            self.resolve(OdaPowerSupply)
        ))
        
        # Repositories
        self.register(TestRepository, lambda: SQLiteTestRepository(
            self.resolve(DatabaseConnection)
        ))
        
        # Use Cases
        self.register(ExecuteEOLTestUseCase, lambda: ExecuteEOLTestUseCase(
            loadcell_service=self.resolve(LoadCellService),
            power_controller_service=self.resolve(PowerControllerService),
            test_repository=self.resolve(TestRepository),
            # ... 기타 의존성
        ))
```

이 재분류를 통해 기존의 복잡한 Controller 코드들을 Clean Architecture의 Infrastructure Layer로 체계적으로 정리하고, Domain과 Application Layer와의 올바른 의존성 관계를 구축할 수 있습니다.