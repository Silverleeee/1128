@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 도서 기록장 실행 중...
echo ========================================
echo.

echo [1/3] Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/3] 필요한 패키지 확인 중...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 필요한 패키지가 설치되어 있지 않습니다. 자동으로 설치합니다...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다.
        echo 수동으로 설치해주세요: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo 패키지 설치 완료
) else (
    echo 모든 패키지가 설치되어 있습니다.
)
echo.

echo [3/3] Streamlit 애플리케이션 실행 중...
echo ========================================
echo.

python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo [오류] 애플리케이션 실행 중 오류가 발생했습니다.
    pause
    exit /b 1
)

pause
