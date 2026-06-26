param(
    [switch]$NoInstall,
    [switch]$NoBrowser,
    [switch]$Help
)

if ($Help) {
    Write-Host "Python Exam Agent one-click runner"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\run.ps1              Start backend on 8000 and frontend on 3000"
    Write-Host "  .\run.ps1 -NoInstall   Skip dependency installation"
    Write-Host "  .\run.ps1 -NoBrowser   Do not open the browser automatically"
    Write-Host "  .\stop.ps1             Stop servers started by this runner"
    exit 0
}

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$RunDir = Join-Path $Root ".run"
$VenvDir = Join-Path $Root ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Stop-ProjectProcess {
    param([string]$Name)

    $PidFile = Join-Path $RunDir "$Name.pid"
    if (-not (Test-Path -LiteralPath $PidFile)) {
        return
    }

    $ProcessIdText = (Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($ProcessIdText -match "^\d+$") {
        $ExistingProcess = Get-Process -Id ([int]$ProcessIdText) -ErrorAction SilentlyContinue
        if ($ExistingProcess) {
            Write-Host "Stopping existing $Name process (PID $ProcessIdText)..."
            Stop-Process -Id ([int]$ProcessIdText) -Force
        }
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

function Wait-ForPort {
    param(
        [int]$Port,
        [string]$Name
    )

    for ($Attempt = 1; $Attempt -le 40; $Attempt++) {
        $Client = New-Object System.Net.Sockets.TcpClient
        try {
            $AsyncResult = $Client.BeginConnect("127.0.0.1", $Port, $null, $null)
            if ($AsyncResult.AsyncWaitHandle.WaitOne(500)) {
                $Client.EndConnect($AsyncResult)
                $Client.Close()
                Write-Host "$Name is ready on port $Port." -ForegroundColor Green
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
        finally {
            $Client.Close()
        }
    }

    Write-Warning "$Name did not answer on port $Port yet. Check .run\$Name.log and .run\$Name-error.log for details."
}

Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null

Write-Step "Preparing Python environment"
if (-not (Test-Path -LiteralPath $PythonExe)) {
    $PyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($PyCommand) {
        & py -3 -m venv $VenvDir
    }
    else {
        $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $PythonCommand) {
            throw "Python was not found. Please install Python 3.12 or newer, then run this script again."
        }
        & python -m venv $VenvDir
    }
}

if (-not $NoInstall) {
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r (Join-Path $Root "requirements.txt")
}
else {
    Write-Host "Skipping dependency installation because -NoInstall was provided."
}

Write-Step "Restarting project servers"
Stop-ProjectProcess "backend"
Stop-ProjectProcess "frontend"

$BackendLog = Join-Path $RunDir "backend.log"
$FrontendLog = Join-Path $RunDir "frontend.log"
$BackendErrorLog = Join-Path $RunDir "backend-error.log"
$FrontendErrorLog = Join-Path $RunDir "frontend-error.log"

Remove-Item -LiteralPath $BackendLog, $FrontendLog, $BackendErrorLog, $FrontendErrorLog -Force -ErrorAction SilentlyContinue

$BackendProcess = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendLog `
    -RedirectStandardError $BackendErrorLog `
    -WindowStyle Hidden `
    -PassThru

$FrontendProcess = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList @("-m", "http.server", "3000") `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendLog `
    -RedirectStandardError $FrontendErrorLog `
    -WindowStyle Hidden `
    -PassThru

$BackendProcess.Id | Set-Content -LiteralPath (Join-Path $RunDir "backend.pid") -Encoding ASCII
$FrontendProcess.Id | Set-Content -LiteralPath (Join-Path $RunDir "frontend.pid") -Encoding ASCII

Wait-ForPort -Port 8000 -Name "backend"
Wait-ForPort -Port 3000 -Name "frontend"

$FrontendUrl = "http://localhost:3000"
$BackendUrl = "http://localhost:8000/docs"

Write-Step "Ready"
Write-Host "Frontend: $FrontendUrl" -ForegroundColor Green
Write-Host "Backend docs: $BackendUrl" -ForegroundColor Green
Write-Host "Logs: .run\backend.log, .run\backend-error.log, .run\frontend.log, .run\frontend-error.log"
Write-Host "Stop servers: .\stop.ps1"

if (-not $NoBrowser) {
    Start-Process $FrontendUrl
}
