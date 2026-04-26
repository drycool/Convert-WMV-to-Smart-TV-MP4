# FFmpeg Installation Guide

## Windows (Recommended Methods)

### Method 1: winget (Fastest)
```powershell
winget install ffmpeg
```
After installation, **restart your terminal** or IDE for PATH changes to take effect.

### Method 2: Manual Installation
1. Download from: https://www.gyan.dev/ffmpeg/builds/
   - Choose `ffmpeg-release-essentials.zip`
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Verify: open new terminal and run `ffmpeg -version`

### Method 3: Chocolatey
```powershell
choco install ffmpeg
```

## Verify Installation
```powershell
ffmpeg -version
```

You should see output like:
```
ffmpeg version 6.x.x ... configuration: ...
```

## Running the Converter
1. Place your `.wmv` files in the same folder as `wmv_to_smarttv.py`
2. Open terminal in that folder
3. Run:
```powershell
python wmv_to_smarttv.py
```

## Troubleshooting

### "ffmpeg not found" after installation
- **Restart your terminal/IDE** (important!)
- Or manually add FFmpeg to PATH:
  ```powershell
  $env:Path += ";C:\ffmpeg\bin"
  ```

### Slow conversion
The script uses `medium` preset by default. For faster (but larger) output:
- Change `-preset medium` to `-preset fast` in the script (line 18)

### NVIDIA GPU Acceleration (Optional)
If you have NVIDIA RTX 3060 or newer, replace `libx264` with `h264_nvenec` in the script for 5-10x faster encoding:
```python
ENCODING_ARGS = [
    "-c:v", "h264_nvenc",    # NVIDIA GPU instead of CPU
    # ... rest of settings
]
```
Note: Slightly lower quality at same bitrate compared to libx264.

## Smart TV Compatibility Notes
- **yuv420p**: Required for Samsung, LG, Sony, Panasonic TVs
- **H.264**: Supported by virtually all Smart TVs
- **AAC 192kbps**: Safe choice - no licensing issues, works everywhere
- **MP4 container**: Universal support across all brands
