"""
Rocket League Custom Map Loader
─────────────────────────────────
Swap custom training maps into Rocket League without modifying game code.
Works alongside Easy Anti-Cheat (offline asset swap only).

Requirements: pip install customtkinter Pillow
"""

import customtkinter as ctk
import json
import shutil
import os
import sys
from tkinter import filedialog, messagebox
from PIL import Image

# ──────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────
APP_NAME = "RL Map Loader"
APP_VERSION = "1.0"
CONFIG_FILE = "rl_map_loader_config.json"
TARGET_MAP = "Labs_Underpass_P.upk"
BACKUP_MAP = "Labs_Underpass_P_ORIGINAL.upk"
COOKED_SUBPATH = os.path.join("TAGame", "CookedPCConsole")
THUMB_EXTENSIONS = (".jfif", ".jpg", ".jpeg", ".png", ".webp", ".bmp")
THUMB_SIZE = (280, 158)

# ──────────────────────────────────────────────────────
# Colors
# ──────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C_BG = "#0f1117"
C_CARD = "#1a1d27"
C_ACCENT = "#00b4d8"
C_ACCENT_HOVER = "#0096c7"
C_SUCCESS = "#2dc653"
C_DANGER = "#e63946"
C_TEXT = "#e8eaed"
C_TEXT_DIM = "#8b8fa3"
C_BORDER = "#2a2e3d"
C_ACTIVE_BADGE = "#1a2a30"


