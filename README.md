# AI SRT Translator

A powerful, fast, and UI-friendly tool to seamlessly translate `.srt` subtitle files into any language while preserving original timestamps and HTML formatting using Google's Gemini AI models.

## Features
- **Native GUI Interface**: Built with modern `customtkinter` with full Dark Mode support and native Linux file picker.
- **Robust AI Integration**: Connects to `gemini-2.5-flash`, `gemini-2.5-pro`, or `gemini-3.1-flash-lite` for hyper-fast, colloquial natural translations.
- **20+ Supported Languages**: Swedish, Norwegian, Polish, German, French, Spanish, Czech, and more.
- **Resume Protection**: Automatically saves progress incrementally. If an API rate limit interrupts translations, just restart the app, insert the same file, and it will pick up exactly where it left off!
- **Uneven Batch Fallback**: Protects against model hallucinations modifying array length using 1-by-1 fallback safety layers.
- **Global Config Persistence**: Remembers API key directly inside `~/.config/ai-srt-translator/config.json`.

## Installation (Ubuntu / Debian)
The easiest and recommended way to install the application and receive automatic updates is via the Gemfury APT repository:

```bash
# 1. Add the repository to your system sources
echo "deb [trusted=yes] https://apt.fury.io/darivsz/ /" | sudo tee /etc/apt/sources.list.d/fury.list

# 2. Update your package lists
sudo apt update

# 3. Install the application
sudo apt install ai-srt-translator
```
*(Once installed, the application will automatically update alongside your system when using `sudo apt upgrade`)*.

## Development Requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the App
```bash
python gui_translator.py
```

## Standalone Compilation / DEB Packaging
To package this app into a standalone `/usr/bin/` binary, use the PyInstaller helper script `build_deb.sh`.
