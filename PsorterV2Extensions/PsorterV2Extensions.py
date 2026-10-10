import os, sys, shutil, datetime, concurrent.futures, time, webbrowser, json, subprocess, threading, urllib.request, zipfile, gc, random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import customtkinter as ctk

try:
    import cv2
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    os.environ['PYTHON_VLC_MODULE_PATH'] = base_dir
    os.environ['PYTHON_VLC_LIB_PATH'] = os.path.join(base_dir, 'libvlc.dll')

HAS_VLC, HAS_PYGAME = False, False
try:
    import vlc
    HAS_VLC = True
except Exception:
    try:
        import pygame
        pygame.mixer.init()
        HAS_PYGAME = True
    except Exception:
        pass

CURRENT_VERSION = "v2.0.0"
GITHUB_REPO = "atilla232/PsorterV2"
EXE_NAME = "PsorterV2Extensions.exe"
CONFIG_FILE = "psorter_extensions_config.json"
NETFLIX_RED, NETFLIX_RED_HOVER = "#E50914", "#B81D24"

THEME_DARK = {
    "bg_main": "#141414", "card_bg": "#1F1F1F", "card_hover": "#2B2B2B",
    "border": "#2B2B2B", "text_primary": "#FFFFFF", "text_secondary": "#AAAAAA",
    "listbox_bg": "#121212", "preview_bg": "#000000"
}

DEFAULT_CONFIG = {
    "active_mode": "media", "performance_threads": 4, "ram_limit_mb": 512,
    "enable_gc_cleanup": True, "enable_video_player": True, "enable_audio_player": True,
    "scan_subfolders": True, "auto_next_after_sort": True, "auto_play_media": False,
    "sound_notifications": True, "confirm_delete": True, "show_metadata_panel": True,
    "check_updates": True, "language": "id", "thumbnail_size": "Sedang (110px)",
    "extensions": {
        "photo": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".ico", ".svg", ".tiff"],
        "video": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".m4v", ".3gp"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus", ".aiff", ".alac", ".amr"],
        "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"],
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "executable": [".exe", ".msi", ".apk", ".bat", ".cmd"]
    }
}

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    return {**DEFAULT_CONFIG, **cfg}
            except Exception: pass
        return DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(cfg):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except Exception: pass

TRANSLATIONS = {
    "id": {
        "title": "PSORTERV2 Extensions - Universal Custom Sorter", "header_app": "PSORTERV2 EXTENSIONS",
        "select_src": "📁 Folder Sumber", "select_dst": "📂 Folder Tujuan", "src_label": "Sumber: ",
        "dst_label": "Tujuan (PSORTER): ", "not_selected": "(belum dipilih)",
        "subfolder_frame": " SUB-FOLDER TUJUAN ", "src_subfolder_frame": " 📁 SUB-FOLDER SUMBER ",
        "all_source_folders": "📂 [Semua File & Sub-Folder]", "root_files_only": "📄 [File di Root Utama]",
        "create_folder": "+ Buat Folder Baru (N)", "rename_folder": "✏️ Rename Folder",
        "delete_folder": "🗑️ Hapus Folder", "pin_folder": "📌 Pin / Unpin Folder",
        "autosort_btn": "⚡ SORTIR OTOMATIS", "direct_move_btn": "📦 PINDAH LANGSUNG",
        "play_media": "▶ PLAY / PAUSE MEDIA (SPASI)", "action_frame": " AKSI FILE ",
        "move_btn": "➡️ PINDAHKAN FILE\n(Enter / Angka 1-9)", "copy_btn": "📋 SALIN FILE\n(Enter / Angka 1-9)",
        "undo_btn": "↩️ BATAL / UNDO (Ctrl+Z)", "rename_file": "✏️ Rename File (R)",
        "batch_rename_file": "🏷️ Batch Rename (PSORTER_1...)", "delete_file": "🗑️ Hapus File (Delete)",
        "prev_btn": "◀ PREV (←)", "next_btn": "NEXT ▶ (→)", "file_counter": "FILE {} DARI {}",
        "initial_info": "Belum ada file yang dipilih", "no_files": "Tidak ada file di folder ini",
        "all_done": "Semua file selesai disortir ke folder PSORTER!", "done": "Selesai",
        "mode_move": "Mode: PINDAH", "mode_copy": "Mode: SALIN", "warn": "Peringatan",
        "warn_no_files": "Tidak ada file di folder sumber!", "warn_select_dst": "Pilih Folder Tujuan Utama terlebih dahulu!",
        "warn_select_sub": "Pilih sub-folder tujuan di panel kiri terlebih dahulu!",
        "warn_select_ren_folder": "Pilih folder yang ingin di-rename!", "warn_select_del_folder": "Pilih folder yang ingin dihapus!",
        "dlg_create_folder_title": "Buat Folder PSORTER", "dlg_create_folder_prompt": "Masukkan nama sub-folder baru:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' menjadi:",
        "dlg_delete_folder_title": "Konfirmasi Hapus Folder", "dlg_delete_folder_prompt": "Apakah kamu yakin ingin menghapus folder '{}' beserta seluruh isinya?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "Masukkan nama file baru:",
        "dlg_batch_rename_title": "Batch Rename", "dlg_batch_rename_prompt": "Masukkan awalan nama file (default: 'FILE'):",
        "dlg_delete_file_title": "Konfirmasi Hapus", "dlg_delete_file_prompt": "Hapus file '{}'?",
        "dlg_autosort_title": "Auto-Sort Otomatis", "dlg_autosort_prompt": "Pilih metode Auto-Sort ke sub-folder:\n\n1 = Berdasarkan Ekstensi Format (JPG, MP3, PDF, dll)\n2 = Berdasarkan Kelompok Tipe (Gambar, Video, Audio, Dokumen)\n3 = Berdasarkan Tanggal File (YYYY-MM-DD)\n\nMasukkan pilihan (1/2/3):",
        "err_title": "Gagal", "err_folder_exists": "Folder sudah ada!", "lang_label": "🌐 Language:",
        "stats_remaining": "Sisa: {} file ({:.1f} MB)", "stats_processed": "Diproses: {} file ({:.1f} MB)",
        "btn_donate": "💛 Saweria", "btn_refresh": "🔄 Refresh (F5)", "btn_settings": "⚙️ Pengaturan Fitur",
        "btn_menu": "🏠 Menu Utama", "msg_direct_moved": "Berhasil memindahkan {} file!"
    },
    "en": {
        "title": "PSORTERV2 Extensions - Universal Custom Sorter", "header_app": "PSORTERV2 EXTENSIONS",
        "select_src": "📁 Source Folder", "select_dst": "📂 Target Folder", "src_label": "Source: ",
        "dst_label": "Target (PSORTER): ", "not_selected": "(not selected)",
        "subfolder_frame": " TARGET SUB-FOLDERS ", "src_subfolder_frame": " 📁 SOURCE SUB-FOLDERS ",
        "all_source_folders": "📂 [All Files & Sub-Folders]", "root_files_only": "📄 [Root Directory Files]",
        "create_folder": "+ Create New Folder (N)", "rename_folder": "✏️ Rename Folder",
        "delete_folder": "🗑️ Delete Folder", "pin_folder": "📌 Pin / Unpin Folder",
        "autosort_btn": "⚡ AUTO-SORT FILES", "direct_move_btn": "📦 MOVE DIRECTLY",
        "play_media": "▶ PLAY / PAUSE MEDIA (SPACE)", "action_frame": " FILE ACTIONS ",
        "move_btn": "➡️ MOVE FILE\n(Enter / Key 1-9)", "copy_btn": "📋 COPY FILE\n(Enter / Key 1-9)",
        "undo_btn": "↩️ UNDO (Ctrl+Z)", "rename_file": "✏️ Rename File (R)",
        "batch_rename_file": "🏷️ Batch Rename (PSORTER_1...)", "delete_file": "🗑️ Delete File (Delete)",
        "prev_btn": "◀ PREV (←)", "next_btn": "NEXT ▶ (→)", "file_counter": "FILE {} OF {}",
        "initial_info": "No file selected", "no_files": "No files in this folder",
        "all_done": "All files sorted successfully to PSORTER folder!", "done": "Done",
        "mode_move": "Mode: MOVE", "mode_copy": "Mode: COPY", "warn": "Warning",
        "warn_no_files": "No files found in source folder!", "warn_select_dst": "Please select Main Target Folder first!",
        "warn_select_sub": "Please select target sub-folder on left panel first!",
        "warn_select_ren_folder": "Please select folder to rename!", "warn_select_del_folder": "Please select folder to delete!",
        "dlg_create_folder_title": "Create PSORTER Folder", "dlg_create_folder_prompt": "Enter new sub-folder name:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' to:",
        "dlg_delete_folder_title": "Confirm Delete Folder", "dlg_delete_folder_prompt": "Are you sure you want to delete folder '{}' and all contents?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "Enter new file name:",
        "dlg_batch_rename_title": "Batch Rename", "dlg_batch_rename_prompt": "Enter file prefix (default: 'FILE'):",
        "dlg_delete_file_title": "Confirm Delete File", "dlg_delete_file_prompt": "Delete file '{}'?",
        "dlg_autosort_title": "Auto-Sort Files", "dlg_autosort_prompt": "Choose Auto-Sort method to sub-folders:\n\n1 = By Extension (JPG, MP3, PDF, etc.)\n2 = By Category Group (Image, Video, Audio, Document)\n3 = By File Date (YYYY-MM-DD)\n\nEnter choice (1/2/3):",
        "err_title": "Error", "err_folder_exists": "Folder already exists!", "lang_label": "🌐 Language:",
        "stats_remaining": "Left: {} files ({:.1f} MB)", "stats_processed": "Done: {} files ({:.1f} MB)",
        "btn_donate": "💛 Saweria", "btn_refresh": "🔄 Refresh (F5)", "btn_settings": "⚙️ Feature Settings",
        "btn_menu": "🏠 Main Menu", "msg_direct_moved": "Successfully moved {} files!"
    }
}

class DownloadProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.t_palette = THEME_DARK
        self.title("Mengunduh Update - PSORTERV2 Extensions")
        self.geometry("420x230")
        self.resizable(False, False)
        self.configure(fg_color=self.t_palette["bg_main"])
        self.transient(parent)
        self.grab_set()
        
        self.is_paused = self.is_cancelled = False
        self.center_window()

        self.lbl_title = ctk.CTkLabel(self, text="Mengunduh Pembaruan PSORTERV2 Extensions...", font=("Arial", 13, "bold"), text_color=self.t_palette["text_primary"])
        self.lbl_title.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self, width=340, height=16, progress_color=NETFLIX_RED, fg_color=self.t_palette["card_hover"])
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Menghubungkan ke server...", font=("Arial", 11), text_color=self.t_palette["text_secondary"])
        self.lbl_status.pack(pady=(0, 15))

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill=tk.X, padx=40)

        self.btn_pause = ctk.CTkButton(btn_box, text="⏸️ Jeda", width=110, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"), command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = ctk.CTkButton(btn_box, text="❌ Batal", width=110, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B", font=("Arial", 11, "bold"), command=self.cancel_download)
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)
        self.protocol("WM_DELETE_WINDOW", self.cancel_download)

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()//2)-(w//2)}+{(self.winfo_screenheight()//2)-(h//2)}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.configure(text="▶️ Lanjutkan" if self.is_paused else "⏸️ Jeda", fg_color=NETFLIX_RED if self.is_paused else self.t_palette["card_hover"])
        self.lbl_status.configure(text="Pengunduhan dijeda..." if self.is_paused else "Mengunduh...")

    def cancel_download(self):
        self.is_cancelled = True
        self.lbl_status.configure(text="Membatalkan pengunduhan...")

    def update_progress(self, downloaded_bytes, total_bytes):
        if self.is_paused or self.is_cancelled: return
        dl_mb = downloaded_bytes / (1024 * 1024)
        if total_bytes > 0:
            percentage = downloaded_bytes / total_bytes
            self.progress_bar.set(percentage)
            tot_mb = total_bytes / (1024 * 1024)
            self.lbl_status.configure(text=f"{int(percentage * 100)}% ({dl_mb:.1f} MB / {tot_mb:.1f} MB)")
        else:
            self.lbl_status.configure(text=f"Terunduh: {dl_mb:.1f} MB")

def check_for_updates_async(root_window=None):
    threading.Thread(target=_check_logic, args=(root_window,), daemon=True).start()

def _check_logic(root_window):
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200: return
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data.get("tag_name", "")
        if not latest_version or latest_version == CURRENT_VERSION: return

        download_url = next((a.get("browser_download_url") for a in data.get("assets", []) if a.get("name", "").lower().endswith(".zip") and "sorter" in a.get("name", "").lower() and "extension" in a.get("name", "").lower()), None)
        if not download_url: return

        def show_dialog():
            if messagebox.askyesno("Update Tersedia", f"Versi baru PSORTERV2 Extensions ({latest_version}) sudah tersedia!\n\nApakah kamu ingin mengunduh dan memperbarui aplikasi sekarang?"):
                _perform_update(download_url, root_window)

        if root_window: root_window.after(0, show_dialog)
    except Exception: pass

def _perform_update(download_url, root_window):
    def run_update_thread():
        dialog_ref = [None]
        root_window.after(0, lambda: dialog_ref.__setitem__(0, DownloadProgressDialog(root_window)))
        while dialog_ref[0] is None: time.sleep(0.05)

        dialog = dialog_ref[0]
        try:
            temp_zip, extract_folder = "temp_update_ext.zip", "temp_extracted_ext"
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                total_bytes = int(response.getheader("Content-Length", 0))
                downloaded, chunk_size = 0, 16384
                with open(temp_zip, "wb") as out_file:
                    while True:
                        if dialog.is_cancelled: break
                        while dialog.is_paused and not dialog.is_cancelled: time.sleep(0.1)
                        if dialog.is_cancelled: break
                        chunk = response.read(chunk_size)
                        if not chunk: break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        d_b, t_b = downloaded, total_bytes
                        root_window.after(0, lambda d=d_b, t=t_b: dialog.update_progress(d, t))

            if dialog.is_cancelled:
                if os.path.exists(temp_zip): os.remove(temp_zip)
                root_window.after(0, dialog.destroy)
                return

            root_window.after(0, lambda: dialog.lbl_status.configure(text="Mengekstrak file update..."))
            with zipfile.ZipFile(temp_zip, "r") as zip_ref: zip_ref.extractall(extract_folder)

            extracted_exe = next((os.path.join(r, f) for r, d, files in os.walk(extract_folder) for f in files if f.lower().endswith(".exe")), None)
            if not extracted_exe:
                root_window.after(0, lambda: messagebox.showerror("Gagal Update", "File .exe tidak ditemukan di dalam archive ZIP!"))
                root_window.after(0, dialog.destroy)
                return

            current_exe = sys.executable if getattr(sys, 'frozen', False) else EXE_NAME
            exe_filename = os.path.basename(current_exe)

            bat_script = f'@echo off\ntimeout /t 2 /nobreak > nul\nmove /y "{extracted_exe}" "{exe_filename}"\nrmdir /s /q "{extract_folder}"\ndel "{temp_zip}"\nstart "" "{exe_filename}"\ndel "%~f0"\n'
            with open("update_ext.bat", "w") as f: f.write(bat_script)

            subprocess.Popen(["update_ext.bat"], shell=True)
            sys.exit(0)
        except Exception as e:
            if not dialog.is_cancelled: root_window.after(0, lambda: messagebox.showerror("Gagal Update", f"Terjadi kesalahan saat mengunduh update: {e}"))
            if dialog: root_window.after(0, dialog.destroy)

    threading.Thread(target=run_update_thread, daemon=True).start()

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, config, on_save_callback):
        super().__init__(parent)
        self.config_data, self.t_palette = config.copy(), THEME_DARK
        self.title("⚙️ Pengaturan Aplikasi")
        self.geometry("760x640")
        self.resizable(False, False)
        self.configure(fg_color=self.t_palette["bg_main"])
        self.on_save_callback = on_save_callback
        self.transient(parent)
        self.grab_set()
        self.center_window()

        ctk.CTkLabel(self, text="⚙️ PENGATURAN & KONFIGURASI", font=("Arial Black", 16, "bold"), text_color=self.t_palette["text_primary"]).pack(pady=(15, 2))
        ctk.CTkLabel(self, text="Kelola opsi fitur, alokasi memori, optimasi performa CPU, dan format file.", font=("Arial", 11), text_color=self.t_palette["text_secondary"]).pack(pady=(0, 10))

        tabview = ctk.CTkTabview(self, fg_color=self.t_palette["card_bg"])
        tabview.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Tab 1: Fitur & Fungsi
        scroll_mod = ctk.CTkScrollableFrame(tabview.add("🎛️ Fitur & Fungsi"), fg_color="transparent")
        scroll_mod.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.switches = {}
        switch_opts = [
            ("enable_video_player", "Pemutar Video Preview (OpenCV Engine)"),
            ("enable_audio_player", "Pemutar Audio Deck (VLC / Pygame Engine)"),
            ("scan_subfolders", "Pindai Sub-Folder Sumber (Rekursif)"),
            ("auto_next_after_sort", "Otomatis Lanjut ke File Berikutnya (Auto-Next)"),
            ("auto_play_media", "Otomatis Putar Media saat Dipilih"),
            ("sound_notifications", "Efek Suara Notifikasi"),
            ("confirm_delete", "Konfirmasi Sebelum Menghapus File/Folder"),
            ("show_metadata_panel", "Tampilkan Panel Informasi Metadata File"),
            ("check_updates", "Cek Pembaruan Otomatis saat Startup")
        ]

        for key, label in switch_opts:
            sw = ctk.CTkSwitch(scroll_mod, text=label, font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"])
            sw.pack(anchor="w", padx=15, pady=8)
            if self.config_data.get(key, True if key != "auto_play_media" else False): sw.select()
            self.switches[key] = sw

        ctk.CTkFrame(scroll_mod, height=2, fg_color=self.t_palette["border"]).pack(fill=tk.X, padx=15, pady=12)
        ctk.CTkLabel(scroll_mod, text="Ukuran Kartu pada Mode Grid:", font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=15, pady=(2, 5))

        self.thumb_size_menu = ctk.CTkOptionMenu(scroll_mod, values=["Kecil (80px)", "Sedang (110px)", "Besar (150px)"], fg_color=self.t_palette["card_hover"], button_color=NETFLIX_RED, text_color=self.t_palette["text_primary"], width=180)
        self.thumb_size_menu.set(self.config_data.get("thumbnail_size", "Sedang (110px)"))
        self.thumb_size_menu.pack(anchor="w", padx=15, pady=(0, 10))

        # Tab 2: Performa & Memori
        scroll_perf = ctk.CTkScrollableFrame(tabview.add("⚡ Performa & Memori"), fg_color="transparent")
        scroll_perf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ctk.CTkLabel(scroll_perf, text="🧠 Alokasi Multi-Threading CPU:", font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=15, pady=(10, 5))
        self.threads_var = tk.IntVar(value=self.config_data.get("performance_threads", 4))
        for val, txt in [(2, "2 Threads (Mode Hemat)"), (4, "4 Threads (Standar / Direkomendasikan)"), (8, "8 Threads (Performa Tinggi)"), (16, "16 Threads (Performa Maksimal)")]:
            ctk.CTkRadioButton(scroll_perf, text=txt, variable=self.threads_var, value=val, text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=25, pady=4)

        ctk.CTkFrame(scroll_perf, height=2, fg_color=self.t_palette["border"]).pack(fill=tk.X, padx=15, pady=15)
        ctk.CTkLabel(scroll_perf, text="💾 Batas Memori RAM (Cache Thumbnail):", font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=15, pady=(5, 5))

        self.ram_var = tk.IntVar(value=self.config_data.get("ram_limit_mb", 512))
        for val, txt in [(256, "256 MB (Hemat Memori)"), (512, "512 MB (Standar)"), (1024, "1024 MB / 1 GB (Performa Cepat)"), (2048, "2048 MB / 2 GB (Kapasitas Besar)")]:
            ctk.CTkRadioButton(scroll_perf, text=txt, variable=self.ram_var, value=val, text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=25, pady=4)

        self.sw_gc = ctk.CTkSwitch(scroll_perf, text="Pembersihan Memori Otomatis (Garbage Collector)", font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"])
        self.sw_gc.pack(anchor="w", padx=15, pady=(15, 10))
        if self.config_data.get("enable_gc_cleanup", True): self.sw_gc.select()

        # Tab 3: Ekstensi File
        tab_ext = tabview.add("📄 Ekstensi File")
        ctk.CTkLabel(tab_ext, text="Daftar ekstensi file yang didukung (pisahkan dengan koma):", font=("Arial", 11), text_color=self.t_palette["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 5))

        ext_dict, self.entries_ext = self.config_data.get("extensions", DEFAULT_CONFIG["extensions"]), {}
        for cat in ["photo", "video", "audio", "document", "archive", "executable"]:
            row_box = ctk.CTkFrame(tab_ext, fg_color="transparent")
            row_box.pack(fill=tk.X, padx=15, pady=4)
            ctk.CTkLabel(row_box, text=f"{cat.capitalize()}:", width=90, anchor="w", font=("Arial", 11, "bold"), text_color=self.t_palette["text_primary"]).pack(side=tk.LEFT)
            entry = ctk.CTkEntry(row_box, font=("Arial", 11), fg_color=self.t_palette["card_bg"], text_color=self.t_palette["text_primary"], border_color=self.t_palette["border"])
            entry.insert(0, ", ".join(ext_dict.get(cat, [])))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries_ext[cat] = entry

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill=tk.X, padx=20, pady=(0, 15))
        ctk.CTkButton(btn_box, text="💾 Simpan & Terapkan", fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 12, "bold"), height=38, command=self.save).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(btn_box, text="Batal", fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 12), height=38, command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()//2)-(w//2)}+{(self.winfo_screenheight()//2)-(h//2)}")

    def save(self):
        for k, sw in self.switches.items(): self.config_data[k] = bool(sw.get())
        self.config_data["performance_threads"] = self.threads_var.get()
        self.config_data["ram_limit_mb"] = self.ram_var.get()
        self.config_data["enable_gc_cleanup"] = bool(self.sw_gc.get())
        self.config_data["thumbnail_size"] = self.thumb_size_menu.get()
        self.config_data["extensions"] = {c: [e.strip().lower() if e.strip().startswith(".") else f".{e.strip().lower()}" for e in en.get().split(",") if e.strip()] for c, en in self.entries_ext.items()}

        ConfigManager.save_config(self.config_data)
        self.on_save_callback(self.config_data)
        self.destroy()

class StartupExtensionDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_mode, on_select_callback):
        super().__init__(parent)
        self.t_palette = THEME_DARK
        self.title("PSORTERV2 Extensions - Pilih Mode Kerja")
        self.geometry("860x520")
        self.resizable(False, False)
        self.configure(fg_color=self.t_palette["bg_main"])
        self.on_select_callback = on_select_callback
        self.transient(parent)
        self.grab_set()
        self.center_window()

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(25, 15))
        ctk.CTkLabel(header_frame, text="PSORTERV2 EXTENSIONS", font=("Arial Black", 24, "bold"), text_color=NETFLIX_RED).pack()
        ctk.CTkLabel(header_frame, text="PILIH MODE SORTIR & BEBAS PERSONALIUSASI", font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"]).pack(pady=(2, 0))
        ctk.CTkLabel(header_frame, text="Setiap mode dilengkapi dengan fitur pemutar khusus dan kebebasan mengkonfigurasi.", font=("Arial", 11), text_color=self.t_palette["text_secondary"]).pack(pady=(2, 0))

        cards_container = ctk.CTkFrame(self, fg_color="transparent")
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        modes_data = [
            {"id": "media", "title": "🖼️ FOTO & VIDEO", "subtitle": "Mode Galeri Visual", "color": "#0088FF", "badge": "OpenCV / PIL", "desc": "• Preview foto resolusi tinggi\n• Video Player interaktif\n• Auto-Sort Tanggal/Format\n• Cocok untuk Pusdokinfo"},
            {"id": "audio", "title": "🎵 AUDIO DECK", "subtitle": "Universal Audio Player", "color": "#00D2FF", "badge": "VLC / Pygame", "desc": "• Putar MP3, FLAC, WAV, M4A\n• Seeking Slider & Volume\n• Deteksi Kualitas Lossless\n• Vinyl Visual Deck"},
            {"id": "all", "title": "📁 SEMUA FILE", "subtitle": "Universal File Sorter", "color": NETFLIX_RED, "badge": "All Extensions", "desc": "• Sortir Dokumen, ZIP, EXE, DLL\n• Pemindaian Sub-Folder Tree\n• Fitur Pindah Langsung\n• Batch Rename Serbaguna"},
            {"id": "custom", "title": "⚙️ KUSTOM BEBAS", "subtitle": "Personalisasi Penuh", "color": "#E5C07B", "badge": "Custom Fitur", "desc": "• Bebas pilih ekstensi nyala/mati\n• Pengaturan Thread Performa\n• Custom RAM Cache Control\n• Akses Panel Settings"}
        ]

        for m in modes_data:
            card = ctk.CTkFrame(cards_container, fg_color=self.t_palette["card_bg"], border_width=1, border_color=self.t_palette["border"], corner_radius=12)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=5)
            ctk.CTkLabel(card, text=m["badge"], font=("Arial", 9, "bold"), text_color="black" if m["color"] in ("#E5C07B", "#00D2FF") else "white", fg_color=m["color"], corner_radius=6, height=20).pack(anchor="ne", padx=10, pady=(10, 0))
            ctk.CTkLabel(card, text=m["title"], font=("Arial Black", 12, "bold"), text_color=self.t_palette["text_primary"]).pack(anchor="w", padx=12, pady=(2, 0))
            ctk.CTkLabel(card, text=m["subtitle"], font=("Arial", 9, "bold"), text_color=m["color"]).pack(anchor="w", padx=12, pady=(0, 8))
            ctk.CTkLabel(card, text=m["desc"], font=("Arial", 9), text_color=self.t_palette["text_secondary"], justify="left", anchor="nw").pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
            ctk.CTkButton(card, text="PILIH MODE", font=("Arial", 10, "bold"), fg_color=m["color"], text_color="black" if m["color"] in ("#E5C07B", "#00D2FF") else "white", corner_radius=8, height=34, command=lambda mode_id=m["id"]: self.select(mode_id)).pack(fill=tk.X, padx=10, pady=(0, 10))

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()//2)-(w//2)}+{(self.winfo_screenheight()//2)-(h//2)}")

    def select(self, mode):
        self.grab_release()
        self.destroy()
        self.on_select_callback(mode)

