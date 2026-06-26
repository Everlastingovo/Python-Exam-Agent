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
$SupportedPythonMajors = @(3)
$SupportedPythonMinors = @(12, 13)
$PreferredPythonVersions = @("3.12", "3.13")

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

function Get-PythonVersionText {
    param([string]$Executable)

    if (-not (Test-Path -LiteralPath $Executable)) {
        return $null
    }

    try {
        $VersionText = & $Executable -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    }
    catch {
        return $null
    }

    if ($LASTEXITCODE -ne 0 -or -not $VersionText) {
        return $null
    }

    return $VersionText
}

function Test-SupportedPython {
    param([string]$Executable)

    $VersionText = Get-PythonVersionText $Executable
    if (-not $VersionText) {
        return $false
    }

    $Parts = $VersionText.Split(".")
    return ($SupportedPythonMajors -contains [int]$Parts[0] -and $SupportedPythonMinors -contains [int]$Parts[1])
}

function Test-SystemPythonSupported {
    param([string]$Command)

    $SystemVersion = & $Command -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        return $false
    }

    $Parts = $SystemVersion.Split(".")
    return ($SupportedPythonMajors -contains [int]$Parts[0] -and $SupportedPythonMinors -contains [int]$Parts[1])
}

function New-ProjectVenv {
    $PyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($PyCommand) {
        foreach ($Version in $PreferredPythonVersions) {
            & py "-$Version" -m venv $VenvDir
            if ($LASTEXITCODE -eq 0) {
                return
            }
        }
        Write-Warning "Python 3.12 or 3.13 was not found by the py launcher."
    }

    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $PythonCommand) {
        throw "Python was not found. Please install Python 3.12 or 3.13, then run this script again."
    }

    $SystemVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-SystemPythonSupported "python")) {
        throw "This project supports Python 3.12 or 3.13. Your default python is $SystemVersion. Please install Python 3.12/3.13 or make it available through the py launcher."
    }

    Invoke-Checked "python" @("-m", "venv", $VenvDir)
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
if (Test-Path -LiteralPath $PythonExe) {
    if (-not (Test-SupportedPython $PythonExe)) {
        $ExistingVersion = Get-PythonVersionText $PythonExe
        Write-Warning "Existing .venv uses Python $ExistingVersion. Recreating .venv with Python 3.12 or 3.13."
        $ResolvedVenv = Resolve-Path -LiteralPath $VenvDir
        $ResolvedRoot = Resolve-Path -LiteralPath $Root
        if (-not $ResolvedVenv.Path.StartsWith($ResolvedRoot.Path)) {
            throw "Refusing to remove a virtual environment outside the project folder: $ResolvedVenv"
        }
        Remove-Item -LiteralPath $VenvDir -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    New-ProjectVenv
}

if (-not (Test-SupportedPython $PythonExe)) {
    $ActualVersion = Get-PythonVersionText $PythonExe
    throw "The virtual environment is using Python $ActualVersion, but this project supports Python 3.12 or 3.13."
}
else {
    $ActualVersion = Get-PythonVersionText $PythonExe
    Write-Host "Using Python $ActualVersion from .venv." -ForegroundColor Green
}

Invoke-Checked $PythonExe @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked $PythonExe @("-m", "pip", "install", "--upgrade", "wheel", "setuptools")

if (-not $NoInstall) {
    try {
        Invoke-Checked $PythonExe @("-m", "pip", "install", "--only-binary=:all:", "-r", (Join-Path $Root "requirements.txt"))
    }
    catch {
        Write-Host ""
        Write-Host "Dependency installation failed." -ForegroundColor Red
        Write-Host "Most likely reason: Python is not 3.12/3.13, or pip cannot download a prebuilt wheel for this machine."
        Write-Host "Please install Python 3.12 or 3.13, then run .\run.ps1 again."
        throw
    }
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
