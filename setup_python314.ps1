# Python 3.14 설정 스크립트
# GUI를 먼저 닫고 실행하세요!

Write-Host "=== Python 3.14 환경 설정 ===" -ForegroundColor Cyan
Write-Host ""

# 1. .venv 삭제
Write-Host "1. 기존 가상환경 삭제 중..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    try {
        Remove-Item -Recurse -Force .venv
        Write-Host "   ✅ 삭제 완료" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 삭제 실패: $_" -ForegroundColor Red
        Write-Host "   GUI 창이 실행 중이면 먼저 닫아주세요!" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   ℹ️  .venv 없음" -ForegroundColor Cyan
}

# 2. Python 3.14 확인
Write-Host ""
Write-Host "2. Python 3.14 확인 중..." -ForegroundColor Yellow
$python314Path = "C:\Users\WithForceUser\AppData\Local\Programs\Python\Python314\python.exe"
if (Test-Path $python314Path) {
    & $python314Path --version
    Write-Host "   ✅ Python 3.14 발견" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python 3.14 없음: $python314Path" -ForegroundColor Red
    exit 1
}

# 3. UV 캐시 정리
Write-Host ""
Write-Host "3. UV 캐시 정리 중..." -ForegroundColor Yellow
uv cache clean
Write-Host "   ✅ 캐시 정리 완료" -ForegroundColor Green

# 4. 가상환경 생성
Write-Host ""
Write-Host "4. 가상환경 생성 중..." -ForegroundColor Yellow
uv venv --python $python314Path
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 가상환경 생성 실패!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 가상환경 생성 완료" -ForegroundColor Green

# 5. 패키지 설치
Write-Host ""
Write-Host "5. 패키지 설치 중 (시간이 걸릴 수 있습니다)..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 패키지 설치 실패!" -ForegroundColor Red
    Write-Host ""
    Write-Host "문제가 발생한 경우:" -ForegroundColor Yellow
    Write-Host "  1. Python 3.14가 정상 설치되었는지 확인" -ForegroundColor White
    Write-Host "  2. 인터넷 연결 확인" -ForegroundColor White
    Write-Host "  3. UV 버전 확인: uv --version" -ForegroundColor White
    exit 1
}
Write-Host "   ✅ 패키지 설치 완료" -ForegroundColor Green

# 6. 테스트
Write-Host ""
Write-Host "6. 설치 확인 중..." -ForegroundColor Yellow
Write-Host "   Python 버전:"
.venv\Scripts\python.exe --version
Write-Host "   PySide6 버전:"
.venv\Scripts\python.exe -c "import PySide6; print(PySide6.__version__)"

Write-Host ""
Write-Host "=== 설정 완료! ===" -ForegroundColor Green
Write-Host ""
Write-Host "이제 다음 명령어를 사용할 수 있습니다:" -ForegroundColor Cyan
Write-Host "  uv run src\main_gui.py   # GUI 실행" -ForegroundColor White
Write-Host "  uv run src\main_cli.py   # CLI 실행" -ForegroundColor White
Write-Host ""
Write-Host "또는:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\python.exe src\main_gui.py" -ForegroundColor White