class PsorterExtensionsApp:
    def __init__(self, root, mode="media"):
        self.root = root
        self.config = ConfigManager.load_config()
        self.config["active_mode"] = mode
        self.t_palette = THEME_DARK
        self.current_lang = self.config.get("language", "id")

        ctk.set_appearance_mode("Dark")
        self.root.geometry("1380x850" if self.config.get("scan_subfolders", True) else "1240x850")
        self.root.configure(fg_color=self.t_palette["bg_main"])

        self.max_workers = self.config.get("performance_threads", 4)
        self.source_dir = self.target_dir = ""
        self.raw_file_list, self.file_list, self.source_subfolders = [], [], []
        self.current_index = 0
        self.selected_source_subfolder = "ALL"

        self.cap = None
        self.is_playing = self.is_seeking = False
        self.video_job = self.audio_job = None
        self.total_frames, self.video_fps, self.audio_length = 0, 30.0, 0.0

        self.has_vlc, self.has_pygame = HAS_VLC, HAS_PYGAME
        self.vlc_instance = self.vlc_player = None
        if self.has_vlc:
            try:
                self.vlc_instance = vlc.Instance('--no-video', '--quiet')
                self.vlc_player = self.vlc_instance.media_player_new()
            except Exception: self.has_vlc = False

        self.volume_level, self.is_muted = 0.8, False
        self.view_mode, self.is_copy_mode = "preview", False
        self.undo_stack, self.pinned_folders = [], set()
        self.filter_mode, self.sort_mode = "Semua", "Nama"
        self.processed_files_count = self.processed_bytes_count = 0

        self.file_stats_cache, self.pil_thumb_cache = {}, {}
        self.photo_img_cache, self.metadata_cache, self.grid_cards = {}, {}, {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

        self.setup_ui()
        self.bind_shortcuts()
        self.update_ui_texts()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        if self.config.get("check_updates", True): check_for_updates_async(self.root)

    def t(self, key, *args):
        text = TRANSLATIONS[self.current_lang].get(key, key)
        return text.format(*args) if args else text

    def get_supported_extensions(self):
        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        mode = self.config.get("active_mode", "media")
        if mode == "media": return tuple(ext_cfg.get("photo", []) + ext_cfg.get("video", []))
        if mode == "audio": return tuple(ext_cfg.get("audio", []))
        return tuple(e for exts in ext_cfg.values() for e in exts)

    def enforce_ram_limit(self):
        ram_limit_mb = self.config.get("ram_limit_mb", 512)
        if len(self.pil_thumb_cache) > int(ram_limit_mb / 2):
            self.pil_thumb_cache.clear()
            self.photo_img_cache.clear()
        if self.config.get("enable_gc_cleanup", True): gc.collect()

    def setup_ui(self):
        brand_frame = ctk.CTkFrame(self.root, fg_color=self.t_palette["card_bg"], corner_radius=0, height=60, border_width=1, border_color=self.t_palette["border"])
        brand_frame.pack(fill=tk.X, side=tk.TOP)

        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_box.pack(side=tk.LEFT, padx=20, pady=10)
        self.lbl_brand = ctk.CTkLabel(logo_box, text="PSORTERV2 EXTENSIONS", font=("Arial Black", 20, "bold"), text_color=NETFLIX_RED)
        self.lbl_brand.pack(side=tk.LEFT)
        self.lbl_sub = ctk.CTkLabel(logo_box, text=f"  FREEDOM SORTER [{self.config.get('active_mode', 'media').upper()} MODE]", font=("Arial", 10, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_sub.pack(side=tk.LEFT, pady=(5, 0))

        right_header_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        right_header_box.pack(side=tk.RIGHT, padx=20)

        self.btn_menu = ctk.CTkButton(right_header_box, text="🏠 Menu Utama", command=self.back_to_menu, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 11, "bold"), width=110)
        self.btn_menu.pack(side=tk.RIGHT, padx=5)

        self.btn_settings = ctk.CTkButton(right_header_box, text="⚙️ Settings", command=self.open_settings, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"), width=100)
        self.btn_settings.pack(side=tk.RIGHT, padx=5)

        self.btn_refresh = ctk.CTkButton(right_header_box, text="🔄 Refresh", command=self.refresh_data, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"), width=90)
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

        self.btn_donate = ctk.CTkButton(right_header_box, text="💛 Saweria", command=lambda: webbrowser.open("https://saweria.co/Atillaraihan"), fg_color="#E5C07B", hover_color="#D19A66", text_color="#000000", font=("Arial", 11, "bold"), width=110)
        self.btn_donate.pack(side=tk.RIGHT, padx=5)

        self.lbl_lang = ctk.CTkLabel(right_header_box, text_color=self.t_palette["text_secondary"], font=("Arial", 11, "bold"))
        self.lbl_lang.pack(side=tk.LEFT, padx=5)

        self.lang_menu = ctk.CTkOptionMenu(right_header_box, values=["Bahasa Indonesia", "English"], command=self.on_language_change, fg_color=self.t_palette["card_hover"], button_color=NETFLIX_RED, dropdown_fg_color=self.t_palette["card_bg"], text_color=self.t_palette["text_primary"], width=130)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        footer_frame = ctk.CTkFrame(self.root, fg_color=self.t_palette["card_bg"], corner_radius=0, height=28)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_footer = ctk.CTkLabel(footer_frame, text="Made by Google Gemini & Atilla • Extensions Edition", font=("Arial", 10, "italic"), text_color=self.t_palette["text_secondary"])
        self.lbl_footer.pack(pady=4)

        top_frame = ctk.CTkFrame(self.root, fg_color=self.t_palette["card_bg"], corner_radius=10, border_width=1, border_color=self.t_palette["border"])
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        self.btn_src = ctk.CTkButton(top_frame, command=self.select_source_dir, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"))
        self.btn_src.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_src = ctk.CTkLabel(top_frame, text_color=self.t_palette["text_primary"], anchor="w")
        self.lbl_src.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_dst = ctk.CTkButton(top_frame, command=self.select_target_dir, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, text_color="white", font=("Arial", 11, "bold"))
        self.btn_dst.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_dst = ctk.CTkLabel(top_frame, text_color=self.t_palette["text_primary"], anchor="w")
        self.lbl_dst.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.mode_switch = ctk.CTkSwitch(top_frame, text="Mode: PINDAH", command=self.toggle_mode_switch, progress_color=NETFLIX_RED, text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"))
        self.mode_switch.pack(side=tk.RIGHT, padx=15)

        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Panel Sub-Folder Sumber
        self.src_folder_frame = ctk.CTkFrame(self.main_frame, fg_color=self.t_palette["card_bg"], corner_radius=12, width=210, border_width=1, border_color=self.t_palette["border"])
        self.lbl_src_folder_title = ctk.CTkLabel(self.src_folder_frame, font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_src_folder_title.pack(pady=(12, 5))

        src_list_container = ctk.CTkFrame(self.src_folder_frame, fg_color=self.t_palette["listbox_bg"], corner_radius=8, border_width=1, border_color=self.t_palette["border"])
        src_list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.src_folder_listbox = tk.Listbox(src_list_container, bg=self.t_palette["listbox_bg"], fg=self.t_palette["text_primary"], selectbackground=NETFLIX_RED, selectforeground="white", bd=0, highlightthickness=0, font=("Arial", 9))
        self.src_folder_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.src_folder_listbox.bind("<<ListboxSelect>>", self.on_source_subfolder_select)

        # Panel Kiri
        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color=self.t_palette["card_bg"], corner_radius=12, width=210, border_width=1, border_color=self.t_palette["border"])
        self.lbl_left_title = ctk.CTkLabel(self.left_frame, font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_left_title.pack(pady=(12, 5))

        list_container = ctk.CTkFrame(self.left_frame, fg_color=self.t_palette["listbox_bg"], corner_radius=8, border_width=1, border_color=self.t_palette["border"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        self.folder_listbox = tk.Listbox(list_container, bg=self.t_palette["listbox_bg"], fg=self.t_palette["text_primary"], selectbackground=NETFLIX_RED, selectforeground="white", bd=0, highlightthickness=0, font=("Arial", 9))
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.btn_folder_box = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_folder_box.pack(fill=tk.X, padx=8, pady=5)

        self.btn_autosort = ctk.CTkButton(self.btn_folder_box, text="⚡ AUTO-SORT FILES", command=self.auto_sort_files, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, text_color="white", font=("Arial", 10, "bold"))
        self.btn_direct_move = ctk.CTkButton(self.btn_folder_box, text="📦 PINDAH LANGSUNG", command=self.move_all_direct, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 10, "bold"))
        self.btn_pin_folder = ctk.CTkButton(self.btn_folder_box, text="📌 Pin / Unpin Folder", command=self.toggle_pin_folder, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_create_folder = ctk.CTkButton(self.btn_folder_box, command=self.create_folder, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_rename_folder = ctk.CTkButton(self.btn_folder_box, command=self.rename_folder, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_delete_folder = ctk.CTkButton(self.btn_folder_box, command=self.delete_folder, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")

        # Panel Tengah
        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color=self.t_palette["card_bg"], corner_radius=12, border_width=1, border_color=self.t_palette["border"])
        top_center_bar = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        top_center_bar.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.view_segmented_btn = ctk.CTkSegmentedButton(top_center_bar, values=["🖼️ Player / Preview Deck", "📁 Mode Grid"], command=self.on_view_mode_change, selected_color=NETFLIX_RED, unselected_color=self.t_palette["card_hover"], text_color=self.t_palette["text_primary"], font=("Arial", 11, "bold"))
        self.view_segmented_btn.set("🖼️ Player / Preview Deck")
        self.view_segmented_btn.pack(side=tk.LEFT, padx=5)

        self.lbl_sort = ctk.CTkLabel(top_center_bar, text="Urutan:", font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_sort.pack(side=tk.RIGHT, padx=(5, 5))
        self.sort_menu = ctk.CTkOptionMenu(top_center_bar, values=["Nama", "Tanggal", "Ukuran"], command=self.on_sort_change, fg_color=self.t_palette["card_hover"], button_color=NETFLIX_RED, text_color=self.t_palette["text_primary"], width=90)
        self.sort_menu.pack(side=tk.RIGHT, padx=5)

        self.lbl_filter = ctk.CTkLabel(top_center_bar, text="Filter:", font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_filter.pack(side=tk.RIGHT, padx=(10, 5))
        filter_vals = ["Semua", "Foto", "Video", "Audio", "Dokumen", "Archive"] if self.config.get("active_mode") in ("all", "custom") else ["Semua", "Foto", "Video"] if self.config.get("active_mode") == "media" else ["Semua", "Lossless", "Lossy"]
        self.filter_menu = ctk.CTkOptionMenu(top_center_bar, values=filter_vals, command=self.on_filter_change, fg_color=self.t_palette["card_hover"], button_color=NETFLIX_RED, text_color=self.t_palette["text_primary"], width=95)
        self.filter_menu.pack(side=tk.RIGHT, padx=5)

        self.lbl_file_info = ctk.CTkLabel(self.center_frame, font=("Arial", 12, "bold"), text_color=self.t_palette["text_primary"])
        self.lbl_file_info.pack(pady=4)

        self.view_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        self.preview_subframe = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.preview_subframe.pack(fill=tk.BOTH, expand=True)

        preview_bg = ctk.CTkFrame(self.preview_subframe, fg_color=self.t_palette["preview_bg"], corner_radius=8)
        preview_bg.pack(fill=tk.BOTH, expand=True, pady=2)

        self.preview_label = tk.Label(preview_bg, bg=self.t_palette["preview_bg"], fg=self.t_palette["text_primary"])
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        self.lbl_metadata = ctk.CTkLabel(self.preview_subframe, text="Format: - | Ukuran: - | Tanggal: -", font=("Arial", 10, "bold"), text_color=self.t_palette["text_secondary"])
        if self.config.get("show_metadata_panel", True): self.lbl_metadata.pack(pady=2)

        timeline_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent")
        timeline_bar.pack(fill=tk.X, pady=(2, 0))

        self.lbl_time_curr = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=NETFLIX_RED, width=45)
        self.lbl_time_curr.pack(side=tk.LEFT, padx=2)

        self.timeline_slider = ctk.CTkSlider(timeline_bar, from_=0, to=100, number_of_steps=100, fg_color=self.t_palette["card_hover"], progress_color=NETFLIX_RED, button_color=NETFLIX_RED, command=self.on_slider_seek)
        self.timeline_slider.set(0)
        self.timeline_slider.configure(state="disabled")
        self.timeline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.lbl_time_total = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"], width=45)
        self.lbl_time_total.pack(side=tk.RIGHT, padx=2)

        controls_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent")
        controls_bar.pack(fill=tk.X, pady=6)
        controls_bar.grid_columnconfigure(0, weight=1)
        controls_bar.grid_columnconfigure(1, weight=0)
        controls_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkFrame(controls_bar, fg_color="transparent").grid(row=0, column=0, sticky="ew")

        self.btn_play = ctk.CTkButton(controls_bar, command=self.toggle_media, state="disabled", fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, text_color="white", font=("Arial", 11, "bold"), height=34, width=200)
        self.btn_play.grid(row=0, column=1, padx=10)

        vol_box = ctk.CTkFrame(controls_bar, fg_color="transparent")
        vol_box.grid(row=0, column=2, sticky="e")

        self.btn_mute = ctk.CTkButton(vol_box, text="🔊", width=34, height=34, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], command=self.toggle_mute)
        self.btn_mute.pack(side=tk.LEFT, padx=(0, 5))

        self.volume_slider = ctk.CTkSlider(vol_box, from_=0, to=1, number_of_steps=100, width=100, fg_color=self.t_palette["card_hover"], progress_color=NETFLIX_RED, button_color=NETFLIX_RED, command=self.on_volume_change)
        self.volume_slider.set(0.8)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        self.lbl_volume_val = ctk.CTkLabel(vol_box, text="80%", font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"], width=35)
        self.lbl_volume_val.pack(side=tk.LEFT, padx=(2, 0))

        self.folder_grid_subframe = ctk.CTkScrollableFrame(self.view_container, fg_color=self.t_palette["bg_main"], corner_radius=8)

        # Panel Kanan
        self.right_frame = ctk.CTkFrame(self.main_frame, fg_color=self.t_palette["card_bg"], corner_radius=12, width=210, border_width=1, border_color=self.t_palette["border"])
        self.lbl_right_title = ctk.CTkLabel(self.right_frame, font=("Arial", 12, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_right_title.pack(pady=(12, 5))

        self.btn_move = ctk.CTkButton(self.right_frame, command=self.move_file, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, text_color="white", font=("Arial", 12, "bold"), height=48)
        self.btn_move.pack(fill=tk.X, padx=10, pady=6)

        self.btn_undo = ctk.CTkButton(self.right_frame, text="↩️ BATAL / UNDO (Ctrl+Z)", command=self.undo_last_action, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"], font=("Arial", 10, "bold"))
        self.btn_undo.pack(fill=tk.X, padx=10, pady=4)

        self.btn_rename_file = ctk.CTkButton(self.right_frame, command=self.rename_file, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_rename_file.pack(fill=tk.X, padx=10, pady=4)

        self.btn_batch_rename = ctk.CTkButton(self.right_frame, command=self.batch_rename_files, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_batch_rename.pack(fill=tk.X, padx=10, pady=4)

        self.btn_delete_file = ctk.CTkButton(self.right_frame, command=self.delete_file, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")
        self.btn_delete_file.pack(fill=tk.X, padx=10, pady=4)

        nav_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        nav_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_prev = ctk.CTkButton(nav_frame, command=self.prev_file, width=85, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_prev.pack(side=tk.LEFT)

        self.btn_next = ctk.CTkButton(nav_frame, command=self.next_file, width=85, fg_color=self.t_palette["card_hover"], hover_color=self.t_palette["border"], text_color=self.t_palette["text_primary"])
        self.btn_next.pack(side=tk.RIGHT)

        self.lbl_counter = ctk.CTkLabel(self.right_frame, font=("Arial", 11, "bold"), text_color=self.t_palette["text_secondary"])
        self.lbl_counter.pack(pady=5)

        stats_box = ctk.CTkFrame(self.right_frame, fg_color=self.t_palette["bg_main"], corner_radius=8, border_width=1, border_color=self.t_palette["border"])
        stats_box.pack(fill=tk.X, padx=10, pady=(10, 10))

        ctk.CTkLabel(stats_box, text="📊 STATISTIK SORTER", font=("Arial", 10, "bold"), text_color=self.t_palette["text_secondary"]).pack(pady=(6, 2))
        self.lbl_stat_remaining = ctk.CTkLabel(stats_box, text="Sisa: 0 file (0.0 MB)", font=("Arial", 9), text_color=self.t_palette["text_primary"])
        self.lbl_stat_remaining.pack()
        self.lbl_stat_processed = ctk.CTkLabel(stats_box, text="Diproses: 0 file (0.0 MB)", font=("Arial", 9), text_color=NETFLIX_RED)
        self.lbl_stat_processed.pack(pady=(0, 6))

        self.update_layout_visibility()

    def back_to_menu(self):
        self.stop_all_media()
        self.executor.shutdown(wait=False)
        self.root.destroy()
        temp_root = ctk.CTk()
        temp_root.withdraw()
        curr_mode = ConfigManager.load_config().get("active_mode", "media")
        dialog = StartupExtensionDialog(temp_root, curr_mode, lambda mode: (temp_root.destroy(), start_app(mode)))
        temp_root.mainloop()

    def update_layout_visibility(self):
        scan_sub = self.config.get("scan_subfolders", True)
        self.root.geometry("1380x850" if scan_sub else "1240x850")

        for f in [self.src_folder_frame, self.left_frame, self.center_frame, self.right_frame]: f.pack_forget()
        for b in [self.btn_autosort, self.btn_direct_move, self.btn_pin_folder, self.btn_create_folder, self.btn_rename_folder, self.btn_delete_folder]: b.pack_forget()

        self.btn_autosort.pack(fill=tk.X, pady=2)
        if scan_sub: self.btn_direct_move.pack(fill=tk.X, pady=2)
        for b in [self.btn_pin_folder, self.btn_create_folder, self.btn_rename_folder, self.btn_delete_folder]: b.pack(fill=tk.X, pady=2)

        if scan_sub:
            self.src_folder_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6), pady=5)
            self.left_frame.configure(width=210)
            self.right_frame.configure(width=210)
            self.btn_prev.configure(width=85)
            self.btn_next.configure(width=85)
            self.refresh_source_folder_list()
        else:
            self.left_frame.configure(width=270)
            self.right_frame.configure(width=230)
            self.btn_prev.configure(width=95)
            self.btn_next.configure(width=95)

        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6), pady=5)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=5)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0), pady=5)

    def open_settings(self): SettingsDialog(self.root, self.config, self.on_config_updated)

    def on_config_updated(self, new_config):
        self.config, self.max_workers = new_config, new_config.get("performance_threads", 4)
        ctk.set_appearance_mode("Dark")
        self.root.configure(fg_color=self.t_palette["bg_main"])
        self.executor.shutdown(wait=False)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.lbl_sub.configure(text=f"  FREEDOM SORTER [{self.config.get('active_mode', 'media').upper()} MODE]", text_color=self.t_palette["text_secondary"])

        if self.config.get("show_metadata_panel", True): self.lbl_metadata.pack(pady=2)
        else: self.lbl_metadata.pack_forget()

        self.update_layout_visibility()
        self.enforce_ram_limit()
        self.refresh_data()

    def refresh_data(self):
        if self.source_dir: self.scan_files()
        if self.target_dir: self.refresh_folder_list()

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def format_size(self, size_bytes): return size_bytes / (1024 * 1024)

    def on_view_mode_change(self, choice):
        self.stop_all_media()
        if "Grid" in choice:
            self.view_mode = "folder"
            self.preview_subframe.pack_forget()
            self.folder_grid_subframe.pack(fill=tk.BOTH, expand=True)
            self.populate_folder_grid()
        else:
            self.view_mode = "preview"
            self.folder_grid_subframe.pack_forget()
            self.preview_subframe.pack(fill=tk.BOTH, expand=True)
            self.load_current_media()

    def populate_folder_grid(self):
        for child in self.folder_grid_subframe.winfo_children(): child.destroy()
        self.grid_cards.clear()

        if not self.file_list:
            ctk.CTkLabel(self.folder_grid_subframe, text=self.t("no_files"), font=("Arial", 13), text_color=self.t_palette["text_primary"]).pack(pady=50)
            return

        columns = 4
        thumb_size_str = self.config.get("thumbnail_size", "Sedang (110px)")
        card_w = card_h = 100 if "Kecil" in thumb_size_str else 160 if "Besar" in thumb_size_str else 130
        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        photo_exts, video_exts = tuple(ext_cfg.get("photo", [])), tuple(ext_cfg.get("video", []))

        for idx, filename in enumerate(self.file_list):
            row, col = idx // columns, idx % columns
            filepath = os.path.join(self.source_dir, filename) if not os.path.isabs(filename) else filename
            is_selected = (idx == self.current_index)

            card = ctk.CTkFrame(self.folder_grid_subframe, fg_color=self.t_palette["card_bg"], border_width=2 if is_selected else 1, border_color=NETFLIX_RED if is_selected else self.t_palette["border"], corner_radius=8, width=card_w, height=card_h)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.pack_propagate(False)
            self.grid_cards[idx] = card

            if filename.lower().endswith(photo_exts + video_exts):
                thumb_lbl = tk.Label(card, bg=self.t_palette["card_bg"], text="...")
                thumb_lbl.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 0))
                if filepath in self.photo_img_cache:
                    thumb_lbl.config(image=self.photo_img_cache[filepath], text="")
                else:
                    self.executor.submit(self._async_load_thumbnail, filepath, filename, thumb_lbl, card_w)
                thumb_lbl.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))
            else:
                ext_str = os.path.splitext(filename)[1].upper().replace('.', '')
                icon_lbl = ctk.CTkLabel(card, text="📄", font=("Arial", 28))
                icon_lbl.pack(pady=(12, 0))
                ctk.CTkLabel(card, text=ext_str, font=("Arial", 9, "bold"), text_color="white", fg_color=NETFLIX_RED, corner_radius=4, height=16, width=40).pack(pady=(2, 4))
                icon_lbl.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))

            display_name = os.path.basename(filename)
            lbl_name = ctk.CTkLabel(card, text=display_name if len(display_name) <= 15 else display_name[:12] + "...", font=("Arial", 9, "bold"), text_color=self.t_palette["text_primary"])
            lbl_name.pack(pady=(2, 4))

            card.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))
            lbl_name.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))

    def _async_load_thumbnail(self, filepath, filename, label_widget, target_width):
        try:
            if filepath not in self.pil_thumb_cache:
                pil_img = self._generate_pil_thumb(filepath, filename, target_width)
                if pil_img: self.pil_thumb_cache[filepath] = pil_img
            if filepath in self.pil_thumb_cache:
                self.root.after(0, lambda: self._apply_thumb_to_widget(filepath, label_widget))
        except Exception: pass

    def _apply_thumb_to_widget(self, filepath, label_widget):
        if not label_widget.winfo_exists(): return
        if filepath not in self.photo_img_cache:
            self.photo_img_cache[filepath] = ImageTk.PhotoImage(self.pil_thumb_cache[filepath])
        label_widget.config(image=self.photo_img_cache[filepath], text="")

    def _generate_pil_thumb(self, filepath, filename, target_width):
        try:
            ext_cfg, fn_lower, thumb_h = self.config.get("extensions", DEFAULT_CONFIG["extensions"]), filename.lower(), int(target_width * 0.75)
            if fn_lower.endswith(tuple(ext_cfg.get("photo", []))):
                with Image.open(filepath) as img:
                    img.thumbnail((target_width - 20, thumb_h), Image.Resampling.NEAREST)
                    return img.copy()
            elif fn_lower.endswith(tuple(ext_cfg.get("video", []))) and HAS_CV2:
                temp_cap = cv2.VideoCapture(filepath)
                ret, frame = temp_cap.read()
                temp_cap.release()
                if ret:
                    h, w = frame.shape[:2]
                    scale = target_width / float(w)
                    resized = cv2.resize(frame, (target_width - 20, int(h * scale)), interpolation=cv2.INTER_NEAREST)
                    return Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        except Exception: pass
        return None

    def select_file_from_grid(self, index):
        old_index, self.current_index = self.current_index, index
        if old_index in self.grid_cards and self.grid_cards[old_index].winfo_exists():
            self.grid_cards[old_index].configure(border_width=1, border_color=self.t_palette["border"])
        if index in self.grid_cards and self.grid_cards[index].winfo_exists():
            self.grid_cards[index].configure(border_width=2, border_color=NETFLIX_RED)

        self.lbl_file_info.configure(text=os.path.basename(self.file_list[self.current_index]))
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))

    def toggle_mode_switch(self):
        self.is_copy_mode = bool(self.mode_switch.get())
        self.mode_switch.configure(text=self.t("mode_copy" if self.is_copy_mode else "mode_move"))
        self.btn_move.configure(text=self.t("copy_btn" if self.is_copy_mode else "move_btn"))

    def on_filter_change(self, choice):
        self.filter_mode = choice
        self.apply_filter_and_sort()

    def on_sort_change(self, choice):
        self.sort_mode = choice
        self.apply_filter_and_sort()

    def on_source_subfolder_select(self, event):
        if not self.config.get("scan_subfolders", True): return
        selected = self.src_folder_listbox.curselection()
        if not selected: return
        idx = selected[0]
        self.selected_source_subfolder = "ALL" if idx == 0 else "ROOT" if idx == 1 else self.source_subfolders[idx - 2]
        self.apply_filter_and_sort()

    def apply_filter_and_sort(self):
        if not self.source_dir or not self.raw_file_list:
            self.file_list, self.current_index = [], 0
            if self.view_mode == "preview":
                self.preview_label.config(image="", text=self.t("no_files"), fg=self.t_palette["text_primary"])
                self.lbl_file_info.configure(text=self.t("initial_info"))
                self.lbl_metadata.configure(text="Format: - | Ukuran: - | Tanggal: -")
                self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
            return

        ext_cfg, filtered = self.config.get("extensions", DEFAULT_CONFIG["extensions"]), []
        for f in self.raw_file_list:
            if self.config.get("scan_subfolders", True):
                rel_dir = os.path.dirname(os.path.normpath(f))
                if self.selected_source_subfolder == "ROOT" and rel_dir != "": continue
                if self.selected_source_subfolder not in ("ALL", "ROOT"):
                    target_sub = os.path.normpath(self.selected_source_subfolder)
                    if not (rel_dir == target_sub or rel_dir.startswith(target_sub + os.sep)): continue

            ext = os.path.splitext(f)[1].lower()
            if (self.filter_mode in ("Foto", "Photo") and ext in ext_cfg.get("photo", [])) or \
               (self.filter_mode in ("Video", "Videos") and ext in ext_cfg.get("video", [])) or \
               (self.filter_mode in ("Audio", "Music") and ext in ext_cfg.get("audio", [])) or \
               (self.filter_mode in ("Dokumen", "Documents") and ext in ext_cfg.get("document", [])) or \
               (self.filter_mode in ("Archive", "Zip") and ext in ext_cfg.get("archive", [])) or \
               self.filter_mode in ("Semua", "All"):
                filtered.append(f)

        if self.sort_mode in ("Nama", "Name"): filtered.sort(key=lambda x: os.path.basename(x).lower())
        elif self.sort_mode in ("Tanggal", "Date"): filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[1])
        elif self.sort_mode in ("Ukuran", "Size"): filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[0], reverse=True)

        self.file_list = filtered
        self.current_index = max(0, min(self.current_index, len(self.file_list) - 1))

        if self.view_mode == "folder": self.populate_folder_grid()
        elif self.file_list: self.load_current_media()
        else:
            self.preview_label.config(image="", text=self.t("no_files"), fg=self.t_palette["text_primary"])
            self.lbl_file_info.configure(text=self.t("initial_info"))
            self.lbl_metadata.configure(text="Format: - | Ukuran: - | Tanggal: -")
            self.lbl_counter.configure(text=self.t("file_counter", 0, 0))

        self.update_statistics()

    def update_statistics(self):
        if not self.source_dir: return
        remaining_bytes = sum(self.file_stats_cache.get(f, (0, 0))[0] for f in self.file_list)
        self.lbl_stat_remaining.configure(text=self.t("stats_remaining", len(self.file_list), self.format_size(remaining_bytes)))
        self.lbl_stat_processed.configure(text=self.t("stats_processed", self.processed_files_count, self.format_size(self.processed_bytes_count)))

    def toggle_pin_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected:
            messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
            return
        raw_name = self.folder_listbox.get(selected[0])
        folder_name = raw_name.replace("📌 ", "").split("] ")[-1] if "]" in raw_name else raw_name.replace("📌 ", "").strip()
        if folder_name in self.pinned_folders: self.pinned_folders.remove(folder_name)
        else: self.pinned_folders.add(folder_name)
        self.refresh_folder_list()

    def move_all_direct(self):
        if not self.source_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))

        selected = self.folder_listbox.curselection()
        dest_dir = os.path.join(self.target_dir, self.folder_listbox.get(selected[0]).replace("📌 ", "").split("] ")[-1]) if selected else self.target_dir
        self.stop_all_media()
        moved_count = 0

        for rel_or_abs in list(self.file_list):
            src_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
            if not os.path.exists(src_path): continue
            dst_path = os.path.join(dest_dir, os.path.basename(src_path))
            file_size = self.file_stats_cache.get(rel_or_abs, (0, 0))[0]

            if self.is_copy_mode:
                shutil.copy2(src_path, dst_path)
                self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path, 'size': file_size})
            else:
                shutil.move(src_path, dst_path)
                self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path, 'size': file_size})
                if rel_or_abs in self.raw_file_list: self.raw_file_list.remove(rel_or_abs)

            self.processed_files_count += 1
            self.processed_bytes_count += file_size
            moved_count += 1

        if self.config.get("sound_notifications", True): self.root.bell()
        self.enforce_ram_limit()
        self.refresh_folder_list()
        self.scan_files()
        messagebox.showinfo(self.t("done"), self.t("msg_direct_moved", moved_count))

    def auto_sort_files(self):
        if not self.source_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))

        choice = simpledialog.askstring(self.t("dlg_autosort_title"), self.t("dlg_autosort_prompt"))
        if not choice or choice.strip() not in ("1", "2", "3"): return

        choice = choice.strip()
        self.stop_all_media()
        sorted_count, ext_cfg = 0, self.config.get("extensions", DEFAULT_CONFIG["extensions"])

        for rel_or_abs in list(self.file_list):
            src_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
            if not os.path.exists(src_path): continue

            filename = os.path.basename(src_path)
            ext = os.path.splitext(filename)[1].lower()
            if choice == "1": sub_name = ext.replace(".", "").upper() if ext else "OTHERS"
            elif choice == "2": sub_name = "IMAGES" if ext in ext_cfg.get("photo", []) else "VIDEOS" if ext in ext_cfg.get("video", []) else "AUDIO" if ext in ext_cfg.get("audio", []) else "DOCUMENTS" if ext in ext_cfg.get("document", []) else "ARCHIVES" if ext in ext_cfg.get("archive", []) else "OTHERS"
            else: sub_name = datetime.datetime.fromtimestamp(self.file_stats_cache.get(rel_or_abs, (0, 0))[1]).strftime('%Y-%m-%d')

            dest_folder = os.path.join(self.target_dir, sub_name)
            if not os.path.exists(dest_folder): os.makedirs(dest_folder)

            dst_path = os.path.join(dest_folder, filename)
            file_size = self.file_stats_cache.get(rel_or_abs, (0, 0))[0]

            if self.is_copy_mode:
                shutil.copy2(src_path, dst_path)
                self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path, 'size': file_size})
            else:
                shutil.move(src_path, dst_path)
                self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path, 'size': file_size})
                if rel_or_abs in self.raw_file_list: self.raw_file_list.remove(rel_or_abs)

            self.processed_files_count += 1
            self.processed_bytes_count += file_size
            sorted_count += 1

        if self.config.get("sound_notifications", True): self.root.bell()
        self.enforce_ram_limit()
        self.refresh_folder_list()
        self.scan_files()
        messagebox.showinfo(self.t("done"), f"Auto-Sort Selesai! {sorted_count} file berhasil diproses ke folder PSORTER.")

    def undo_last_action(self):
        if not self.undo_stack: return
        last_act = self.undo_stack.pop()
        self.stop_all_media()
        try:
            if last_act['action'] == 'move' and os.path.exists(last_act['dst']):
                shutil.move(last_act['dst'], last_act['src'])
            elif last_act['action'] == 'copy' and os.path.exists(last_act['dst']):
                os.remove(last_act['dst'])

            if self.processed_files_count > 0:
                self.processed_files_count -= 1
                self.processed_bytes_count -= last_act['size']

            self.enforce_ram_limit()
            self.scan_files()
        except Exception as e: messagebox.showerror(self.t("err_title"), f"Gagal undo: {e}")

    def on_volume_change(self, value):
        self.volume_level = float(value)
        if self.has_vlc and self.vlc_player:
            self.vlc_player.audio_set_volume(int(self.volume_level * 100) if not self.is_muted else 0)
        elif self.has_pygame and not self.is_muted:
            pygame.mixer.music.set_volume(self.volume_level)
        self.lbl_volume_val.configure(text=f"{int(self.volume_level * 100)}%")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.btn_mute.configure(text="🔇" if self.is_muted else "🔊")
        if self.is_muted:
            if self.has_vlc and self.vlc_player: self.vlc_player.audio_set_volume(0)
            elif self.has_pygame: pygame.mixer.music.set_volume(0.0)
        else: self.on_volume_change(self.volume_level)

    def on_language_change(self, choice):
        self.current_lang = "id" if choice == "Bahasa Indonesia" else "en"
        self.config["language"] = self.current_lang
        ConfigManager.save_config(self.config)
        self.update_ui_texts()

    def update_ui_texts(self):
        self.root.title(self.t("title"))
        self.lbl_brand.configure(text=self.t("header_app"))
        self.lbl_sub.configure(text=f"  FREEDOM SORTER [{self.config.get('active_mode', 'media').upper()} MODE]")
        self.btn_src.configure(text=self.t("select_src"))
        self.btn_dst.configure(text=self.t("select_dst"))
        self.btn_menu.configure(text=self.t("btn_menu"))
        self.btn_donate.configure(text=self.t("btn_donate"))
        self.btn_refresh.configure(text=self.t("btn_refresh"))
        self.btn_settings.configure(text=self.t("btn_settings"))
        self.lbl_lang.configure(text=self.t("lang_label"))

        self.lbl_src.configure(text=self.t("src_label") + (self.source_dir or self.t("not_selected")))
        self.lbl_dst.configure(text=self.t("dst_label") + (self.target_dir or self.t("not_selected")))

        if self.config.get("scan_subfolders", True):
            self.lbl_src_folder_title.configure(text=self.t("src_subfolder_frame"))
            self.btn_direct_move.configure(text=self.t("direct_move_btn"))
            self.refresh_source_folder_list()

        self.lbl_left_title.configure(text=self.t("subfolder_frame"))
        self.btn_autosort.configure(text=self.t("autosort_btn"))
        self.btn_pin_folder.configure(text=self.t("pin_folder"))
        self.btn_create_folder.configure(text=self.t("create_folder"))
        self.btn_rename_folder.configure(text=self.t("rename_folder"))
        self.btn_delete_folder.configure(text=self.t("delete_folder"))
        self.btn_play.configure(text=self.t("play_media"))

        self.lbl_right_title.configure(text=self.t("action_frame"))
        self.btn_move.configure(text=self.t("copy_btn" if self.is_copy_mode else "move_btn"))
        self.btn_undo.configure(text=self.t("undo_btn"))
        self.btn_rename_file.configure(text=self.t("rename_file"))
        self.btn_batch_rename.configure(text=self.t("batch_rename_file"))
        self.btn_delete_file.configure(text=self.t("delete_file"))
        self.btn_prev.configure(text=self.t("prev_btn"))
        self.btn_next.configure(text=self.t("next_btn"))

        if not self.file_list:
            self.lbl_file_info.configure(text=self.t("initial_info"))
            self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
        elif self.view_mode == "preview":
            self.load_current_media()

    def bind_shortcuts(self):
        self.root.bind("<Right>", lambda e: self.next_file())
        self.root.bind("<Left>", lambda e: self.prev_file())
        self.root.bind("<space>", lambda e: self.toggle_media())
        self.root.bind("<F5>", lambda e: self.refresh_data())
        self.root.bind("<Return>", lambda e: self.move_file())
        self.root.bind("<Delete>", lambda e: self.delete_file())
        self.root.bind("r", lambda e: self.rename_file())
        self.root.bind("R", lambda e: self.rename_file())
        self.root.bind("n", lambda e: self.create_folder())
        self.root.bind("N", lambda e: self.create_folder())
        self.root.bind("<Control-z>", lambda e: self.undo_last_action())
        self.root.bind("<Control-Z>", lambda e: self.undo_last_action())
        for i in range(1, 10): self.root.bind(str(i), lambda e, idx=i-1: self.quick_move_by_index(idx))

    def select_source_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_src"))
        if folder:
            self.source_dir = os.path.normpath(folder)
            self.lbl_src.configure(text=self.t("src_label") + self.source_dir)
            for cache in [self.pil_thumb_cache, self.photo_img_cache, self.metadata_cache, self.file_stats_cache]: cache.clear()
            self.scan_files()

    def select_target_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_dst"))
        if folder:
            psorter_folder = os.path.normpath(os.path.join(folder, "PSORTER"))
            if not os.path.exists(psorter_folder): os.makedirs(psorter_folder)
            self.target_dir = psorter_folder
            self.lbl_dst.configure(text=self.t("dst_label") + psorter_folder)
            self.refresh_folder_list()

    def scan_files(self):
        self.stop_all_media()
        if not self.source_dir: return

        self.raw_file_list, valid_exts = [], self.get_supported_extensions()
        target_abs = os.path.abspath(self.target_dir) if self.target_dir else None

        if self.config.get("scan_subfolders", True):
            self.source_subfolders = []
            for root_dir, dirs, files in os.walk(self.source_dir):
                if target_abs and os.path.abspath(root_dir).startswith(target_abs): continue
                rel_folder = os.path.normpath(os.path.relpath(root_dir, self.source_dir))
                if rel_folder != "." and rel_folder not in self.source_subfolders: self.source_subfolders.append(rel_folder)

                for f in files:
                    if f.lower().endswith(valid_exts):
                        self.raw_file_list.append(os.path.normpath(os.path.relpath(os.path.join(root_dir, f), self.source_dir)))
            self.refresh_source_folder_list()
        else:
            self.raw_file_list = [f for f in sorted(os.listdir(self.source_dir)) if f.lower().endswith(valid_exts)]

        for f in self.raw_file_list:
            if f not in self.file_stats_cache:
                p = os.path.join(self.source_dir, f) if not os.path.isabs(f) else f
                try:
                    st = os.stat(p)
                    self.file_stats_cache[f] = (st.st_size, st.st_mtime)
                except Exception: self.file_stats_cache[f] = (0, 0)

        self.enforce_ram_limit()
        self.apply_filter_and_sort()

    def refresh_source_folder_list(self):
        if not self.config.get("scan_subfolders", True): return
        self.src_folder_listbox.delete(0, tk.END)
        self.src_folder_listbox.insert(tk.END, self.t("all_source_folders"))
        self.src_folder_listbox.insert(tk.END, self.t("root_files_only"))
        for sf in self.source_subfolders: self.src_folder_listbox.insert(tk.END, f"📁 {sf}")
        if self.src_folder_listbox.size() > 0:
            self.src_folder_listbox.selection_set(0)
            self.src_folder_listbox.activate(0)

    def refresh_folder_list(self):
        self.folder_listbox.delete(0, tk.END)
        if not self.target_dir or not os.path.exists(self.target_dir): return
        subfolders = [f for f in sorted(os.listdir(self.target_dir)) if os.path.isdir(os.path.join(self.target_dir, f))]
        final_folders = [f for f in subfolders if f in self.pinned_folders] + [f for f in subfolders if f not in self.pinned_folders]

        for idx, folder in enumerate(final_folders):
            pin_icon = "📌 " if folder in self.pinned_folders else ""
            prefix = f"[{idx+1}] " if idx < 9 else "    "
            self.folder_listbox.insert(tk.END, f"{prefix}{pin_icon}{folder}")

    def load_current_media(self):
        self.stop_all_media()
        if not self.file_list or self.current_index >= len(self.file_list):
            self.preview_label.config(image="", text=self.t("all_done"), fg=self.t_palette["text_primary"])
            self.lbl_file_info.configure(text=self.t("done"))
            self.lbl_metadata.configure(text="Format: - | Ukuran: - | Tanggal: -")
            self.lbl_counter.configure(text=self.t("file_counter", len(self.file_list), len(self.file_list)))
            self.timeline_slider.configure(state="disabled")
            self.btn_play.configure(state="disabled")
            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text="00:00")
            return

        rel_or_abs = self.file_list[self.current_index]
        filepath = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
        filename = os.path.basename(filepath)

        self.lbl_file_info.configure(text=rel_or_abs)
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))
        if self.config.get("show_metadata_panel", True): self.update_metadata_panel(filepath, filename, rel_or_abs)

        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        fn_lower = filename.lower()

        if fn_lower.endswith(tuple(ext_cfg.get("photo", []))):
            self.btn_play.configure(state="disabled")
            self.timeline_slider.configure(state="disabled")
            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text="00:00")
            self.display_image(filepath)

        elif fn_lower.endswith(tuple(ext_cfg.get("video", []))):
            if self.config.get("enable_video_player", True) and HAS_CV2:
                self.btn_play.configure(state="normal")
                self.prepare_video(filepath)
                if self.config.get("auto_play_media", False): self.toggle_media()
            else:
                self.btn_play.configure(state="disabled")
                self.timeline_slider.configure(state="disabled")
                self.preview_label.config(image="", text="🎥 PREVIEW VIDEO (DISABLED)", fg="#EAB308")

        elif fn_lower.endswith(tuple(ext_cfg.get("audio", []))):
            if self.config.get("enable_audio_player", True):
                self.btn_play.configure(state="normal")
                self.timeline_slider.configure(state="normal")
                self.preview_label.config(image="", text=f"🎧 AUDIO DECK PLAYER\n\n{filename}", fg=NETFLIX_RED, font=("Arial", 16, "bold"))
                self.prepare_audio(filepath)
                if self.config.get("auto_play_media", False): self.toggle_media()
            else:
                self.btn_play.configure(state="disabled")
                self.timeline_slider.configure(state="disabled")
                self.preview_label.config(image="", text="🎵 PREVIEW AUDIO (DISABLED)", fg="#EAB308")

        else:
            self.btn_play.configure(state="disabled")
            self.timeline_slider.configure(state="disabled")
            ext_upper = os.path.splitext(filename)[1].upper()
            self.preview_label.config(image="", text=f"📄 FILE DOCUMENT / ARCHIVE [{ext_upper}]\n\n{filename}", fg=self.t_palette["text_primary"], font=("Arial", 14, "bold"))

    def update_metadata_panel(self, filepath, filename, key_file):
        if filepath in self.metadata_cache:
            return self.lbl_metadata.configure(text=self.metadata_cache[filepath])
        if not os.path.exists(filepath): return

        size_bytes, mtime_val = self.file_stats_cache.get(key_file, (os.path.getsize(filepath), os.path.getmtime(filepath)))
        size_mb = size_bytes / (1024 * 1024)
        mtime = datetime.datetime.fromtimestamp(mtime_val).strftime('%Y-%m-%d %H:%M')

        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        dim_str = "Dimensi: -"

        if filename.lower().endswith(tuple(ext_cfg.get("photo", []))):
            try:
                with Image.open(filepath) as img: dim_str = f"Dimensi: {img.width}x{img.height}"
            except Exception: pass
        elif filename.lower().endswith(tuple(ext_cfg.get("video", []))) and HAS_CV2:
            try:
                temp_cap = cv2.VideoCapture(filepath)
                w, h, fps = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(temp_cap.get(cv2.CAP_PROP_FPS))
                dim_str = f"Dimensi: {w}x{h} ({fps}fps)"
                temp_cap.release()
            except Exception: pass

        meta_text = f"{dim_str} | Ukuran: {size_mb:.2f} MB | Tanggal: {mtime}"
        self.metadata_cache[filepath] = meta_text
        self.lbl_metadata.configure(text=meta_text)

    def display_image(self, filepath):
        try:
            img = Image.open(filepath)
            img.thumbnail((620, 420), Image.Resampling.NEAREST)
            img_tk = ImageTk.PhotoImage(img)
            self.preview_label.config(image=img_tk, text="")
            self.preview_label.image = img_tk
        except Exception as e:
            self.preview_label.config(image="", text=f"Gagal memuat gambar: {e}", fg="#EF4444")

    def prepare_video(self, filepath):
        if not HAS_CV2: return
        self.cap = cv2.VideoCapture(filepath)
        if self.cap.isOpened():
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0

            if self.total_frames > 1:
                self.timeline_slider.configure(state="normal", from_=0, to=self.total_frames - 1, number_of_steps=self.total_frames)
            else: self.timeline_slider.configure(state="disabled")

            self.is_seeking = True
            self.timeline_slider.set(0)
            self.is_seeking = False

            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text=self.format_time(self.total_frames / self.video_fps))

            if self.has_vlc and self.vlc_instance:
                try:
                    self.vlc_player.set_media(self.vlc_instance.media_new(filepath))
                    self.on_volume_change(self.volume_level)
                except Exception: pass

            ret, frame = self.cap.read()
            if ret: self.show_frame(frame)

    def prepare_audio(self, filepath):
        if self.has_vlc and self.vlc_instance:
            try:
                media = self.vlc_instance.media_new(filepath)
                self.vlc_player.set_media(media)
                media.parse_with_options(vlc.MediaParseFlag.local, 0)
                time.sleep(0.05)
                self.on_volume_change(self.volume_level)
                self.lbl_time_curr.configure(text="00:00")
                self.lbl_time_total.configure(text="--:--")
                return
            except Exception: pass

        if self.has_pygame:
            try:
                pygame.mixer.music.load(filepath)
                self.lbl_time_curr.configure(text="00:00")
                self.lbl_time_total.configure(text="--:--")
            except Exception: pass

    def show_frame(self, frame):
        h, w = frame.shape[:2]
        scale = min(640 / float(w), 420 / float(h))
        if scale < 1.0:
            frame = cv2.resize(frame, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_NEAREST)

        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.preview_label.config(image=img_tk, text="")
        self.preview_label.image = img_tk

    def toggle_media(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        filename = os.path.basename(self.file_list[self.current_index])
        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        fn_lower = filename.lower()

        if fn_lower.endswith(tuple(ext_cfg.get("video", []))) and HAS_CV2 and self.cap:
            if self.is_playing:
                self.is_playing = False
                if self.video_job: self.root.after_cancel(self.video_job)
                if self.has_vlc and self.vlc_player: self.vlc_player.pause()
            else:
                self.is_playing = True
                if self.has_vlc and self.vlc_player: self.vlc_player.play()
                self.play_video_loop()

        elif fn_lower.endswith(tuple(ext_cfg.get("audio", []))):
            if self.has_vlc and self.vlc_player:
                if self.is_playing:
                    self.vlc_player.pause()
                    self.is_playing = False
                    if self.audio_job: self.root.after_cancel(self.audio_job)
                else:
                    self.vlc_player.play()
                    self.is_playing = True
                    self.update_audio_loop()
            elif self.has_pygame:
                if self.is_playing:
                    pygame.mixer.music.pause()
                    self.is_playing = False
                    if self.audio_job: self.root.after_cancel(self.audio_job)
                else:
                    pygame.mixer.music.play()
                    self.is_playing = True
                    self.update_audio_loop()

    def play_video_loop(self):
        if self.is_playing and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                curr_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.is_seeking = True
                self.timeline_slider.set(curr_frame)
                self.is_seeking = False
                self.lbl_time_curr.configure(text=self.format_time(curr_frame / self.video_fps))
                self.show_frame(frame)
                self.video_job = self.root.after(max(15, int(1000 / self.video_fps) if self.video_fps > 0 else 33), self.play_video_loop)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                if self.has_vlc and self.vlc_player: self.vlc_player.set_time(0)
                self.video_job = self.root.after(33, self.play_video_loop)

    def update_audio_loop(self):
        if self.is_playing:
            if self.has_vlc and self.vlc_player:
                ms, length_ms = self.vlc_player.get_time(), self.vlc_player.get_length()
                if length_ms > 0:
                    self.audio_length = length_ms / 1000.0
                    self.lbl_time_total.configure(text=self.format_time(self.audio_length))
                    self.timeline_slider.configure(from_=0, to=self.audio_length)

                if ms >= 0 and self.audio_length > 0:
                    curr_sec = ms / 1000.0
                    if not self.is_seeking: self.timeline_slider.set(curr_sec)
                    self.lbl_time_curr.configure(text=self.format_time(curr_sec))

                if self.vlc_player.get_state() == vlc.State.Ended:
                    self.stop_all_media()
                    return

            elif self.has_pygame:
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms >= 0:
                    curr_sec = pos_ms / 1000.0
                    if not self.is_seeking: self.timeline_slider.set(curr_sec)
                    self.lbl_time_curr.configure(text=self.format_time(curr_sec))

            self.audio_job = self.root.after(200, self.update_audio_loop)

    def on_slider_seek(self, value):
        if not self.file_list or self.current_index >= len(self.file_list): return
        filename = os.path.basename(self.file_list[self.current_index])
        ext_cfg = self.config.get("extensions", DEFAULT_CONFIG["extensions"])
        fn_lower = filename.lower()

        if fn_lower.endswith(tuple(ext_cfg.get("video", []))) and HAS_CV2 and self.cap:
            if self.is_seeking or not self.cap.isOpened(): return
            target_frame = int(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = self.cap.read()
            if ret:
                curr_sec = target_frame / self.video_fps
                self.lbl_time_curr.configure(text=self.format_time(curr_sec))
                self.show_frame(frame)
                if self.has_vlc and self.vlc_player: self.vlc_player.set_time(int(curr_sec * 1000))

        elif fn_lower.endswith(tuple(ext_cfg.get("audio", []))):
            self.is_seeking = True
            seek_sec = float(value)
            if self.has_vlc and self.vlc_player: self.vlc_player.set_time(int(seek_sec * 1000))
            elif self.has_pygame:
                try: pygame.mixer.music.play(start=seek_sec)
                except Exception: pass
            self.lbl_time_curr.configure(text=self.format_time(seek_sec))
            self.is_seeking = False

    def stop_all_media(self):
        self.is_playing = False
        if self.video_job:
            self.root.after_cancel(self.video_job)
            self.video_job = None
        if self.cap:
            self.cap.release()
            self.cap = None

        if self.has_vlc and self.vlc_player: self.vlc_player.stop()
        elif self.has_pygame: pygame.mixer.music.stop()

        if self.audio_job:
            self.root.after_cancel(self.audio_job)
            self.audio_job = None

    def create_folder(self):
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))
        name = simpledialog.askstring(self.t("dlg_create_folder_title"), self.t("dlg_create_folder_prompt"))
        if name:
            path = os.path.join(self.target_dir, name.strip())
            if not os.path.exists(path):
                os.makedirs(path)
                self.refresh_folder_list()
            else: messagebox.showerror(self.t("err_title"), self.t("err_folder_exists"))

    def rename_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: return messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
        raw_name = self.folder_listbox.get(selected[0])
        old_name = raw_name.replace("📌 ", "").split("] ")[-1] if "]" in raw_name else raw_name.replace("📌 ", "").strip()

        new_name = simpledialog.askstring(self.t("dlg_rename_folder_title"), self.t("dlg_rename_folder_prompt", old_name), initialvalue=old_name)
        if new_name and new_name.strip() != old_name:
            os.rename(os.path.join(self.target_dir, old_name), os.path.join(self.target_dir, new_name.strip()))
            if old_name in self.pinned_folders:
                self.pinned_folders.remove(old_name)
                self.pinned_folders.add(new_name.strip())
            self.refresh_folder_list()

    def delete_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: return messagebox.showwarning(self.t("warn"), self.t("warn_select_del_folder"))
        raw_name = self.folder_listbox.get(selected[0])
        folder_name = raw_name.replace("📌 ", "").split("] ")[-1] if "]" in raw_name else raw_name.replace("📌 ", "").strip()

        if self.config.get("confirm_delete", True) and not messagebox.askyesno(self.t("dlg_delete_folder_title"), self.t("dlg_delete_folder_prompt", folder_name)):
            return

        shutil.rmtree(os.path.join(self.target_dir, folder_name))
        if folder_name in self.pinned_folders: self.pinned_folders.remove(folder_name)
        self.refresh_folder_list()

    def quick_move_by_index(self, index):
        if index < self.folder_listbox.size():
            self.folder_listbox.selection_clear(0, tk.END)
            self.folder_listbox.selection_set(index)
            self.folder_listbox.activate(index)
            self.move_file()

    def move_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        selected = self.folder_listbox.curselection()
        if not selected: return messagebox.showwarning(self.t("warn"), self.t("warn_select_sub"))

        raw_name = self.folder_listbox.get(selected[0])
        dest_dir = os.path.join(self.target_dir, raw_name.replace("📌 ", "").split("] ")[-1] if "]" in raw_name else raw_name.replace("📌 ", "").strip())

        self.stop_all_media()
        rel_or_abs = self.file_list[self.current_index]
        src_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
        dst_path = os.path.join(dest_dir, os.path.basename(src_path))
        file_size = self.file_stats_cache.get(rel_or_abs, (0, 0))[0]

        if self.is_copy_mode:
            shutil.copy2(src_path, dst_path)
            self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path, 'size': file_size})
        else:
            shutil.move(src_path, dst_path)
            self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path, 'size': file_size})
            del self.raw_file_list[self.raw_file_list.index(rel_or_abs)]

        self.processed_files_count += 1
        self.processed_bytes_count += file_size
        if self.config.get("sound_notifications", True): self.root.bell()
        self.enforce_ram_limit()
        self.apply_filter_and_sort()
        if self.config.get("auto_next_after_sort", True) and self.is_copy_mode: self.next_file()

    def rename_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        rel_or_abs = self.file_list[self.current_index]
        old_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
        old_filename = os.path.basename(old_path)
        self.stop_all_media()

        new_filename = simpledialog.askstring(self.t("dlg_rename_file_title"), self.t("dlg_rename_file_prompt"), initialvalue=old_filename)
        if new_filename and new_filename.strip() != old_filename:
            new_path = os.path.join(os.path.dirname(old_path), new_filename.strip())
            os.rename(old_path, new_path)
            self.raw_file_list[self.raw_file_list.index(rel_or_abs)] = os.path.relpath(new_path, self.source_dir)

        self.apply_filter_and_sort()

    def batch_rename_files(self):
        if not self.file_list: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        self.stop_all_media()
        prefix = simpledialog.askstring(self.t("dlg_batch_rename_title"), self.t("dlg_batch_rename_prompt"), initialvalue="FILE")
        if not prefix or not prefix.strip(): return

        prefix, temp_file_map = prefix.strip(), []
        for i, rel_or_abs in enumerate(self.file_list):
            old_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
            old_filename = os.path.basename(old_path)
            parent_dir, ext = os.path.dirname(old_path), os.path.splitext(old_filename)[1]
            temp_path = os.path.join(parent_dir, f"__temp_psorter_{i}_{old_filename}")
            try:
                os.rename(old_path, temp_path)
                temp_file_map.append((temp_path, parent_dir, ext, rel_or_abs))
            except Exception as e:
                messagebox.showerror(self.t("err_title"), f"Gagal merename file {old_filename}: {e}")
                self.scan_files()
                return

        for i, (temp_path, parent_dir, ext, rel_or_abs) in enumerate(temp_file_map):
            final_path = os.path.join(parent_dir, f"{prefix}_{i+1}{ext}")
            os.rename(temp_path, final_path)
            self.raw_file_list[self.raw_file_list.index(rel_or_abs)] = os.path.relpath(final_path, self.source_dir)

        self.apply_filter_and_sort()

    def delete_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        rel_or_abs = self.file_list[self.current_index]
        if self.config.get("confirm_delete", True) and not messagebox.askyesno(self.t("dlg_delete_file_title"), self.t("dlg_delete_file_prompt", os.path.basename(rel_or_abs))):
            return

        self.stop_all_media()
        os.remove(os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs)
        del self.raw_file_list[self.raw_file_list.index(rel_or_abs)]

        if self.config.get("sound_notifications", True): self.root.bell()
        self.enforce_ram_limit()
        self.apply_filter_and_sort()

    def next_file(self):
        if self.current_index < len(self.file_list) - 1:
            self.current_index += 1
            if self.view_mode == "preview": self.load_current_media()
            else: self.select_file_from_grid(self.current_index)

    def prev_file(self):
        if self.current_index > 0:
            self.current_index -= 1
            if self.view_mode == "preview": self.load_current_media()
            else: self.select_file_from_grid(self.current_index)

    def on_closing(self):
        self.stop_all_media()
        self.executor.shutdown(wait=False)
        if random.random() < 0.35 and messagebox.askyesno("💛 Dukung Pengembang", "Terima kasih sudah menggunakan PSORTERV2 Extensions!\n\nJika aplikasi ini membantu pekerjaanmu, ingin traktir permen melalui Saweria?"):
            webbrowser.open("https://saweria.co/Atillaraihan")
        self.root.destroy()

def start_app(selected_mode):
    root = ctk.CTk()
    app = PsorterExtensionsApp(root, mode=selected_mode)
    root.mainloop()

if __name__ == "__main__":
    temp_root = ctk.CTk()
    temp_root.withdraw()
    cfg = ConfigManager.load_config()
    dialog = StartupExtensionDialog(temp_root, cfg.get("active_mode", "media"), lambda mode: (temp_root.destroy(), start_app(mode)))
    temp_root.mainloop()