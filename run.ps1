# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 현재 스크립트의 디렉토리로 이동 (한글 경로 처리 개선)
# $PSScriptRoot를 우선 사용 (PowerShell 3.0+)
if ($PSScriptRoot) {
    try {
        Push-Location -LiteralPath $PSScriptRoot -ErrorAction Stop
    } catch {
        # Push-Location 실패 시 Set-Location 시도
        try {
            Set-Location -LiteralPath $PSScriptRoot -ErrorAction Stop
        } catch {
            # 경로 설정 실패해도 계속 진행
            Write-Host "경로 설정을 건너뜁니다. 현재 디렉토리를 사용합니다." -ForegroundColor Yellow
        }
    }
} else {
    # $PSScriptRoot가 없는 경우 (PowerShell 2.0 이하)
    try {
        $scriptPath = $MyInvocation.MyCommand.Path
        if ($scriptPath) {
            $scriptDir = [System.IO.Path]::GetDirectoryName($scriptPath)
            if ([System.IO.Directory]::Exists($scriptDir)) {
                Push-Location -LiteralPath $scriptDir -ErrorAction Stop
            }
        }
    } catch {
        Write-Host "경로 설정을 건너뜁니다. 현재 디렉토리를 사용합니다." -ForegroundColor Yellow
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "도서 기록장 실행 중..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python 설치 확인 (방법 1 개선 - 출력 내용으로 확인)
Write-Host "[1/3] Python 설치 확인 중..." -ForegroundColor Yellow
try {
    $pythonOutput = & python --version 2>&1 | Out-String
    if ($pythonOutput -match "Python\s+\d+\.\d+") {
        Write-Host "✓ $($pythonOutput.Trim())" -ForegroundColor Green
    } else {
        throw "Python을 찾을 수 없습니다."
    }
} catch {
    Write-Host "✗ Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "  Python을 먼저 설치해주세요: https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# 필요한 패키지 확인 및 설치 (방법 2 개선 - 출력 내용으로 확인)
Write-Host ""
Write-Host "[2/3] 필요한 패키지 확인 중..." -ForegroundColor Yellow
$needsInstall = $false

try {
    $pipOutput = & pip show streamlit 2>&1 | Out-String
    if (-not ($pipOutput -match "Name:\s+streamlit")) {
        $needsInstall = $true
    }
} catch {
    $needsInstall = $true
}

if ($needsInstall) {
    Write-Host "✗ 필요한 패키지가 설치되어 있지 않습니다." -ForegroundColor Yellow
    Write-Host "  자동으로 설치합니다..." -ForegroundColor Yellow
    try {
        $installOutput = & pip install -r requirements.txt 2>&1 | Out-String
        if ($installOutput -match "Successfully installed" -or $installOutput -match "Requirement already satisfied") {
            Write-Host "✓ 패키지 설치 완료" -ForegroundColor Green
        } else {
            # 설치 실패 여부를 더 정확히 확인
            if ($installOutput -match "ERROR" -or $installOutput -match "Could not find") {
                throw "패키지 설치 실패"
            } else {
                # 경고만 있고 설치가 완료된 경우
                Write-Host "✓ 패키지 설치 완료" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "✗ 패키지 설치에 실패했습니다." -ForegroundColor Red
        Write-Host "  수동으로 설치해주세요: pip install -r requirements.txt" -ForegroundColor Red
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
} else {
    Write-Host "✓ 모든 패키지가 설치되어 있습니다." -ForegroundColor Green
}

# Streamlit 실행
Write-Host ""
Write-Host "[3/3] Streamlit 애플리케이션 실행 중..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& python -m streamlit run app.py
