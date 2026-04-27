#!/usr/bin/env python3
"""
WMV to MP4 Converter for Smart TVs.
Modern GUI with GPU acceleration and multilingual support (RU/EN).
Requires: pip install customtkinter
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk


SCRIPT_DIR = Path(__file__).resolve().parent


def _runtime_root() -> Path:
    """Return the base directory for source and bundled executions."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return SCRIPT_DIR


RUNTIME_ROOT = _runtime_root()


def _find_ffmpeg() -> str:
    """Find FFmpeg executable for source, portable, and PATH usage."""
    candidates = [
        RUNTIME_ROOT / "_internal" / "bin" / "ffmpeg.exe",
        RUNTIME_ROOT / "bin" / "ffmpeg.exe",
        SCRIPT_DIR / "bin" / "ffmpeg.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "ffmpeg"


FFMPEG_PATH = _find_ffmpeg()

LANGUAGE_LABELS = {
    "en": "English",
    "ru": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439",
}

LANGUAGES = {
    "en": {
        "lang_label": "Language:",
        "title": "WMV to Smart TV Converter",
        "subtitle": "Optimized for Samsung, LG, Sony, and other Smart TVs",
        "folder_label": "Folder:",
        "browse_btn": "Browse",
        "gpu_checkbox": "GPU Acceleration (NVIDIA NVENC)",
        "encoder_gpu": "Using: h264_nvenc (GPU)",
        "encoder_cpu": "Using: libx264 (CPU)",
        "settings_info": "H.264 | yuv420p | AAC 192kbps | MP4 | CRF 22",
        "progress_ready": "Ready - Click 'Convert All' to start",
        "file_count": "{count} WMV file(s) found",
        "convert_btn": "Convert All",
        "stop_btn": "Stop",
        "refresh_btn": "Refresh",
        "open_folder_btn": "Open Folder",
        "log_title": "Conversion Log:",
        "ffmpeg_ok": "[OK] FFmpeg: {version}",
        "ffmpeg_nvenc_ok": "[OK] NVIDIA NVENC detected - GPU acceleration available",
        "ffmpeg_nvenc_fail": "[!] NVENC not found - will use CPU encoding",
        "ffmpeg_not_found": "[ERROR] FFmpeg not found!",
        "ffmpeg_install_hint": "  1. Download 'ffmpeg-binaries.zip' from Releases",
        "ffmpeg_install_hint2": "  2. Extract to 'bin/' or '_internal/bin/' next to the executable",
        "ffmpeg_install_hint3": "  3. Or install via: winget install ffmpeg",
        "ffmpeg_timeout": "[ERROR] FFmpeg check timed out",
        "scan_folder": "Folder: {folder}",
        "scan_found": "Found {count} WMV file(s)",
        "scan_no_files": "No WMV files found in: {folder}",
        "file_size": "  {name} ({size:.1f} MB)",
        "conv_separator": "=" * 50,
        "conv_start": "STARTING CONVERSION",
        "conv_encoder": "Encoder: {encoder}",
        "conv_total": "Total files: {total}",
        "conv_stopped": "[INFO] Conversion stopped by user",
        "conv_skip_exists": "[SKIP] {name} (already exists)",
        "conv_input": "  Input: {size:.1f} MB",
        "conv_start_file": "[START {idx}/{total}] {name}",
        "conv_output": "  Output: {size:.1f} MB ({ratio:.1f}% reduction)",
        "conv_time": "  Time: {time:.1f}s",
        "conv_success": "[SUCCESS {idx}/{total}]",
        "conv_error": "[ERROR] {message}",
        "conv_timeout": "[ERROR] Timeout (>1 hour) - file skipped",
        "conv_complete": "CONVERSION COMPLETE",
        "conv_success_count": "  Success: {count}",
        "conv_error_count": "  Failed: {count}",
        "conv_skip_count": "  Skipped: {count}",
        "conv_total_count": "  Total: {total}",
        "conv_output_folder": "[INFO] Output folder: {folder}",
        "conv_view_results": "[INFO] Click 'Open Folder' to view results",
        "status_starting": "Starting...",
        "status_skipped": "Skipped",
        "status_done": "Done",
        "status_error": "Error",
        "msg_no_files": "No Files",
        "msg_no_files_text": "No WMV files found in selected folder.",
        "msg_ffmpeg_error": "FFmpeg Error",
        "msg_ffmpeg_unavailable": "FFmpeg is not available.",
        "msg_conv_complete": "Conversion Finished",
        "msg_conv_errors": "Completed with {errors} error(s).\nCheck the log for details.",
        "msg_conv_success": "Successfully converted {count} file(s)!\n\nClick 'Open Folder' to view results.",
        "msg_folder_error": "Error",
        "msg_folder_not_found": "Output folder not found.",
        "msg_ffmpeg_error_title": "FFmpeg Not Found",
        "msg_ffmpeg_error_text": "FFmpeg is not installed.\n\nOptions:\n1. Download 'ffmpeg-binaries.zip' from Releases\n2. Extract to 'bin/' next to the script or '_internal/bin/' for the portable build\n3. Or install: winget install ffmpeg",
        "stop_requested": "[INFO] Stop requested... finishing current file",
    },
    "ru": {
        "lang_label": "\u042f\u0437\u044b\u043a:",
        "title": "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0435\u0440 WMV \u0434\u043b\u044f Smart TV",
        "subtitle": "\u041e\u043f\u0442\u0438\u043c\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043e \u0434\u043b\u044f Samsung, LG, Sony \u0438 \u0434\u0440\u0443\u0433\u0438\u0445 Smart TV",
        "folder_label": "\u041f\u0430\u043f\u043a\u0430:",
        "browse_btn": "\u041e\u0431\u0437\u043e\u0440",
        "gpu_checkbox": "\u0423\u0441\u043a\u043e\u0440\u0435\u043d\u0438\u0435 GPU (NVIDIA NVENC)",
        "encoder_gpu": "\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f: h264_nvenc (GPU)",
        "encoder_cpu": "\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f: libx264 (CPU)",
        "settings_info": "H.264 | yuv420p | AAC 192kbps | MP4 | CRF 22",
        "progress_ready": "\u0413\u043e\u0442\u043e\u0432\u043e - \u043d\u0430\u0436\u043c\u0438\u0442\u0435 '\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0432\u0441\u0451'",
        "file_count": "\u041d\u0430\u0439\u0434\u0435\u043d\u043e \u0444\u0430\u0439\u043b\u043e\u0432: {count}",
        "convert_btn": "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0432\u0441\u0451",
        "stop_btn": "\u0421\u0442\u043e\u043f",
        "refresh_btn": "\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c",
        "open_folder_btn": "\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443",
        "log_title": "\u0416\u0443\u0440\u043d\u0430\u043b \u043a\u043e\u043d\u0432\u0435\u0440\u0442\u0430\u0446\u0438\u0438:",
        "ffmpeg_ok": "[OK] FFmpeg: {version}",
        "ffmpeg_nvenc_ok": "[OK] NVIDIA NVENC \u043d\u0430\u0439\u0434\u0435\u043d - \u0443\u0441\u043a\u043e\u0440\u0435\u043d\u0438\u0435 GPU \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e",
        "ffmpeg_nvenc_fail": "[!] NVENC \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d - \u0431\u0443\u0434\u0435\u0442 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f CPU",
        "ffmpeg_not_found": "[ERROR] FFmpeg \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d!",
        "ffmpeg_install_hint": "  1. \u0421\u043a\u0430\u0447\u0430\u0439\u0442\u0435 'ffmpeg-binaries.zip' \u0438\u0437 Releases",
        "ffmpeg_install_hint2": "  2. \u0420\u0430\u0441\u043f\u0430\u043a\u0443\u0439\u0442\u0435 \u0432 'bin/' \u0438\u043b\u0438 '_internal/bin/'",
        "ffmpeg_install_hint3": "  3. \u0418\u043b\u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0435: winget install ffmpeg",
        "ffmpeg_timeout": "[ERROR] \u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 FFmpeg \u043f\u0440\u0435\u0432\u044b\u0441\u0438\u043b\u0430 \u0432\u0440\u0435\u043c\u044f",
        "scan_folder": "\u041f\u0430\u043f\u043a\u0430: {folder}",
        "scan_found": "\u041d\u0430\u0439\u0434\u0435\u043d\u043e WMV \u0444\u0430\u0439\u043b\u043e\u0432: {count}",
        "scan_no_files": "WMV \u0444\u0430\u0439\u043b\u044b \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b \u0432: {folder}",
        "file_size": "  {name} ({size:.1f} \u041c\u0411)",
        "conv_separator": "=" * 50,
        "conv_start": "\u041d\u0410\u0427\u0410\u041b\u041e \u041a\u041e\u041d\u0412\u0415\u0420\u0422\u0410\u0426\u0418\u0418",
        "conv_encoder": "\u041a\u043e\u0434\u0435\u043a: {encoder}",
        "conv_total": "\u0412\u0441\u0435\u0433\u043e \u0444\u0430\u0439\u043b\u043e\u0432: {total}",
        "conv_stopped": "[INFO] \u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0430\u0446\u0438\u044f \u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c",
        "conv_skip_exists": "[\u041f\u0420\u041e\u041f\u0423\u0421\u041a] {name} (\u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442)",
        "conv_input": "  \u0412\u0445\u043e\u0434\u043d\u043e\u0439: {size:.1f} \u041c\u0411",
        "conv_start_file": "[\u0421\u0422\u0410\u0420\u0422 {idx}/{total}] {name}",
        "conv_output": "  \u0412\u044b\u0445\u043e\u0434\u043d\u043e\u0439: {size:.1f} \u041c\u0411 ({ratio:.1f}% \u0441\u0436\u0430\u0442\u0438\u0435)",
        "conv_time": "  \u0412\u0440\u0435\u043c\u044f: {time:.1f}\u0441",
        "conv_success": "[\u0423\u0421\u041f\u0415\u0425 {idx}/{total}]",
        "conv_error": "[\u041e\u0428\u0418\u0411\u041a\u0410] {message}",
        "conv_timeout": "[\u041e\u0428\u0418\u0411\u041a\u0410] \u0422\u0430\u0439\u043c\u0430\u0443\u0442 (>1 \u0447\u0430\u0441) - \u0444\u0430\u0439\u043b \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d",
        "conv_complete": "\u041a\u041e\u041d\u0412\u0415\u0420\u0422\u0410\u0426\u0418\u042f \u0417\u0410\u0412\u0415\u0420\u0428\u0415\u041d\u0410",
        "conv_success_count": "  \u0423\u0441\u043f\u0435\u0448\u043d\u043e: {count}",
        "conv_error_count": "  \u041e\u0448\u0438\u0431\u043e\u043a: {count}",
        "conv_skip_count": "  \u041f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u043e: {count}",
        "conv_total_count": "  \u0412\u0441\u0435\u0433\u043e: {total}",
        "conv_output_folder": "[INFO] \u041f\u0430\u043f\u043a\u0430 \u0432\u044b\u0432\u043e\u0434\u0430: {folder}",
        "conv_view_results": "[INFO] \u041d\u0430\u0436\u043c\u0438\u0442\u0435 '\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443' \u0434\u043b\u044f \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0430",
        "status_starting": "\u0417\u0430\u043f\u0443\u0441\u043a...",
        "status_skipped": "\u041f\u0440\u043e\u043f\u0443\u0449\u0435\u043d",
        "status_done": "\u0413\u043e\u0442\u043e\u0432\u043e",
        "status_error": "\u041e\u0448\u0438\u0431\u043a\u0430",
        "msg_no_files": "\u041d\u0435\u0442 \u0444\u0430\u0439\u043b\u043e\u0432",
        "msg_no_files_text": "WMV \u0444\u0430\u0439\u043b\u044b \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b \u0432 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0439 \u043f\u0430\u043f\u043a\u0435.",
        "msg_ffmpeg_error": "\u041e\u0448\u0438\u0431\u043a\u0430 FFmpeg",
        "msg_ffmpeg_unavailable": "FFmpeg \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u0435\u043d.",
        "msg_conv_complete": "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0430\u0446\u0438\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430",
        "msg_conv_errors": "\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e \u0441 {errors} \u043e\u0448\u0438\u0431\u043a\u043e\u0439(\u0430\u043c\u0438).\n\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0436\u0443\u0440\u043d\u0430\u043b.",
        "msg_conv_success": "\u0423\u0441\u043f\u0435\u0448\u043d\u043e \u043a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043e {count} \u0444\u0430\u0439\u043b(\u043e\u0432)!\n\n\u041d\u0430\u0436\u043c\u0438\u0442\u0435 '\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443' \u0434\u043b\u044f \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0430.",
        "msg_folder_error": "\u041e\u0448\u0438\u0431\u043a\u0430",
        "msg_folder_not_found": "\u0412\u044b\u0445\u043e\u0434\u043d\u0430\u044f \u043f\u0430\u043f\u043a\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430.",
        "msg_ffmpeg_error_title": "FFmpeg \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
        "msg_ffmpeg_error_text": "FFmpeg \u043d\u0435 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d.\n\n\u0412\u0430\u0440\u0438\u0430\u043d\u0442\u044b:\n1. \u0421\u043a\u0430\u0447\u0430\u0439\u0442\u0435 'ffmpeg-binaries.zip' \u0438\u0437 Releases\n2. \u0420\u0430\u0441\u043f\u0430\u043a\u0443\u0439\u0442\u0435 \u0432 'bin/' \u0440\u044f\u0434\u043e\u043c \u0441\u043e \u0441\u043a\u0440\u0438\u043f\u0442\u043e\u043c \u0438\u043b\u0438 \u0432 '_internal/bin/' \u0434\u043b\u044f portable-\u0441\u0431\u043e\u0440\u043a\u0438\n3. \u0418\u043b\u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0435: winget install ffmpeg",
        "stop_requested": "[INFO] \u0417\u0430\u043f\u0440\u043e\u0441 \u043d\u0430 \u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0443... \u0437\u0430\u0432\u0435\u0440\u0448\u0430\u0435\u043c \u0442\u0435\u043a\u0443\u0449\u0438\u0439 \u0444\u0430\u0439\u043b",
    },
}


class WMVConverterGUI(ctk.CTk):
    """Main GUI application for WMV to MP4 conversion."""

    def __init__(self) -> None:
        super().__init__()
        self.lang = "en"
        self.L = LANGUAGES[self.lang]

        self.title(self.L["title"])
        self.geometry("800x700")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.selected_folder = ctk.StringVar(value=str(Path.cwd()))
        self.use_gpu = ctk.BooleanVar(value=True)
        self.is_converting = False
        self.stop_requested = False
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.wmv_files: list[Path] = []
        self._widgets: dict[str, object] = {}

        self._create_widgets()
        self.after(100, self._process_log_queue)
        self.after(300, self._check_ffmpeg)
        self.after(500, self._scan_folder)

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=25, pady=(10, 0))

        self._widgets["lang_label"] = ctk.CTkLabel(lang_frame, text=self.L["lang_label"])
        self._widgets["lang_label"].pack(side="right", padx=(0, 5))

        self._widgets["lang_menu"] = ctk.CTkOptionMenu(
            lang_frame,
            values=list(LANGUAGE_LABELS.values()),
            command=self._change_language,
            width=100,
        )
        self._widgets["lang_menu"].pack(side="right")
        self._widgets["lang_menu"].set(LANGUAGE_LABELS[self.lang])

        self._widgets["title"] = ctk.CTkLabel(
            self,
            text=self.L["title"],
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self._widgets["title"].pack(pady=(15, 5))

        self._widgets["subtitle"] = ctk.CTkLabel(
            self,
            text=self.L["subtitle"],
            font=ctk.CTkFont(size=12),
            text_color="gray70",
        )
        self._widgets["subtitle"].pack(pady=(0, 15))

        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=25, pady=5)

        self._widgets["folder_label"] = ctk.CTkLabel(
            folder_frame,
            text=self.L["folder_label"],
            font=ctk.CTkFont(size=14),
        )
        self._widgets["folder_label"].pack(side="left", padx=(0, 10))

        folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.selected_folder,
            width=450,
            height=35,
        )
        folder_entry.pack(side="left", padx=(0, 10))

        self._widgets["browse_btn"] = ctk.CTkButton(
            folder_frame,
            text=self.L["browse_btn"],
            command=self._browse_folder,
            width=90,
            height=35,
        )
        self._widgets["browse_btn"].pack(side="left")

        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=25, pady=10)

        self._widgets["gpu_checkbox"] = ctk.CTkCheckBox(
            options_frame,
            text=self.L["gpu_checkbox"],
            variable=self.use_gpu,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=13),
            command=self._update_encoder_label,
        )
        self._widgets["gpu_checkbox"].pack(side="left")

        self._widgets["encoder_label"] = ctk.CTkLabel(
            options_frame,
            text=self.L["encoder_gpu"],
            text_color="green",
            font=ctk.CTkFont(size=11),
        )
        self._widgets["encoder_label"].pack(side="left", padx=(15, 0))

        info_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        info_frame.pack(fill="x", padx=25, pady=8)

        self._widgets["settings_info"] = ctk.CTkLabel(
            info_frame,
            text=self.L["settings_info"],
            font=ctk.CTkFont(size=11),
        )
        self._widgets["settings_info"].pack(pady=8)

        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=25, pady=10)

        self._widgets["progress_label"] = ctk.CTkLabel(
            progress_frame,
            text=self.L["progress_ready"],
            font=ctk.CTkFont(size=13),
        )
        self._widgets["progress_label"].pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=18)
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.set(0)

        self._widgets["file_count_label"] = ctk.CTkLabel(
            progress_frame,
            text="",
            text_color="gray60",
            font=ctk.CTkFont(size=11),
        )
        self._widgets["file_count_label"].pack(anchor="w", pady=(5, 0))

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=25, pady=15)

        self._widgets["convert_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["convert_btn"],
            command=self._start_conversion,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green"),
        )
        self._widgets["convert_btn"].pack(side="left", padx=(0, 10))

        self._widgets["stop_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["stop_btn"],
            command=self._stop_conversion,
            state="disabled",
            height=42,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            width=100,
        )
        self._widgets["stop_btn"].pack(side="left", padx=(0, 10))

        self._widgets["refresh_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["refresh_btn"],
            command=self._scan_folder,
            height=42,
            width=100,
        )
        self._widgets["refresh_btn"].pack(side="left")

        self._widgets["open_folder_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["open_folder_btn"],
            command=self._open_output_folder,
            height=42,
            fg_color=("gray40", "gray30"),
            width=120,
        )
        self._widgets["open_folder_btn"].pack(side="left", padx=(10, 0))

        self._widgets["log_label"] = ctk.CTkLabel(
            self,
            text=self.L["log_title"],
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._widgets["log_label"].pack(anchor="w", padx=25, pady=(5, 0))

        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=25, pady=(5, 20))

        self.log_text = ctk.CTkTextbox(log_frame, font=("Consolas", 11), state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ctk.CTkScrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _set_language(self, lang: str) -> None:
        """Apply the selected language to the UI."""
        self.lang = lang
        self.L = LANGUAGES[self.lang]
        self.title(self.L["title"])
        self._widgets["lang_label"].configure(text=self.L["lang_label"])
        self._widgets["lang_menu"].set(LANGUAGE_LABELS[self.lang])
        self._widgets["title"].configure(text=self.L["title"])
        self._widgets["subtitle"].configure(text=self.L["subtitle"])
        self._widgets["folder_label"].configure(text=self.L["folder_label"])
        self._widgets["browse_btn"].configure(text=self.L["browse_btn"])
        self._widgets["gpu_checkbox"].configure(text=self.L["gpu_checkbox"])
        self._widgets["settings_info"].configure(text=self.L["settings_info"])
        self._widgets["progress_label"].configure(text=self.L["progress_ready"])
        self._widgets["convert_btn"].configure(text=self.L["convert_btn"])
        self._widgets["stop_btn"].configure(text=self.L["stop_btn"])
        self._widgets["refresh_btn"].configure(text=self.L["refresh_btn"])
        self._widgets["open_folder_btn"].configure(text=self.L["open_folder_btn"])
        self._widgets["log_label"].configure(text=self.L["log_title"])
        self._update_encoder_label()
        self._update_file_count()

    def _change_language(self, new_lang: str) -> None:
        """Change UI language from the option menu value."""
        lang = "ru" if new_lang == LANGUAGE_LABELS["ru"] else "en"
        self._set_language(lang)

    def _update_encoder_label(self) -> None:
        """Update encoder label based on GPU setting."""
        if self.use_gpu.get():
            self._widgets["encoder_label"].configure(text=self.L["encoder_gpu"], text_color="green")
        else:
            self._widgets["encoder_label"].configure(text=self.L["encoder_cpu"], text_color="orange")

    def _update_file_count(self) -> None:
        """Update file count label."""
        count = len(self.wmv_files)
        self._widgets["file_count_label"].configure(text=self.L["file_count"].format(count=count))

    def _browse_folder(self) -> None:
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.selected_folder.get())
        if folder:
            self.selected_folder.set(folder)
            self._scan_folder()

    def _scan_folder(self) -> None:
        """Scan selected folder for WMV files."""
        folder = Path(self.selected_folder.get())
        if not folder.exists():
            self.wmv_files = []
            self._update_file_count()
            self._log(self.L["scan_no_files"].format(folder=folder))
            self._update_encoder_label()
            return

        wmv_set = set(folder.glob("*.wmv")) | set(folder.glob("*.WMV"))
        self.wmv_files = sorted(wmv_set)
        self._update_file_count()

        if self.wmv_files:
            self._log(self.L["scan_folder"].format(folder=folder))
            self._log(self.L["scan_found"].format(count=len(self.wmv_files)))
            for media_file in self.wmv_files:
                size_mb = media_file.stat().st_size / (1024 * 1024)
                self._log(self.L["file_size"].format(name=media_file.name, size=size_mb))
        else:
            self._log(self.L["scan_no_files"].format(folder=folder))

        self._update_encoder_label()

    def _check_ffmpeg(self) -> None:
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                [FFMPEG_PATH, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise FileNotFoundError

            version_line = result.stdout.splitlines()[0]
            self._log(self.L["ffmpeg_ok"].format(version=version_line))

            encoders = subprocess.run(
                [FFMPEG_PATH, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "h264_nvenc" in encoders.stdout:
                self._log(self.L["ffmpeg_nvenc_ok"])
                self.use_gpu.set(True)
            else:
                self._log(self.L["ffmpeg_nvenc_fail"])
                self.use_gpu.set(False)
            self._update_encoder_label()
        except FileNotFoundError:
            self._log(self.L["ffmpeg_not_found"])
            self._log(self.L["ffmpeg_install_hint"])
            self._log(self.L["ffmpeg_install_hint2"])
            self._log(self.L["ffmpeg_install_hint3"])
            messagebox.showerror(self.L["msg_ffmpeg_error_title"], self.L["msg_ffmpeg_error_text"])
            self._widgets["convert_btn"].configure(state="disabled")
        except subprocess.TimeoutExpired:
            self._log(self.L["ffmpeg_timeout"])
            self._widgets["convert_btn"].configure(state="disabled")

    def _get_encoding_args(self) -> list[str]:
        """Get encoding arguments based on GPU setting."""
        if self.use_gpu.get():
            return [
                "-c:v",
                "h264_nvenc",
                "-preset",
                "p7",
                "-rc:v",
                "vbr",
                "-cq:v",
                "22",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
            ]
        return [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
        ]

    def _log(self, message: str) -> None:
        """Add message to log queue."""
        self.log_queue.put(message)

    def _process_log_queue(self) -> None:
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

    def _update_progress(self, current: int, total: int, filename: str, status: str) -> None:
        """Update progress bar."""
        if total > 0:
            self.progress_bar.set(current / total)
            status_text = f"[{current}/{total}] {filename}"
            if status:
                status_text += f" - {status}"
            self._widgets["progress_label"].configure(text=status_text)

    def _start_conversion(self) -> None:
        """Start conversion in a background thread."""
        if self.is_converting:
            return

        if not self.wmv_files:
            messagebox.showwarning(self.L["msg_no_files"], self.L["msg_no_files_text"])
            return

        try:
            subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            messagebox.showerror(self.L["msg_ffmpeg_error"], self.L["msg_ffmpeg_unavailable"])
            return

        self.is_converting = True
        self.stop_requested = False
        self._widgets["stop_btn"].configure(state="normal")
        self._widgets["convert_btn"].configure(state="disabled")

        thread = threading.Thread(target=self._conversion_worker, daemon=True)
        thread.start()

    def _stop_conversion(self) -> None:
        """Request stop of conversion."""
        self.stop_requested = True
        self._log(self.L["stop_requested"])

    def _conversion_worker(self) -> None:
        """Worker thread for conversion."""
        total = len(self.wmv_files)
        success_count = 0
        error_count = 0
        skipped_count = 0
        encoding_args = self._get_encoding_args()
        encoder_name = "h264_nvenc (GPU)" if self.use_gpu.get() else "libx264 (CPU)"

        self._log(self.L["conv_separator"])
        self._log(self.L["conv_start"])
        self._log(self.L["conv_encoder"].format(encoder=encoder_name))
        self._log(self.L["conv_total"].format(total=total))
        self._log(self.L["conv_separator"])

        for idx, wmv_file in enumerate(self.wmv_files, start=1):
            if self.stop_requested:
                self._log(self.L["conv_stopped"])
                break

            output_file = wmv_file.with_suffix(".mp4")
            self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_starting"])

            if output_file.exists():
                self._log(self.L["conv_skip_exists"].format(name=wmv_file.name))
                skipped_count += 1
                self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_skipped"])
                continue

            input_size_mb = wmv_file.stat().st_size / (1024 * 1024)
            self._log("")
            self._log(self.L["conv_start_file"].format(idx=idx, total=total, name=wmv_file.name))
            self._log(self.L["conv_input"].format(size=input_size_mb))

            start_time = datetime.now()
            cmd = [
                FFMPEG_PATH,
                "-i",
                str(wmv_file),
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                *encoding_args,
                str(output_file),
            ]

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                _, stderr = process.communicate(timeout=3600)

                if process.returncode == 0:
                    duration = (datetime.now() - start_time).total_seconds()
                    output_size_mb = output_file.stat().st_size / (1024 * 1024)
                    ratio = (1 - output_size_mb / input_size_mb) * 100 if input_size_mb else 0

                    self._log(self.L["conv_output"].format(size=output_size_mb, ratio=ratio))
                    self._log(self.L["conv_time"].format(time=duration))
                    self._log(self.L["conv_success"].format(idx=idx, total=total))
                    success_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_done"])
                else:
                    error_msg = stderr.strip().splitlines()[-1] if stderr else "Unknown error"
                    self._log(self.L["conv_error"].format(message=error_msg))
                    error_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_error"])
            except subprocess.TimeoutExpired:
                process.kill()
                self._log(self.L["conv_timeout"])
                error_count += 1
            except Exception as exc:
                self._log(self.L["conv_error"].format(message=str(exc)))
                error_count += 1

        self._log("")
        self._log(self.L["conv_separator"])
        self._log(self.L["conv_complete"])
        self._log(self.L["conv_success_count"].format(count=success_count))
        self._log(self.L["conv_error_count"].format(count=error_count))
        self._log(self.L["conv_skip_count"].format(count=skipped_count))
        self._log(self.L["conv_total_count"].format(total=total))
        self._log(self.L["conv_separator"])

        if success_count > 0:
            self._log("")
            self._log(self.L["conv_output_folder"].format(folder=self.selected_folder.get()))
            self._log(self.L["conv_view_results"])

        self.after(0, self._conversion_finished, success_count, error_count)

    def _conversion_finished(self, success: int, errors: int) -> None:
        """Handle conversion completion."""
        self.is_converting = False
        self._widgets["stop_btn"].configure(state="disabled")
        self._widgets["convert_btn"].configure(state="normal")
        self.progress_bar.set(0)
        self._widgets["progress_label"].configure(text=self.L["progress_ready"])

        if errors > 0:
            messagebox.showwarning(
                self.L["msg_conv_complete"],
                self.L["msg_conv_errors"].format(errors=errors),
            )
        elif success > 0:
            messagebox.showinfo(
                self.L["msg_conv_complete"],
                self.L["msg_conv_success"].format(count=success),
            )

    def _open_output_folder(self) -> None:
        """Open the output folder in file explorer."""
        folder = self.selected_folder.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showerror(self.L["msg_folder_error"], self.L["msg_folder_not_found"])


def main() -> None:
    """Main entry point."""
    app = WMVConverterGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
