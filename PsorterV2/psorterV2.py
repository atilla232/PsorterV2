import os, shutil, datetime, concurrent.futures, webbrowser, json, subprocess, sys, threading, urllib.request, zipfile, time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2, customtkinter as ctk

try: import psutil; HAS_PSUTIL = True
except Exception: HAS_PSUTIL = False

try: import vlc; HAS_VLC = True
except Exception: HAS_VLC = False

try: import pygame; pygame.mixer.init(); HAS_PYGAME = True
except Exception: HAS_PYGAME = False

if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    os.environ['PYTHON_VLC_MODULE_PATH'] = base_dir
    os.environ['PYTHON_VLC_LIB_PATH'] = os.path.join(base_dir, 'libvlc.dll')

CURRENT_VERSION, GITHUB_REPO, EXE_NAME = "v2.0.0", "atilla232/PsorterV2", "psorterV2.exe"
NETFLIX_RED, NETFLIX_RED_HOVER, BG_DARK, CARD_BG, CARD_BG_LIGHT, TEXT_MUTED = "#E50914", "#B81D24", "#141414", "#1F1F1F", "#2B2B2B", "#AAAAAA"
SAWERIA_YELLOW, SAWERIA_HOVER = "#E5C07B", "#D19A66"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

TRANSLATIONS = {
    "id": {
        "title": "PSORTERV2 - Pusdokinfo Sorter", "header_app": "PSORTERV2", "header_sub": "PUSDOKINFO MEDIA SORTER",
        "select_src": "📁 Folder Sumber", "select_dst": "📂 Folder Tujuan Utama", "src_label": "Sumber: ", "dst_label": "Tujuan (PSORTER): ",
        "not_selected": "(belum dipilih)", "subfolder_frame": " SUB-FOLDER TUJUAN ", "create_folder": "+ Buat Folder Baru (N)",
        "rename_folder": "✏️ Rename Folder", "delete_folder": "🗑️ Hapus Folder", "pin_folder": "📌 Pin / Unpin Folder",
        "autosort_btn": "⚡ SORTIR OTOMATIS", "preview_frame": " PREVIEW & METADATA ", "initial_info": "Pilih folder sumber untuk memulai",
        "play_video": "▶ PLAY / PAUSE VIDEO (SPASI)", "action_frame": " AKSI FILE ", "move_btn": "➡️ PINDAHKAN FILE\n(Enter / Angka 1-9)",
        "copy_btn": "📋 SALIN FILE\n(Enter / Angka 1-9)", "undo_btn": "↩️ BATAL / UNDO (Ctrl+Z)", "rename_file": "✏️ Rename File (R)",
        "batch_rename_file": "🏷️ Rename Semua (PSORTER_1...)", "delete_file": "🗑️ Hapus File (Delete)", "prev_btn": "◀ PREV (←)",
        "next_btn": "NEXT ▶ (→)", "file_counter": "FILE {} DARI {}", "no_files": "Tidak ada foto/video di folder ini",
        "all_done": "Semua file selesai disortir ke folder PSORTER!", "done": "Selesai", "mode_move": "Mode: PINDAH", "mode_copy": "Mode: SALIN",
        "err_load_img": "Gagal memuat gambar: {}", "err_load_vid": "Gagal memuat video", "warn": "Peringatan", "warn_no_files": "Tidak ada file di folder sumber!",
        "warn_select_dst": "Pilih Folder Tujuan Utama terlebih dahulu!", "warn_select_sub": "Pilih sub-folder tujuan di panel kiri terlebih dahulu!",
        "warn_select_ren_folder": "Pilih folder yang ingin di-rename!", "warn_select_del_folder": "Pilih folder yang ingin dihapus!",
        "dlg_create_folder_title": "Buat Folder PSORTER", "dlg_create_folder_prompt": "Masukkan nama sub-folder baru:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' menjadi:",
        "dlg_delete_folder_title": "Konfirmasi Hapus Folder", "dlg_delete_folder_prompt": "Apakah kamu yakin ingin menghapus folder '{}' beserta seluruh isinya?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "Masukkan nama file baru:",
        "dlg_batch_rename_title": "Batch Rename PSORTER", "dlg_batch_rename_prompt": "Masukkan awalan nama file (default: 'PSORTER'):",
        "dlg_delete_file_title": "Konfirmasi Hapus File", "dlg_delete_file_prompt": "Hapus file '{}'?",
        "dlg_autosort_title": "Auto-Sort Media Otomatis", "dlg_autosort_prompt": "Pilih metode Auto-Sort ke sub-folder:\n\n1 = Berdasarkan Format Ekstensi (JPG, PNG, MP4, dll)\n2 = Berdasarkan Tanggal Pengambilan (YYYY-MM-DD)\n\nMasukkan pilihan (1/2):",
        "err_title": "Gagal", "err_folder_exists": "Folder sudah ada!", "lang_label": "🌐 Language:",
        "stats_remaining": "Sisa: {} file ({:.1f} MB)", "stats_processed": "Diproses: {} file ({:.1f} MB)",
        "btn_donate": "💛 Saweria", "btn_refresh": "🔄 Refresh (F5)", "btn_menu": "🏠 Menu Utama"
    },
    "en": {
        "title": "PSORTERV2 - Pusdokinfo Sorter", "header_app": "PSORTERV2", "header_sub": "PUSDOKINFO MEDIA SORTER",
        "select_src": "📁 Source Folder", "select_dst": "📂 Main Target Folder", "src_label": "Source: ", "dst_label": "Target (PSORTER): ",
        "not_selected": "(not selected)", "subfolder_frame": " TARGET SUB-FOLDERS ", "create_folder": "+ Create New Folder (N)",
        "rename_folder": "✏️ Rename Folder", "delete_folder": "🗑️ Delete Folder", "pin_folder": "📌 Pin / Unpin Folder",
        "autosort_btn": "⚡ AUTO-SORT MEDIA", "preview_frame": " PREVIEW & METADATA ", "initial_info": "Select a source folder to start",
        "play_video": "▶ PLAY / PAUSE VIDEO (SPACE)", "action_frame": " FILE ACTIONS ", "move_btn": "➡️ MOVE FILE\n(Enter / Num 1-9)",
        "copy_btn": "📋 COPY FILE\n(Enter / Num 1-9)", "undo_btn": "↩️ UNDO ACTION (Ctrl+Z)", "rename_file": "✏️ Rename File (R)",
        "batch_rename_file": "🏷️ Rename All (PSORTER_1...)", "delete_file": "🗑️ Delete File (Delete)", "prev_btn": "◀ PREV (←)",
        "next_btn": "NEXT ▶ (→)", "file_counter": "FILE {} OF {}", "no_files": "No photos/videos found in this folder",
        "all_done": "All files sorted successfully to PSORTER folder!", "done": "Done", "mode_move": "Mode: MOVE", "mode_copy": "Mode: COPY",
        "err_load_img": "Failed to load image: {}", "err_load_vid": "Failed to load video", "warn": "Warning", "warn_no_files": "No files found in source folder!",
        "warn_select_dst": "Please select Main Target Folder first!", "warn_select_sub": "Please select target sub-folder on the left panel first!",
        "warn_select_ren_folder": "Please select a folder to rename!", "warn_select_del_folder": "Please select a folder to delete!",
        "dlg_create_folder_title": "Create PSORTER Folder", "dlg_create_folder_prompt": "Enter new sub-folder name:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' to:",
        "dlg_delete_folder_title": "Confirm Delete Folder", "dlg_delete_folder_prompt": "Are you sure you want to delete folder '{}' and all its contents?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "Enter new file name:",
        "dlg_batch_rename_title": "PSORTER Batch Rename", "dlg_batch_rename_prompt": "Enter file name prefix (default: 'PSORTER'):",
        "dlg_delete_file_title": "Confirm Delete File", "dlg_delete_file_prompt": "Delete file '{}'?",
        "dlg_autosort_title": "Auto-Sort Media", "dlg_autosort_prompt": "Select Auto-Sort method into new sub-folders:\n\n1 = By File Extension Format (JPG, PNG, MP4, etc.)\n2 = By Date Created (YYYY-MM-DD)\n\nEnter choice (1/2):",
        "err_title": "Error", "err_folder_exists": "Folder already exists!", "lang_label": "🌐 Language:",
        "stats_remaining": "Left: {} files ({:.1f} MB)", "stats_processed": "Done: {} files ({:.1f} MB)",
        "btn_donate": "💛 Saweria", "btn_refresh": "🔄 Refresh (F5)", "btn_menu": "🏠 Main Menu"
    }
}

class DownloadProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mengunduh Update")
        self.geometry("420x230")
        self.resizable(False, False)
        self.configure(fg_color="#141414")
        self.transient(parent)
        self.grab_set()
        self.is_paused, self.is_cancelled = False, False

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 210
        y = (self.winfo_screenheight() // 2) - 115
        self.geometry(f"420x230+{x}+{y}")

        ctk.CTkLabel(self, text="Mengunduh Pembaruan PSORTERV2...", font=("Arial", 13, "bold"), text_color="white").pack(pady=(20, 5))
        self.progress_bar = ctk.CTkProgressBar(self, width=340, height=16, progress_color=NETFLIX_RED, fg_color="#2B2B2B")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Menghubungkan ke server...", font=("Arial", 11), text_color=TEXT_MUTED)
        self.lbl_status.pack(pady=(0, 15))

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill=tk.X, padx=40)

        self.btn_pause = ctk.CTkButton(btn_box, text="⏸️ Jeda", width=110, fg_color="#2B2B2B", hover_color="#3A3A3A", font=("Arial", 11, "bold"), command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_box, text="❌ Batal", width=110, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B", font=("Arial", 11, "bold"), command=self.cancel_download).pack(side=tk.RIGHT, padx=5)
        self.protocol("WM_DELETE_WINDOW", self.cancel_download)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.configure(text="▶️ Lanjutkan" if self.is_paused else "⏸️ Jeda", fg_color=NETFLIX_RED if self.is_paused else "#2B2B2B", hover_color=NETFLIX_RED_HOVER if self.is_paused else "#3A3A3A")
        if self.is_paused: self.lbl_status.configure(text="Pengunduhan dijeda...")

    def cancel_download(self):
        self.is_cancelled = True
        self.lbl_status.configure(text="Membatalkan pengunduhan...")

    def update_progress(self, downloaded_bytes, total_bytes):
        if self.is_paused or self.is_cancelled: return
        dl_mb = downloaded_bytes / 1048576
        if total_bytes > 0:
            percentage = downloaded_bytes / total_bytes
            self.progress_bar.set(percentage)
            self.lbl_status.configure(text=f"{int(percentage * 100)}% ({dl_mb:.1f} MB / {total_bytes / 1048576:.1f} MB)")
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

        download_url = next((a.get("browser_download_url") for a in data.get("assets", []) if a.get("name", "").lower().endswith(".zip") and "psorter" in a.get("name", "").lower() and not any(k in a.get("name", "").lower() for k in ["audio", "extension"])), None)
        if download_url and root_window:
            root_window.after(0, lambda: _perform_update(download_url, root_window) if messagebox.askyesno("Update Tersedia", f"Versi baru ({latest_version}) sudah tersedia!\n\nIngin mengunduh sekarang?") else None)
    except Exception: pass

def _perform_update(download_url, root_window):
    def run_update_thread():
        dialog = None
        def create_dialog(): nonlocal dialog; dialog = DownloadProgressDialog(root_window)
        root_window.after(0, create_dialog)
        while dialog is None: time.sleep(0.05)

        try:
            temp_zip, extract_folder = "temp_update.zip", "temp_extracted"
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                total_bytes, downloaded = int(response.getheader("Content-Length", 0)), 0
                with open(temp_zip, "wb") as out_file:
                    while not dialog.is_cancelled:
                        while dialog.is_paused and not dialog.is_cancelled: time.sleep(0.1)
                        chunk = response.read(16384)
                        if not chunk or dialog.is_cancelled: break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        root_window.after(0, lambda d=downloaded, t=total_bytes: dialog.update_progress(d, t))

            if dialog.is_cancelled:
                if os.path.exists(temp_zip): os.remove(temp_zip)
                root_window.after(0, dialog.destroy)
                return

            root_window.after(0, lambda: dialog.lbl_status.configure(text="Mengekstrak file update..."))
            with zipfile.ZipFile(temp_zip, "r") as zip_ref: zip_ref.extractall(extract_folder)

            extracted_exe = next((os.path.join(r, f) for r, _, files in os.walk(extract_folder) for f in files if f.lower().endswith(".exe")), None)
            if not extracted_exe:
                root_window.after(0, lambda: messagebox.showerror("Gagal Update", "File .exe tidak ditemukan di archive ZIP!"))
                root_window.after(0, dialog.destroy)
                return

            current_exe = sys.executable if getattr(sys, 'frozen', False) else EXE_NAME
            exe_filename = os.path.basename(current_exe)
            with open("update.bat", "w") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\nmove /y "{extracted_exe}" "{exe_filename}"\nrmdir /s /q "{extract_folder}"\ndel "{temp_zip}"\nstart "" "{exe_filename}"\ndel "%~f0"\n')

            subprocess.Popen(["update.bat"], shell=True)
            sys.exit(0)
        except Exception as e:
            if not dialog.is_cancelled: root_window.after(0, lambda: messagebox.showerror("Gagal Update", f"Terjadi kesalahan: {e}"))
            root_window.after(0, dialog.destroy)

    threading.Thread(target=run_update_thread, daemon=True).start()

class StartupModeDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_select_callback):
        super().__init__(parent)
        self.title("PSORTER - Pilih Mode Performa")
        self.geometry("560x480")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self.on_select_callback = on_select_callback
        self.transient(parent); self.grab_set(); self.center_window()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(25, 15))
        ctk.CTkLabel(header, text="PSORTER", font=("Arial Black", 24, "bold"), text_color=NETFLIX_RED).pack()
        ctk.CTkLabel(header, text="PILIH MODE PERFORMA APLIKASI", font=("Arial", 12, "bold"), text_color="white").pack(pady=(2, 0))
        ctk.CTkLabel(header, text="Pilih mode yang sesuai dengan spesifikasi perangkat dan jumlah media kamu.", font=("Arial", 11), text_color=TEXT_MUTED).pack(pady=(2, 0))

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        modes = [
            {"id": "optimasi", "title": "⚡ OPTIMASI", "subtitle": "Super Ringan", "color": "#2EB872", "badge": "Hemat RAM & CPU", "desc": "• Pemutar video dimatikan\n• Light Multi-thread (2 Threads)\n• Penggunaan RAM minimalis\n• Untuk spek rendah atau diatas 10rb file"},
            {"id": "normal", "title": "⚖️ NORMAL", "subtitle": "Standar & Seimbang", "color": "#0088FF", "badge": "Rekomendasi", "desc": "• Pemutar video & audio aktif\n• Render thumbnail (4 Threads)\n• Caching memori seimbang\n• Untuk penggunaan harian"}
        ]

        for m in modes:
            card = ctk.CTkFrame(container, fg_color=CARD_BG, border_width=2, border_color=CARD_BG_LIGHT, corner_radius=12)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=5)
            ctk.CTkLabel(card, text=m["badge"], font=("Arial", 9, "bold"), text_color="white", fg_color=m["color"], corner_radius=6, height=20).pack(anchor="ne", padx=12, pady=(12, 0))
            ctk.CTkLabel(card, text=m["title"], font=("Arial Black", 14, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(2, 0))
            ctk.CTkLabel(card, text=m["subtitle"], font=("Arial", 10, "bold"), text_color=m["color"]).pack(anchor="w", padx=15, pady=(0, 10))
            ctk.CTkLabel(card, text=m["desc"], font=("Arial", 10), text_color=TEXT_MUTED, justify="left", anchor="nw").pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
            ctk.CTkButton(card, text="PILIH MODE", font=("Arial", 11, "bold"), fg_color=m["color"], hover_color=NETFLIX_RED_HOVER if m["color"] == NETFLIX_RED else m["color"], corner_radius=8, height=36, command=lambda mode_id=m["id"]: self.select(mode_id)).pack(fill=tk.X, padx=12, pady=(0, 12))

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 280
        y = (self.winfo_screenheight() // 2) - 240
        self.geometry(f"560x480+{x}+{y}")

    def select(self, mode):
        self.grab_release(); self.destroy()
        self.on_select_callback(mode)

class MediaSorterApp:
    def __init__(self, root, mode="normal"):
        self.root, self.app_mode, self.current_lang = root, mode, "id"
        self.root.geometry("1240x850")
        self.root.configure(fg_color=BG_DARK)

        self.max_workers = 2 if self.app_mode == "optimasi" else 4
        self.enable_video_player = (self.app_mode != "optimasi")

        self.source_dir = self.target_dir = ""
        self.raw_file_list, self.file_list, self.current_index = [], [], 0

        self.cap, self.is_playing, self.video_job, self.total_frames, self.video_fps, self.is_seeking = None, False, None, 0, 30.0, False
        self.has_vlc, self.vlc_instance, self.vlc_player = HAS_VLC, None, None

        if self.has_vlc:
            try:
                self.vlc_instance = vlc.Instance('--no-video', '--quiet')
                self.vlc_player = self.vlc_instance.media_player_new()
            except Exception: self.has_vlc = False

        self.volume_level, self.is_muted = 0.8, False
        self.view_mode, self.is_copy_mode, self.filter_mode, self.sort_mode = "preview", False, "Semua", "Nama"
        self.undo_stack, self.pinned_folders = [], set()
        self.processed_files_count = self.processed_bytes_count = 0

        self.file_stats_cache, self.pil_thumb_cache, self.photo_img_cache, self.metadata_cache, self.grid_cards = {}, {}, {}, {}, {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

        self.photo_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico', '.svg')
        self.video_exts = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v')

        self.setup_ui()
        self.bind_shortcuts()
        self.update_ui_texts()
        self.update_sys_stats()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        check_for_updates_async(self.root)

    def t(self, key, *args):
        text = TRANSLATIONS[self.current_lang].get(key, key)
        return text.format(*args) if args else text

    def open_donation(self): webbrowser.open("https://saweria.co/Atillaraihan")

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def format_size(self, size_bytes): return size_bytes / 1048576

    def update_sys_stats(self):
        if HAS_PSUTIL:
            try: self.lbl_sys_stats.configure(text=f"💻 CPU: {psutil.cpu_percent()}%  |  💾 RAM: {psutil.virtual_memory().percent}%")
            except Exception: pass
        else: self.lbl_sys_stats.configure(text="psutil tidak terinstall")
        self.root.after(2000, self.update_sys_stats)

    def back_to_menu(self):
        self.stop_video()
        self.executor.shutdown(wait=False)
        self.root.destroy()
        temp_root = ctk.CTk()
        temp_root.withdraw()
        StartupModeDialog(temp_root, lambda m: (temp_root.destroy(), start_app(m)))
        temp_root.mainloop()

    def setup_ui(self):
        brand_frame = ctk.CTkFrame(self.root, fg_color="#000000", corner_radius=0, height=60)
        brand_frame.pack(fill=tk.X, side=tk.TOP)

        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_box.pack(side=tk.LEFT, padx=20, pady=10)
        self.lbl_brand = ctk.CTkLabel(logo_box, text="PSORTER", font=("Arial Black", 22, "bold"), text_color=NETFLIX_RED)
        self.lbl_brand.pack(side=tk.LEFT)
        self.lbl_sub = ctk.CTkLabel(logo_box, font=("Arial", 10, "bold"), text_color=TEXT_MUTED)
        self.lbl_sub.pack(side=tk.LEFT, pady=(5, 0))

        right_header_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        right_header_box.pack(side=tk.RIGHT, padx=20)

        self.btn_menu = ctk.CTkButton(right_header_box, text="🏠 Menu Utama", command=self.back_to_menu, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, text_color="white", font=("Arial", 11, "bold"), width=110)
        self.btn_menu.pack(side=tk.RIGHT, padx=5)
        self.btn_refresh = ctk.CTkButton(right_header_box, text="🔄 Refresh", command=self.refresh_data, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A", text_color="white", font=("Arial", 11, "bold"), width=100)
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)
        self.btn_donate = ctk.CTkButton(right_header_box, text="💛 Saweria", command=self.open_donation, fg_color=SAWERIA_YELLOW, hover_color=SAWERIA_HOVER, text_color="#000000", font=("Arial", 11, "bold"), width=110)
        self.btn_donate.pack(side=tk.RIGHT, padx=5)

        self.lbl_lang = ctk.CTkLabel(right_header_box, text_color=TEXT_MUTED, font=("Arial", 11, "bold"))
        self.lbl_lang.pack(side=tk.LEFT, padx=5)
        self.lang_menu = ctk.CTkOptionMenu(right_header_box, values=["Bahasa Indonesia", "English"], command=self.on_language_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, button_hover_color=NETFLIX_RED_HOVER, dropdown_fg_color=CARD_BG_LIGHT, width=130)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        footer_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", corner_radius=0, height=28)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ctk.CTkLabel(footer_frame, text="Made by Google Gemini & Atilla", font=("Arial", 10, "italic"), text_color="#777777").pack(side=tk.LEFT, padx=15, pady=4)
        self.lbl_sys_stats = ctk.CTkLabel(footer_frame, text="💻 CPU: --%  |  💾 RAM: --%", font=("Arial", 10, "bold"), text_color=TEXT_MUTED)
        self.lbl_sys_stats.pack(side=tk.RIGHT, padx=15, pady=4)

        top_frame = ctk.CTkFrame(self.root, fg_color=CARD_BG, corner_radius=10)
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        self.btn_src = ctk.CTkButton(top_frame, command=self.select_source_dir, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A", font=("Arial", 11, "bold"))
        self.btn_src.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_src = ctk.CTkLabel(top_frame, text_color="white", anchor="w")
        self.lbl_src.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_dst = ctk.CTkButton(top_frame, command=self.select_target_dir, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 11, "bold"))
        self.btn_dst.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_dst = ctk.CTkLabel(top_frame, text_color="white", anchor="w")
        self.lbl_dst.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.mode_switch = ctk.CTkSwitch(top_frame, text="Mode: PINDAH", command=self.toggle_mode_switch, progress_color=NETFLIX_RED, button_color="white", font=("Arial", 11, "bold"))
        self.mode_switch.pack(side=tk.RIGHT, padx=15)

        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.left_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=12, width=270)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6), pady=5)
        self.left_frame.pack_propagate(False)

        self.lbl_left_title = ctk.CTkLabel(self.left_frame, font=("Arial", 12, "bold"), text_color=TEXT_MUTED)
        self.lbl_left_title.pack(pady=(12, 5))

        list_container = ctk.CTkFrame(self.left_frame, fg_color="#121212", corner_radius=8)
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        self.folder_listbox = tk.Listbox(list_container, bg="#121212", fg="white", selectbackground=NETFLIX_RED, selectforeground="white", bd=0, highlightthickness=0, font=("Arial", 10))
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        btn_folder_box = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_folder_box.pack(fill=tk.X, padx=8, pady=5)

        self.btn_autosort = ctk.CTkButton(btn_folder_box, text="⚡ AUTO-SORT MEDIA", command=self.auto_sort_files, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 11, "bold"))
        self.btn_autosort.pack(fill=tk.X, pady=2)
        self.btn_pin_folder = ctk.CTkButton(btn_folder_box, text="📌 Pin / Unpin Folder", command=self.toggle_pin_folder, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_pin_folder.pack(fill=tk.X, pady=2)
        self.btn_create_folder = ctk.CTkButton(btn_folder_box, command=self.create_folder, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_create_folder.pack(fill=tk.X, pady=2)
        self.btn_rename_folder = ctk.CTkButton(btn_folder_box, command=self.rename_folder, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_rename_folder.pack(fill=tk.X, pady=2)
        self.btn_delete_folder = ctk.CTkButton(btn_folder_box, command=self.delete_folder, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")
        self.btn_delete_folder.pack(fill=tk.X, pady=2)

        self.center_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=12)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=5)

        top_center_bar = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        top_center_bar.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.view_segmented_btn = ctk.CTkSegmentedButton(top_center_bar, values=["🖼️ Mode Preview", "📁 Mode Folder (Grid)"], command=self.on_view_mode_change, selected_color=NETFLIX_RED, selected_hover_color=NETFLIX_RED_HOVER, unselected_color=CARD_BG_LIGHT, unselected_hover_color="#3A3A3A", font=("Arial", 11, "bold"))
        self.view_segmented_btn.set("🖼️ Mode Preview")
        self.view_segmented_btn.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(top_center_bar, text="Urutan:", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(side=tk.RIGHT, padx=(5, 5))
        self.sort_menu = ctk.CTkOptionMenu(top_center_bar, values=["Nama", "Tanggal", "Ukuran"], command=self.on_sort_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, width=90)
        self.sort_menu.pack(side=tk.RIGHT, padx=5)

        ctk.CTkLabel(top_center_bar, text="Filter:", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(side=tk.RIGHT, padx=(10, 5))
        self.filter_menu = ctk.CTkOptionMenu(top_center_bar, values=["Semua", "Foto", "Video"], command=self.on_filter_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, width=85)
        self.filter_menu.pack(side=tk.RIGHT, padx=5)

        self.lbl_file_info = ctk.CTkLabel(self.center_frame, font=("Arial", 12, "bold"), text_color="white")
        self.lbl_file_info.pack(pady=4)

        self.view_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        self.preview_subframe = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.preview_subframe.pack(fill=tk.BOTH, expand=True)

        preview_bg = ctk.CTkFrame(self.preview_subframe, fg_color="#000000", corner_radius=8)
        preview_bg.pack(fill=tk.BOTH, expand=True, pady=2)
        self.preview_label = tk.Label(preview_bg, bg="#000000")
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        self.lbl_metadata = ctk.CTkLabel(self.preview_subframe, text="Dimensi: - | Ukuran: - | Tanggal: -", font=("Arial", 10, "bold"), text_color=TEXT_MUTED)
        self.lbl_metadata.pack(pady=2)

        timeline_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent")
        timeline_bar.pack(fill=tk.X, pady=(2, 0))

        self.lbl_time_curr = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=NETFLIX_RED, width=45)
        self.lbl_time_curr.pack(side=tk.LEFT, padx=2)
        self.timeline_slider = ctk.CTkSlider(timeline_bar, from_=0, to=100, number_of_steps=100, fg_color=CARD_BG_LIGHT, progress_color=NETFLIX_RED, button_color=NETFLIX_RED, button_hover_color=NETFLIX_RED_HOVER, command=self.on_slider_seek)
        self.timeline_slider.set(0); self.timeline_slider.configure(state="disabled")
        self.timeline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.lbl_time_total = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=TEXT_MUTED, width=45)
        self.lbl_time_total.pack(side=tk.RIGHT, padx=2)

        controls_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent")
        controls_bar.pack(fill=tk.X, pady=6)

        self.btn_play = ctk.CTkButton(controls_bar, command=self.toggle_video, state="disabled", fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 11, "bold"), height=34, width=200)
        self.btn_play.pack(side=tk.LEFT, expand=True)

        vol_box = ctk.CTkFrame(controls_bar, fg_color="transparent")
        vol_box.pack(side=tk.RIGHT)

        self.btn_mute = ctk.CTkButton(vol_box, text="🔊", width=34, height=34, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A", command=self.toggle_mute)
        self.btn_mute.pack(side=tk.LEFT, padx=(0, 5))
        self.volume_slider = ctk.CTkSlider(vol_box, from_=0, to=1, number_of_steps=100, width=100, fg_color=CARD_BG_LIGHT, progress_color=NETFLIX_RED, button_color=NETFLIX_RED, button_hover_color=NETFLIX_RED_HOVER, command=self.on_volume_change)
        self.volume_slider.set(0.8); self.volume_slider.pack(side=tk.LEFT, padx=5)
        self.lbl_volume_val = ctk.CTkLabel(vol_box, text="80%", font=("Arial", 11, "bold"), text_color=TEXT_MUTED, width=35)
        self.lbl_volume_val.pack(side=tk.LEFT, padx=(2, 0))

        self.folder_grid_subframe = ctk.CTkScrollableFrame(self.view_container, fg_color="#121212", corner_radius=8)

        self.right_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=12, width=230)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0), pady=5)
        self.right_frame.pack_propagate(False)

        self.lbl_right_title = ctk.CTkLabel(self.right_frame, font=("Arial", 12, "bold"), text_color=TEXT_MUTED)
        self.lbl_right_title.pack(pady=(12, 5))

        self.btn_move = ctk.CTkButton(self.right_frame, command=self.move_file, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 12, "bold"), height=48)
        self.btn_move.pack(fill=tk.X, padx=10, pady=6)
        self.btn_undo = ctk.CTkButton(self.right_frame, command=self.undo_last_action, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A", font=("Arial", 10, "bold"))
        self.btn_undo.pack(fill=tk.X, padx=10, pady=4)
        self.btn_rename_file = ctk.CTkButton(self.right_frame, command=self.rename_file, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_rename_file.pack(fill=tk.X, padx=10, pady=4)
        self.btn_batch_rename = ctk.CTkButton(self.right_frame, command=self.batch_rename_files, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_batch_rename.pack(fill=tk.X, padx=10, pady=4)
        self.btn_delete_file = ctk.CTkButton(self.right_frame, command=self.delete_file, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")
        self.btn_delete_file.pack(fill=tk.X, padx=10, pady=4)

        nav_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        self.btn_prev = ctk.CTkButton(nav_frame, command=self.prev_file, width=90, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_prev.pack(side=tk.LEFT)
        self.btn_next = ctk.CTkButton(nav_frame, command=self.next_file, width=90, fg_color=CARD_BG_LIGHT, hover_color="#3A3A3A")
        self.btn_next.pack(side=tk.RIGHT)

        self.lbl_counter = ctk.CTkLabel(self.right_frame, font=("Arial", 11, "bold"), text_color=TEXT_MUTED)
        self.lbl_counter.pack(pady=5)

        stats_box = ctk.CTkFrame(self.right_frame, fg_color="#121212", corner_radius=8)
        stats_box.pack(fill=tk.X, padx=10, pady=(10, 10))
        ctk.CTkLabel(stats_box, text="📊 STATISTIK SORTER", font=("Arial", 10, "bold"), text_color=TEXT_MUTED).pack(pady=(6, 2))
        self.lbl_stat_remaining = ctk.CTkLabel(stats_box, text="Sisa: 0 file (0.0 MB)", font=("Arial", 10), text_color="white")
        self.lbl_stat_remaining.pack()
        self.lbl_stat_processed = ctk.CTkLabel(stats_box, text="Diproses: 0 file (0.0 MB)", font=("Arial", 10), text_color=NETFLIX_RED)
        self.lbl_stat_processed.pack(pady=(0, 6))

    def refresh_data(self):
        if self.source_dir: self.scan_files()
        if self.target_dir: self.refresh_folder_list()

    def on_view_mode_change(self, choice):
        self.stop_video()
        if "Folder" in choice or "Grid" in choice:
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
            ctk.CTkLabel(self.folder_grid_subframe, text=self.t("no_files"), font=("Arial", 13), text_color="white").pack(pady=50)
            return

        for idx, filename in enumerate(self.file_list):
            row, col = idx // 4, idx % 4
            filepath = os.path.join(self.source_dir, filename) if not os.path.isabs(filename) else filename
            is_selected = (idx == self.current_index)

            card = ctk.CTkFrame(self.folder_grid_subframe, fg_color=CARD_BG_LIGHT, border_width=2 if is_selected else 0, border_color=NETFLIX_RED if is_selected else CARD_BG_LIGHT, corner_radius=8, width=130, height=130)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.pack_propagate(False)
            self.grid_cards[idx] = card

            thumb_lbl = tk.Label(card, bg=CARD_BG_LIGHT, text="...")
            thumb_lbl.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 0))

            display_name = os.path.basename(filename)
            lbl_name = ctk.CTkLabel(card, text=display_name if len(display_name) <= 15 else display_name[:12] + "...", font=("Arial", 9, "bold"), text_color="white")
            lbl_name.pack(pady=(2, 4))

            for widget in (card, thumb_lbl, lbl_name):
                widget.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))

            if filepath in self.photo_img_cache:
                thumb_lbl.config(image=self.photo_img_cache[filepath], text="")
            else:
                self.executor.submit(self._async_load_thumbnail, filepath, filename, thumb_lbl)

    def _async_load_thumbnail(self, filepath, filename, label_widget):
        try:
            if filepath not in self.pil_thumb_cache:
                pil_img = self._generate_pil_thumb(filepath, filename)
                if pil_img: self.pil_thumb_cache[filepath] = pil_img
            if filepath in self.pil_thumb_cache:
                self.root.after(0, lambda: self._apply_thumb_to_widget(filepath, label_widget))
        except Exception: pass

    def _apply_thumb_to_widget(self, filepath, label_widget):
        if not label_widget.winfo_exists(): return
        if filepath not in self.photo_img_cache:
            self.photo_img_cache[filepath] = ImageTk.PhotoImage(self.pil_thumb_cache[filepath])
        label_widget.config(image=self.photo_img_cache[filepath], text="")

    def _generate_pil_thumb(self, filepath, filename):
        try:
            fn_lower = filename.lower()
            if fn_lower.endswith(self.photo_exts):
                with Image.open(filepath) as img:
                    img.thumbnail((110, 85), Image.Resampling.NEAREST)
                    return img.copy()
            elif fn_lower.endswith(self.video_exts):
                temp_cap = cv2.VideoCapture(filepath)
                ret, frame = temp_cap.read()
                temp_cap.release()
                if ret:
                    h, w = frame.shape[:2]
                    resized = cv2.resize(frame, (120, int(h * (120 / float(w)))), interpolation=cv2.INTER_NEAREST)
                    return Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        except Exception: pass
        return None

    def select_file_from_grid(self, index):
        old_index = self.current_index
        self.current_index = index
        if old_index in self.grid_cards and self.grid_cards[old_index].winfo_exists():
            self.grid_cards[old_index].configure(border_width=0, border_color=CARD_BG_LIGHT)
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

    def apply_filter_and_sort(self):
        if not self.source_dir or not self.raw_file_list:
            self.file_list, self.current_index = [], 0
            if self.view_mode == "preview":
                self.preview_label.config(image="", text=self.t("no_files"), fg="white")
                self.lbl_file_info.configure(text="-")
                self.lbl_metadata.configure(text="Dimensi: - | Ukuran: - | Tanggal: -")
                self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
            return

        filtered = [f for f in self.raw_file_list if (self.filter_mode in ("Foto", "Photo") and f.lower().endswith(self.photo_exts)) or (self.filter_mode in ("Video", "Videos") and f.lower().endswith(self.video_exts)) or self.filter_mode in ("Semua", "All")]

        if self.sort_mode in ("Nama", "Name"):
            filtered.sort(key=lambda x: os.path.basename(x).lower())
        elif self.sort_mode in ("Tanggal", "Date"):
            filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[1])
        elif self.sort_mode in ("Ukuran", "Size"):
            filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[0], reverse=True)

        self.file_list, self.current_index = filtered, 0
        if self.view_mode == "folder":
            self.populate_folder_grid()
        elif self.file_list:
            self.load_current_media()
        else:
            self.preview_label.config(image="", text=self.t("no_files"), fg="white")
            self.lbl_file_info.configure(text="-")
            self.lbl_metadata.configure(text="Dimensi: - | Ukuran: - | Tanggal: -")
            self.lbl_counter.configure(text=self.t("file_counter", 0, 0))

        self.update_statistics()

    def update_statistics(self):
        if not self.source_dir: return
        rem_bytes = sum(self.file_stats_cache.get(f, (0, 0))[0] for f in self.file_list)
        self.lbl_stat_remaining.configure(text=self.t("stats_remaining", len(self.file_list), self.format_size(rem_bytes)))
        self.lbl_stat_processed.configure(text=self.t("stats_processed", self.processed_files_count, self.format_size(self.processed_bytes_count)))

    def toggle_pin_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected:
            messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
            return
        raw = self.folder_listbox.get(selected[0])
        fname = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        self.pinned_folders.remove(fname) if fname in self.pinned_folders else self.pinned_folders.add(fname)
        self.refresh_folder_list()

    def auto_sort_files(self):
        if not self.source_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))

        choice = simpledialog.askstring(self.t("dlg_autosort_title"), self.t("dlg_autosort_prompt"))
        if not choice or choice.strip() not in ("1", "2"): return

        choice = choice.strip()
        self.stop_video()
        sorted_count = 0

        for rel_or_abs in list(self.file_list):
            src_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
            filename = os.path.basename(src_path)
            if not os.path.exists(src_path): continue

            sub_name = os.path.splitext(filename)[1].replace(".", "").upper() or "OTHERS" if choice == "1" else datetime.datetime.fromtimestamp(self.file_stats_cache.get(rel_or_abs, (0, 0))[1]).strftime('%Y-%m-%d')
            dest_folder = os.path.join(self.target_dir, sub_name)
            os.makedirs(dest_folder, exist_ok=True)

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

        self.refresh_folder_list()
        self.scan_files()
        messagebox.showinfo(self.t("done"), f"Auto-Sort Selesai! {sorted_count} file berhasil diproses ke folder PSORTER.")

    def undo_last_action(self):
        if not self.undo_stack: return
        act = self.undo_stack.pop()
        self.stop_video()
        try:
            if act['action'] == 'move' and os.path.exists(act['dst']): shutil.move(act['dst'], act['src'])
            elif act['action'] == 'copy' and os.path.exists(act['dst']): os.remove(act['dst'])
            if self.processed_files_count > 0:
                self.processed_files_count -= 1
                self.processed_bytes_count -= act['size']
            self.scan_files()
        except Exception as e: messagebox.showerror(self.t("err_title"), f"Gagal undo: {e}")

    def on_volume_change(self, value):
        self.volume_level = float(value)
        if self.has_vlc and self.vlc_player: self.vlc_player.audio_set_volume(int(self.volume_level * 100) if not self.is_muted else 0)
        elif HAS_PYGAME and not self.is_muted: pygame.mixer.music.set_volume(self.volume_level)
        self.lbl_volume_val.configure(text=f"{int(self.volume_level * 100)}%")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.btn_mute.configure(text="🔇" if self.is_muted else "🔊")
        if self.is_muted:
            if self.has_vlc and self.vlc_player: self.vlc_player.audio_set_volume(0)
            elif HAS_PYGAME: pygame.mixer.music.set_volume(0.0)
        else: self.on_volume_change(self.volume_level)

    def on_language_change(self, choice):
        self.current_lang = "id" if choice == "Bahasa Indonesia" else "en"
        self.update_ui_texts()

    def update_ui_texts(self):
        self.root.title(self.t("title"))
        self.lbl_brand.configure(text=self.t("header_app"))
        self.lbl_sub.configure(text=f"  PUSDOKINFO MEDIA SORTER [{self.app_mode.upper()} MODE]")
        self.btn_src.configure(text=self.t("select_src"))
        self.btn_dst.configure(text=self.t("select_dst"))
        self.btn_menu.configure(text=self.t("btn_menu"))
        self.btn_donate.configure(text=self.t("btn_donate"))
        self.btn_refresh.configure(text=self.t("btn_refresh"))
        self.lbl_lang.configure(text=self.t("lang_label"))
        self.lbl_src.configure(text=self.t("src_label") + (self.source_dir or self.t("not_selected")))
        self.lbl_dst.configure(text=self.t("dst_label") + (self.target_dir or self.t("not_selected")))
        self.lbl_left_title.configure(text=self.t("subfolder_frame"))
        self.btn_autosort.configure(text=self.t("autosort_btn"))
        self.btn_pin_folder.configure(text=self.t("pin_folder"))
        self.btn_create_folder.configure(text=self.t("create_folder"))
        self.btn_rename_folder.configure(text=self.t("rename_folder"))
        self.btn_delete_folder.configure(text=self.t("delete_folder"))
        self.btn_play.configure(text=self.t("play_video"))
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
        shortcuts = {
            "<Right>": lambda e: self.next_file(), "<Left>": lambda e: self.prev_file(),
            "<space>": lambda e: self.toggle_video(), "<F5>": lambda e: self.refresh_data(),
            "<Return>": lambda e: self.move_file(), "<Delete>": lambda e: self.delete_file(),
            "r": lambda e: self.rename_file(), "R": lambda e: self.rename_file(),
            "n": lambda e: self.create_folder(), "N": lambda e: self.create_folder(),
            "<Control-z>": lambda e: self.undo_last_action(), "<Control-Z>": lambda e: self.undo_last_action()
        }
        for k, v in shortcuts.items(): self.root.bind(k, v)
        for i in range(1, 10): self.root.bind(str(i), lambda e, idx=i-1: self.quick_move_by_index(idx))

    def select_source_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_src"))
        if folder:
            self.source_dir = os.path.normpath(folder)
            self.lbl_src.configure(text=self.t("src_label") + self.source_dir)
            self.pil_thumb_cache.clear(); self.photo_img_cache.clear(); self.metadata_cache.clear(); self.file_stats_cache.clear()
            self.scan_files()

    def select_target_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_dst"))
        if folder:
            psorter_folder = os.path.normpath(os.path.join(folder, "PSORTER"))
            os.makedirs(psorter_folder, exist_ok=True)
            self.target_dir = psorter_folder
            self.lbl_dst.configure(text=self.t("dst_label") + psorter_folder)
            self.refresh_folder_list()

    def scan_files(self):
        self.stop_video()
        if not self.source_dir: return
        self.raw_file_list = [f for f in sorted(os.listdir(self.source_dir)) if f.lower().endswith(self.photo_exts + self.video_exts)]
        for f in self.raw_file_list:
            if f not in self.file_stats_cache:
                p = os.path.join(self.source_dir, f) if not os.path.isabs(f) else f
                try: st = os.stat(p); self.file_stats_cache[f] = (st.st_size, st.st_mtime)
                except Exception: self.file_stats_cache[f] = (0, 0)
        self.apply_filter_and_sort()

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
        self.stop_video()
        if not self.file_list or self.current_index >= len(self.file_list):
            self.preview_label.config(image="", text=self.t("all_done"), fg="white")
            self.lbl_file_info.configure(text=self.t("done"))
            self.lbl_metadata.configure(text="Dimensi: - | Ukuran: - | Tanggal: -")
            self.lbl_counter.configure(text=self.t("file_counter", len(self.file_list), len(self.file_list)))
            self.timeline_slider.configure(state="disabled")
            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text="00:00")
            return

        rel_or_abs = self.file_list[self.current_index]
        filepath = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
        filename = os.path.basename(filepath)

        self.lbl_file_info.configure(text=rel_or_abs)
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))
        self.update_metadata_panel(filepath, filename, rel_or_abs)

        fn_lower = filename.lower()
        if fn_lower.endswith(self.photo_exts):
            self.btn_play.configure(state="disabled")
            self.timeline_slider.configure(state="disabled")
            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text="00:00")
            self.display_image(filepath)
        elif fn_lower.endswith(self.video_exts):
            if self.enable_video_player:
                self.btn_play.configure(state="normal")
                self.prepare_video(filepath)
            else:
                self.btn_play.configure(state="disabled")
                self.timeline_slider.configure(state="disabled")
                self.preview_label.config(image="", text="🎥 PREVIEW VIDEO NONAKTIF (MODE OPTIMASI)", fg="yellow")

    def update_metadata_panel(self, filepath, filename, key_file):
        if filepath in self.metadata_cache:
            self.lbl_metadata.configure(text=self.metadata_cache[filepath])
            return
        if not os.path.exists(filepath): return

        size_bytes, mtime_val = self.file_stats_cache.get(key_file, (os.path.getsize(filepath), os.path.getmtime(filepath)))
        mtime = datetime.datetime.fromtimestamp(mtime_val).strftime('%Y-%m-%d %H:%M')
        dim_str = "Dimensi: -"

        fn_lower = filename.lower()
        if fn_lower.endswith(self.photo_exts):
            try:
                with Image.open(filepath) as img: dim_str = f"Dimensi: {img.width}x{img.height}"
            except Exception: pass
        elif fn_lower.endswith(self.video_exts) and self.enable_video_player:
            try:
                temp_cap = cv2.VideoCapture(filepath)
                w, h, fps = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(temp_cap.get(cv2.CAP_PROP_FPS))
                dim_str = f"Dimensi: {w}x{h} ({fps}fps)"
                temp_cap.release()
            except Exception: pass

        meta_text = f"{dim_str} | Ukuran: {size_bytes / 1048576:.2f} MB | Tanggal: {mtime}"
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
            self.preview_label.config(image="", text=self.t("err_load_img", e), fg="red")

    def prepare_video(self, filepath):
        if not self.enable_video_player: return
        self.cap = cv2.VideoCapture(filepath)
        if self.cap.isOpened():
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = max(30.0, self.cap.get(cv2.CAP_PROP_FPS))

            if self.total_frames > 1:
                self.timeline_slider.configure(state="normal", from_=0, to=self.total_frames - 1, number_of_steps=self.total_frames)
            else:
                self.timeline_slider.configure(state="disabled")

            self.is_seeking = True; self.timeline_slider.set(0); self.is_seeking = False
            self.lbl_time_curr.configure(text="00:00")
            self.lbl_time_total.configure(text=self.format_time(self.total_frames / self.video_fps))

            if self.has_vlc and self.vlc_instance:
                try:
                    self.vlc_player.set_media(self.vlc_instance.media_new(filepath))
                    self.on_volume_change(self.volume_level)
                except Exception: pass

            ret, frame = self.cap.read()
            if ret: self.show_frame(frame)
            else: self.preview_label.config(image="", text=self.t("err_load_vid"), fg="red")

    def show_frame(self, frame):
        h, w = frame.shape[:2]
        scale = min(640 / float(w), 420 / float(h))
        if scale < 1.0:
            frame = cv2.resize(frame, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_NEAREST)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.preview_label.config(image=img_tk, text="")
        self.preview_label.image = img_tk

    def toggle_video(self):
        if not self.enable_video_player or not self.cap or not self.cap.isOpened(): return
        if self.is_playing:
            self.is_playing = False
            if self.video_job: self.root.after_cancel(self.video_job)
            if self.has_vlc and self.vlc_player: self.vlc_player.pause()
        else:
            self.is_playing = True
            if self.has_vlc and self.vlc_player: self.vlc_player.play()
            self.play_video_loop()

    def play_video_loop(self):
        if self.is_playing and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                curr_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.is_seeking = True; self.timeline_slider.set(curr_frame); self.is_seeking = False
                self.lbl_time_curr.configure(text=self.format_time(curr_frame / self.video_fps))
                self.show_frame(frame)
                self.video_job = self.root.after(max(15, int(1000 / self.video_fps)), self.play_video_loop)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                if self.has_vlc and self.vlc_player: self.vlc_player.set_time(0)
                self.video_job = self.root.after(33, self.play_video_loop)

    def on_slider_seek(self, value):
        if not self.enable_video_player or self.is_seeking or not self.cap or not self.cap.isOpened(): return
        target_frame = int(value)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = self.cap.read()
        if ret:
            curr_sec = target_frame / self.video_fps
            self.lbl_time_curr.configure(text=self.format_time(curr_sec))
            self.show_frame(frame)
            if self.has_vlc and self.vlc_player: self.vlc_player.set_time(int(curr_sec * 1000))

    def stop_video(self):
        self.is_playing = False
        if self.video_job: self.root.after_cancel(self.video_job); self.video_job = None
        if self.cap: self.cap.release(); self.cap = None
        if self.has_vlc and self.vlc_player: self.vlc_player.stop()

    def create_folder(self):
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))
        name = simpledialog.askstring(self.t("dlg_create_folder_title"), self.t("dlg_create_folder_prompt"))
        if name:
            path = os.path.join(self.target_dir, name.strip())
            if not os.path.exists(path): os.makedirs(path); self.refresh_folder_list()
            else: messagebox.showerror(self.t("err_title"), self.t("err_folder_exists"))

    def rename_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: return messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
        raw = self.folder_listbox.get(selected[0])
        old_name = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        new_name = simpledialog.askstring(self.t("dlg_rename_folder_title"), self.t("dlg_rename_folder_prompt", old_name), initialvalue=old_name)
        if new_name and new_name.strip() != old_name:
            os.rename(os.path.join(self.target_dir, old_name), os.path.join(self.target_dir, new_name.strip()))
            if old_name in self.pinned_folders:
                self.pinned_folders.remove(old_name); self.pinned_folders.add(new_name.strip())
            self.refresh_folder_list()

    def delete_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: return messagebox.showwarning(self.t("warn"), self.t("warn_select_del_folder"))
        raw = self.folder_listbox.get(selected[0])
        fname = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        if messagebox.askyesno(self.t("dlg_delete_folder_title"), self.t("dlg_delete_folder_prompt", fname)):
            shutil.rmtree(os.path.join(self.target_dir, fname))
            if fname in self.pinned_folders: self.pinned_folders.remove(fname)
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

        raw = self.folder_listbox.get(selected[0])
        target_folder = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        dest_dir = os.path.join(self.target_dir, target_folder)

        self.stop_video()
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
            self.raw_file_list.remove(rel_or_abs)

        self.processed_files_count += 1
        self.processed_bytes_count += file_size
        self.apply_filter_and_sort()

    def rename_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        rel_or_abs = self.file_list[self.current_index]
        old_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
        old_filename = os.path.basename(old_path)
        self.stop_video()

        new_filename = simpledialog.askstring(self.t("dlg_rename_file_title"), self.t("dlg_rename_file_prompt"), initialvalue=old_filename)
        if new_filename and new_filename.strip() != old_filename:
            new_path = os.path.join(os.path.dirname(old_path), new_filename.strip())
            os.rename(old_path, new_path)
            self.raw_file_list[self.raw_file_list.index(rel_or_abs)] = os.path.relpath(new_path, self.source_dir)

        self.apply_filter_and_sort()

    def batch_rename_files(self):
        if not self.file_list: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        self.stop_video()

        prefix = simpledialog.askstring(self.t("dlg_batch_rename_title"), self.t("dlg_batch_rename_prompt"), initialvalue="PSORTER")
        if not prefix or not prefix.strip(): return

        prefix, temp_file_map = prefix.strip(), []
        for i, rel_or_abs in enumerate(self.file_list):
            old_path = os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs
            old_filename = os.path.basename(old_path)
            parent_dir = os.path.dirname(old_path)
            temp_path = os.path.join(parent_dir, f"__temp_psorter_{i}_{old_filename}")
            try:
                os.rename(old_path, temp_path)
                temp_file_map.append((temp_path, parent_dir, os.path.splitext(old_filename)[1], rel_or_abs))
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
        if messagebox.askyesno(self.t("dlg_delete_file_title"), self.t("dlg_delete_file_prompt", os.path.basename(rel_or_abs))):
            self.stop_video()
            os.remove(os.path.join(self.source_dir, rel_or_abs) if not os.path.isabs(rel_or_abs) else rel_or_abs)
            self.raw_file_list.remove(rel_or_abs)
            self.apply_filter_and_sort()

    def next_file(self):
        if self.current_index < len(self.file_list) - 1:
            self.current_index += 1
            self.load_current_media() if self.view_mode == "preview" else self.select_file_from_grid(self.current_index)

    def prev_file(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_media() if self.view_mode == "preview" else self.select_file_from_grid(self.current_index)

    def on_closing(self):
        self.stop_video()
        self.executor.shutdown(wait=False)
        self.root.destroy()

def start_app(selected_mode):
    root = ctk.CTk()
    MediaSorterApp(root, mode=selected_mode)
    root.mainloop()

if __name__ == "__main__":
    temp_root = ctk.CTk()
    temp_root.withdraw()
    StartupModeDialog(temp_root, lambda m: (temp_root.destroy(), start_app(m)))
    temp_root.mainloop()