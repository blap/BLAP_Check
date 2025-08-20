@echo off
echo "Building standalone executable..."

REM Run PyInstaller with the spec file
REM --noconfirm will overwrite the dist folder without asking
pyinstaller main.spec --noconfirm

REM Check if build was successful
if %errorlevel% equ 0 (
  echo "Build successful."
  echo "The portable application is available in the 'dist\KetarinClone' folder."
  echo "You can zip this folder to share it."
) else (
  echo "Build failed."
  exit /b 1
)
