# FFmpeg Installation Guide

## Method 0: Portable (Recommended)

**This is the easiest way to use the converter.**

1. Download `ffmpeg-binaries.zip` from the [Releases page](https://github.com/drycool/Convert-WMV-to-Smart-TV-MP4/releases)
2. Extract the archive
3. You will get a `bin/` folder containing:
   - `ffmpeg.exe` - video encoder
   - `ffplay.exe` - media player
   - `ffprobe.exe` - media analyzer
4. Place the `bin/` folder in the same directory as `wmv_to_smarttv.py`
5. Run the converter - it will automatically find FFmpeg

```
Your folder should look like:
wmv-to-smarttv/
├── wmv_to_smarttv.py
├── bin/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
└── (your .wmv files here)
```

---

## Method 1: winget (System Installation)

If you prefer a system-wide installation:

```powershell
winget install ffmpeg
```

After installation, **restart your terminal** or IDE for PATH changes to take effect.

---

## Method 2: Manual Installation

1. Download from: https://www.gyan.dev/ffmpeg/builds/
   - Choose `ffmpeg-release-essentials.zip`
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Verify: open new terminal and run `ffmpeg -version`

---

## Method 3: Chocolatey

```powershell
choco install ffmpeg
```

---

## Verify Installation

```powershell
ffmpeg -version
```

You should see output like:
```
ffmpeg version 8.x.x ... configuration: ...
```

---

## FFmpeg Detection Logic

The converter looks for FFmpeg in this order:

1. **Local `bin/` folder** (portable mode) - `bin/ffmpeg.exe` next to the script
2. **System PATH** - if FFmpeg is installed system-wide

---

## Troubleshooting

### "FFmpeg not found"
- Make sure `bin/` folder is **next to** `wmv_to_smarttv.py`, not inside it
- **Restart your terminal/IDE** after installing FFmpeg
- Or manually add FFmpeg to PATH:
  ```powershell
  $env:Path += ";C:\ffmpeg\bin"
  ```

### GPU encoding issues
- Verify NVIDIA drivers are installed
- Try CPU mode as fallback (uncheck "GPU Acceleration")

---

## Smart TV Compatibility Notes

| Setting | Value | Why It Matters |
|---------|-------|----------------|
| yuv420p | Pixel format | Critical! TVs cannot play 4:4:4 or 10-bit color |
| H.264 | Video codec | Required by virtually all Smart TV chipsets |
| AAC 192kbps | Audio | Universal support, no licensing issues |
| MP4 | Container | Most compatible container format |
