# WMV to Smart TV Converter

A desktop application for converting WMV video files to MP4 with settings tuned for Smart TV playback.

## Features

- Multilingual interface: English and Russian
- CustomTkinter desktop GUI
- NVIDIA NVENC acceleration
- Smart TV compatible MP4 output
- Batch conversion with progress log
- Portable mode with bundled FFmpeg

## Repository and Releases

Repository:

`https://github.com/drycool/Convert-WMV-to-Smart-TV-MP4`

Releases:

`https://github.com/drycool/Convert-WMV-to-Smart-TV-MP4/releases`

Expected release assets:

- `WMV_to_SmartTV-portable.zip`
- `ffmpeg-binaries.zip`
- `wmv_to_smarttv.py`

## Quick Start

### Portable package

1. Download the portable archive from Releases.
2. Extract the archive.
3. Run `WMV_to_SmartTV.exe`.

The executable searches for FFmpeg in this order:

1. `_internal/bin/ffmpeg.exe`
2. `bin/ffmpeg.exe`
3. System `PATH`

### Script mode

1. Download `wmv_to_smarttv.py`
2. Download `ffmpeg-binaries.zip`
3. Extract the archive so `bin/` is next to `wmv_to_smarttv.py`
4. Run:

```bash
python wmv_to_smarttv.py
```

### Optional system FFmpeg

```powershell
winget install ffmpeg
```

## Usage

1. Select the UI language in the top-right corner.
2. Choose a folder with `.wmv` files.
3. Enable GPU mode if NVENC is available.
4. Click `Convert All`.
5. Open the folder with converted MP4 files.

## Compatibility Defaults

- Video codec: `H.264`
- Pixel format: `yuv420p`
- Audio codec: `AAC 192k`
- Container: `MP4`

`yuv420p` is required for reliable playback on many TVs.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run from source:

```bash
python wmv_to_smarttv.py
```

## Portable Build

Build the application as an onedir package:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --onedir --name WMV_to_SmartTV --add-data "bin;_internal/bin" wmv_to_smarttv.py
```

Portable resource check:

```bash
python test_portable_resources.py dist/WMV_to_SmartTV/WMV_to_SmartTV.exe
```

## Troubleshooting

### FFmpeg not found

1. Download `ffmpeg-binaries.zip` from Releases
2. Extract to `bin/` next to the script, or `_internal/bin/` inside the portable build
3. Or install FFmpeg with `winget install ffmpeg`

### GPU mode is unavailable

- Update NVIDIA drivers
- Confirm your GPU supports NVENC
- Switch to CPU mode if needed

## License

MIT License. FFmpeg is licensed under LGPL 2.1.
