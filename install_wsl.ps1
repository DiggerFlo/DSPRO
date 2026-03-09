#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Installs WSL2 with Ubuntu 24.04 on a new Windows machine.

.DESCRIPTION
    Run this script as Administrator in PowerShell on any Windows machine.
    It enables WSL2, installs Ubuntu 24.04, and tells you what to do after restart.

.EXAMPLE
    Right-click PowerShell -> "Run as Administrator"
    .\install_wsl.ps1
#>

param(
    [string]$Distribution = "Ubuntu-24.04"
)

$ErrorActionPreference = "Stop"

function Write-Step  { param($msg) Write-Host "`n  >> $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  [!]  $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "  [X]  $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "=================================================" -ForegroundColor Magenta
Write-Host "   DSPRO - WSL2 Development Environment Setup   " -ForegroundColor Magenta
Write-Host "=================================================" -ForegroundColor Magenta
Write-Host ""

# ── 1. Admin check ────────────────────────────────────────────────────────────
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Fail "Dieses Skript muss als Administrator ausgefuehrt werden."
    Write-Host "         Rechtsklick auf PowerShell -> 'Als Administrator ausfuehren'" -ForegroundColor White
    exit 1
}

# ── 2. Windows-Version pruefen ────────────────────────────────────────────────
Write-Step "Pruefe Windows-Version..."
$build = [System.Environment]::OSVersion.Version.Build
if ($build -lt 19041) {
    Write-Fail "WSL2 benoetigt mindestens Windows 10 Build 19041 (du hast Build $build)."
    Write-Host "         Bitte fuehre zuerst ein Windows-Update durch." -ForegroundColor White
    exit 1
}
Write-Ok "Windows Build $build ist kompatibel."

# ── 3. WSL bereits installiert? ───────────────────────────────────────────────
Write-Step "Pruefe ob WSL bereits installiert ist..."
$wslAvailable = $false
try {
    $null = wsl --status 2>&1
    if ($LASTEXITCODE -eq 0) { $wslAvailable = $true }
} catch {}

if ($wslAvailable) {
    Write-Ok "WSL ist bereits installiert."

    Write-Step "Pruefe ob $Distribution bereits vorhanden ist..."
    $distros = wsl --list --quiet 2>&1
    $distroFound = ($distros | Where-Object { $_ -match $Distribution.Replace(".", "\.") }).Count -gt 0

    if ($distroFound) {
        Write-Ok "$Distribution ist bereits installiert — kein Neustart noetig."
        Write-Host ""
        Write-Host "  Oeffne Ubuntu und fahre mit Schritt 2 fort (bootstrap_wsl.sh)." -ForegroundColor Green
        Write-Host ""
        exit 0
    }
}

# ── 4. WSL2 + Ubuntu installieren ────────────────────────────────────────────
Write-Step "Installiere WSL2 mit $Distribution ..."
Write-Warn "Dies kann einige Minuten dauern. Danach ist ein Neustart erforderlich."
Write-Host ""

wsl --install -d $Distribution

# ── 5. Hinweise nach Installation ─────────────────────────────────────────────
Write-Host ""
Write-Host "=================================================" -ForegroundColor Green
Write-Host "   WSL2 + $Distribution erfolgreich installiert! " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  NAECHSTE SCHRITTE nach dem Neustart:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Windows neu starten (falls noch nicht passiert)"
Write-Host "  2. Ubuntu oeffnet sich automatisch"
Write-Host "     -> Benutzername + Passwort festlegen"
Write-Host ""
Write-Host "  3. Im Ubuntu-Terminal folgendes ausfuehren:" -ForegroundColor Yellow
Write-Host ""
Write-Host "     curl -fsSL https://raw.githubusercontent.com/<DEIN-USER>/<DEIN-REPO>/main/bootstrap_wsl.sh | bash"  -ForegroundColor Cyan
Write-Host ""
Write-Host "     ODER: Repo klonen und dann ausfuehren:" -ForegroundColor White
Write-Host "     git clone https://github.com/<DEIN-USER>/<DEIN-REPO>.git" -ForegroundColor Cyan
Write-Host "     cd <DEIN-REPO> && bash bootstrap_wsl.sh" -ForegroundColor Cyan
Write-Host ""

$restart = Read-Host "Jetzt neu starten? (j/n)"
if ($restart -eq "j" -or $restart -eq "J" -or $restart -eq "y" -or $restart -eq "Y") {
    Write-Warn "Starte in 5 Sekunden neu..."
    Start-Sleep -Seconds 5
    Restart-Computer -Force
} else {
    Write-Warn "Bitte manuell neu starten, damit WSL aktiviert wird."
}
