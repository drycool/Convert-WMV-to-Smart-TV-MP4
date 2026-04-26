#!/usr/bin/env python3
"""
WMV to MP4 Converter for Smart TVs
Modern GUI with GPU acceleration and multilingual support (RU/EN).
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
    local_ffmpeg = SCRIPT_DIR / "bin" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    return "ffmpeg"


FFMPEG_PATH = _find_ffmpeg()


# Multilingual support
LANGUAGES = {
    "en": {
        # Window
        "title": "WMV to Smart TV Converter",
        "subtitle": "Optimized for Samsung, LG, Sony, and other Smart TVs",

        # Folder section
        "folder_label": "Folder:",
        "browse_btn": "Browse",

        # Options
        "gpu_checkbox": "GPU Acceleration (NVIDIA NVENC)",
        "encoder_gpu": "Using: h264_nvenc (GPU)",
        "encoder_cpu": "Using: libx264 (CPU)",
        "settings_info": "H.264 | yuv420p | AAC 192kbps | MP4 | CRF 22",

        # Progress
        "progress_ready": "Ready - Click 'Convert All' to start",
        "file_count": "{count} WMV file(s) found",

        # Buttons
        "convert_btn": "Convert All",
        "stop_btn": "Stop",
        "refresh_btn": "Refresh",
        "open_folder_btn": "Open Folder",

        # Log
        "log_title": "Conversion Log:",

        # FFmpeg check
        "ffmpeg_ok": "[OK] FFmpeg: {version}",
        "ffmpeg_nvenc_ok": "[OK] NVIDIA NVENC detected - GPU acceleration available",
        "ffmpeg_nvenc_fail": "[!] NVENC not found - will use CPU encoding",
        "ffmpeg_not_found": "[ERROR] FFmpeg not found!",
        "ffmpeg_install_hint": "  1. Download 'ffmpeg-binaries.zip' from Releases",
        "ffmpeg_install_hint2": "  2. Extract to 'bin/' folder next to this script",
        "ffmpeg_install_hint3": "  3. Or install via: winget install ffmpeg",
        "ffmpeg_timeout": "[ERROR] FFmpeg check timed out",

        # Scan results
        "scan_folder": "Folder: {folder}",
        "scan_found": "Found {count} WMV file(s)",
        "scan_no_files": "No WMV files found in: {folder}",
        "file_size": "  {name} ({size:.1f} MB)",

        # Conversion
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

        # Progress status
        "status_starting": "Starting...",
        "status_skipped": "Skipped",
        "status_done": "Done",
        "status_error": "Error",

        # Messages
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
        "msg_ffmpeg_error_text": "FFmpeg is not installed.\n\nOptions:\n1. Download 'ffmpeg-binaries.zip' from Releases\n2. Extract to 'bin/' folder next to this script\n3. Or install: winget install ffmpeg",
    },
    "ru": {
        # Window
        "title": "Конвертер WMV для Smart TV",
        "subtitle": "Оптимизировано для Samsung, LG, Sony и других Smart TV",

        # Folder section
        "folder_label": "Папка:",
        "browse_btn": "Обзор",

        # Options
        "gpu_checkbox": "Ускорение GPU (NVIDIA NVENC)",
        "encoder_gpu": "Используется: h264_nvenc (GPU)",
        "encoder_cpu": "Используется: libx264 (CPU)",
        "settings_info": "H.264 | yuv420p | AAC 192kbps | MP4 | CRF 22",

        # Progress
        "progress_ready": "Готово - нажмите 'Конвертировать всё'",
        "file_count": "Найдено файлов: {count}",

        # Buttons
        "convert_btn": "Конвертировать всё",
        "stop_btn": "Стоп",
        "refresh_btn": "Обновить",
        "open_folder_btn": "Открыть папку",

        # Log
        "log_title": "Журнал конвертации:",

        # FFmpeg check
        "ffmpeg_ok": "[OK] FFmpeg: {version}",
        "ffmpeg_nvenc_ok": "[OK] NVIDIA NVENC найден - ускорение GPU доступно",
        "ffmpeg_nvenc_fail": "[!] NVENC не найден - будет использоваться CPU",
        "ffmpeg_not_found": "[ERROR] FFmpeg не найден!",
        "ffmpeg_install_hint": "  1. Скачайте 'ffmpeg-binaries.zip' из Releases",
        "ffmpeg_install_hint2": "  2. Распакуйте в папку 'bin/' рядом со скриптом",
        "ffmpeg_install_hint3": "  3. Или установите: winget install ffmpeg",
        "ffmpeg_timeout": "[ERROR] Проверка FFmpeg превысила время",

        # Scan results
        "scan_folder": "Папка: {folder}",
        "scan_found": "Найдено WMV файлов: {count}",
        "scan_no_files": "WMV файлы не найдены в: {folder}",
        "file_size": "  {name} ({size:.1f} МБ)",

        # Conversion
        "conv_separator": "=" * 50,
        "conv_start": "НАЧАЛО КОНВЕРТАЦИИ",
        "conv_encoder": "Кодек: {encoder}",
        "conv_total": "Всего файлов: {total}",
        "conv_stopped": "[INFO] Конвертация остановлена пользователем",
        "conv_skip_exists": "[ПРОПУСК] {name} (уже существует)",
        "conv_input": "  Входной: {size:.1f} МБ",
        "conv_start_file": "[СТАРТ {idx}/{total}] {name}",
        "conv_output": "  Выходной: {size:.1f} МБ ({ratio:.1f}% сжатие)",
        "conv_time": "  Время: {time:.1f}с",
        "conv_success": "[УСПЕХ {idx}/{total}]",
        "conv_error": "[ОШИБКА] {message}",
        "conv_timeout": "[ОШИБКА] Таймаут (>1 час) - файл пропущен",
        "conv_complete": "КОНВЕРТАЦИЯ ЗАВЕРШЕНА",
        "conv_success_count": "  Успешно: {count}",
        "conv_error_count": "  Ошибок: {count}",
        "conv_skip_count": "  Пропущено: {count}",
        "conv_total_count": "  Всего: {total}",
        "conv_output_folder": "[INFO] Папка вывода: {folder}",
        "conv_view_results": "[INFO] Нажмите 'Открыть папку' для просмотра",

        # Progress status
        "status_starting": "Запуск...",
        "status_skipped": "Пропущен",
        "status_done": "Готово",
        "status_error": "Ошибка",

        # Messages
        "msg_no_files": "Нет файлов",
        "msg_no_files_text": "WMV файлы не найдены в выбранной папке.",
        "msg_ffmpeg_error": "Ошибка FFmpeg",
        "msg_ffmpeg_unavailable": "FFmpeg недоступен.",
        "msg_conv_complete": "Конвертация завершена",
        "msg_conv_errors": "Завершено с {errors} ошибкой(ами).\nПроверьте журнал.",
        "msg_conv_success": "Успешно конвертировано {count} файл(ов)!\n\nНажмите 'Открыть папку' для просмотра.",
        "msg_folder_error": "Ошибка",
        "msg_folder_not_found": "Выходная папка не найдена.",
        "msg_ffmpeg_error_title": "FFmpeg не найден",
        "msg_ffmpeg_error_text": "FFmpeg не установлен.\n\nВарианты:\n1. Скачайте 'ffmpeg-binaries.zip' из Releases\n2. Распакуйте в папку 'bin/' рядом со скриптом\n3. Или установите: winget install ffmpeg",
    },
}


class WMVConverterGUI(ctk.CTk):
    """Main GUI application for WMV to MP4 conversion."""

    def __init__(self):
        super().__init__()

        # Language
        self.lang = "en"
        self.L = LANGUAGES[self.lang]

        # Window configuration
        self.title(self.L["title"])
        self.geometry("800x700")
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

        # Widget references for language change
        self._widgets = {}

        # Build UI
        self._create_widgets()

        # Start log processor
        self.after(100, self._process_log_queue)

        # Check FFmpeg and scan folder
        self.after(300, self._check_ffmpeg)
        self.after(500, self._scan_folder)

    def _create_widgets(self):
        """Create all UI widgets."""
        # Language selector (top right)
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=25, pady=(10, 0))

        ctk.CTkLabel(lang_frame, text="Language:").pack(side="right", padx=(0, 5))
        self._widgets["lang_menu"] = ctk.CTkOptionMenu(
            lang_frame,
            values=["English", "Русский"],
            command=self._change_language,
            width=100
        )
        self._widgets["lang_menu"].pack(side="right")
        self._widgets["lang_menu"].set("English")

        # Title
        self._widgets["title"] = ctk.CTkLabel(
            self,
            text=self.L["title"],
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self._widgets["title"].pack(pady=(15, 5))

        # Subtitle
        self._widgets["subtitle"] = ctk.CTkLabel(
            self,
            text=self.L["subtitle"],
            font=ctk.CTkFont(size=12),
            text_color=("gray70")
        )
        self._widgets["subtitle"].pack(pady=(0, 15))

        # Folder selection frame
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=25, pady=5)

        self._widgets["folder_label"] = ctk.CTkLabel(
            folder_frame,
            text=self.L["folder_label"],
            font=ctk.CTkFont(size=14)
        )
        self._widgets["folder_label"].pack(side="left", padx=(0, 10))

        folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.selected_folder,
            width=450,
            height=35
        )
        folder_entry.pack(side="left", padx=(0, 10))

        self._widgets["browse_btn"] = ctk.CTkButton(
            folder_frame,
            text=self.L["browse_btn"],
            command=self._browse_folder,
            width=90,
            height=35
        )
        self._widgets["browse_btn"].pack(side="left")

        # Options frame
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=25, pady=10)

        self._widgets["gpu_checkbox"] = ctk.CTkCheckBox(
            options_frame,
            text=self.L["gpu_checkbox"],
            variable=self.use_gpu,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=13)
        )
        self._widgets["gpu_checkbox"].pack(side="left")

        self._widgets["encoder_label"] = ctk.CTkLabel(
            options_frame,
            text=self.L["encoder_gpu"],
            text_color="green",
            font=ctk.CTkFont(size=11)
        )
        self._widgets["encoder_label"].pack(side="left", padx=(15, 0))

        # Settings info
        info_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        info_frame.pack(fill="x", padx=25, pady=8)

        self._widgets["settings_info"] = ctk.CTkLabel(
            info_frame,
            text=self.L["settings_info"],
            font=ctk.CTkFont(size=11)
        )
        self._widgets["settings_info"].pack(pady=8)

        # Progress section
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=25, pady=10)

        self._widgets["progress_label"] = ctk.CTkLabel(
            progress_frame,
            text=self.L["progress_ready"],
            font=ctk.CTkFont(size=13)
        )
        self._widgets["progress_label"].pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=18)
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.set(0)

        self._widgets["file_count_label"] = ctk.CTkLabel(
            progress_frame,
            text="",
            text_color=("gray60"),
            font=ctk.CTkFont(size=11)
        )
        self._widgets["file_count_label"].pack(anchor="w", pady=(5, 0))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=25, pady=15)

        self._widgets["convert_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["convert_btn"],
            command=self._start_conversion,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
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
            width=100
        )
        self._widgets["stop_btn"].pack(side="left", padx=(0, 10))

        self._widgets["refresh_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["refresh_btn"],
            command=self._scan_folder,
            height=42,
            width=100
        )
        self._widgets["refresh_btn"].pack(side="left")

        self._widgets["open_folder_btn"] = ctk.CTkButton(
            buttons_frame,
            text=self.L["open_folder_btn"],
            command=self._open_output_folder,
            height=42,
            fg_color=("gray40", "gray30"),
            width=120
        )
        self._widgets["open_folder_btn"].pack(side="left", padx=(10, 0))

        # Log window
        self._widgets["log_label"] = ctk.CTkLabel(
            self,
            text=self.L["log_title"],
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self._widgets["log_label"].pack(anchor="w", padx=25, pady=(5, 0))

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

    def _change_language(self, new_lang: str):
        """Change UI language."""
        self.lang = "ru" if "Русский" in new_lang else "en"
        self.L = LANGUAGES[self.lang]

        # Update window title
        self.title(self.L["title"])

        # Update all widgets
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

    def _update_encoder_label(self):
        """Update encoder label based on GPU setting."""
        if self.use_gpu.get():
            self._widgets["encoder_label"].configure(
                text=self.L["encoder_gpu"],
                text_color="green"
            )
        else:
            self._widgets["encoder_label"].configure(
                text=self.L["encoder_cpu"],
                text_color="orange"
            )

    def _update_file_count(self):
        """Update file count label."""
        count = len(self.wmv_files)
        self._widgets["file_count_label"].configure(
            text=self.L["file_count"].format(count=count)
        )

    def _browse_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.selected_folder.get())
        if folder:
            self.selected_folder.set(folder)
            self._scan_folder()

    def _scan_folder(self):
        """Scan selected folder for WMV files."""
        folder = Path(self.selected_folder.get())
        wmv_set = set(folder.glob("*.wmv")) | set(folder.glob("*.WMV"))
        self.wmv_files = sorted(wmv_set)

        count = len(self.wmv_files)
        self._update_file_count()

        if count > 0:
            self._log(self.L["scan_folder"].format(folder=folder))
            self._log(self.L["scan_found"].format(count=count))
            for f in self.wmv_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                self._log(self.L["file_size"].format(name=f.name, size=size_mb))
        else:
            self._log(self.L["scan_no_files"].format(folder=folder))

        self._update_encoder_label()

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
                self._log(self.L["ffmpeg_ok"].format(version=version_line))

                encoders = subprocess.run(
                    [FFMPEG_PATH, "-hide_banner", "-encoders"],
                    capture_output=True,
                    text=True,
                    timeout=10
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

    def _update_progress(self, current: int, total: int, filename: str, status: str):
        """Update progress bar."""
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            status_text = f"[{current}/{total}] {filename}"
            if status:
                status_text += f" - {status}"
            self._widgets["progress_label"].configure(text=status_text)

    def _start_conversion(self):
        """Start conversion in a separate thread."""
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
        self._widgets["stop_btn"].configure(state="normal")
        self._widgets["convert_btn"].configure(state="disabled")
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

        self._log(self.L["conv_separator"])
        self._log(self.L["conv_start"])
        self._log(self.L["conv_encoder"].format(encoder=encoder_name))
        self._log(self.L["conv_total"].format(total=total))
        self._log(self.L["conv_separator"])

        for idx, wmv_file in enumerate(self.wmv_files, 1):
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

                    self._log(self.L["conv_output"].format(size=output_size_mb, ratio=ratio))
                    self._log(self.L["conv_time"].format(time=duration))
                    self._log(self.L["conv_success"].format(idx=idx, total=total))
                    success_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_done"])
                else:
                    error_msg = stderr.strip().split("\n")[-1] if stderr else "Unknown error"
                    self._log(self.L["conv_error"].format(message=error_msg))
                    error_count += 1
                    self.after(0, self._update_progress, idx, total, wmv_file.name, self.L["status_error"])

            except subprocess.TimeoutExpired:
                process.kill()
                self._log(self.L["conv_timeout"])
                error_count += 1
            except Exception as e:
                self._log(self.L["conv_error"].format(message=str(e)))
                error_count += 1

        # Summary
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

    def _conversion_finished(self, success: int, errors: int):
        """Handle conversion completion."""
        self.is_converting = False
        self._widgets["stop_btn"].configure(state="disabled")
        self._widgets["convert_btn"].configure(state="normal")
        self.progress_bar.set(0)
        self._widgets["progress_label"].configure(text=self.L["progress_ready"])

        if errors > 0:
            messagebox.showwarning(
                self.L["msg_conv_complete"],
                self.L["msg_conv_errors"].format(errors=errors)
            )
        elif success > 0:
            messagebox.showinfo(
                self.L["msg_conv_complete"],
                self.L["msg_conv_success"].format(count=success)
            )

    def _open_output_folder(self):
        """Open the output folder in file explorer."""
        folder = self.selected_folder.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showerror(self.L["msg_folder_error"], self.L["msg_folder_not_found"])


def main():
    """Main entry point."""
    app = WMVConverterGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
