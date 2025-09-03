# CLI 전용 EOL Tester 사용법

## 개요
`main_cli.py`는 하드웨어 버튼 모니터링과 웹 API 종속성을 제거한 순수 CLI 전용 실행파일입니다.

## 실행 방법

### 1. 직접 실행
```bash
# Python으로 직접 실행
python main_cli.py

# 또는 실행 권한이 있는 경우
./main_cli.py
```

### 2. 가상환경에서 실행
```bash
# 가상환경 활성화 (필요시)
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# CLI 실행
python main_cli.py
```

## 주요 특징

### ✅ 포함된 기능
- **Enhanced CLI Interface**: Rich UI를 사용한 대화형 명령줄 인터페이스
- **EOL Force Test**: End-of-Line 테스트 실행
- **Configuration Management**: YAML 기반 설정 관리
- **Hardware Service Facade**: 하드웨어 서비스 (선택적 연결)
- **Dependency Injection**: ApplicationContainer 기반 의존성 주입
- **Logging**: 파일 및 콘솔 로깅

### ❌ 제거된 기능
- **Button Monitoring Service**: DIO 버튼 모니터링 서비스
- **Emergency Stop Service**: 응급 정지 서비스  
- **Web API Dependencies**: FastAPI 웹서버 관련 종속성
- **Background Hardware Monitoring**: 백그라운드 하드웨어 모니터링

## 하드웨어 연결

### 자동 연결 시도
CLI는 시작시 자동으로 하드웨어 연결을 시도하지만, 연결 실패 시에도 계속 실행됩니다:

```
🔧 Digital I/O service connection status: False
⚠️ Could not connect Digital I/O service: Connection failed
💡 CLI will continue in software-only mode
```

### 소프트웨어 전용 모드
하드웨어가 연결되지 않아도 다음 기능들은 정상 작동합니다:
- CLI 메뉴 시스템
- 설정 관리
- 테스트 시뮬레이션
- 로깅 및 리포팅

## 로그 파일
- 위치: `Logs/application/eol_tester_cli_YYYY-MM-DD.log`
- 형식: 날짜별 분리 (파일 잠금 방지)
- 레벨: DEBUG (파일), INFO (콘솔)

## 종료 방법
- `Ctrl+C`: 정상 종료
- `exit` 또는 `quit`: CLI 메뉴에서 종료
- `Ctrl+Break`: Windows에서 강제 종료

## 개발 및 디버그

### 디버그 모드
```python
# setup_logging() 함수에서 debug=True로 설정
setup_logging(debug=True)
```

### 하드웨어 없이 테스트
CLI는 하드웨어 연결 실패를 우아하게 처리하므로 개발 환경에서도 안전하게 테스트할 수 있습니다.

## 문제 해결

### 일반적인 문제
1. **모듈을 찾을 수 없음**: `src/` 디렉토리가 올바른 위치에 있는지 확인
2. **설정 파일 오류**: `configuration/application.yaml` 파일 존재 확인
3. **권한 오류**: 로그 디렉토리 쓰기 권한 확인

### 로그 확인
문제 발생시 로그 파일을 확인하여 상세한 오류 정보를 얻을 수 있습니다:
```bash
tail -f Logs/application/eol_tester_cli_$(date +%Y-%m-%d).log
```