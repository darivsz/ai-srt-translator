#!/bin/bash
# Helper script explaining how the .deb package is built using PyInstaller.

# 1. Compile Source Using Pyinstaller
# Find CustomTkinter path:
CTK_PATH=$(python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))")

# Run pyinstaller:
pyinstaller --noconfirm --onefile --windowed \
    --add-data "$CTK_PATH:customtkinter/" \
    --add-data "icon.png:." \
    --icon=icon.png gui_translator.py

echo "Build complete! Binary located in ./dist/gui_translator"

# 2. Package into .deb (example script)
# mkdir -p deb_build/ai-srt-translator_1.3.0_amd64/usr/bin
# mkdir -p deb_build/ai-srt-translator_1.3.0_amd64/usr/share/applications
# mkdir -p deb_build/ai-srt-translator_1.3.0_amd64/usr/share/pixmaps
# mkdir -p deb_build/ai-srt-translator_1.3.0_amd64/DEBIAN
# cp dist/gui_translator deb_build/ai-srt-translator_1.3.0_amd64/usr/bin/ai-srt-translator
# cp icon.png deb_build/ai-srt-translator_1.3.0_amd64/usr/share/pixmaps/ai-srt-translator.png
# ... create DEBIAN/control ...
# dpkg-deb --build deb_build/ai-srt-translator_1.3.0_amd64 .
