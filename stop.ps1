param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Stop Python Exam Agent servers started by run.ps1"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\stop.ps1"
    exit 0
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".run"

function Stop-ProjectProcess {
    param([string]$Name)

    $PidFile = Join-Path $RunDir "$Name.pid"
    if (-not (Test-Path -LiteralPath $PidFile)) {
        Write-Host "$Name is not running."
        return
    }

    $ProcessIdText = (Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($ProcessIdText -match "^\d+$") {
        $ExistingProcess = Get-Process -Id ([int]$ProcessIdText) -ErrorAction SilentlyContinue
        if ($ExistingProcess) {
            Stop-Process -Id ([int]$ProcessIdText) -Force
            Write-Host "Stopped $Name (PID $ProcessIdText)." -ForegroundColor Green
        }
        else {
            Write-Host "$Name process was already stopped."
        }
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

Stop-ProjectProcess "backend"
Stop-ProjectProcess "frontend"
