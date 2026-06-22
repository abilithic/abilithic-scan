@echo off
REM ============================================================
REM  Abilithic Scan - one-click Windows build
REM  Produces dist\AbilithicScan.exe
REM ============================================================
setlocal

echo [1/4] Creating / activating virtual environment...
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements-dev.txt

echo [3/4] (Optional) Place a Windows Nmap build in abilithic_scan\data\nmap\
echo        (nmap.exe + data files) to ship a self-contained binary.

echo [4/4] Building the .exe with PyInstaller...
pyinstaller abilithic-scan.spec --noconfirm --clean

echo.
echo Done. Your executable is at: dist\AbilithicScan.exe
echo Generating SHA-256 checksum...
certutil -hashfile dist\AbilithicScan.exe SHA256 > dist\AbilithicScan.exe.sha256.txt

echo.
echo Build complete.
pause
endlocal
