# WMV to Smart TV Converter

A modern, user-friendly desktop application for converting WMV video files to MP4 format, optimized for maximum compatibility with Smart TVs (Samsung, LG, Sony, Panasonic, and others).

## Features

- **Modern GUI** - Clean, dark-themed interface built with CustomTkinter
- **GPU Acceleration** - Optional NVIDIA NVENC support for 5-10x faster encoding on RTX GPUs
- **Smart TV Optimized** - Output settings specifically tuned for TV playback compatibility
- **Batch Processing** - Convert multiple WMV files automatically
- **Progress Tracking** - Real-time progress bar and detailed conversion log
- **Portable** - No installation required, FFmpeg bundled in the package

## Quick Start

### Prerequisites

- Windows 10/11
- Python 3.9+ (if running from source)

### Option 1: Standalone Executable

1. Download the latest release
2. Run `wmv_to_smarttv.exe`
3. Select a folder with WMV files
4. Click "Convert All"

### Option 2: Running from Source

```bash
pip install customtkinter
python wmv_to_smarttv.py
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

## Supported Smart TVs

- Samsung (Tizen, webOS)
- LG (webOS)
- Sony (Android TV)
- Panasonic
- Philips
- TCL (Roku TV)
- Hisense
- And most other H.264-compatible Smart TVs

## Project Structure

```
wmv-to-smarttv/
├── bin/                    # FFmpeg executables
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── wmv_to_smarttv.py       # Main application (GUI)
├── README.md
├── LICENSE
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### "FFmpeg not found" error
The FFmpeg binary should be in the `bin/` folder. If running from source, ensure FFmpeg is in your PATH or in the project directory.

### Conversion fails on Smart TV
Ensure you're using the default settings. The `yuv420p` pixel format is critical for TV compatibility.

### GPU encoding not working
- Verify NVIDIA drivers are installed
- Ensure your GPU supports NVENC (GTX/RTX series)
- Check that FFmpeg was built with NVENC support

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed wmv_to_smarttv.py
```

## License

This project uses FFmpeg under the [LGPL license](https://www.ffmpeg.org/legal.html).

## Credits

- FFmpeg: https://ffmpeg.org/
- CustomTkinter: https://github.com/TomSchimansky/CustomTkinter
