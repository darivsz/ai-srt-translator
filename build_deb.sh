#!/bin/bash
set -e

VERSION="1.4.0"
PACKAGE_NAME="ai-srt-translator"
BUILD_DIR="deb_build/${PACKAGE_NAME}_${VERSION}_amd64"

echo "=== Building standalone binary with PyInstaller ==="
# Run pyinstaller using the spec file
pyinstaller --noconfirm gui_translator.spec

echo "=== Preparing .deb directory structure ==="
# Clean old builds
rm -rf deb_build
rm -f ${PACKAGE_NAME}_${VERSION}_amd64.deb

# Create directory structure
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/pixmaps"
mkdir -p "${BUILD_DIR}/DEBIAN"

# Copy binary and icon
cp dist/gui_translator "${BUILD_DIR}/usr/bin/ai-srt-translator"
cp icon.png "${BUILD_DIR}/usr/share/pixmaps/ai-srt-translator.png"

# Create .desktop file
cat <<EOT > "${BUILD_DIR}/usr/share/applications/ai-srt-translator.desktop"
[Desktop Entry]
Version=${VERSION}
Name=AI Subtitle Translator
Comment=Translate SRT subtitles using Google Gemini AI
Exec=ai-srt-translator
Icon=ai-srt-translator
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOT

# Create DEBIAN/control file
cat <<EOT > "${BUILD_DIR}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: amd64
Maintainer: darivsz <darivsz@gmail.com>
Depends: libc6
Section: utils
Priority: optional
Description: A powerful tool to translate subtitle files using Google Gemini AI.
EOT

echo "=== Building .deb package ==="
dpkg-deb --build "${BUILD_DIR}" .

echo "=== Cleanup ==="
rm -rf deb_build

echo "=== SUCCESS! Package ${PACKAGE_NAME}_${VERSION}_amd64.deb has been built! ==="

