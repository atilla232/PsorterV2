import os, shutil, datetime, webbrowser, tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

RED, RED_H, BG, CARD, CARD_L, MUTED = "#E50914", "#B81D24", "#141414", "#1F1F1F", "#2B2B2B", "#AAAAAA"
SAWERIA_Y, SAWERIA_H = "#E5C07B", "#D19A66"

TR = {
    "id": {
        "title": "PSORTERV2 Lite", "header_app": "PSORTERV2 Lite", "header_sub": "OPTIMIZED PHOTO SORTER",
        "select_src": "📁 Folder Sumber", "select_dst": "📂 Folder Tujuan Utama", "src_label": "Sumber: ",
        "dst_label": "Tujuan (PSORTER): ", "not_selected": "(belum dipilih)", "subfolder_frame": " SUB-FOLDER TUJUAN ",
        "create_folder": "+ Buat Folder (N)", "rename_folder": "✏️ Rename Folder", "delete_folder": "🗑️ Hapus Folder",
        "pin_folder": "📌 Pin / Unpin Folder", "autosort_btn": "⚡ SORTIR OTOMATIS", "action_frame": " AKSI FOTO ",
        "move_btn": "➡️ PINDAHKAN FOTO\n(Enter / Angka 1-9)", "copy_btn": "📋 SALIN FOTO\n(Enter / Angka 1-9)",
        "undo_btn": "↩️ BATAL / UNDO (Ctrl+Z)", "rename_file": "✏️ Rename Foto (R)",
        "batch_rename_file": "🏷️ Rename Semua (PHOTO_1...)", "delete_file": "🗑️ Hapus Foto (Delete)",
        "prev_btn": "◀ PREV (←)", "next_btn": "NEXT ▶ (→)", "file_counter": "FOTO {} DARI {}",
        "no_files": "Tidak ada foto di folder ini", "all_done": "Semua foto selesai disortir!", "done": "Selesai",
        "mode_move": "Mode: PINDAH", "mode_copy": "Mode: SALIN", "err_load_img": "Gagal memuat foto: {}",
        "warn": "Peringatan", "warn_no_files": "Tidak ada foto di folder sumber!",
        "warn_select_dst": "Pilih Folder Tujuan Utama terlebih dahulu!",
        "warn_select_sub": "Pilih sub-folder tujuan di panel kiri terlebih dahulu!",
        "warn_select_ren_folder": "Pilih folder yang ingin di-rename!",
        "warn_select_del_folder": "Pilih folder yang ingin dihapus!",
        "dlg_create_folder_title": "Buat Folder PSORTER", "dlg_create_folder_prompt": "Masukkan nama sub-folder baru:",
        "dlg_rename_folder_title": "Rename Folder", "dlg_rename_folder_prompt": "Rename '{}' menjadi:",
        "dlg_delete_folder_title": "Konfirmasi Hapus Folder", "dlg_delete_folder_prompt": "Hapus folder '{}' beserta isinya?",
        "dlg_rename_file_title": "Rename Foto", "dlg_rename_file_prompt": "Masukkan nama foto baru:",
        "dlg_batch_rename_title": "Batch Rename PSORTER", "dlg_batch_rename_prompt": "Masukkan awalan nama foto (default: 'PHOTO'):",
        "dlg_delete_file_title": "Konfirmasi Hapus Foto", "dlg_delete_file_prompt": "Hapus foto '{}'?",
        "dlg_autosort_title": "Auto-Sort Foto Otomatis",
        "dlg_autosort_prompt": "Pilih metode Auto-Sort:\n\n1 = Ekstensi File (JPG, PNG, dll)\n2 = Tanggal Buat (YYYY-MM-DD)\n\nPilihan (1/2):",
        "err_title": "Gagal", "err_folder_exists": "Folder sudah ada!", "stats_remaining": "Sisa: {} foto",
        "stats_processed": "Diproses: {} foto", "btn_refresh": "🔄 Refresh (F5)", "btn_donate": "💛 Saweria"
    }
}

class PsorterUltraLiteApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "id"
        self.root.geometry("1000x680")
        self.root.configure(fg_color=BG)

        self.source_dir = self.target_dir = ""
        self.raw_file_list, self.file_list, self.undo_stack, self.pinned_folders = [], [], [], set()
        self.current_index = self.processed_files_count = 0
        self.is_copy_mode = False
        self.sort_mode = "Nama"
        self.photo_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif', '.ico', '.tiff')

        self.setup_ui()
        self.bind_shortcuts()
        self.update_ui_texts()

    def t(self, key, *args):
        return TR[self.current_lang].get(key, key).format(*args)

    def open_donation(self):
        webbrowser.open("https://saweria.co/Atillaraihan")

    def _get_sel_folder(self):
        sel = self.folder_listbox.curselection()
        if not sel: return None
        raw = self.folder_listbox.get(sel[0])
        return raw.replace("📌 ", "").split("] ")[-1] if "]" in raw else raw.replace("📌 ", "").strip()

    def _get_curr_file(self):
        if not self.file_list or self.current_index >= len(self.file_list): return None, None
        rel = self.file_list[self.current_index]
        return rel, os.path.normpath(os.path.join(self.source_dir, rel)) if not os.path.isabs(rel) else rel

    def setup_ui(self):
        # Header
        brand_frame = ctk.CTkFrame(self.root, fg_color="#000000", corner_radius=0, height=45)
        brand_frame.pack(fill=tk.X, side=tk.TOP)
        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_box.pack(side=tk.LEFT, padx=12, pady=6)
        self.lbl_brand = ctk.CTkLabel(logo_box, text="PSORTER", font=("Arial Black", 18, "bold"), text_color=RED)
        self.lbl_brand.pack(side=tk.LEFT)
        self.lbl_sub = ctk.CTkLabel(logo_box, text="  ULTRALITE (1-CORE EDITION)", font=("Arial", 9, "bold"), text_color=MUTED)
        self.lbl_sub.pack(side=tk.LEFT, pady=(3, 0))

        right_hdr = ctk.CTkFrame(brand_frame, fg_color="transparent")
        right_hdr.pack(side=tk.RIGHT, padx=12)
        self.btn_refresh = ctk.CTkButton(right_hdr, text="🔄 Refresh", command=self.refresh_data, fg_color=CARD_L, hover_color="#3A3A3A", font=("Arial", 10, "bold"), width=80)
        self.btn_refresh.pack(side=tk.RIGHT, padx=(4, 0))
        self.btn_donate = ctk.CTkButton(right_hdr, text="💛 Saweria", command=self.open_donation, fg_color=SAWERIA_Y, hover_color=SAWERIA_H, text_color="#000000", font=("Arial", 10, "bold"), width=80)
        self.btn_donate.pack(side=tk.RIGHT, padx=4)

        # Footer
        footer = ctk.CTkFrame(self.root, fg_color="#0A0A0A", corner_radius=0, height=22)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        ctk.CTkLabel(footer, text="PSORTER UltraLite • 1-Core Mode Active", font=("Arial", 9, "italic"), text_color="#666666").pack(side=tk.LEFT, padx=12, pady=1)

        # Top Bar
        top_frame = ctk.CTkFrame(self.root, fg_color=CARD, corner_radius=8)
        top_frame.pack(fill=tk.X, padx=12, pady=(8, 4))
        self.btn_src = ctk.CTkButton(top_frame, command=self.select_source_dir, fg_color=CARD_L, hover_color="#3A3A3A", font=("Arial", 11, "bold"))
        self.btn_src.pack(side=tk.LEFT, padx=8, pady=6)
        self.lbl_src = ctk.CTkLabel(top_frame, text_color="white", anchor="w")
        self.lbl_src.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.btn_dst = ctk.CTkButton(top_frame, command=self.select_target_dir, fg_color=RED, hover_color=RED_H, font=("Arial", 11, "bold"))
        self.btn_dst.pack(side=tk.LEFT, padx=8, pady=6)
        self.lbl_dst = ctk.CTkLabel(top_frame, text_color="white", anchor="w")
        self.lbl_dst.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.mode_switch = ctk.CTkSwitch(top_frame, text="Mode: PINDAH", command=self.toggle_mode_switch, progress_color=RED, button_color="white", font=("Arial", 10, "bold"))
        self.mode_switch.pack(side=tk.RIGHT, padx=12)

        # Main Workspace
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Left Panel
        self.left_frame = ctk.CTkFrame(main_frame, fg_color=CARD, corner_radius=10, width=220)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=4)
        self.left_frame.pack_propagate(False)
        self.lbl_left_title = ctk.CTkLabel(self.left_frame, font=("Arial", 11, "bold"), text_color=MUTED)
        self.lbl_left_title.pack(pady=(8, 4))

        list_box_frame = ctk.CTkFrame(self.left_frame, fg_color="#121212", corner_radius=6)
        list_box_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.folder_listbox = tk.Listbox(list_box_frame, bg="#121212", fg="white", selectbackground=RED, selectforeground="white", bd=0, highlightthickness=0, font=("Arial", 9))
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        btn_f_box = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_f_box.pack(fill=tk.X, padx=6, pady=4)
        self.btn_autosort = ctk.CTkButton(btn_f_box, text="⚡ SORTIR OTOMATIS", command=self.auto_sort_files, fg_color=RED, hover_color=RED_H, font=("Arial", 10, "bold"))
        self.btn_autosort.pack(fill=tk.X, pady=2)
        self.btn_pin_folder = ctk.CTkButton(btn_f_box, command=self.toggle_pin_folder, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_pin_folder.pack(fill=tk.X, pady=2)
        self.btn_create_folder = ctk.CTkButton(btn_f_box, command=self.create_folder, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_create_folder.pack(fill=tk.X, pady=2)
        self.btn_rename_folder = ctk.CTkButton(btn_f_box, command=self.rename_folder, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_rename_folder.pack(fill=tk.X, pady=2)
        self.btn_delete_folder = ctk.CTkButton(btn_f_box, command=self.delete_folder, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")
        self.btn_delete_folder.pack(fill=tk.X, pady=2)

        # Center Panel
        self.center_frame = ctk.CTkFrame(main_frame, fg_color=CARD, corner_radius=10)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3, pady=4)
        top_c_bar = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        top_c_bar.pack(fill=tk.X, padx=8, pady=(8, 0))
        self.lbl_sort = ctk.CTkLabel(top_c_bar, text="Urutan:", font=("Arial", 10, "bold"), text_color=MUTED)
        self.lbl_sort.pack(side=tk.RIGHT, padx=4)
        self.sort_menu = ctk.CTkOptionMenu(top_c_bar, values=["Nama", "Ukuran"], command=self.on_sort_change, fg_color=CARD_L, button_color=RED, width=80)
        self.sort_menu.pack(side=tk.RIGHT, padx=4)

        self.lbl_file_info = ctk.CTkLabel(self.center_frame, font=("Arial", 11, "bold"), text_color="white")
        self.lbl_file_info.pack(pady=2)
        preview_bg = ctk.CTkFrame(self.center_frame, fg_color="#000000", corner_radius=6)
        preview_bg.pack(fill=tk.BOTH, expand=True, padx=8, pady=2)
        self.preview_label = tk.Label(preview_bg, bg="#000000")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        self.lbl_metadata = ctk.CTkLabel(self.center_frame, text="Dimensi: - | Ukuran: -", font=("Arial", 10, "bold"), text_color=MUTED)
        self.lbl_metadata.pack(pady=4)

        # Right Panel
        self.right_frame = ctk.CTkFrame(main_frame, fg_color=CARD, corner_radius=10, width=200)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), pady=4)
        self.right_frame.pack_propagate(False)
        self.lbl_right_title = ctk.CTkLabel(self.right_frame, font=("Arial", 11, "bold"), text_color=MUTED)
        self.lbl_right_title.pack(pady=(8, 4))

        self.btn_move = ctk.CTkButton(self.right_frame, command=self.move_file, fg_color=RED, hover_color=RED_H, font=("Arial", 11, "bold"), height=42)
        self.btn_move.pack(fill=tk.X, padx=8, pady=4)
        self.btn_undo = ctk.CTkButton(self.right_frame, command=self.undo_last_action, fg_color=CARD_L, hover_color="#3A3A3A", font=("Arial", 10, "bold"))
        self.btn_undo.pack(fill=tk.X, padx=8, pady=3)
        self.btn_rename_file = ctk.CTkButton(self.right_frame, command=self.rename_file, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_rename_file.pack(fill=tk.X, padx=8, pady=3)
        self.btn_batch_rename = ctk.CTkButton(self.right_frame, command=self.batch_rename_files, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_batch_rename.pack(fill=tk.X, padx=8, pady=3)
        self.btn_delete_file = ctk.CTkButton(self.right_frame, command=self.delete_file, fg_color="#3A1214", hover_color="#52181B", text_color="#FF6B6B")
        self.btn_delete_file.pack(fill=tk.X, padx=8, pady=3)

        nav_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        nav_frame.pack(fill=tk.X, padx=8, pady=8)
        self.btn_prev = ctk.CTkButton(nav_frame, command=self.prev_file, width=75, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_prev.pack(side=tk.LEFT)
        self.btn_next = ctk.CTkButton(nav_frame, command=self.next_file, width=75, fg_color=CARD_L, hover_color="#3A3A3A")
        self.btn_next.pack(side=tk.RIGHT)

        self.lbl_counter = ctk.CTkLabel(self.right_frame, font=("Arial", 10, "bold"), text_color=MUTED)
        self.lbl_counter.pack(pady=4)
        stats_box = ctk.CTkFrame(self.right_frame, fg_color="#121212", corner_radius=6)
        stats_box.pack(fill=tk.X, padx=8, pady=(8, 8))
        self.lbl_stat_remaining = ctk.CTkLabel(stats_box, text="Sisa: 0 foto", font=("Arial", 9), text_color="white")
        self.lbl_stat_remaining.pack(pady=(4, 1))
        self.lbl_stat_processed = ctk.CTkLabel(stats_box, text="Diproses: 0 foto", font=("Arial", 9), text_color=RED)
        self.lbl_stat_processed.pack(pady=(1, 4))

    def refresh_data(self):
        if self.source_dir: self.scan_files()
        if self.target_dir: self.refresh_folder_list()

    def toggle_mode_switch(self):
        self.is_copy_mode = bool(self.mode_switch.get())
        self.mode_switch.configure(text=self.t("mode_copy" if self.is_copy_mode else "mode_move"))
        self.btn_move.configure(text=self.t("copy_btn" if self.is_copy_mode else "move_btn"))

    def on_sort_change(self, choice):
        self.sort_mode = choice
        self.apply_sort()

    def apply_sort(self):
        if not self.source_dir or not self.raw_file_list:
            self.file_list, self.current_index = [], 0
            self.preview_label.config(image="", text=self.t("no_files"), fg="white")
            self.lbl_file_info.configure(text="-")
            self.lbl_metadata.configure(text="Dimensi: - | Ukuran: -")
            self.lbl_counter.configure(text=self.t("file_counter", 0, 0))
            return

        filtered = list(self.raw_file_list)
        if self.sort_mode in ("Nama", "Name"):
            filtered.sort(key=lambda x: os.path.basename(x).lower())
        elif self.sort_mode in ("Ukuran", "Size"):
            filtered.sort(key=lambda f: os.path.getsize(os.path.join(self.source_dir, f)) if os.path.exists(os.path.join(self.source_dir, f)) else 0, reverse=True)

        self.file_list, self.current_index = filtered, 0
        self.load_current_media() if self.file_list else self.preview_label.config(image="", text=self.t("no_files"), fg="white")
        self.update_statistics()

    def update_statistics(self):
        if self.source_dir:
            self.lbl_stat_remaining.configure(text=self.t("stats_remaining", len(self.file_list)))
            self.lbl_stat_processed.configure(text=self.t("stats_processed", self.processed_files_count))

    def toggle_pin_folder(self):
        folder_name = self._get_sel_folder()
        if not folder_name:
            return messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
        self.pinned_folders.remove(folder_name) if folder_name in self.pinned_folders else self.pinned_folders.add(folder_name)
        self.refresh_folder_list()

    def auto_sort_files(self):
        if not self.source_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        if not self.target_dir: return messagebox.showwarning(self.t("warn"), self.t("warn_select_dst"))

        choice = simpledialog.askstring(self.t("dlg_autosort_title"), self.t("dlg_autosort_prompt"))
        if not choice or choice.strip() not in ("1", "2"): return

        sorted_count = 0
        for rel_or_abs in list(self.file_list):
            src_path = os.path.normpath(os.path.join(self.source_dir, rel_or_abs)) if not os.path.isabs(rel_or_abs) else rel_or_abs
            if not os.path.exists(src_path): continue

            filename = os.path.basename(src_path)
            sub_name = os.path.splitext(filename)[1].replace(".", "").upper() or "OTHERS" if choice.strip() == "1" else datetime.datetime.fromtimestamp(os.path.getmtime(src_path)).strftime('%Y-%m-%d')
            dest_folder = os.path.join(self.target_dir, sub_name)
            os.makedirs(dest_folder, exist_ok=True)

            dst_path = os.path.join(dest_folder, filename)
            if self.is_copy_mode:
                shutil.copy2(src_path, dst_path)
                self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path})
            else:
                shutil.move(src_path, dst_path)
                self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path})
                if rel_or_abs in self.raw_file_list: self.raw_file_list.remove(rel_or_abs)

            self.processed_files_count += 1
            sorted_count += 1

        self.refresh_folder_list()
        self.scan_files()
        messagebox.showinfo(self.t("done"), f"Auto-Sort Selesai! {sorted_count} foto diproses.")

    def undo_last_action(self):
        if not self.undo_stack: return
        act = self.undo_stack.pop()
        try:
            if act['action'] == 'move' and os.path.exists(act['dst']): shutil.move(act['dst'], act['src'])
            elif act['action'] == 'copy' and os.path.exists(act['dst']): os.remove(act['dst'])
            if self.processed_files_count > 0: self.processed_files_count -= 1
            self.scan_files()
        except Exception as e: messagebox.showerror(self.t("err_title"), f"Gagal undo: {e}")

    def update_ui_texts(self):
        self.root.title(self.t("title"))
        self.lbl_brand.configure(text=self.t("header_app"))
        self.lbl_sub.configure(text=self.t("header_sub"))
        self.btn_src.configure(text=self.t("select_src"))
        self.btn_dst.configure(text=self.t("select_dst"))
        self.btn_refresh.configure(text=self.t("btn_refresh"))
        self.btn_donate.configure(text=self.t("btn_donate"))

        self.lbl_src.configure(text=self.t("src_label") + (self.source_dir or self.t("not_selected")))
        self.lbl_dst.configure(text=self.t("dst_label") + (self.target_dir or self.t("not_selected")))

        self.lbl_left_title.configure(text=self.t("subfolder_frame"))
        self.btn_autosort.configure(text=self.t("autosort_btn"))
        self.btn_pin_folder.configure(text=self.t("pin_folder"))
        self.btn_create_folder.configure(text=self.t("create_folder"))
        self.btn_rename_folder.configure(text=self.t("rename_folder"))
        self.btn_delete_folder.configure(text=self.t("delete_folder"))

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

    def bind_shortcuts(self):
        self.root.bind("<Right>", lambda e: self.next_file())
        self.root.bind("<Left>", lambda e: self.prev_file())
        self.root.bind("<F5>", lambda e: self.refresh_data())
        self.root.bind("<Return>", lambda e: self.move_file())
        self.root.bind("<Delete>", lambda e: self.delete_file())
        for k in ("r", "R"): self.root.bind(k, lambda e: self.rename_file())
        for k in ("n", "N"): self.root.bind(k, lambda e: self.create_folder())
        for k in ("<Control-z>", "<Control-Z>"): self.root.bind(k, lambda e: self.undo_last_action())
        for i in range(1, 10): self.root.bind(str(i), lambda e, idx=i-1: self.quick_move_by_index(idx))

    def select_source_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_src"))
        if folder:
            self.source_dir = os.path.normpath(folder)
            self.lbl_src.configure(text=self.t("src_label") + self.source_dir)
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
        if not self.source_dir: return
        self.raw_file_list = [f for f in sorted(os.listdir(self.source_dir)) if f.lower().endswith(self.photo_exts)]
        self.apply_sort()

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
        rel, filepath = self._get_curr_file()
        if not rel:
            self.preview_label.config(image="", text=self.t("all_done"), fg="white")
            self.lbl_file_info.configure(text=self.t("done"))
            self.lbl_metadata.configure(text="Dimensi: - | Ukuran: -")
            self.lbl_counter.configure(text=self.t("file_counter", len(self.file_list), len(self.file_list)))
            return

        self.lbl_file_info.configure(text=rel)
        self.lbl_counter.configure(text=self.t("file_counter", self.current_index + 1, len(self.file_list)))
        self.display_image_and_meta(filepath)

    def display_image_and_meta(self, filepath):
        try:
            if not os.path.exists(filepath): return
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            with Image.open(filepath) as img:
                w, h = img.width, img.height
                img.thumbnail((560, 400), Image.Resampling.NEAREST)
                img_tk = ImageTk.PhotoImage(img)

            self.preview_label.config(image=img_tk, text="")
            self.preview_label.image = img_tk
            self.lbl_metadata.configure(text=f"Dimensi: {w}x{h} | Ukuran: {size_mb:.2f} MB")
        except Exception as e:
            self.preview_label.config(image="", text=self.t("err_load_img", e), fg="red")

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
        old_name = self._get_sel_folder()
        if not old_name: return messagebox.showwarning(self.t("warn"), self.t("warn_select_ren_folder"))
        new_name = simpledialog.askstring(self.t("dlg_rename_folder_title"), self.t("dlg_rename_folder_prompt", old_name), initialvalue=old_name)
        if new_name and new_name.strip() != old_name:
            os.rename(os.path.join(self.target_dir, old_name), os.path.join(self.target_dir, new_name.strip()))
            if old_name in self.pinned_folders:
                self.pinned_folders.remove(old_name)
                self.pinned_folders.add(new_name.strip())
            self.refresh_folder_list()

    def delete_folder(self):
        folder_name = self._get_sel_folder()
        if not folder_name: return messagebox.showwarning(self.t("warn"), self.t("warn_select_del_folder"))
        if messagebox.askyesno(self.t("dlg_delete_folder_title"), self.t("dlg_delete_folder_prompt", folder_name)):
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
        rel, src_path = self._get_curr_file()
        target_folder_name = self._get_sel_folder()
        if not rel: return
        if not target_folder_name: return messagebox.showwarning(self.t("warn"), self.t("warn_select_sub"))

        dst_path = os.path.join(self.target_dir, target_folder_name, os.path.basename(src_path))
        if self.is_copy_mode:
            shutil.copy2(src_path, dst_path)
            self.undo_stack.append({'action': 'copy', 'src': src_path, 'dst': dst_path})
        else:
            shutil.move(src_path, dst_path)
            self.undo_stack.append({'action': 'move', 'src': src_path, 'dst': dst_path})
            self.raw_file_list.remove(rel)

        self.processed_files_count += 1
        self.apply_sort()

    def rename_file(self):
        rel, old_path = self._get_curr_file()
        if not rel: return
        old_filename = os.path.basename(old_path)
        new_filename = simpledialog.askstring(self.t("dlg_rename_file_title"), self.t("dlg_rename_file_prompt"), initialvalue=old_filename)
        if new_filename and new_filename.strip() != old_filename:
            new_path = os.path.join(os.path.dirname(old_path), new_filename.strip())
            os.rename(old_path, new_path)
            self.raw_file_list[self.raw_file_list.index(rel)] = os.path.relpath(new_path, self.source_dir)
            self.apply_sort()

    def batch_rename_files(self):
        if not self.file_list: return messagebox.showwarning(self.t("warn"), self.t("warn_no_files"))
        prefix = simpledialog.askstring(self.t("dlg_batch_rename_title"), self.t("dlg_batch_rename_prompt"), initialvalue="PHOTO")
        if not prefix or not prefix.strip(): return

        prefix, temp_file_map = prefix.strip(), []
        for i, rel in enumerate(self.file_list):
            old_path = os.path.normpath(os.path.join(self.source_dir, rel)) if not os.path.isabs(rel) else rel
            old_fn = os.path.basename(old_path)
            p_dir, ext = os.path.dirname(old_path), os.path.splitext(old_fn)[1]
            temp_path = os.path.join(p_dir, f"__temp_psorter_{i}_{old_fn}")
            try:
                os.rename(old_path, temp_path)
                temp_file_map.append((temp_path, p_dir, ext, rel))
            except Exception as e:
                messagebox.showerror(self.t("err_title"), f"Gagal merename foto {old_fn}: {e}")
                return self.scan_files()

        for i, (temp_path, p_dir, ext, rel) in enumerate(temp_file_map):
            final_path = os.path.join(p_dir, f"{prefix}_{i+1}{ext}")
            os.rename(temp_path, final_path)
            self.raw_file_list[self.raw_file_list.index(rel)] = os.path.relpath(final_path, self.source_dir)

        self.apply_sort()

    def delete_file(self):
        rel, filepath = self._get_curr_file()
        if not rel: return
        if messagebox.askyesno(self.t("dlg_delete_file_title"), self.t("dlg_delete_file_prompt", os.path.basename(rel))):
            os.remove(filepath)
            self.raw_file_list.remove(rel)
            self.apply_sort()

    def next_file(self):
        if self.current_index < len(self.file_list) - 1:
            self.current_index += 1
            self.load_current_media()

    def prev_file(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_media()

if __name__ == "__main__":
    root = ctk.CTk()
    app = PsorterUltraLiteApp(root)
    root.mainloop()