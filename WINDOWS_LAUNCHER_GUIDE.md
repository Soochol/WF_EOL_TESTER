# Windows Launcher Guide - WF EOL Tester

Windows에서 WF EOL Tester를 더블클릭으로 쉽게 실행할 수 있도록 하는 런처 스크립트들의 사용 방법을 설명합니다.

## 📁 제공되는 런처 파일들

### 1. `run.bat` ⭐ **추천**
- **용도**: 일반적인 실행용
- **사용법**: 더블클릭으로 실행
- **특징**:
  - 가장 간단하고 안정적
  - 가상환경 자동 활성화
  - 에러 발생시 창이 바로 닫히지 않음
  - Python 버전 체크

### 2. `run_debug.bat`
- **용도**: 디버그 모드 실행
- **사용법**: 더블클릭으로 실행
- **특징**:
  - 상세한 디버그 정보 출력
  - 시스템 정보 표시
  - 환경 변수 설정 확인
  - 의존성 패키지 체크

### 3. `setup_windows.bat`
- **용도**: 최초 환경 설정
- **사용법**: 더블클릭으로 실행 (처음 한 번만)
- **특징**:
  - 가상환경 생성
  - 의존성 패키지 설치
  - 환경 검증
  - 테스트 실행 옵션

### 4. `run.ps1`
- **용도**: PowerShell 기반 실행 (고급 사용자용)
- **사용법**: PowerShell에서 `.\run.ps1` 실행
- **특징**:
  - 컬러 출력
  - 고급 에러 처리
  - 명령줄 옵션 지원
  - 자세한 실행 로그

## 🚀 빠른 시작 가이드

### 1단계: 초기 설정 (처음 한 번만)
1. `setup_windows.bat`을 더블클릭하여 실행
2. 설정이 완료될 때까지 기다림
3. 테스트 실행 여부를 묻는 경우 `y` 입력 (권장)

### 2단계: 애플리케이션 실행
- **일반 실행**: `run.bat`을 더블클릭
- **문제 발생시**: `run_debug.bat`을 더블클릭하여 자세한 정보 확인

## 📋 시스템 요구사항

### 필수 요구사항
- **Windows 7** 이상
- **Python 3.8** 이상
- **최소 1GB** 여유 공간

### 설치 확인 방법
1. `Win + R` → `cmd` → Enter
2. `python --version` 입력
3. Python 3.8.x 이상 표시되면 OK

## 🔧 각 런처의 세부 기능

### `run.bat` 세부 기능
```batch
✓ Python 설치 확인
✓ 가상환경 활성화 (있는 경우)
✓ main.py 존재 확인
✓ 애플리케이션 실행
✓ 종료 코드 표시
✓ 오류시 창 유지 (pause)
```

### `run_debug.bat` 세부 기능
```batch
✓ 상세 시스템 정보 표시
✓ Python 버전 및 경로 확인
✓ 가상환경 상태 점검
✓ 의존성 패키지 확인
✓ 환경변수 설정 표시
✓ 실행 로그 상세 출력
✓ 종료 후 디버그 정보 요약
```

### `setup_windows.bat` 세부 기능
```batch
✓ Python 버전 검증 (3.8+ 확인)
✓ pip 설치 확인
✓ 가상환경 생성/재생성
✓ 의존성 패키지 설치
✓ 설정 파일 확인
✓ 기본 테스트 실행
✓ 설치 완료 검증
```

### `run.ps1` 세부 기능 및 옵션
```powershell
# 기본 실행
.\run.ps1

# 디버그 모드
.\run.ps1 -Debug

# 상세 출력 모드
.\run.ps1 -Verbose

# 도움말 표시
.\run.ps1 -Help

# 디버그 + 상세 출력
.\run.ps1 -Debug -Verbose
```

## ❗ 문제 해결

### Python을 찾을 수 없는 경우
```
[ERROR] Python is not installed or not in PATH
```
**해결방법**:
1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.8+ 설치
2. 설치 시 "Add Python to PATH" 체크박스 선택
3. 명령 프롬프트 재시작

### 가상환경을 찾을 수 없는 경우
```
[WARNING] Virtual environment not found at 'venv\'
```
**해결방법**:
1. `setup_windows.bat` 실행하여 가상환경 생성
2. 또는 수동으로: `python -m venv venv`

### main.py를 찾을 수 없는 경우
```
[ERROR] main.py not found in current directory
```
**해결방법**:
1. 런처 파일들이 main.py와 같은 폴더에 있는지 확인
2. 프로젝트 루트 디렉토리에서 실행

### 권한 오류가 발생하는 경우
```
Access is denied
```
**해결방법**:
1. 관리자 권한으로 명령 프롬프트 실행
2. 또는 바이러스 백신 예외 설정에 프로젝트 폴더 추가

### PowerShell 실행 정책 오류
```
Execution of scripts is disabled on this system
```
**해결방법**:
```powershell
# 관리자 권한 PowerShell에서 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 💡 사용 팁

### 바탕화면 바로가기 만들기
1. `run.bat` 파일을 우클릭
2. "바로 가기 만들기" 선택
3. 생성된 바로가기를 바탕화면으로 이동

### 시작 메뉴에 추가
1. 바로가기를 생성한 후
2. `Win + R` → `shell:programs` → Enter
3. 바로가기를 해당 폴더에 복사

### 자동 시작 설정
1. `Win + R` → `shell:startup` → Enter
2. `run.bat`의 바로가기를 해당 폴더에 복사
3. Windows 시작시 자동으로 EOL Tester 실행

## 📝 로그 및 출력

### 로그 파일 위치
- **애플리케이션 로그**: `logs/eol_tester.log`
- **테스트 결과**: `ResultsLog/` 폴더

### 콘솔 출력 설정
- `run.bat`: 기본 출력
- `run_debug.bat`: 상세 출력
- `run.ps1 -Debug`: 컬러 출력 + 상세 정보

## 🔄 업데이트 및 유지보수

### 의존성 패키지 업데이트
```batch
# 가상환경 활성화 후
pip install --upgrade -r requirements.txt
```

### 런처 파일 업데이트
새 버전의 런처 파일을 받았을 때:
1. 기존 파일들 백업
2. 새 파일들로 교체
3. `setup_windows.bat` 재실행 (필요시)

## 📞 지원 및 문의

문제가 지속되는 경우:
1. `run_debug.bat` 실행하여 상세 로그 확인
2. `logs/eol_tester.log` 파일 내용 확인
3. 시스템 정보와 오류 메시지를 포함하여 문의

---
**작성일**: 2025년 8월
**버전**: 1.0.0
**지원 OS**: Windows 7, 8, 10, 11