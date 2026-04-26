#!/usr/bin/env python3
"""
WMV to MP4 Converter for Smart TVs
Modern GUI with GPU acceleration support.
Requires: pip install customtkinter
"""

import subprocess
import threading
import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, messagebox
import queue
import sys
import os

# FFmpeg path resolution
# Priority: 1) local bin/ folder (portable), 2) system PATH
SCRIPT_DIR = Path(__file__).parent.resolve()


def _find_ffmpeg() -> str:
    """Find FFmpeg executable - prefers local bin/ then system PATH."""
    # Check local bin folder first (portable deployment)
    local_ffmpeg = SCRIPT_DIR / "bin" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    # Fall back to system PATH
    return "ffmpeg"


FFMPEG_PATH = _find_ffmpeg()


class WMVConverterGUI(ctk.CTk):
    """Main GUI application for WMV to MP4 conversion."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("WMV to Smart TV Converter")
        self.geometry("750x650")
        self.resizable(False, False)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables
        self.selected_folder = ctk.StringVar(value=str(Path.cwd()))
        self.use_gpu = ctk.BooleanVar(value=True)
        self.is_converting = False
        self.stop_requested = False
        self.log_queue = queue.Queue()
        self.wmv_files = []

        # Build UI
        self._create_widgets()

        # Start log processor
        self.after(100, self._process_log_queue)

        # Check FFmpeg and scan folder
        self.after(300, self._check_ffmpeg)
        self.after(500, self._scan_folder)

    def _create_widgets(self):
        """Create all UI widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="WMV to Smart TV Converter",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=(20, 5))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Optimized for Samsung, LG, Sony, and other Smart TVs",
            font=ctk.CTkFont(size=12),
            text_color=("gray70")
        )
        subtitle.pack(pady=(0, 15))

        # Folder selection frame
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=25, pady=5)

        folder_label = ctk.CTkLabel(folder_frame, text="Folder:", font=ctk.CTkFont(size=14))
        folder_label.pack(side="left", padx=(0, 10))

        folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.selected_folder,
            width=450,
            height=35
        )
        folder_entry.pack(side="left", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            command=self._browse_folder,
            width=90,
            height=35
        )
        browse_btn.pack(side="left")

        # Options frame
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=25, pady=10)

        # GPU checkbox
        gpu_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="GPU Acceleration (NVIDIA NVENC)",
            variable=self.use_gpu,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=13)
        )
        gpu_checkbox.pack(side="left")

        self.encoder_label = ctk.CTkLabel(
            options_frame,
            text="",
            text_color="green",
            font=ctk.CTkFont(size=11)
        )
        self.encoder_label.pack(side="left", padx=(15, 0))

        # Settings info
        info_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        info_frame.pack(fill="x", padx=25, pady=8)

        settings = "H.264 (Smart TV) | yuv420p | AAC 192kbps | MP4 | CRF 22"
        info_text = ctk.CTkLabel(
            info_frame,
            text=settings,
            font=ctk.CTkFont(size=11)
        )
        info_text.pack(pady=8)

        # Progress section
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=25, pady=10)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready - Click 'Convert All' to start",
            font=ctk.CTkFont(size=13)
        )
        self.progress_label.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=18)
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.set(0)

        self.file_count_label = ctk.CTkLabel(
            progress_frame,
            text="",
            text_color=("gray60"),
            font=ctk.CTkFont(size=11)
        )
        self.file_count_label.pack(anchor="w", pady=(5, 0))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=25, pady=15)

        self.convert_btn = ctk.CTkButton(
            buttons_frame,
            text="Convert All",
            command=self._start_conversion,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        self.convert_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="Stop",
            command=self._stop_conversion,
            state="disabled",
            height=42,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            width=100
        )
        self.stop_btn.pack(side="left", padx=(0, 10))

        scan_btn = ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            command=self._scan_folder,
            height=42,
            width=100
        )
        scan_btn.pack(side="left")

        # Open folder button
        self.open_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="Open Folder",
            command=self._open_output_folder,
            height=42,
            fg_color=("gray40", "gray30"),
            width=110
        )
        self.open_folder_btn.pack(side="left", padx=(10, 0))

        # Log window
        log_label = ctk.CTkLabel(self, text="Conversion Log:", anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
        log_label.pack(anchor="w", padx=25, pady=(5, 0))

        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=25, pady=(5, 20))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=("Consolas", 11),
            state="disabled"
        )
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ctk.CTkScrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _browse_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.selected_folder.get())
        if folder:
            self.selected_folder.set(folder)
            self._scan_folder()

    def _scan_folder(self):
        """Scan selected folder for WMV files."""
        folder = Path(self.selected_folder.get())
        # Use set to avoid duplicates on case-insensitive filesystems (Windows)
        wmv_set = set(folder.glob("*.wmv")) | set(folder.glob("*.WMV"))
        self.wmv_files = sorted(wmv_set)

        count = len(self.wmv_files)
        self.file_count_label.configure(text=f"{count} WMV file(s) found")

        if count > 0:
            self._log(f"Folder: {folder}")
            self._log(f"Found {count} WMV file(s)")
            for f in self.wmv_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                self._log(f"  {f.name} ({size_mb:.1f} MB)")
        else:
            self._log(f"No WMV files found in: {folder}")

        self._update_encoder_label()

    def _update_encoder_label(self):
        """Update encoder label based on GPU setting."""
        if self.use_gpu.get():
            self.encoder_label.configure(text="Using: h264_nvenc (GPU)", text_color="green")
        else:
            self.encoder_label.configure(text="Using: libx264 (CPU)", text_color="orange")

    def _check_ffmpeg(self):
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                [FFMPEG_PATH, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split("\n")[0]
                self._log(f"[OK] FFmpeg: {version_line}")
                # Check for NVENC support
                encoders = subprocess.run(
                    [FFMPEG_PATH, "-hide_banner", "-encoders"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "h264_nvenc" in encoders.stdout:
                    self._log("[OK] NVIDIA NVENC detected - GPU acceleration available")
                    self.use_gpu.set(True)
                else:
                    self._log("[!] NVENC not found - will use CPU encoding")
                    self.use_gpu.set(False)
                self._update_encoder_label()
        except FileNotFoundError:
            self._log("[ERROR] FFmpeg not found!")
            self._log("Please either:")
            self._log("  1. Download 'ffmpeg-binaries.zip' from Releases")
            self._log("  2. Extract it to 'bin/' folder next to this script")
            self._log("  3. Or install via: winget install ffmpeg")
            messagebox.showerror(
                "FFmpeg Not Found",
                "FFmpeg is not installed.\n\n"
                "Options:\n"
                "1. Download 'ffmpeg-binaries.zip' from Releases\n"
                "2. Extract to 'bin/' folder next to this script\n"
                "3. Or install: winget install ffmpeg"
            )
            self.convert_btn.configure(state="disabled")
        except subprocess.TimeoutExpired:
            self._log("[ERROR] FFmpeg check timed out")
            self.convert_btn.configure(state="disabled")

    def _get_encoding_args(self) -> list:
        """Get encoding arguments based on GPU setting."""
        if self.use_gpu.get():
            return [
                "-c:v", "h264_nvenc",
                "-preset", "p7",
                "-rc:v", "vbr",
                "-cq:v", "22",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
            ]
        else:
            return [
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
            ]

    def _log(self, message: str):
        """Add message to log queue."""
        self.log_queue.put(message)

    def _process_log_queue(self):
        """Process messages from log queue."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", message + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._process_log_queue)

    def _update_progress(self, current: int, total: int, filename: str, status: str = ""):
        """Update progress bar."""
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            text = f"[{current}/{total}] {filename}"
            if status:
                text += f" - {status}"
            self.progress_label.configure(text=text)

    def _start_conversion(self):
        """Start conversion in a separate thread."""
        if self.is_converting:
            return

        if not self.wmv_files:
            messagebox.showwarning("No Files", "No WMV files found in selected folder.")
            return

        # Verify FFmpeg one more time
        try:
            subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            messagebox.showerror("FFmpeg Error", "FFmpeg is not available.")
            return

        self.is_converting = True
        self.stop_btn.configure(state="normal")
        self.convert_btn.configure(state="disabled")
        self.stop_requested = False

        thread = threading.Thread(target=self._conversion_worker, daemon=True)
        thread.start()

    def _stop_conversion(self):
        """Request stop of conversion."""
        self.stop_requested = True
        self._log("[INFO] Stop requested... finishing current file")

    def _conversion_worker(self):
        """Worker thread for conversion."""
        total = len(self.wmv_files)
        success_count = 0
        error_count = 0
        skipped_count = 0
        encoding_args = self._get_encoding_args()
        encoder_name = "h264_nvenc (GPU)" if self.use_gpu.get() else "libx264 (CPU)"

        self._log("=" * 50)
        self._log(f"STARTING CONVERSION")
        self._log(f"Encoder: {encoder_name}")
        self._log(f"Total files: {total}")
        self._log("=" * 50)

        for idx, wmv_file in enumerate(self.wmv_files, 1):
            if self.stop_requested:
                self._log("[INFO] Conversion stopped by user")
                break

            output_file = wmv_file.with_suffix(".mp4")
            self.after(0, self._update_progress, idx, total, wmv_file.name, "Starting...")

            # Skip if output exists
            if output_file.exists():
                self._log(f"[SKIP] {wmv_file.name} (already exists)")
                skipped_count += 1
                self.after(0, self._update_progress, idx, total, wmv_file.name, "Skipped")
                continue

            input_size_mb = wmv_file.stat().st_size / (1024 * 1024)
            self._log(f"\n[START {idx}/{total}] {wmv_file.name}")
            self._log(f"  Input: {input_size_mb:.1f} MB")

            start_time = datetime.now()
            cmd = [
                FFMPEG_PATH,
                "-i", str(wmv_file),
                "-y",
                "-hide_banner",
                "-loglevel", "error",
                *encoding_args,
                str(output_file)
            ]

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout, stderr = process.communicate(timeout=3600)

                if process.returncode == 0:
                    duration = (datetime.now() - start_time).total_seconds()
                    output_size_mb = output_file.stat().st_size / (1024 * 1024)
                    ratio = (1 - output_size_mb / input_size_mb) * 100

                    self._log(f"  Output: {output_size_mb:.1f} MB ({ratio:.1f}% reduction)")
                    self._log(f"  Time: {duration:.1f}s")
                    self._log(f"[SUCCESS {idx}/{total}]")
                    success_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, "Done")
                else:
                    error_msg = stderr.strip().split("\n")[-1] if stderr else "Unknown error"
                    self._log(f"[ERROR] {error_msg}")
                    error_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, "Error")

            except subprocess.TimeoutExpired:
                process.kill()
                self._log("[ERROR] Timeout (>1 hour) - file skipped")
                error_count += 1
            except Exception as e:
                self._log(f"[ERROR] {str(e)}")
                error_count += 1

        # Summary
        self._log("\n" + "=" * 50)
        self._log("CONVERSION COMPLETE")
        self._log(f"  Success: {success_count}")
        self._log(f"  Failed: {error_count}")
        self._log(f"  Skipped: {skipped_count}")
        self._log(f"  Total: {total}")
        self._log("=" * 50)

        if success_count > 0:
            self._log(f"\n[INFO] Output folder: {self.selected_folder.get()}")
            self._log("[INFO] You can click 'Open Folder' to view results")

        self.after(0, self._conversion_finished, success_count, error_count)

    def _conversion_finished(self, success: int, errors: int):
        """Handle conversion completion."""
        self.is_converting = False
        self.stop_btn.configure(state="disabled")
        self.convert_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Conversion complete")

        if errors > 0:
            messagebox.showwarning(
                "Conversion Finished",
                f"Completed with {errors} error(s).\nCheck the log for details."
            )
        elif success > 0:
            messagebox.showinfo(
                "Success",
                f"Successfully converted {success} file(s)!\n\nClick 'Open Folder' to view results."
            )

    def _open_output_folder(self):
        """Open the output folder in file explorer."""
        folder = self.selected_folder.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showerror("Error", "Output folder not found.")


def main():
    """Main entry point."""
    app = WMVConverterGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
