# Presentation Layer Controllers 상세 설계

## 🎯 Controller 목적 및 역할 명확화

### 1. TestExecutionController (핵심 EOL 테스트 실행)

#### 목적
- **단일 책임**: EOL 테스트 전체 워크플로우 실행만 담당
- **핵심 Use Case 실행**: ExecuteEOLTestUseCase 호출 및 결과 처리
- **사용자 인터페이스 어댑터**: CLI/GUI 요청을 Application Layer 명령으로 변환

#### 담당 기능
```yaml
✅ 담당하는 기능:
- EOL 테스트 시작/중지/일시정지
- 테스트 진행 상태 모니터링
- 테스트 결과 표시 및 저장
- 테스트 설정 및 검증
- 보고서 생성 트리거

❌ 담당하지 않는 기능:
- 개별 하드웨어 제어 (HardwareStatusController 담당)
- 직접적인 측정값 수집 (Use Case 내부에서 처리)
- 하드웨어 상태 진단 (HardwareStatusController 담당)
```

#### 구현 예시
```python
# src/presentation/controllers/test_execution_controller.py
class TestExecutionController:
    """EOL 테스트 실행 전용 Controller"""
    
    def __init__(self,
                 execute_eol_test_use_case: ExecuteEOLTestUseCase,
                 generate_report_use_case: GenerateTestReportUseCase):
        self._execute_test_use_case = execute_eol_test_use_case
        self._generate_report_use_case = generate_report_use_case
    
    async def start_eol_test(self, request: EOLTestRequestDTO) -> EOLTestResponseDTO:
        """EOL 테스트 시작"""
        
        # 1. DTO → Command 변환 (Presentation Layer 책임)
        command = ExecuteEOLTestCommand(
            dut_id=DUTId(request.dut_serial),
            test_type=TestType(request.test_type),
            operator_id=OperatorId(request.operator),
            test_configuration=TestConfiguration.from_dto(request.configuration)
        )
        
        try:
            # 2. Use Case 실행 (Application Layer에 위임)
            result = await self._execute_test_use_case.execute(command)
            
            # 3. Result → DTO 변환 (Presentation Layer 책임)
            return EOLTestResponseDTO(
                test_id=result.test_id.value,
                pass_fail=result.pass_fail_status.value,
                test_duration=result.test_duration.total_seconds(),
                measurements_count=len(result.measurements),
                completed_at=result.completed_at.isoformat()
            )
            
        except TestExecutionException as e:
            # 4. 예외 처리 및 사용자 친화적 메시지 변환
            raise ControllerException(f"테스트 실행 실패: {e.message}")
    
    async def get_test_status(self, test_id: str) -> TestStatusDTO:
        """테스트 진행 상태 조회"""
        # Use Case를 통한 상태 조회
        pass
    
    async def stop_test(self, test_id: str) -> None:
        """테스트 중단"""
        # Use Case를 통한 테스트 중단
        pass
    
    async def generate_test_report(self, test_id: str, format: str) -> ReportResponseDTO:
        """테스트 보고서 생성"""
        
        command = GenerateReportCommand(
            test_id=TestId(test_id),
            report_format=ReportFormat(format)
        )
        
        result = await self._generate_report_use_case.execute(command)
        
        return ReportResponseDTO(
            report_id=result.report_id.value,
            file_path=result.file_path,
            generated_at=result.generated_at.isoformat()
        )
```

### 2. HardwareStatusController (하드웨어 상태 및 개별 제어)

#### 목적
- **단일 책임**: 하드웨어 장치 상태 모니터링 및 개별 제어만 담당
- **진단 및 설정**: 개별 하드웨어의 연결, 설정, 진단 기능
- **독립적 하드웨어 제어**: EOL 테스트와 무관한 개별 하드웨어 조작

#### 담당 기능
```yaml
✅ 담당하는 기능:
- 하드웨어 연결 상태 모니터링
- 개별 하드웨어 연결/해제
- 하드웨어 설정 및 구성
- 하드웨어 진단 및 캘리브레이션
- 하드웨어 에러 상태 확인
- 개별 측정값 읽기 (테스트 외 용도)

❌ 담당하지 않는 기능:
- EOL 테스트 워크플로우 실행 (TestExecutionController 담당)
- 테스트 결과 생성 및 저장 (Use Case 내부에서 처리)
- 보고서 생성 (TestExecutionController 담당)
```

