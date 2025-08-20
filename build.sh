#!/bin/bash
echo "Building standalone executable..."

# Run PyInstaller with the spec file
# --noconfirm will overwrite the dist folder without asking
pyinstaller main.spec --noconfirm

# Check if build was successful
if [ $? -eq 0 ]; then
  echo "Build successful. Zipping the output..."
  # Navigate into the dist directory to zip its contents
  (cd dist/KetarinClone && zip -r ../KetarinClone-linux-portable.zip .)
  echo ""
  echo "Portable version created at: dist/KetarinClone-linux-portable.zip"
else
  echo "Build failed."
  exit 1
fi
