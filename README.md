# WMV to Smart TV Converter

A modern desktop application for converting WMV video files to MP4, optimized for maximum compatibility with Smart TVs (Samsung, LG, Sony, Panasonic, and others).

## Features

- **Modern GUI** - Clean, dark-themed interface built with CustomTkinter
- **GPU Acceleration** - NVIDIA NVENC support for 5-10x faster encoding on RTX GPUs
- **Smart TV Optimized** - Output settings specifically tuned for TV playback
- **Batch Processing** - Convert multiple WMV files automatically
- **Progress Tracking** - Real-time progress bar and detailed log
- **Portable Mode** - No installation required, FFmpeg bundled separately

## System Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows 10/11 |
| Python | 3.10+ (for running from source) |
| GPU | NVIDIA GPU with NVENC (optional, for hardware acceleration) |
| RAM | 4GB+ recommended |
| Disk | 200MB for FFmpeg + space for video files |

## Quick Start

### 1. Download

Go to **https://github.com/drycool/Convert-WMV-to-Smart-TV-MP4/releases**

Download:
- `wmv_to_smarttv.py` - the converter script
- `ffmpeg-binaries.zip` - FFmpeg executables

### 2. Setup (Portable Mode)

```
1. Extract ffmpeg-binaries.zip
2. You will get a "bin/" folder containing:
   ├── ffmpeg.exe
   ├── ffplay.exe
   └── ffprobe.exe
3. Place the "bin/" folder in the same directory as wmv_to_smarttv.py
4. Run: python wmv_to_smarttv.py
```

**Important:** The `bin/` folder must be next to `wmv_to_smarttv.py`, not inside it.

### 3. Alternative: System FFmpeg

If you prefer not to use the portable version:
```powershell
winget install ffmpeg
```
The script will automatically detect FFmpeg in your system PATH.

## Usage

1. **Select Folder** - Click "Browse" to choose a folder with WMV files
2. **GPU Option** - Check "GPU Acceleration" for NVIDIA GPUs (recommended)
3. **Convert** - Click "Convert All" to start batch conversion
4. **Open Folder** - Click to view your new MP4 files

## Why These Settings Work on Smart TVs

| Parameter | Value | Why It Matters |
|-----------|-------|----------------|
| Video Codec | H.264 (AVC) | Required by virtually all Smart TV chipsets |
| Pixel Format | yuv420p | Critical! TVs cannot play 4:4:4 or 10-bit color |
| Audio Codec | AAC 192kbps | Universal support, no licensing issues |
| Container | MP4 | Most compatible container format |
| Quality | CRF 22 | High quality, smaller file size |

The `yuv420p` pixel format is the most important setting. Many converters produce files that play on PC but fail on TVs due to incompatible color formats.

## GPU vs CPU Encoding

| Mode | Encoder | Speed | Quality | Use Case |
|------|---------|-------|---------|----------|
| GPU | h264_nvenc | 5-10x faster | Good | RTX/GTX GPUs, large files |
| CPU | libx264 | Slow | Excellent | No NVIDIA GPU |

## Supported Smart TVs

- Samsung (Tizen, webOS)
- LG (webOS)
- Sony (Android TV)
- Panasonic (Firefox OS)
- Philips
- TCL / Roku TV
- Hisense
- And most other H.264-compatible Smart TVs

## Project Structure

```
wmv-to-smarttv/
├── wmv_to_smarttv.py       # Main application
├── bin/                    # FFmpeg (from Releases)
│   ├── ffmpeg.exe          # Video encoder
│   ├── ffplay.exe          # Media player
│   └── ffprobe.exe         # Media analyzer
├── README.md
├── LICENSE
└── requirements.txt        # Python dependencies
```

## Installing Dependencies (Development)

```bash
pip install customtkinter
python wmv_to_smarttv.py
```

## Troubleshooting

### "FFmpeg not found"
1. Download `ffmpeg-binaries.zip` from Releases
2. Extract so `bin/` folder is next to `wmv_to_smarttv.py`
3. Or install system FFmpeg: `winget install ffmpeg`

### Video plays on PC but not on Smart TV
- The `yuv420p` setting is critical for TV compatibility
- Don't change the default pixel format unless advised

### GPU encoding is slow or fails
- Verify NVIDIA drivers are installed
- Ensure your GPU supports NVENC (GTX/RTX series)
- Try CPU mode as fallback

## Building Executable

```bash
pip install pyinstaller customtkinter
pyinstaller --onefile --windowed --add-binary "bin;bin" wmv_to_smarttv.py
```

## License

MIT License - see LICENSE file

FFmpeg is licensed under [LGPL 2.1](https://www.ffmpeg.org/legal.html)