#### 구현 예시
```python
# src/presentation/controllers/hardware_status_controller.py
class HardwareStatusController:
    """하드웨어 상태 모니터링 및 개별 제어 전용 Controller"""
    
    def __init__(self,
                 control_hardware_use_case: ControlHardwareUseCase,
                 calibrate_hardware_use_case: CalibrateHardwareUseCase,
                 loadcell_service: LoadCellService):
        self._control_hardware_use_case = control_hardware_use_case
        self._calibrate_hardware_use_case = calibrate_hardware_use_case
        self._loadcell_service = loadcell_service  # 직접 서비스 호출로 변경
    
    async def get_all_hardware_status(self) -> List[HardwareStatusDTO]:
        """모든 하드웨어 상태 조회"""
        
        hardware_types = [
            HardwareType.LOADCELL,
            HardwareType.POWER_CONTROLLER,
            HardwareType.DIO_CONTROLLER,
            HardwareType.MCU_CONTROLLER,
            HardwareType.ROBOT_CONTROLLER
        ]
        
        status_list = []
        for hw_type in hardware_types:
            status = await self._get_hardware_status(hw_type)
            status_list.append(status)
        
        return status_list
    
    async def connect_hardware(self, hardware_type: str) -> HardwareControlResponseDTO:
        """개별 하드웨어 연결"""
        
        command = ControlHardwareCommand(
            hardware_type=HardwareType(hardware_type),
            control_type=ControlType.CONNECT
        )
        
        result = await self._control_hardware_use_case.execute(command)
        
        return HardwareControlResponseDTO(
            hardware_type=hardware_type,
            control_result=result.success,
            message=result.message,
            timestamp=datetime.now().isoformat()
        )
    
    async def disconnect_hardware(self, hardware_type: str) -> HardwareControlResponseDTO:
        """개별 하드웨어 연결 해제"""
        
        command = ControlHardwareCommand(
            hardware_type=HardwareType(hardware_type),
            control_type=ControlType.DISCONNECT
        )
        
        result = await self._control_hardware_use_case.execute(command)
        
        return HardwareControlResponseDTO(
            hardware_type=hardware_type,
            control_result=result.success,
            message=result.message,
            timestamp=datetime.now().isoformat()
        )
    
    async def read_loadcell_value(self) -> MeasurementResponseDTO:
        """로드셀 개별 측정 (테스트 외 용도) - 직접 서비스 호출"""
        
        # Use Case 대신 직접 서비스 호출로 단순화
        force_value = await self._loadcell_service.read_force_value()
        
        return MeasurementResponseDTO(
            value=force_value.value,
            unit=force_value.unit.value,
            timestamp=force_value.timestamp.isoformat(),
            precision=force_value.precision
        )
    
    async def calibrate_loadcell(self) -> CalibrationResponseDTO:
        """로드셀 캘리브레이션"""
        
        command = CalibrateHardwareCommand(
            hardware_type=HardwareType.LOADCELL,
            calibration_type=CalibrationType.ZERO_POINT
        )
        
        result = await self._calibrate_hardware_use_case.execute(command)
        
        return CalibrationResponseDTO(
            calibration_type=result.calibration_type.value,
            success=result.success,
            offset_value=result.offset_value,
            performed_at=result.performed_at.isoformat()
        )
    
    async def diagnose_hardware(self, hardware_type: str) -> DiagnosisResponseDTO:
        """하드웨어 진단"""
        
        command = ControlHardwareCommand(
            hardware_type=HardwareType(hardware_type),
            control_type=ControlType.DIAGNOSE
        )
        
        result = await self._control_hardware_use_case.execute(command)
        
        return DiagnosisResponseDTO(
            hardware_type=hardware_type,
            diagnosis_result=result.diagnosis_details,
            health_score=result.health_score,
            recommendations=result.recommendations,
            timestamp=datetime.now().isoformat()
        )
```

## 🔄 Controller 간 협력 패턴

### 분리된 책임
```yaml
TestExecutionController:
  입력: EOL 테스트 요청
  출력: 테스트 결과 및 보고서
  
HardwareStatusController:
  입력: 하드웨어 제어/상태 요청
  출력: 하드웨어 상태 및 제어 결과
```

### 독립적 동작
- 두 Controller는 서로 직접 호출하지 않음
- 각각 독립적인 Use Case를 통해 작업 수행
- 공통 데이터는 Repository를 통해 공유

### 사용 시나리오
```yaml
EOL 테스트 실행:
  1. HardwareStatusController로 하드웨어 상태 확인
  2. TestExecutionController로 테스트 실행
  3. 테스트 중 문제 발생 시 HardwareStatusController로 진단

개별 하드웨어 작업:
  1. HardwareStatusController로 특정 하드웨어 제어
  2. 필요시 개별 측정 수행
  3. 캘리브레이션 등 유지보수 작업
```

이렇게 명확히 분리된 책임을 통해 각 Controller가 단일 책임 원칙을 준수하며, 유지보수와 테스트가 용이한 구조를 만들 수 있습니다.