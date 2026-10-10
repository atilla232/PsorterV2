import os, sys, shutil, datetime, concurrent.futures, time, webbrowser, json, subprocess, threading, urllib.request, zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    os.environ['PYTHON_VLC_MODULE_PATH'] = base_dir
    os.environ['PYTHON_VLC_LIB_PATH'] = os.path.join(base_dir, 'libvlc.dll')

HAS_VLC, HAS_PYGAME = False, False
try:
    import vlc; HAS_VLC = True
except Exception:
    try:
        import pygame; pygame.mixer.init(); HAS_PYGAME = True
    except Exception: pass

CURRENT_VERSION, GITHUB_REPO, EXE_NAME = "v2.0.0", "atilla232/PsorterV2", "PsorterV2Audio.exe"
ctk.set_appearance_mode("Dark"); ctk.set_default_color_theme("dark-blue")

NETFLIX_RED, NETFLIX_RED_HOVER, CYAN_ACCENT = "#E50914", "#B81D24", "#00D2FF"
BG_DARK, CARD_BG, CARD_BG_LIGHT, TEXT_MUTED = "#141414", "#1F1F1F", "#2B2B2B", "#AAAAAA"
SAWERIA_YELLOW, SAWERIA_HOVER = "#E5C07B", "#D19A66"

AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus', '.aiff', '.alac', '.amr', '.mid')
LOSSLESS_EXTS = ('.flac', '.wav', '.aiff', '.alac')

TRANSLATIONS = {
    "id": {
        "title": "PSORTERV2 Audio", "header_app": "PSORTERV2 AUDIO", "header_sub": "PLAY & SORT ALL AUDIO FORMATS",
        "select_src": "📁 Folder Sumber", "select_dst": "📂 Folder Tujuan", "src_label": "Sumber: ", "dst_label": "Tujuan: ",
        "not_selected": "(belum dipilih)", "subfolder_frame": " SUB-FOLDER TUJUAN ", "create_folder": "+ Buat Folder (N)",
        "rename_folder": "✏️ Rename Folder", "delete_folder": "🗑️ Hapus Folder", "pin_folder": "📌 Pin / Unpin",
        "autosort_btn": "⚡ SORTIR OTOMATIS", "initial_info": "Pilih folder sumber audio untuk memulai", "play_audio": "▶ PLAY / PAUSE (SPASI)",
        "action_frame": " AKSI FILE ", "move_btn": "➡️ PINDAHKAN FILE\n(Enter / 1-9)", "copy_btn": "📋 SALIN FILE\n(Enter / 1-9)",
        "undo_btn": "↩️ BATAL / UNDO (Ctrl+Z)", "rename_file": "✏️ Rename File (R)", "batch_rename_file": "🏷️ Rename Semua",
        "delete_file": "🗑️ Hapus File (Del)", "prev_btn": "◀ PREV (←)", "next_btn": "NEXT ▶ (→)", "file_counter": "TRACK {} DARI {}",
        "no_files": "Tidak ada file audio", "all_done": "Selesai disortir!", "done": "Selesai", "mode_move": "Mode: PINDAH",
        "mode_copy": "Mode: SALIN", "warn": "Peringatan", "warn_no_files": "Tidak ada file audio!", "warn_select_dst": "Pilih Folder Tujuan!",
        "warn_select_sub": "Pilih sub-folder tujuan!", "warn_select_ren_folder": "Pilih folder!", "warn_select_del_folder": "Pilih folder!",
        "dlg_create_folder_title": "Buat Folder", "dlg_create_folder_prompt": "Nama sub-folder baru:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' menjadi:",
        "dlg_delete_folder_title": "Hapus Folder", "dlg_delete_folder_prompt": "Hapus folder '{}'?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "Nama file baru:",
        "dlg_batch_rename_title": "Batch Rename", "dlg_batch_rename_prompt": "Awalan nama file (default: 'AUDIO'):",
        "dlg_delete_file_title": "Hapus Audio", "dlg_delete_file_prompt": "Hapus file '{}'?",
        "dlg_autosort_title": "Auto-Sort", "dlg_autosort_prompt": "Pilih metode (1=Format, 2=Kualitas, 3=Tanggal):",
        "err_title": "Gagal", "err_folder_exists": "Folder sudah ada!", "lang_label": "🌐 Language:",
        "stats_remaining": "Sisa: {} track ({:.1f} MB)", "stats_processed": "Diproses: {} track ({:.1f} MB)",
        "btn_donate": "💛 Dukung via Saweria", "btn_refresh": "🔄 Refresh (F5)"
    },
    "en": {
        "title": "PSORTERV2 Audio", "header_app": "PSORTERV2 AUDIO", "header_sub": "PLAY & SORT ALL AUDIO FORMATS",
        "select_src": "📁 Source Folder", "select_dst": "📂 Main Target", "src_label": "Source: ", "dst_label": "Target: ",
        "not_selected": "(not selected)", "subfolder_frame": " TARGET SUB-FOLDERS ", "create_folder": "+ Create Folder (N)",
        "rename_folder": "✏️ Rename Folder", "delete_folder": "🗑️ Delete Folder", "pin_folder": "📌 Pin / Unpin",
        "autosort_btn": "⚡ AUTO-SORT AUDIO", "initial_info": "Select source audio folder to start", "play_audio": "▶ PLAY / PAUSE (SPACE)",
        "action_frame": " FILE ACTIONS ", "move_btn": "➡️ MOVE FILE\n(Enter / Key 1-9)", "copy_btn": "📋 COPY FILE\n(Enter / Key 1-9)",
        "undo_btn": "↩️ UNDO (Ctrl+Z)", "rename_file": "✏️ Rename File (R)", "batch_rename_file": "🏷️ Batch Rename",
        "delete_file": "🗑️ Delete File (Del)", "prev_btn": "◀ PREV (←)", "next_btn": "NEXT ▶ (→)", "file_counter": "TRACK {} OF {}",
        "no_files": "No audio files", "all_done": "All sorted!", "done": "Done", "mode_move": "Mode: MOVE",
        "mode_copy": "Mode: COPY", "warn": "Warning", "warn_no_files": "No audio files!", "warn_select_dst": "Select Target Folder!",
        "warn_select_sub": "Select target sub-folder!", "warn_select_ren_folder": "Select folder!", "warn_select_del_folder": "Select folder!",
        "dlg_create_folder_title": "Create Folder", "dlg_create_folder_prompt": "New sub-folder name:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' to:",
        "dlg_delete_folder_title": "Delete Folder", "dlg_delete_folder_prompt": "Delete folder '{}'?",
        "dlg_rename_file_title": "Rename File", "dlg_rename_file_prompt": "New file name:",
        "dlg_batch_rename_title": "Batch Rename", "dlg_batch_rename_prompt": "Prefix (default: 'AUDIO'):",
        "dlg_delete_file_title": "Delete Audio", "dlg_delete_file_prompt": "Delete audio file '{}'?",
        "dlg_autosort_title": "Auto-Sort", "dlg_autosort_prompt": "Choice (1=Format, 2=Quality, 3=Date):",
        "err_title": "Error", "err_folder_exists": "Folder exists!", "lang_label": "🌐 Language:",
        "stats_remaining": "Left: {} tracks ({:.1f} MB)", "stats_processed": "Done: {} tracks ({:.1f} MB)",
        "btn_donate": "💛 Support via Saweria", "btn_refresh": "🔄 Refresh (F5)"
    }
}

class DownloadProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mengunduh Update")
        self.geometry("420x230"); self.resizable(False, False)
        self.configure(fg_color="#141414"); self.transient(parent); self.grab_set()
        self.is_paused = self.is_cancelled = False

        self.lbl_title = ctk.CTkLabel(self, text="Mengunduh Pembaruan...", font=("Arial", 13, "bold"), text_color="white")
        self.lbl_title.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self, width=340, height=16, progress_color=NETFLIX_RED, fg_color="#2B2B2B")
        self.progress_bar.set(0); self.progress_bar.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Menghubungkan...", font=("Arial", 11), text_color=TEXT_MUTED)
        self.lbl_status.pack(pady=(0, 15))

        btn_box = ctk.CTkFrame(self, fg_color="transparent"); btn_box.pack(fill=tk.X, padx=40)
        self.btn_pause = ctk.CTkButton(btn_box, text="⏸️ Jeda", width=110, fg_color="#2B2B2B", command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        self.btn_cancel = ctk.CTkButton(btn_box, text="❌ Batal", width=110, fg_color="#3A1214", text_color="#FF6B6B", command=self.cancel_download)
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)
        self.protocol("WM_DELETE_WINDOW", self.cancel_download)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.configure(text="▶️ Lanjutkan" if self.is_paused else "⏸️ Jeda", fg_color=NETFLIX_RED if self.is_paused else "#2B2B2B")
        self.lbl_status.configure(text="Pengunduhan dijeda..." if self.is_paused else "Mengunduh...")

    def cancel_download(self):
        self.is_cancelled = True
        self.lbl_status.configure(text="Membatalkan...")

    def update_progress(self, dl, total):
        if self.is_paused or self.is_cancelled: return
        if total > 0:
            p = dl / total
            self.progress_bar.set(p)
            self.lbl_status.configure(text=f"{int(p * 100)}% ({dl / 1048576:.1f} MB / {total / 1048576:.1f} MB)")
        else:
            self.lbl_status.configure(text=f"Terunduh: {dl / 1048576:.1f} MB")

def check_for_updates_async(root_window=None):
    threading.Thread(target=_check_logic, args=(root_window,), daemon=True).start()

def _check_logic(root_window):
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            if res.status != 200: return
            data = json.loads(res.read().decode("utf-8"))

        latest = data.get("tag_name", "")
        if not latest or latest == CURRENT_VERSION: return

        download_url = next((a.get("browser_download_url") for a in data.get("assets", []) if a.get("name", "").lower().endswith(".zip") and "psorter" in a.get("name", "").lower() and "audio" in a.get("name", "").lower()), None)
        if not download_url: return

        def show_dialog():
            if messagebox.askyesno("Update Tersedia", f"Versi baru ({latest}) tersedia!\nUnduh sekarang?"):
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
            temp_zip, extract_folder = "temp_update_audio.zip", "temp_extracted_audio"
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                total = int(response.getheader("Content-Length", 0))
                dl = 0
                with open(temp_zip, "wb") as f:
                    while not dialog.is_cancelled:
                        while dialog.is_paused and not dialog.is_cancelled: time.sleep(0.1)
                        if dialog.is_cancelled: break
                        chunk = response.read(16384)
                        if not chunk: break
                        f.write(chunk); dl += len(chunk)
                        root_window.after(0, lambda d=dl, t=total: dialog.update_progress(d, t))

            if dialog.is_cancelled:
                if os.path.exists(temp_zip): os.remove(temp_zip)
                root_window.after(0, dialog.destroy); return

            root_window.after(0, lambda: dialog.lbl_status.configure(text="Mengekstrak file update..."))
            with zipfile.ZipFile(temp_zip, "r") as z: z.extractall(extract_folder)

            extracted_exe = next((os.path.join(r, f) for r, d, fs in os.walk(extract_folder) for f in fs if f.lower().endswith(".exe")), None)
            if not extracted_exe:
                root_window.after(0, lambda: messagebox.showerror("Gagal", "File .exe tidak ditemukan!"))
                root_window.after(0, dialog.destroy); return

            exe_filename = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else EXE_NAME)
            with open("update_audio.bat", "w") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\nmove /y "{extracted_exe}" "{exe_filename}"\nrmdir /s /q "{extract_folder}"\ndel "{temp_zip}"\nstart "" "{exe_filename}"\ndel "%~f0"\n')

            subprocess.Popen(["update_audio.bat"], shell=True); sys.exit(0)
        except Exception as e:
            if not dialog.is_cancelled:
                root_window.after(0, lambda: messagebox.showerror("Gagal Update", f"Error: {e}"))
            root_window.after(0, dialog.destroy)

    threading.Thread(target=run_update_thread, daemon=True).start()

class UniversalAudioSorterApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "id"
        self.root.geometry("1240x850")
        self.root.configure(fg_color=BG_DARK)

        self.source_dir = self.target_dir = ""
        self.raw_file_list, self.file_list = [], []
        self.current_index = 0

        self.has_vlc, self.has_pygame = HAS_VLC, HAS_PYGAME
        self.vlc_instance = self.vlc_player = None
        if self.has_vlc:
            try:
                self.vlc_instance = vlc.Instance('--no-video', '--quiet')
                self.vlc_player = self.vlc_instance.media_player_new()
            except Exception: self.has_vlc = False

        self.is_playing = self.is_seeking = self.is_muted = self.is_copy_mode = False
        self.audio_length, self.volume_level = 0.0, 0.8
        self.audio_job = None

        self.view_mode = "preview"
        self.undo_stack, self.pinned_folders = [], set()
        self.filter_mode, self.sort_mode = "Semua", "Nama"
        self.processed_files_count = self.processed_bytes_count = 0

        self.file_stats_cache, self.metadata_cache, self.grid_cards = {}, {}, {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        self.setup_ui()
        self.bind_shortcuts()
        self.update_ui_texts()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        check_for_updates_async(self.root)

    def t(self, key, *args):
        text = TRANSLATIONS[self.current_lang].get(key, key)
        return text.format(*args) if args else text

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def get_audio_quality_type(self, filename):
        return "Lossless Audio" if os.path.splitext(filename)[1].lower() in LOSSLESS_EXTS else "Lossy Audio"

    def setup_ui(self):
        # Header
        brand_frame = ctk.CTkFrame(self.root, fg_color="#000000", corner_radius=0, height=60)
        brand_frame.pack(fill=tk.X, side=tk.TOP)
        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent"); logo_box.pack(side=tk.LEFT, padx=20, pady=10)

        self.lbl_brand = ctk.CTkLabel(logo_box, text="PSORTER AUDIO", font=("Arial Black", 20, "bold"), text_color=NETFLIX_RED)
        self.lbl_brand.pack(side=tk.LEFT)
        engine_tag = " [VLC ENGINE]" if self.has_vlc else " [PYGAME ENGINE]"
        self.lbl_sub = ctk.CTkLabel(logo_box, text=f"  UNIVERSAL SORTER{engine_tag}", font=("Arial", 10, "bold"), text_color=CYAN_ACCENT)
        self.lbl_sub.pack(side=tk.LEFT, pady=(5, 0))

        right_h = ctk.CTkFrame(brand_frame, fg_color="transparent"); right_h.pack(side=tk.RIGHT, padx=20)
        self.btn_refresh = ctk.CTkButton(right_h, text="🔄 Refresh", command=self.refresh_data, fg_color=CARD_BG_LIGHT, width=100)
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)
        self.btn_donate = ctk.CTkButton(right_h, text="💛 Saweria", command=lambda: webbrowser.open("https://saweria.co/Atillaraihan"), fg_color=SAWERIA_YELLOW, text_color="#000000", width=120)
        self.btn_donate.pack(side=tk.RIGHT, padx=5)

        self.lbl_lang = ctk.CTkLabel(right_h, font=("Arial", 11, "bold"))
        self.lbl_lang.pack(side=tk.LEFT, padx=5)
        self.lang_menu = ctk.CTkOptionMenu(right_h, values=["Bahasa Indonesia", "English"], command=self.on_language_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, width=130)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        # Footer & Path Selectors
        footer = ctk.CTkFrame(self.root, fg_color="#0A0A0A", height=28); footer.pack(side=tk.BOTTOM, fill=tk.X)
        ctk.CTkLabel(footer, text="Made by Google Gemini & Atilla • Audio Edition", font=("Arial", 10, "italic"), text_color="#777777").pack(pady=4)

        top_frame = ctk.CTkFrame(self.root, fg_color=CARD_BG, corner_radius=10); top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        self.btn_src = ctk.CTkButton(top_frame, command=self.select_source_dir, fg_color=CARD_BG_LIGHT); self.btn_src.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_src = ctk.CTkLabel(top_frame, anchor="w"); self.lbl_src.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.btn_dst = ctk.CTkButton(top_frame, command=self.select_target_dir, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER); self.btn_dst.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_dst = ctk.CTkLabel(top_frame, anchor="w"); self.lbl_dst.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.mode_switch = ctk.CTkSwitch(top_frame, text="Mode: PINDAH", command=self.toggle_mode_switch, progress_color=NETFLIX_RED)
        self.mode_switch.pack(side=tk.RIGHT, padx=15)

        # Main Workspace
        main = ctk.CTkFrame(self.root, fg_color="transparent"); main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left Panel
        self.left_frame = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=12, width=270); self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8), pady=5); self.left_frame.pack_propagate(False)
        self.lbl_left_title = ctk.CTkLabel(self.left_frame, font=("Arial", 12, "bold"), text_color=TEXT_MUTED); self.lbl_left_title.pack(pady=(12, 5))

        list_container = ctk.CTkFrame(self.left_frame, fg_color="#121212", corner_radius=8); list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.folder_listbox = tk.Listbox(list_container, bg="#121212", fg="white", selectbackground=NETFLIX_RED, bd=0, highlightthickness=0, font=("Arial", 10))
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_f_box = ctk.CTkFrame(self.left_frame, fg_color="transparent"); btn_f_box.pack(fill=tk.X, padx=10, pady=5)
        self.btn_autosort = ctk.CTkButton(btn_f_box, command=self.auto_sort_files, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, font=("Arial", 11, "bold")); self.btn_autosort.pack(fill=tk.X, pady=3)
        self.btn_pin_folder = ctk.CTkButton(btn_f_box, command=self.toggle_pin_folder, fg_color=CARD_BG_LIGHT); self.btn_pin_folder.pack(fill=tk.X, pady=3)
        self.btn_create_folder = ctk.CTkButton(btn_f_box, command=self.create_folder, fg_color=CARD_BG_LIGHT); self.btn_create_folder.pack(fill=tk.X, pady=3)
        self.btn_rename_folder = ctk.CTkButton(btn_f_box, command=self.rename_folder, fg_color=CARD_BG_LIGHT); self.btn_rename_folder.pack(fill=tk.X, pady=3)
        self.btn_delete_folder = ctk.CTkButton(btn_f_box, command=self.delete_folder, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B"); self.btn_delete_folder.pack(fill=tk.X, pady=3)

        # Center Panel
        self.center_frame = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=12); self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        top_c_bar = ctk.CTkFrame(self.center_frame, fg_color="transparent"); top_c_bar.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.view_segmented_btn = ctk.CTkSegmentedButton(top_c_bar, values=["🎵 Audio Deck", "📁 Mode Grid"], command=self.on_view_mode_change, selected_color=NETFLIX_RED, fg_color=CARD_BG_LIGHT)
        self.view_segmented_btn.set("🎵 Audio Deck"); self.view_segmented_btn.pack(side=tk.LEFT, padx=5)

        self.sort_menu = ctk.CTkOptionMenu(top_c_bar, values=["Nama", "Tanggal", "Ukuran"], command=self.on_sort_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, width=90); self.sort_menu.pack(side=tk.RIGHT, padx=5)
        ctk.CTkLabel(top_c_bar, text="Urutan:", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(side=tk.RIGHT, padx=2)

        self.filter_menu = ctk.CTkOptionMenu(top_c_bar, values=["Semua", "Lossless", "Lossy"], command=self.on_filter_change, fg_color=CARD_BG_LIGHT, button_color=NETFLIX_RED, width=95); self.filter_menu.pack(side=tk.RIGHT, padx=5)
        ctk.CTkLabel(top_c_bar, text="Filter:", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(side=tk.RIGHT, padx=2)

        self.lbl_file_info = ctk.CTkLabel(self.center_frame, font=("Arial", 13, "bold"), text_color="white"); self.lbl_file_info.pack(pady=4)

        self.view_container = ctk.CTkFrame(self.center_frame, fg_color="transparent"); self.view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        self.preview_subframe = ctk.CTkFrame(self.view_container, fg_color="transparent"); self.preview_subframe.pack(fill=tk.BOTH, expand=True)

        deck_bg = ctk.CTkFrame(self.preview_subframe, fg_color="#0D0D0D", corner_radius=12); deck_bg.pack(fill=tk.BOTH, expand=True, pady=5)
        vinyl_box = ctk.CTkFrame(deck_bg, fg_color="transparent"); vinyl_box.pack(expand=True, pady=20)
        self.lbl_vinyl_icon = ctk.CTkLabel(vinyl_box, text="🎧", font=("Arial", 72)); self.lbl_vinyl_icon.pack()
        self.lbl_track_title = ctk.CTkLabel(vinyl_box, text="Belum Ada Audio Dipilih", font=("Arial", 16, "bold")); self.lbl_track_title.pack(pady=(10, 2))
        self.lbl_track_format = ctk.CTkLabel(vinyl_box, text="[ ALL FORMATS SUPPORTED ]", font=("Arial", 11, "bold"), text_color=CYAN_ACCENT); self.lbl_track_format.pack()

        self.lbl_metadata = ctk.CTkLabel(self.preview_subframe, text="Format: - | Ukuran: - | Tanggal: -", font=("Arial", 10, "bold"), text_color=TEXT_MUTED); self.lbl_metadata.pack(pady=2)

        timeline_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent"); timeline_bar.pack(fill=tk.X, pady=(5, 0))
        self.lbl_time_curr = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=NETFLIX_RED, width=45); self.lbl_time_curr.pack(side=tk.LEFT)
        self.timeline_slider = ctk.CTkSlider(timeline_bar, from_=0, to=100, fg_color=CARD_BG_LIGHT, progress_color=NETFLIX_RED, button_color=NETFLIX_RED, command=self.on_slider_seek)
        self.timeline_slider.set(0); self.timeline_slider.configure(state="disabled"); self.timeline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.lbl_time_total = ctk.CTkLabel(timeline_bar, text="00:00", font=("Arial", 11, "bold"), text_color=TEXT_MUTED, width=45); self.lbl_time_total.pack(side=tk.RIGHT)

        controls_bar = ctk.CTkFrame(self.preview_subframe, fg_color="transparent"); controls_bar.pack(fill=tk.X, pady=8)
        self.btn_play = ctk.CTkButton(controls_bar, command=self.toggle_audio, state="disabled", fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, height=36, width=220)
        self.btn_play.pack(side=tk.LEFT, expand=True)

        vol_box = ctk.CTkFrame(controls_bar, fg_color="transparent"); vol_box.pack(side=tk.RIGHT)
        self.btn_mute = ctk.CTkButton(vol_box, text="🔊", width=34, height=34, fg_color=CARD_BG_LIGHT, command=self.toggle_mute); self.btn_mute.pack(side=tk.LEFT, padx=(0, 5))
        self.volume_slider = ctk.CTkSlider(vol_box, from_=0, to=1, width=100, progress_color=CYAN_ACCENT, button_color=CYAN_ACCENT, command=self.on_volume_change)
        self.volume_slider.set(0.8); self.volume_slider.pack(side=tk.LEFT, padx=5)
        self.lbl_volume_val = ctk.CTkLabel(vol_box, text="80%", font=("Arial", 11, "bold"), text_color=TEXT_MUTED, width=35); self.lbl_volume_val.pack(side=tk.LEFT)

        self.folder_grid_subframe = ctk.CTkScrollableFrame(self.view_container, fg_color="#121212", corner_radius=8)

        # Right Panel
        self.right_frame = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=12, width=230); self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0), pady=5); self.right_frame.pack_propagate(False)
        self.lbl_right_title = ctk.CTkLabel(self.right_frame, font=("Arial", 12, "bold"), text_color=TEXT_MUTED); self.lbl_right_title.pack(pady=(12, 5))

        self.btn_move = ctk.CTkButton(self.right_frame, command=self.move_file, fg_color=NETFLIX_RED, hover_color=NETFLIX_RED_HOVER, height=48); self.btn_move.pack(fill=tk.X, padx=10, pady=6)
        self.btn_undo = ctk.CTkButton(self.right_frame, command=self.undo_last_action, fg_color=CARD_BG_LIGHT); self.btn_undo.pack(fill=tk.X, padx=10, pady=4)
        self.btn_rename_file = ctk.CTkButton(self.right_frame, command=self.rename_file, fg_color=CARD_BG_LIGHT); self.btn_rename_file.pack(fill=tk.X, padx=10, pady=4)
        self.btn_batch_rename = ctk.CTkButton(self.right_frame, command=self.batch_rename_files, fg_color=CARD_BG_LIGHT); self.btn_batch_rename.pack(fill=tk.X, padx=10, pady=4)
        self.btn_delete_file = ctk.CTkButton(self.right_frame, command=self.delete_file, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B"); self.btn_delete_file.pack(fill=tk.X, padx=10, pady=4)

        nav_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent"); nav_frame.pack(fill=tk.X, padx=10, pady=10)
        self.btn_prev = ctk.CTkButton(nav_frame, command=self.prev_file, width=90, fg_color=CARD_BG_LIGHT); self.btn_prev.pack(side=tk.LEFT)
        self.btn_next = ctk.CTkButton(nav_frame, command=self.next_file, width=90, fg_color=CARD_BG_LIGHT); self.btn_next.pack(side=tk.RIGHT)

        self.lbl_counter = ctk.CTkLabel(self.right_frame, font=("Arial", 11, "bold"), text_color=TEXT_MUTED); self.lbl_counter.pack(pady=5)

        stats_box = ctk.CTkFrame(self.right_frame, fg_color="#121212", corner_radius=8); stats_box.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(stats_box, text="📊 STATISTIK AUDIO", font=("Arial", 10, "bold"), text_color=TEXT_MUTED).pack(pady=(6, 2))
        self.lbl_stat_remaining = ctk.CTkLabel(stats_box, text="Sisa: 0 track (0.0 MB)", font=("Arial", 10)); self.lbl_stat_remaining.pack()
        self.lbl_stat_processed = ctk.CTkLabel(stats_box, text="Diproses: 0 track (0.0 MB)", font=("Arial", 10), text_color=CYAN_ACCENT); self.lbl_stat_processed.pack(pady=(0, 6))

    def on_language_change(self, choice):
        self.current_lang = "id" if choice == "Bahasa Indonesia" else "en"
        self.update_ui_texts()

    def update_ui_texts(self):
        self.root.title(self.t("title"))
        self.lbl_brand.configure(text=self.t("header_app"))
        self.lbl_sub.configure(text=f"  {self.t('header_sub')}")
        self.btn_src.configure(text=self.t("select_src")); self.btn_dst.configure(text=self.t("select_dst"))
        self.btn_donate.configure(text=self.t("btn_donate")); self.btn_refresh.configure(text=self.t("btn_refresh"))
        self.lbl_lang.configure(text=self.t("lang_label"))

        self.lbl_src.configure(text=self.t("src_label") + (self.source_dir or self.t("not_selected")))
        self.lbl_dst.configure(text=self.t("dst_label") + (self.target_dir or self.t("not_selected")))

        self.lbl_left_title.configure(text=self.t("subfolder_frame"))
        self.btn_autosort.configure(text=self.t("autosort_btn"))
        self.btn_pin_folder.configure(text=self.t("pin_folder"))
        self.btn_create_folder.configure(text=self.t("create_folder"))
        self.btn_rename_folder.configure(text=self.t("rename_folder"))
        self.btn_delete_folder.configure(text=self.t("delete_folder"))

        self.btn_play.configure(text=self.t("play_audio"))
        self.lbl_right_title.configure(text=self.t("action_frame"))
        self.btn_move.configure(text=self.t("copy_btn") if self.is_copy_mode else self.t("move_btn"))
        self.btn_undo.configure(text=self.t("undo_btn"))
        self.btn_rename_file.configure(text=self.t("rename_file"))
        self.btn_batch_rename.configure(text=self.t("batch_rename_file"))
        self.btn_delete_file.configure(text=self.t("delete_file"))
        self.btn_prev.configure(text=self.t("prev_btn")); self.btn_next.configure(text=self.t("next_btn"))

        if not self.file_list:
            self.lbl_file_info.configure(text=self.t("initial_info"))
            self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
        elif self.view_mode == "preview":
            self.load_current_media()

    def refresh_data(self):
        if self.source_dir: self.scan_files()
        if self.target_dir: self.refresh_folder_list()

    def on_view_mode_change(self, choice):
        self.stop_audio()
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
            ctk.CTkLabel(self.folder_grid_subframe, text=self.t("no_files"), font=("Arial", 13)).pack(pady=50)
            return

        for idx, filename in enumerate(self.file_list):
            r, c = divmod(idx, 4)
            ext = os.path.splitext(filename)[1].upper().replace('.', '')
            is_sel = (idx == self.current_index)

            card = ctk.CTkFrame(self.folder_grid_subframe, fg_color=CARD_BG_LIGHT, border_width=2 if is_sel else 0, border_color=NETFLIX_RED if is_sel else CARD_BG_LIGHT, width=130, height=130)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew"); card.pack_propagate(False)
            self.grid_cards[idx] = card

            icon = ctk.CTkLabel(card, text="🎵", font=("Arial", 28)); icon.pack(pady=(12, 0))
            badge = ctk.CTkLabel(card, text=ext, font=("Arial", 9, "bold"), text_color="white", fg_color=CYAN_ACCENT if ext in ('FLAC', 'WAV', 'AIFF', 'ALAC') else NETFLIX_RED, height=16, width=40)
            badge.pack(pady=(2, 4))

            disp = filename if len(filename) <= 15 else filename[:12] + "..."
            name = ctk.CTkLabel(card, text=disp, font=("Arial", 9, "bold")); name.pack(pady=(0, 4))

            for w in (card, icon, name):
                w.bind("<Button-1>", lambda e, i=idx: self.select_file_from_grid(i))

    def select_file_from_grid(self, index):
        old_idx = self.current_index
        self.current_index = index
        if old_idx in self.grid_cards and self.grid_cards[old_idx].winfo_exists():
            self.grid_cards[old_idx].configure(border_width=0, border_color=CARD_BG_LIGHT)
        if index in self.grid_cards and self.grid_cards[index].winfo_exists():
            self.grid_cards[index].configure(border_width=2, border_color=NETFLIX_RED)

        self.lbl_file_info.configure(text=self.file_list[self.current_index])
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))

    def toggle_mode_switch(self):
        self.is_copy_mode = bool(self.mode_switch.get())
        self.mode_switch.configure(text=self.t("mode_copy" if self.is_copy_mode else "mode_move"))
        self.btn_move.configure(text=self.t("copy_btn" if self.is_copy_mode else "move_btn"))

    def on_filter_change(self, choice): self.filter_mode = choice; self.apply_filter_and_sort()
    def on_sort_change(self, choice): self.sort_mode = choice; self.apply_filter_and_sort()

    def apply_filter_and_sort(self):
        if not self.source_dir or not self.raw_file_list:
            self.file_list = []; return

        filtered = [f for f in self.raw_file_list if self.filter_mode == "Semua" or (self.filter_mode in self.get_audio_quality_type(f))]
        if self.sort_mode in ("Nama", "Name"): filtered.sort()
        elif self.sort_mode in ("Tanggal", "Date"): filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[1])
        elif self.sort_mode in ("Ukuran", "Size"): filtered.sort(key=lambda f: self.file_stats_cache.get(f, (0, 0))[0], reverse=True)

        self.file_list = filtered; self.current_index = 0
        if self.view_mode == "folder": self.populate_folder_grid()
        else:
            if self.file_list: self.load_current_media()
            else:
                self.lbl_track_title.configure(text=self.t("no_files")); self.lbl_track_format.configure(text="[ NONE ]")
                self.lbl_file_info.configure(text="-"); self.lbl_metadata.configure(text="Format: - | Ukuran: - | Tanggal: -")
                self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
        self.update_statistics()

    def update_statistics(self):
        if not self.source_dir: return
        rem_mb = sum(self.file_stats_cache.get(f, (0, 0))[0] for f in self.file_list) / 1048576
        proc_mb = self.processed_bytes_count / 1048576
        self.lbl_stat_remaining.configure(text=self.t("stats_remaining", len(self.file_list), rem_mb))
        self.lbl_stat_processed.configure(text=self.t("stats_processed", self.processed_files_count, proc_mb))

    def toggle_pin_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder")); return
        raw = self.folder_listbox.get(selected[0])
        fn = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        self.pinned_folders.remove(fn) if fn in self.pinned_folders else self.pinned_folders.add(fn)
        self.refresh_folder_list()

    def auto_sort_files(self):
        if not self.source_dir: messagebox.showwarning(self.t("warn"), self.t("warn_no_files")); return
        if not self.target_dir: messagebox.showwarning(self.t("warn"), self.t("warn_select_dst")); return

        choice = simpledialog.askstring(self.t("dlg_autosort_title"), self.t("dlg_autosort_prompt"))
        if not choice or choice.strip() not in ("1", "2", "3"): return

        choice = choice.strip()
        self.stop_audio()
        sorted_count = 0

        for filename in list(self.file_list):
            src_path = os.path.join(self.source_dir, filename)
            if not os.path.exists(src_path): continue

            if choice == "1": sub_name = os.path.splitext(filename)[1].replace(".", "").upper() or "OTHERS"
            elif choice == "2": sub_name = self.get_audio_quality_type(filename).upper().replace(" ", "_")
            else: sub_name = datetime.datetime.fromtimestamp(self.file_stats_cache.get(filename, (0, 0))[1]).strftime('%Y-%m-%d')

            dest = os.path.join(self.target_dir, sub_name)
            os.makedirs(dest, exist_ok=True)

            dst_path, size = os.path.join(dest, filename), self.file_stats_cache.get(filename, (0, 0))[0]
            if self.is_copy_mode:
                shutil.copy2(src_path, dst_path)
                self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path, 'size': size})
            else:
                shutil.move(src_path, dst_path)
                self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path, 'size': size})
                self.raw_file_list.remove(filename)

            self.processed_files_count += 1; self.processed_bytes_count += size; sorted_count += 1

        self.refresh_folder_list(); self.scan_files()
        messagebox.showinfo(self.t("done"), f"Auto-Sort Selesai! {sorted_count} track diproses.")

    def undo_last_action(self):
        if not self.undo_stack: return
        act = self.undo_stack.pop()
        self.stop_audio()
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
        if self.has_vlc and self.vlc_player:
            self.vlc_player.audio_set_volume(0 if self.is_muted else int(self.volume_level * 100))
        elif self.has_pygame and not self.is_muted:
            pygame.mixer.music.set_volume(self.volume_level)
        self.lbl_volume_val.configure(text=f"{int(self.volume_level * 100)}%")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.btn_mute.configure(text="🔇" if self.is_muted else "🔊")
        self.on_volume_change(self.volume_level)

    def bind_shortcuts(self):
        for k, fn in [("<Right>", self.next_file), ("<Left>", self.prev_file), ("<space>", self.toggle_audio),
                      ("<F5>", self.refresh_data), ("<Return>", self.move_file), ("<Delete>", self.delete_file)]:
            self.root.bind(k, lambda e, func=fn: func())

        for k in ("r", "R"): self.root.bind(k, lambda e: self.rename_file())
        for k in ("n", "N"): self.root.bind(k, lambda e: self.create_folder())
        for k in ("<Control-z>", "<Control-Z>"): self.root.bind(k, lambda e: self.undo_last_action())

        for i in range(1, 10):
            self.root.bind(str(i), lambda e, idx=i-1: self.quick_move_by_index(idx))

    def select_source_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_src"))
        if folder:
            self.source_dir = folder
            self.lbl_src.configure(text=self.t("src_label") + folder)
            self.metadata_cache.clear(); self.file_stats_cache.clear()
            self.scan_files()

    def select_target_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_dst"))
        if folder:
            p_folder = os.path.join(folder, "PSORTER")
            os.makedirs(p_folder, exist_ok=True)
            self.target_dir = p_folder
            self.lbl_dst.configure(text=self.t("dst_label") + p_folder)
            self.refresh_folder_list()

    def scan_files(self):
        self.stop_audio()
        if not self.source_dir: return
        self.raw_file_list = [f for f in sorted(os.listdir(self.source_dir)) if f.lower().endswith(AUDIO_EXTENSIONS) and os.path.isfile(os.path.join(self.source_dir, f))]

        for f in self.raw_file_list:
            if f not in self.file_stats_cache:
                try:
                    st = os.stat(os.path.join(self.source_dir, f))
                    self.file_stats_cache[f] = (st.st_size, st.st_mtime)
                except Exception: self.file_stats_cache[f] = (0, 0)

        self.apply_filter_and_sort()

    def refresh_folder_list(self):
        self.folder_listbox.delete(0, tk.END)
        if not self.target_dir or not os.path.exists(self.target_dir): return
        subs = [f for f in sorted(os.listdir(self.target_dir)) if os.path.isdir(os.path.join(self.target_dir, f))]
        folders = [f for f in subs if f in self.pinned_folders] + [f for f in subs if f not in self.pinned_folders]

        for idx, f in enumerate(folders):
            pin, pref = ("📌 " if f in self.pinned_folders else ""), (f"[{idx+1}] " if idx < 9 else "    ")
            self.folder_listbox.insert(tk.END, f"{pref}{pin}{f}")

    def load_current_media(self):
        self.stop_audio()
        if not self.file_list or self.current_index >= len(self.file_list):
            self.lbl_track_title.configure(text=self.t("all_done")); self.lbl_track_format.configure(text="[ FINISHED ]")
            self.lbl_file_info.configure(text=self.t("done")); self.lbl_metadata.configure(text="Format: - | Ukuran: - | Tanggal: -")
            self.lbl_counter.configure(text=self.t("file_counter", len(self.file_list), len(self.file_list)))
            self.timeline_slider.configure(state="disabled"); self.btn_play.configure(state="disabled")
            self.lbl_time_curr.configure(text="00:00"); self.lbl_time_total.configure(text="00:00")
            return

        filename = self.file_list[self.current_index]
        filepath = os.path.join(self.source_dir, filename)
        ext = os.path.splitext(filename)[1].upper().replace('.', '')

        self.lbl_file_info.configure(text=filename)
        self.lbl_track_title.configure(text=filename if len(filename) <= 30 else filename[:27] + "...")
        self.lbl_track_format.configure(text=f"[ {ext} • {self.get_audio_quality_type(filename).upper()} ]")
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))

        if filepath not in self.metadata_cache and os.path.exists(filepath):
            sz, mt = self.file_stats_cache.get(filename, (os.path.getsize(filepath), os.path.getmtime(filepath)))
            self.metadata_cache[filepath] = f"Format: {ext} | Ukuran: {sz / 1048576:.2f} MB | Tanggal: {datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M')}"

        self.lbl_metadata.configure(text=self.metadata_cache.get(filepath, ""))
        self.prepare_audio(filepath)

    def prepare_audio(self, filepath):
        if self.has_vlc and self.vlc_instance:
            try:
                m = self.vlc_instance.media_new(filepath)
                self.vlc_player.set_media(m)
                m.parse_with_options(vlc.MediaParseFlag.local, 0)
                time.sleep(0.05)
                self.btn_play.configure(state="normal"); self.timeline_slider.configure(state="normal")
                self.on_volume_change(self.volume_level)
                self.lbl_time_curr.configure(text="00:00"); self.lbl_time_total.configure(text="--:--")
                return
            except Exception: pass

        if self.has_pygame:
            try:
                pygame.mixer.music.load(filepath)
                self.btn_play.configure(state="normal"); self.timeline_slider.configure(state="normal")
                self.lbl_time_curr.configure(text="00:00"); self.lbl_time_total.configure(text="--:--")
                return
            except Exception: pass

        self.btn_play.configure(state="disabled"); self.timeline_slider.configure(state="disabled")

    def toggle_audio(self):
        if self.has_vlc and self.vlc_player:
            if self.is_playing:
                self.vlc_player.pause(); self.is_playing = False; self.lbl_vinyl_icon.configure(text="🎧")
                if self.audio_job: self.root.after_cancel(self.audio_job)
            else:
                self.vlc_player.play(); self.is_playing = True; self.lbl_vinyl_icon.configure(text="📻")
                self.update_audio_loop()
        elif self.has_pygame:
            if self.is_playing:
                pygame.mixer.music.pause(); self.is_playing = False; self.lbl_vinyl_icon.configure(text="🎧")
                if self.audio_job: self.root.after_cancel(self.audio_job)
            else:
                pygame.mixer.music.play(); self.is_playing = True; self.lbl_vinyl_icon.configure(text="📻")
                self.update_audio_loop()

    def update_audio_loop(self):
        if self.is_playing:
            if self.has_vlc and self.vlc_player:
                ms, l_ms = self.vlc_player.get_time(), self.vlc_player.get_length()
                if l_ms > 0:
                    self.audio_length = l_ms / 1000.0
                    self.lbl_time_total.configure(text=self.format_time(self.audio_length))
                    self.timeline_slider.configure(from_=0, to=self.audio_length)

                if ms >= 0 and self.audio_length > 0:
                    curr = ms / 1000.0
                    if not self.is_seeking: self.timeline_slider.set(curr)
                    self.lbl_time_curr.configure(text=self.format_time(curr))

                if self.vlc_player.get_state() == vlc.State.Ended: self.stop_audio(); return

            elif self.has_pygame:
                pos = pygame.mixer.music.get_pos()
                if pos >= 0:
                    curr = pos / 1000.0
                    if not self.is_seeking: self.timeline_slider.set(curr)
                    self.lbl_time_curr.configure(text=self.format_time(curr))

            self.audio_job = self.root.after(200, self.update_audio_loop)

    def on_slider_seek(self, value):
        self.is_seeking = True
        sec = float(value)
        if self.has_vlc and self.vlc_player: self.vlc_player.set_time(int(sec * 1000))
        elif self.has_pygame:
            try: pygame.mixer.music.play(start=sec)
            except Exception: pass
        self.lbl_time_curr.configure(text=self.format_time(sec))
        self.is_seeking = False

    def stop_audio(self):
        self.is_playing = False
        if self.has_vlc and self.vlc_player: self.vlc_player.stop()
        elif self.has_pygame: pygame.mixer.music.stop()
        if self.audio_job: self.root.after_cancel(self.audio_job); self.audio_job = None
        self.lbl_vinyl_icon.configure(text="🎧")

    def create_folder(self):
        if not self.target_dir: messagebox.showwarning(self.t("warn"), self.t("warn_select_dst")); return
        name = simpledialog.askstring(self.t("dlg_create_folder_title"), self.t("dlg_create_folder_prompt"))
        if name:
            p = os.path.join(self.target_dir, name.strip())
            if not os.path.exists(p): os.makedirs(p); self.refresh_folder_list()
            else: messagebox.showerror(self.t("err_title"), self.t("err_folder_exists"))

    def rename_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder")); return
        raw = self.folder_listbox.get(selected[0])
        old = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()

        new_n = simpledialog.askstring(self.t("dlg_rename_folder_title"), self.t("dlg_rename_folder_prompt", old), initialvalue=old)
        if new_n and new_n.strip() != old:
            os.rename(os.path.join(self.target_dir, old), os.path.join(self.target_dir, new_n.strip()))
            if old in self.pinned_folders: self.pinned_folders.remove(old); self.pinned_folders.add(new_n.strip())
            self.refresh_folder_list()

    def delete_folder(self):
        selected = self.folder_listbox.curselection()
        if not selected: messagebox.showwarning(self.t("warn"), self.t("warn_select_del_folder")); return
        raw = self.folder_listbox.get(selected[0])
        fn = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()

        if messagebox.askyesno(self.t("dlg_delete_folder_title"), self.t("dlg_delete_folder_prompt", fn)):
            shutil.rmtree(os.path.join(self.target_dir, fn))
            if fn in self.pinned_folders: self.pinned_folders.remove(fn)
            self.refresh_folder_list()

    def quick_move_by_index(self, index):
        if index < self.folder_listbox.size():
            self.folder_listbox.selection_clear(0, tk.END)
            self.folder_listbox.selection_set(index); self.folder_listbox.activate(index)
            self.move_file()

    def move_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        selected = self.folder_listbox.curselection()
        if not selected: messagebox.showwarning(self.t("warn"), self.t("warn_select_sub")); return

        raw = self.folder_listbox.get(selected[0])
        fn = raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()
        dest_dir = os.path.join(self.target_dir, fn)

        self.stop_audio()
        filename = self.file_list[self.current_index]
        src, dst, size = os.path.join(self.source_dir, filename), os.path.join(dest_dir, filename), self.file_stats_cache.get(filename, (0, 0))[0]

        if self.is_copy_mode:
            shutil.copy2(src, dst)
            self.undo_stack.append({'action': 'copy', 'src': src, 'dst': dst, 'size': size})
        else:
            shutil.move(src, dst)
            self.undo_stack.append({'action': 'move', 'src': src, 'dst': dst, 'size': size})
            self.raw_file_list.remove(filename)

        self.processed_files_count += 1; self.processed_bytes_count += size
        self.apply_filter_and_sort()

    def rename_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        old = self.file_list[self.current_index]
        self.stop_audio()

        new_f = simpledialog.askstring(self.t("dlg_rename_file_title"), self.t("dlg_rename_file_prompt"), initialvalue=old)
        if new_f and new_f.strip() != old:
            os.rename(os.path.join(self.source_dir, old), os.path.join(self.source_dir, new_f.strip()))
            self.raw_file_list[self.raw_file_list.index(old)] = new_f.strip()

        self.apply_filter_and_sort()

    def batch_rename_files(self):
        if not self.file_list: messagebox.showwarning(self.t("warn"), self.t("warn_no_files")); return
        self.stop_audio()

        prefix = simpledialog.askstring(self.t("dlg_batch_rename_title"), self.t("dlg_batch_rename_prompt"), initialvalue="AUDIO")
        if not prefix or not prefix.strip(): return

        prefix = prefix.strip()
        temp_file_map = []

        for i, old in enumerate(self.file_list):
            ext = os.path.splitext(old)[1]
            temp = f"__temp_psorter_{i}_{old}"
            try:
                os.rename(os.path.join(self.source_dir, old), os.path.join(self.source_dir, temp))
                temp_file_map.append((temp, ext, old))
            except Exception as e:
                messagebox.showerror(self.t("err_title"), f"Gagal merename {old}: {e}")
                self.scan_files(); return

        for i, (temp, ext, old) in enumerate(temp_file_map):
            final_name = f"{prefix}_{i+1}{ext}"
            os.rename(os.path.join(self.source_dir, temp), os.path.join(self.source_dir, final_name))
            self.raw_file_list[self.raw_file_list.index(old)] = final_name

        self.apply_filter_and_sort()

    def delete_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return
        filename = self.file_list[self.current_index]
        if messagebox.askyesno(self.t("dlg_delete_file_title"), self.t("dlg_delete_file_prompt", filename)):
            self.stop_audio()
            os.remove(os.path.join(self.source_dir, filename))
            self.raw_file_list.remove(filename)
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
        self.stop_audio()
        self.executor.shutdown(wait=False)
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = UniversalAudioSorterApp(root)
    root.mainloop()