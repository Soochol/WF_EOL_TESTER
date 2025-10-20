# WF EOL Tester - 배포 파일 빌드 가이드

## 📋 목차
- [사전 요구사항](#사전-요구사항)
- [빌드 파일 구조](#빌드-파일-구조)
- [빌드 방법](#빌드-방법)
- [파일 설명](#파일-설명)
- [문제 해결](#문제-해결)

## 🔧 사전 요구사항

### 필수 소프트웨어

1. **Python 환경**
   - Python 3.10 이상
   - uv 패키지 매니저 (권장) 또는 pip

2. **PyInstaller**
   ```batch
   uv sync
   ```
   또는
   ```batch
   pip install pyinstaller
   ```

3. **Inno Setup** (설치 파일 생성용)
   - 다운로드: https://jrsoftware.org/isdl.php
   - 기본 설치 경로:
     - `C:\Program Files (x86)\Inno Setup 6\` (32비트)
     - `C:\Program Files\Inno Setup 6\` (64비트)

## 📁 빌드 파일 구조

빌드 후 생성되는 디렉토리 구조:

```
WF_EOL_TESTER/
├── build/
│   ├── application/              # 실행 파일
│   │   └── WF_EOL_Tester/
│   │       ├── WF_EOL_Tester.exe    # 메인 실행 파일
│   │       ├── _internal/            # Python 런타임 및 DLL
│   │       ├── configuration/        # 설정 파일들
│   │       └── driver/               # AXL 드라이버 DLL
│   │           └── AXL/
│   │               ├── AXL.dll
│   │               └── EzBasicAxl.dll
│   └── installer/                # 설치 파일
│       └── WF_EOL_Tester_Setup_0.1.0.exe
│
├── wf_eol_tester.spec            # PyInstaller 설정
├── installer.iss                 # Inno Setup 스크립트
├── build_all.bat                 # 전체 빌드
├── build_exe.bat                 # 실행 파일만 빌드
└── build_installer.bat           # 설치 파일만 빌드
```

## 🚀 빌드 방법

### 방법 1: 전체 빌드 (권장)

실행 파일과 설치 파일을 한 번에 생성:

```batch
build_all.bat
```

**빌드 시간**: 약 3~5분 (하드웨어에 따라 다름)

**결과물**:
- `build/application/WF_EOL_Tester/WF_EOL_Tester.exe` - 실행 파일
- `build/installer/WF_EOL_Tester_Setup_0.1.0.exe` - 설치 파일

### 방법 2: 실행 파일만 빌드

빠른 테스트를 위해 실행 파일만 생성:

```batch
build_exe.bat
```

**빌드 시간**: 약 2~3분

**사용 시나리오**:
- 코드 변경 후 빠른 테스트
- 설치 파일 없이 실행 파일만 배포
- 개발 중 반복 빌드

### 방법 3: 설치 파일만 빌드

실행 파일이 이미 있을 때 설치 파일만 생성:

```batch
build_installer.bat
```

**빌드 시간**: 약 30초~1분

**사전 조건**: `build/application/WF_EOL_Tester/WF_EOL_Tester.exe` 존재 필요

## 📄 파일 설명

### 1. `wf_eol_tester.spec`

PyInstaller 빌드 설정 파일

**주요 설정**:
- 진입점: `src/main_gui.py`
- 윈도우 모드: GUI (콘솔 창 없음)
- 포함 데이터:
  - `configuration/` - 모든 설정 파일
  - `src/driver/ajinextek/AXL(Library)/Library/64Bit/` - AXL DLL
- Hidden imports: PySide6, loguru, numpy, scipy 등

### 2. `installer.iss`

Inno Setup 설치 스크립트

**주요 설정**:
- 앱 이름: WF EOL Tester
- 버전: 0.1.0
- 기본 설치 경로: `C:\Program Files\WF EOL Tester`
- 설치 항목:
  - 실행 파일 및 의존성
  - 설정 파일 (`configuration/`)
  - 드라이버 파일 (`driver/AXL/`)
- 바탕화면 바로가기 생성 옵션
- 시작 메뉴 등록

**설치 후 디렉토리**:
```
C:\Program Files\WF EOL Tester\
├── WF_EOL_Tester.exe
├── _internal/
├── configuration/
│   ├── application.yaml
│   ├── hardware_config.yaml
│   ├── heating_cooling_time_test.yaml
│   └── test_profiles/
└── driver/
    └── AXL/
        ├── AXL.dll
        └── EzBasicAxl.dll
```

### 3. 빌드 배치 파일

#### `build_all.bat` - 전체 빌드
1. 이전 빌드 정리
2. PyInstaller로 실행 파일 생성
3. Inno Setup으로 설치 파일 생성
4. 빌드 결과 요약 표시

#### `build_exe.bat` - 실행 파일만
1. 이전 실행 파일 빌드 정리
2. PyInstaller 실행
3. 빌드 결과 표시
4. 실행 옵션 제공

#### `build_installer.bat` - 설치 파일만
1. 실행 파일 존재 확인
2. Inno Setup 실행
3. 빌드 결과 표시
4. 설치 옵션 제공

## 🐛 문제 해결

### PyInstaller 빌드 실패

**증상**: "ERROR: PyInstaller build failed!"

**해결 방법**:

1. **의존성 확인**:
   ```batch
   uv sync
   ```

2. **Python 경로 확인**:
   ```batch
   python --version
   ```
   Python 3.10 이상이어야 함

3. **캐시 정리 후 재빌드**:
   ```batch
   rmdir /s /q build
   rmdir /s /q dist
   build_exe.bat
   ```

4. **상세 로그 확인**:
   ```batch
   uv run pyinstaller wf_eol_tester.spec --clean --log-level DEBUG
   ```

### Inno Setup 빌드 실패

**증상**: "WARNING: Inno Setup not found!" 또는 "ERROR: Inno Setup build failed!"

**해결 방법**:

1. **Inno Setup 설치 확인**:
   - https://jrsoftware.org/isdl.php 에서 다운로드
   - 설치 완료 후 경로 확인:
     - `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
     - `C:\Program Files\Inno Setup 6\ISCC.exe`

2. **수동으로 Inno Setup 실행**:
   - Inno Setup Compiler 실행
   - `installer.iss` 파일 열기
   - Build → Compile 클릭

3. **실행 파일 존재 확인**:
   ```batch
   dir build\application\WF_EOL_Tester\WF_EOL_Tester.exe
   ```

### 실행 파일이 시작되지 않음

**증상**: 실행 파일 더블클릭 시 아무 반응 없음

**해결 방법**:

1. **콘솔에서 실행하여 에러 확인**:
   ```batch
   cd build\application\WF_EOL_Tester
   WF_EOL_Tester.exe
   ```

2. **의존 DLL 확인**:
   - `_internal/` 디렉토리 존재 확인
   - `driver/AXL/` 디렉토리 및 DLL 존재 확인

3. **설정 파일 확인**:
   - `configuration/` 디렉토리 존재 확인
   - YAML 파일들 존재 확인

4. **바이러스 백신 예외 추가**:
   - 일부 바이러스 백신이 PyInstaller 실행 파일을 차단할 수 있음
   - 빌드 디렉토리를 예외 목록에 추가

### 설치 파일이 실행되지 않음

**증상**: 설치 파일 실행 시 에러 발생

**해결 방법**:

1. **관리자 권한으로 실행**:
   - 설치 파일 우클릭 → "관리자 권한으로 실행"

2. **Windows Defender SmartScreen**:
   - "추가 정보" 클릭 → "실행" 클릭
   - (디지털 서명이 없는 경우 나타날 수 있음)

3. **설치 파일 재생성**:
   ```batch
   build_installer.bat
   ```

## 📦 배포 시 참고사항

### 설치 파일 배포

1. **파일 위치**:
   ```
   build/installer/WF_EOL_Tester_Setup_0.1.0.exe
   ```

2. **배포 방법**:
   - 네트워크 공유 폴더
   - USB 드라이브
   - 다운로드 서버

3. **사용자 안내사항**:
   - 관리자 권한 필요
   - 설치 후 `C:\Program Files\WF EOL Tester\` 에 설치됨
   - 시작 메뉴와 바탕화면에 바로가기 생성 (옵션)

### 실행 파일 직접 배포 (포터블)

1. **파일 위치**:
   ```
   build/application/WF_EOL_Tester/
   ```

2. **배포 방법**:
   - 전체 폴더를 ZIP으로 압축
   - 압축 해제 후 `WF_EOL_Tester.exe` 실행

3. **주의사항**:
   - 전체 폴더 구조를 유지해야 함
   - `_internal/`, `configuration/`, `driver/` 폴더 필수

## 🔄 버전 업데이트

새 버전 빌드 시:

1. **버전 번호 업데이트**:
   - `pyproject.toml`: `version = "0.2.0"`
   - `installer.iss`: `#define MyAppVersion "0.2.0"`

2. **전체 빌드 실행**:
   ```batch
   build_all.bat
   ```

3. **결과 확인**:
   - 설치 파일 이름에 새 버전 번호 확인
   - `build/installer/WF_EOL_Tester_Setup_0.2.0.exe`

## 📞 지원

문제가 계속되면:
- 빌드 로그 파일 확인
- Python 환경 재설정
- 프로젝트 Issue 트래커에 문의