class RLMapLoader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("900x700")
        self.minsize(750, 550)
        self.configure(fg_color=C_BG)

        self.config_data = self._load_config()
        self.maps = []
        self.active_map = None
        self.map_widgets = []
        self._image_refs = []

        self._build_ui()
        self._detect_active_map()
        self._refresh_maps()

    # ──────────────────────────────────────────────────
    # Config
    # ──────────────────────────────────────────────────
    def _config_path(self):
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, CONFIG_FILE)

    def _load_config(self):
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"rl_path": "", "maps_folder": ""}

    def _save_config(self):
        with open(self._config_path(), "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)

    # ──────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=20, pady=(12, 4))
        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame,
            text="⚽  RL Map Loader",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=C_TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text=f"  v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color=C_TEXT_DIM,
        ).pack(side="left", padx=(4, 0), pady=(6, 0))

        # Status badge
        self.status_frame = ctk.CTkFrame(header, fg_color=C_CARD, corner_radius=8)
        self.status_frame.pack(side="right", fill="y", pady=8)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="  No map loaded  ",
            font=ctk.CTkFont(size=12),
            text_color=C_TEXT_DIM,
        )
        self.status_label.pack(padx=12, pady=4)

        # ── Settings bar ──
        settings = ctk.CTkFrame(
            self,
            fg_color=C_CARD,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        settings.pack(fill="x", padx=20, pady=(4, 8))

        # Rocket League path
        rl_row = ctk.CTkFrame(settings, fg_color="transparent")
        rl_row.pack(fill="x", padx=15, pady=(10, 3))

        ctk.CTkLabel(
            rl_row,
            text="Rocket League:",
            width=120,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C_TEXT,
        ).pack(side="left")

        self.rl_path_var = ctk.StringVar(value=self.config_data.get("rl_path", ""))
        ctk.CTkEntry(
            rl_row,
            textvariable=self.rl_path_var,
            height=30,
            fg_color=C_BG,
            border_color=C_BORDER,
            text_color=C_TEXT,
            placeholder_text="Select Rocket League install folder...",
        ).pack(side="left", fill="x", expand=True, padx=(8, 8))

        ctk.CTkButton(
            rl_row,
            text="Browse",
            width=90,
            height=30,
            fg_color=C_ACCENT,
            hover_color=C_ACCENT_HOVER,
            command=self._browse_rl,
        ).pack(side="right")

        # Maps folder path
        maps_row = ctk.CTkFrame(settings, fg_color="transparent")
        maps_row.pack(fill="x", padx=15, pady=(3, 10))

        ctk.CTkLabel(
            maps_row,
            text="Maps Folder:",
            width=120,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C_TEXT,
        ).pack(side="left")

        self.maps_path_var = ctk.StringVar(
            value=self.config_data.get("maps_folder", "")
        )
        ctk.CTkEntry(
            maps_row,
            textvariable=self.maps_path_var,
            height=30,
            fg_color=C_BG,
            border_color=C_BORDER,
            text_color=C_TEXT,
            placeholder_text="Select folder with custom maps...",
        ).pack(side="left", fill="x", expand=True, padx=(8, 8))

        ctk.CTkButton(
            maps_row,
            text="Browse",
            width=90,
            height=30,
            fg_color=C_ACCENT,
            hover_color=C_ACCENT_HOVER,
            command=self._browse_maps,
        ).pack(side="right")

        # ── Action buttons ──
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 4))

        self.restore_btn = ctk.CTkButton(
            btn_row,
            text="🔄  Restore Original",
            height=34,
            fg_color=C_DANGER,
            hover_color="#c1121f",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._restore_original,
        )
        self.restore_btn.pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="🔃  Refresh",
            height=34,
            fg_color="#2a2e3d",
            hover_color="#363b4f",
            font=ctk.CTkFont(size=13),
            command=self._refresh_maps,
        ).pack(side="left", padx=(10, 0))

        ctk.CTkButton(
            btn_row,
            text="📂  Open RL Maps",
            height=34,
            fg_color="#2a2e3d",
            hover_color="#363b4f",
            font=ctk.CTkFont(size=13),
            command=self._open_cooked_folder,
        ).pack(side="right")

        # ── Maps list header ──
        self.maps_count_label = ctk.CTkLabel(
            self,
            text="Maps (0)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        )
        self.maps_count_label.pack(fill="x", padx=22, pady=(4, 2))

        # ── Scrollable map list ──
        self.maps_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=C_BORDER,
            scrollbar_button_hover_color=C_ACCENT,
        )
        self.maps_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.maps_scroll.columnconfigure(0, weight=1)

        self.placeholder = ctk.CTkLabel(
            self.maps_scroll,
            text="Set Rocket League path and maps folder above to get started ☝️",
            font=ctk.CTkFont(size=14),
            text_color=C_TEXT_DIM,
        )
        self.placeholder.grid(row=0, column=0, pady=60)

    # ──────────────────────────────────────────────────
    # Browsing
    # ──────────────────────────────────────────────────
    def _browse_rl(self):
        path = filedialog.askdirectory(title="Select Rocket League folder")
        if path:
            self.rl_path_var.set(path)
            self.config_data["rl_path"] = path
            self._save_config()
            self._detect_active_map()
            self._refresh_maps()

    def _browse_maps(self):
        path = filedialog.askdirectory(title="Select custom maps folder")
        if path:
            self.maps_path_var.set(path)
            self.config_data["maps_folder"] = path
            self._save_config()
            self._refresh_maps()

    # ──────────────────────────────────────────────────
    # Map scanning
    # ──────────────────────────────────────────────────
    def _scan_maps(self):
        maps_folder = self.maps_path_var.get()
        if not maps_folder or not os.path.isdir(maps_folder):
            return []

        found = []
        for entry in sorted(os.scandir(maps_folder), key=lambda e: e.name.lower()):
            if not entry.is_dir():
                continue

            upk_file = None
            thumb_file = None

            for f in os.scandir(entry.path):
                if f.is_file():
                    low = f.name.lower()
                    if low.endswith(".upk") and upk_file is None:
                        upk_file = f.path
                    if any(low.endswith(ext) for ext in THUMB_EXTENSIONS):
                        if thumb_file is None or low.startswith(
                            entry.name.lower().replace(" ", "_")
                        ):
                            thumb_file = f.path

            if upk_file:
                found.append(
                    {
                        "name": entry.name.replace("_", " "),
                        "folder": entry.path,
                        "upk": upk_file,
                        "thumb": thumb_file,
                        "upk_size_mb": round(
                            os.path.getsize(upk_file) / (1024 * 1024), 1
                        ),
                    }
                )

        return found

    # ──────────────────────────────────────────────────
    # Active map detection
    # ──────────────────────────────────────────────────
    def _get_cooked_path(self):
        rl = self.rl_path_var.get()
        if not rl:
            return None
        return os.path.join(rl, COOKED_SUBPATH)

    def _detect_active_map(self):
        cooked = self._get_cooked_path()
        if not cooked:
            self.active_map = None
            return

        backup = os.path.join(cooked, BACKUP_MAP)
        meta_path = os.path.join(cooked, "rl_map_loader_meta.json")

        if os.path.exists(backup):
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    self.active_map = meta.get("active_map", "Unknown map")
                except Exception:
                    self.active_map = "Unknown map"
            else:
                self.active_map = "Unknown map"
        else:
            self.active_map = None

    def _update_status(self):
        if self.active_map:
            self.status_label.configure(
                text=f"  ▶  {self.active_map}  ", text_color=C_SUCCESS
            )
            self.status_frame.configure(fg_color=C_ACTIVE_BADGE)
        else:
            self.status_label.configure(text="  No map loaded  ", text_color=C_TEXT_DIM)
            self.status_frame.configure(fg_color=C_CARD)

    # ──────────────────────────────────────────────────
    # UI refresh
    # ──────────────────────────────────────────────────
    def _refresh_maps(self):
        self._image_refs.clear()
        for w in self.map_widgets:
            w.destroy()
        self.map_widgets.clear()

        self.maps = self._scan_maps()
        self.maps_count_label.configure(text=f"Maps ({len(self.maps)})")
        self._update_status()

        if not self.maps:
            self.placeholder.grid(row=0, column=0, pady=60)
            if self.maps_path_var.get():
                self.placeholder.configure(
                    text="No maps found in the selected folder (.upk)"
                )
            else:
                self.placeholder.configure(
                    text="Set Rocket League path and maps folder above to get started ☝️"
                )
            return

        self.placeholder.grid_forget()

        for i, map_data in enumerate(self.maps):
            try:
                card = self._create_map_card(map_data)
                card.grid(row=i, column=0, sticky="ew", pady=(0, 6))
                self.map_widgets.append(card)
            except Exception as e:
                print(f"[WARN] Failed to create card for '{map_data['name']}': {e}")

    def _create_map_card(self, map_data):
        is_active = self.active_map == map_data["name"]

        card = ctk.CTkFrame(
            self.maps_scroll,
            fg_color=C_CARD,
            corner_radius=10,
            border_width=2,
            border_color=C_SUCCESS if is_active else C_BORDER,
            height=100,
        )
        card.grid_propagate(False)
        card.columnconfigure(1, weight=1)

        # ── Thumbnail ──
        thumb_frame = ctk.CTkFrame(
            card, fg_color="#000000", corner_radius=8, width=140, height=80
        )
        thumb_frame.grid(row=0, column=0, padx=(10, 0), pady=10)
        thumb_frame.pack_propagate(False)

        if map_data["thumb"]:
            try:
                img = Image.open(map_data["thumb"])
                img = img.resize(THUMB_SIZE, Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(136, 76))
                self._image_refs.append(ctk_img)
                ctk.CTkLabel(thumb_frame, image=ctk_img, text="").pack(expand=True)
            except Exception:
                ctk.CTkLabel(
                    thumb_frame,
                    text="🗺️",
                    font=ctk.CTkFont(size=24),
                    text_color=C_TEXT_DIM,
                ).pack(expand=True)
        else:
            ctk.CTkLabel(
                thumb_frame, text="🗺️", font=ctk.CTkFont(size=24), text_color=C_TEXT_DIM
            ).pack(expand=True)

        # ── Info (middle) ──
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, padx=(12, 0), pady=10, sticky="nsw")

        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(anchor="w")

        ctk.CTkLabel(
            name_row,
            text=map_data["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C_TEXT,
        ).pack(side="left")

        if is_active:
            ctk.CTkLabel(
                name_row,
                text="  ACTIVE  ",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=C_SUCCESS,
                fg_color=C_ACTIVE_BADGE,
                corner_radius=4,
            ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            info,
            text=f"📦 {map_data['upk_size_mb']} MB  •  📁 {os.path.basename(map_data['upk'])}",
            font=ctk.CTkFont(size=11),
            text_color=C_TEXT_DIM,
            anchor="w",
        ).pack(anchor="w", pady=(1, 0))

        ctk.CTkLabel(
            info,
            text=f"Path: {map_data['folder']}",
            font=ctk.CTkFont(size=10),
            text_color="#5a5e72",
            anchor="w",
        ).pack(anchor="w")

        # ── Button (right) ──
        if is_active:
            btn = ctk.CTkButton(
                card,
                text="✓  Loaded",
                height=38,
                width=110,
                fg_color=C_SUCCESS,
                hover_color="#25a244",
                font=ctk.CTkFont(size=13, weight="bold"),
                state="disabled",
            )
        else:
            btn = ctk.CTkButton(
                card,
                text="▶  Load Map",
                height=38,
                width=110,
                fg_color=C_ACCENT,
                hover_color=C_ACCENT_HOVER,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda m=map_data: self._load_map(m),
            )
        btn.grid(row=0, column=2, padx=(0, 12), pady=10)

        return card

    # ──────────────────────────────────────────────────
    # Map loading
    # ──────────────────────────────────────────────────
    def _ensure_backup(self):
        cooked = self._get_cooked_path()
        if not cooked:
            return False

        target = os.path.join(cooked, TARGET_MAP)
        backup = os.path.join(cooked, BACKUP_MAP)

        if not os.path.exists(target):
            messagebox.showerror(
                "Error",
                f"File {TARGET_MAP} was not found.\n\n"
                f"Expected path:\n{target}\n\n"
                "Check your Rocket League path.",
            )
            return False

        if not os.path.exists(backup):
            try:
                shutil.copy2(target, backup)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup original map:\n{e}")
                return False

        return True

    def _save_meta(self, map_name):
        cooked = self._get_cooked_path()
        if cooked:
            meta_path = os.path.join(cooked, "rl_map_loader_meta.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump({"active_map": map_name}, f, ensure_ascii=False)

    def _load_map(self, map_data):
        cooked = self._get_cooked_path()
        if not cooked or not os.path.isdir(cooked):
            messagebox.showerror(
                "Error",
                "CookedPCConsole folder was not found.\n"
                "Check your Rocket League path.",
            )
            return

        if not self._ensure_backup():
            return

        target = os.path.join(cooked, TARGET_MAP)

        try:
            shutil.copy2(map_data["upk"], target)
            self._save_meta(map_data["name"])
            self.active_map = map_data["name"]
            self._refresh_maps()

            messagebox.showinfo(
                "Done! 🎮",
                f"Map \"{map_data['name']}\" has been loaded!\n\n"
                "Now in Rocket League go to:\n"
                "Play → Exhibition/Freeplay → Underpass\n\n"
                "Enjoy your training! 🚀",
            )
        except PermissionError:
            messagebox.showerror(
                "Error",
                "Permission denied.\n"
                "Try running the app as Administrator,\n"
                "or close Rocket League if it's running.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map:\n{e}")

    def _restore_original(self):
        cooked = self._get_cooked_path()
        if not cooked:
            messagebox.showwarning("Warning", "Set Rocket League path first.")
            return

        backup = os.path.join(cooked, BACKUP_MAP)
        target = os.path.join(cooked, TARGET_MAP)

        if not os.path.exists(backup):
            messagebox.showinfo(
                "Info", "Original map is already active (no backup found)."
            )
            return

        try:
            shutil.copy2(backup, target)
            os.remove(backup)
            meta_path = os.path.join(cooked, "rl_map_loader_meta.json")
            if os.path.exists(meta_path):
                os.remove(meta_path)
            self.active_map = None
            self._refresh_maps()
            messagebox.showinfo("Done", "Original Underpass map has been restored! ✓")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore map:\n{e}")

    def _open_cooked_folder(self):
        cooked = self._get_cooked_path()
        if cooked and os.path.isdir(cooked):
            os.startfile(cooked)
        else:
            messagebox.showwarning("Warning", "CookedPCConsole folder was not found.")


# ──────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app = RLMapLoader()
    app.mainloop()
