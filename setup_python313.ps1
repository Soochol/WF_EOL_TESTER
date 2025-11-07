# Python 3.13 설정 스크립트
# Python 3.13을 먼저 설치하고 실행하세요!

Write-Host "=== Python 3.13 환경 설정 ===" -ForegroundColor Cyan
Write-Host ""

# Python 3.13 경로 확인
$python313Paths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Python313\python.exe"
)

$python313Path = $null
foreach ($path in $python313Paths) {
    if (Test-Path $path) {
        $python313Path = $path
        break
    }
}

if ($null -eq $python313Path) {
    Write-Host "❌ Python 3.13을 찾을 수 없습니다!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python 3.13을 먼저 설치하세요:" -ForegroundColor Yellow
    Write-Host "  1. https://www.python.org/downloads/ 방문" -ForegroundColor White
    Write-Host "  2. 'Python 3.13.x' 다운로드" -ForegroundColor White
    Write-Host "  3. 설치 시 'Add Python to PATH' 체크!" -ForegroundColor White
    Write-Host ""
    Write-Host "설치 후 PowerShell을 재시작하고 이 스크립트를 다시 실행하세요." -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Python 3.13 발견: $python313Path" -ForegroundColor Green
& $python313Path --version
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

# 2. .venv_old 백업 삭제
Write-Host ""
Write-Host "2. 이전 백업 정리 중..." -ForegroundColor Yellow
if (Test-Path ".venv_old_windowsstore") {
    Remove-Item -Recurse -Force .venv_old_windowsstore
    Write-Host "   ✅ 백업 삭제 완료" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  백업 없음" -ForegroundColor Cyan
}

# 3. UV 캐시 정리
Write-Host ""
Write-Host "3. UV 캐시 정리 중..." -ForegroundColor Yellow
uv cache clean
Write-Host "   ✅ 캐시 정리 완료" -ForegroundColor Green

# 4. 가상환경 생성
Write-Host ""
Write-Host "4. 가상환경 생성 중..." -ForegroundColor Yellow
uv venv --python $python313Path
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 가상환경 생성 실패!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 가상환경 생성 완료" -ForegroundColor Green

# 5. 패키지 설치
Write-Host ""
Write-Host "5. 패키지 설치 중 (5-10분 소요 예상)..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 패키지 설치 실패!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 패키지 설치 완료" -ForegroundColor Green

# 6. 설치 확인
Write-Host ""
Write-Host "6. 설치 확인 중..." -ForegroundColor Yellow
Write-Host "   Python 버전:" -ForegroundColor Cyan
.venv\Scripts\python.exe --version
Write-Host "   PySide6 버전:" -ForegroundColor Cyan
.venv\Scripts\python.exe -c "import PySide6; print(PySide6.__version__)"
Write-Host "   dependency-injector:" -ForegroundColor Cyan
.venv\Scripts\python.exe -c "import dependency_injector; print(dependency_injector.__version__)"

# 7. UV 실행 테스트
Write-Host ""
Write-Host "7. UV 실행 테스트 중..." -ForegroundColor Yellow
Write-Host "   명령: uv run python --version" -ForegroundColor Gray
uv run python --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ UV 정상 작동!" -ForegroundColor Green
} else {
    Write-Host "   ❌ UV 실행 실패" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 설정 완료! ===" -ForegroundColor Green
Write-Host ""
Write-Host "이제 다음 명령어를 사용할 수 있습니다:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  🚀 GUI 실행:" -ForegroundColor Yellow
Write-Host "     uv run src\main_gui.py" -ForegroundColor White
Write-Host ""
Write-Host "  📟 CLI 실행:" -ForegroundColor Yellow
Write-Host "     uv run src\main_cli.py" -ForegroundColor White
Write-Host ""
Write-Host "  🛠️  개발 도구:" -ForegroundColor Yellow
Write-Host "     uv run black src/" -ForegroundColor White
Write-Host "     uv run mypy src/" -ForegroundColor White
Write-Host "     uv run pylint src/" -ForegroundColor White
Write-Host ""
Write-Host "  ✅ 또는 직접 실행:" -ForegroundColor Yellow
Write-Host "     .venv\Scripts\python.exe src\main_gui.py" -ForegroundColor White
Write-Host ""
