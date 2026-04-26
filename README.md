# WMV to Smart TV Converter

A modern desktop application for converting WMV video files to MP4, optimized for maximum compatibility with Smart TVs (Samsung, LG, Sony, Panasonic, and others).

## Features

- **Modern GUI** - Clean, dark-themed interface built with CustomTkinter
- **GPU Acceleration** - Optional NVIDIA NVENC support for 5-10x faster encoding on RTX GPUs
- **Smart TV Optimized** - Output settings specifically tuned for TV playback compatibility
- **Batch Processing** - Convert multiple WMV files automatically
- **Progress Tracking** - Real-time progress bar and detailed conversion log
- **Portable** - No installation required (FFmpeg as separate download)

## Quick Start

### 1. Download

Download the latest release from: **https://github.com/drycool/Convert-WMV-to-Smart-TV-MP4/releases**

Contains two parts:
- `wmv-to-smarttv.exe` or `wmv_to_smarttv.py` - the converter
- `ffmpeg-binaries.zip` - FFmpeg executables

### 2. Setup

**Option A: Using Release package (recommended)**
1. Extract both archives to the same folder
2. Keep `bin/` folder next to the executable
3. Run `wmv_to_smarttv.py` or double-click `wmv-to-smarttv.exe`

**Option B: Using system FFmpeg**
1. Install FFmpeg: `winget install ffmpeg`
2. Run the converter - it will use system FFmpeg automatically

### 3. Run

```bash
python wmv_to_smarttv.py
```

Or if you have the executable:
```bash
./wmv-to-smarttv.exe
```

## Usage

1. **Select Folder** - Click "Browse" to choose a folder containing WMV files
2. **GPU Option** - Enable "GPU Acceleration" for NVIDIA GPUs (recommended)
3. **Convert** - Click "Convert All" to start batch conversion
4. **View Results** - Click "Open Folder" when done to see your MP4 files

## Encoding Settings

| Parameter | Value | Description |
|------------|-------|-------------|
| Video Codec | H.264 (libx264/h264_nvenc) | Universal Smart TV support |
| Pixel Format | yuv420p | Required by most TV chipsets |
| Audio Codec | AAC 192kbps | Stereo, works on all brands |
| Container | MP4 | Universal container format |
| Quality | CRF 22 | High quality, reasonable file size |

### GPU vs CPU Encoding

| Mode | Encoder | Speed | Quality |
|------|---------|-------|---------|
| GPU | h264_nvenc | Fast (5-10x) | Good |
| CPU | libx264 | Slow | Excellent |

**Note:** GPU mode uses NVIDIA NVENC. Requires RTX/GTX GPU with drivers installed.

## Supported Smart TVs

- Samsung (Tizen, webOS)
- LG (webOS)
- Sony (Android TV)
- Panasonic
- Philips
- TCL (Roku TV)
- Hisense
- And most other H.264-compatible Smart TVs

## FFmpeg

This project uses FFmpeg under the [LGPL license](https://www.ffmpeg.org/legal.html).

FFmpeg binaries are not included in the repository. Download from Releases or install separately.

## Project Structure

```
wmv-to-smarttv/
├── wmv_to_smarttv.py       # Main application (Python)
├── wmv-to-smarttv.exe      # Compiled executable (if available)
├── bin/                    # FFmpeg (from Releases or your own)
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── README.md
├── LICENSE
└── requirements.txt
```

## Installing Dependencies (for Python source)

```bash
pip install customtkinter
```

## Troubleshooting

### "FFmpeg not found" error
1. Download `ffmpeg-binaries.zip` from Releases
2. Extract to `bin/` folder next to the script
3. Or install FFmpeg system-wide: `winget install ffmpeg`

### Conversion fails on Smart TV
Ensure you're using the default settings. The `yuv420p` pixel format is critical for TV compatibility.

### GPU encoding not working
- Verify NVIDIA drivers are installed
- Ensure your GPU supports NVENC (GTX/RTX series)
- Check that FFmpeg was built with NVENC support

## Building Executable

```bash
pip install pyinstaller customtkinter
pyinstaller --onefile --windowed --add-binary "bin;bin" wmv_to_smarttv.py
```

## License

MIT License - see LICENSE file

FFmpeg is licensed under [LGPL 2.1](https://www.ffmpeg.org/legal.html)
