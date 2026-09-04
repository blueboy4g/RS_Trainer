import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess, threading, os, sys, json, requests, webbrowser
import ctypes
from pathlib import Path
from config.config import *
from order_key_binds import reorder_keybinds_json

CURRENT_VERSION = "1.3.0"
VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version.json"
APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)
last_boss_selected_save = os.path.join(APPDATA_DIR, "last_boss_selected.txt")
last_rotation_selected_save = os.path.join(APPDATA_DIR, "last_rotation_selected.txt")
KEYBINDS_FILE = os.path.join(APPDATA_DIR, "keybinds.json")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
BUILD_ROTATION_FILE = os.path.join(APPDATA_DIR, "build_rotation.txt")
DEFAULT_BUILD_ROTATION_FILE = os.path.join("config", "build_rotation.txt")
SETTINGS_FILE = os.path.join(APPDATA_DIR, "ui_settings.json")
SOURCE_BOSS_DIR = "boss_rotations"
# frozen (exe): bundled via --add-data into _MEIPASS; dev: resources/ next to this file
if getattr(sys, "frozen", False):
    ICON_PATH = os.path.join(sys._MEIPASS, "resources", "azulyn_icon.ico")
else:
    ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "azulyn_icon.ico"))
YOUTUBE_URL = "https://www.youtube.com/@Azulyn1"
DISCORD_URL = "https://discord.gg/uhnJpVkXpu"
DONATE_URL = "https://buymeacoffee.com/azulyn"
ROTATION_CREATOR_URL = "https://blueboy4g.github.io/RS_Rotation_Creator/"

THEMES = {
    "classic": {
        "font": "MS Sans Serif",
        "bg": "#c0c0c0", "panel": "#c0c0c0", "card": "#c0c0c0", "entry": "#ffffff",
        "fg": "#000000", "muted": "#404040", "faint": "#808080", "accent": "#000080", "accent_hover": "#1084d0",
        "border": "#808080", "btn_bg": "#c0c0c0", "btn_hi": "#dfdfdf", "accent_btn": "#c0c0c0",
        "btn_fg": "#000000", "sel_fg": "#000000", "rain": False, "header": "#000080", "header_fg": "#ffffff",
        "hdr_h": 52, "accent_border": "#000080",
    },
    "midnight": {
        "font": "Segoe UI",
        "bg": "#161b2c", "panel": "#1b2236", "card": "#1f2740", "entry": "#252e4a",
        "fg": "#e8e9ee", "muted": "#9aa3bd", "faint": "#5d6580", "accent": "#5b8dff", "accent_hover": "#7ba4ff",
        "border": "#39415e", "btn_bg": "#232c48", "btn_hi": "#323d63", "accent_btn": "#3d64c4",
        "btn_fg": "#ffffff", "sel_fg": "#ffffff", "rain": False, "header": "#0b1020", "header_fg": "#e8e9ee",
        "hdr_h": 56, "accent_border": "#5b8dff",
    },
    "matrix": {
        "font": "Consolas",
        "bg": "#050805", "panel": "#0a120a", "card": "#0a120a", "entry": "#061006",
        "fg": "#00ff41", "muted": "#2e7d3a", "faint": "#1d5426", "accent": "#1f8f38", "accent_hover": "#0f5c22",
        "border": "#1d6b2f", "btn_bg": "#0a1a0c", "btn_hi": "#123812", "accent_btn": "#003b12",
        "btn_fg": "#00ff41", "sel_fg": "#001100", "rain": True, "header": "#04140a", "header_fg": "#00ff41",
        "hdr_h": 76, "accent_border": "#1f8f38",
    },
    "osrs": {
        "font": "Segoe UI",
        "bg": "#3e3529", "panel": "#494034", "card": "#52473a", "entry": "#2e2820",
        "fg": "#ff981f", "muted": "#c9b892", "faint": "#8a7a5c", "accent": "#6f5d3f", "accent_hover": "#8a744e",
        "border": "#6a5a3f", "btn_bg": "#5c4f3d", "btn_hi": "#6f5f49", "accent_btn": "#7a5c2e",
        "btn_fg": "#ffcf70", "sel_fg": "#ffffff", "rain": False, "header": "#2e2820", "header_fg": "#ff981f",
        "hdr_h": 56, "accent_border": "#ff981f",
    },
    "rs3": {
        "font": "Segoe UI",
        "bg": "#10131a", "panel": "#161b26", "card": "#1d2330", "entry": "#12161f",
        "fg": "#e6d9a8", "muted": "#9a917a", "faint": "#6b6350", "accent": "#f5c542", "accent_hover": "#ffd766",
        "border": "#3a4356", "btn_bg": "#232b3d", "btn_hi": "#2f3a52", "accent_btn": "#3d3524",
        "btn_fg": "#f5d97e", "sel_fg": "#ffffff", "rain": False, "header": "#0a0c12", "header_fg": "#f5d97e",
        "hdr_h": 56, "accent_border": "#f5c542",
    },
}

def load_ui_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_ui_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

UI_SETTINGS = load_ui_settings()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RS Trainer")
        w, h = UI_SETTINGS.get("win_w", 560), UI_SETTINGS.get("win_h", 394)
        self.minsize(500, 374)
        self.geometry(f"{w}x{h}")
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                pass
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        self.trainer_proc = None
        self.overlay_proc = None
        self._rain_state = None
        self._rain_job = None
        self._meteor_job = None
        self._meteor_id = None
        self._twinkle_job = None
        self._twinkle_set = []
        self._stars = []
        self._sky_state = None
        self._sky_job = None
        self._twinkle = 0.0
        self.theme_name = UI_SETTINGS.get("theme", "midnight")
        if self.theme_name not in THEMES:
            self.theme_name = "midnight"
        self.T = THEMES[self.theme_name]
        self._build_style()
        self._build_ui()
        self._apply_theme()
        if self.T["rain"]:
            self._animate_rain()
        self.bind("<Configure>", self._on_first_configure, add="+")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_first_configure(self, event):
        if event.widget is not self:
            return
        self.unbind("<Configure>")
        self._on_first_configure = lambda e: None
        # window is now mapped with its real size; redraw the header art
        # (it was first drawn before mapping, when winfo_width() was tiny)
        self.after(50, self._apply_theme)
    # ---------- styling ----------
    def _build_style(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    def _apply_theme(self):
        T = self.T
        st = self.style
        self.configure(bg=T["bg"])
        st.configure("TFrame", background=T["bg"])
        st.configure("TLabel", background=T["bg"], foreground=T["fg"], font=(T["font"], 10))
        st.configure("Muted.TLabel", background=T["bg"], foreground=T["muted"], font=(T["font"], 9))
        st.configure("Head.TLabel", background=T["bg"], foreground=T["fg"], font=(T["font"], 15, "bold"))
        st.configure("Btn.TButton", background=T["btn_bg"], foreground=T["btn_fg"], bordercolor=T["border"],
                     borderwidth=1, relief="flat", focusthickness=0, font=(T["font"], 10, "bold"), padding=6)
        st.configure("Link.TButton", background=T["btn_bg"], foreground=T["btn_fg"], bordercolor=T["border"],
                     borderwidth=1, relief="flat", focusthickness=0, font=(T["font"], 8, "bold"), padding=1)
        st.map("Link.TButton",
               background=[("active", T["btn_hi"]), ("pressed", T["accent_btn"])],
               foreground=[("active", T["btn_fg"]), ("pressed", T["btn_fg"])],
               bordercolor=[("active", T["border"])])
        st.map("Btn.TButton",
               background=[("active", T["btn_hi"]), ("pressed", T["accent_btn"])],
               foreground=[("active", T["btn_fg"]), ("pressed", T["btn_fg"])],
               bordercolor=[("active", T["accent"])])
        st.configure("Accent.Btn.TButton", background=T["accent_btn"], foreground=T["btn_fg"], bordercolor=T["accent_border"],
                     borderwidth=2, relief="flat", focusthickness=0, font=(T["font"], 10, "bold"), padding=6)
        st.map("Accent.Btn.TButton",
               background=[("active", T["btn_hi"]), ("pressed", T["accent_btn"])],
               bordercolor=[("active", T["accent_border"]), ("pressed", T["accent_border"])])
        st.configure("TCombobox", fieldbackground=T["entry"], background=T["btn_bg"], foreground=T["fg"],
                     arrowcolor=T["fg"], bordercolor=T["border"], lightcolor=T["border"], darkcolor=T["border"])
        st.map("TCombobox", fieldbackground=[("readonly", T["entry"])], foreground=[("readonly", T["fg"])])
        self.option_add("*TCombobox*Listbox.background", T["entry"])
        if self.theme_name == "classic":
            st.configure("Btn.TButton", relief="raised", borderwidth=2)
            st.configure("Accent.Btn.TButton", relief="raised", borderwidth=2)
            st.configure("Link.TButton", relief="raised", borderwidth=2, font=("MS Sans Serif", 8, "bold"), padding=2)
            # Win95 sunken inputs with the classic double-ridge look
            st.configure("TCombobox", relief="sunken", borderwidth=2,
                         lightcolor="#404040", darkcolor="#ffffff",
                         bordercolor="#808080")
            st.configure("TFrame", background=T["bg"])
            self.card.configure(highlightbackground="#ffffff", highlightthickness=1)
        self.option_add("*TCombobox*Listbox.foreground", T["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", T["accent"])
        self.option_add("*TCombobox*Font", (T["font"], 11))
        for wdg, key in self._theme_widgets:
            wdg.configure(**key(T))
        if T["rain"] and not self._rain_job:
            self._animate_rain()
        elif not T["rain"] and self._rain_job:
            self.after_cancel(self._rain_job)
            self._rain_job = None
            self.rain.delete("all")
        if self.theme_name == "midnight" and not self._meteor_job:
            self._schedule_meteor()
        elif self.theme_name != "midnight" and self._meteor_job:
            self.after_cancel(self._meteor_job)
            self._meteor_job = None
            self.rain.delete("meteor")
        if self.theme_name != "midnight" and self._twinkle_job:
            self.after_cancel(self._twinkle_job)
            self._twinkle_job = None
            for sid, base in getattr(self, "_stars", []):
                try:
                    self.rain.itemconfigure(sid, fill=base)
                except Exception:
                    pass
        self.rain.delete("hdr")
        self.rain.configure(bg=T["header"])
        name = "matrix" if T["rain"] else ("classic" if T["header"] == "#000080" else "midnight")
        self.title_lbl.configure(bg=T["header"], fg=T["header_fg"])
        self.ver_lbl.configure(bg=T["header"], fg=T["muted"])
        if self.theme_name == "classic":
            self.ver_lbl.place_forget()   # fully hidden: caption buttons own this corner
        else:
            self.ver_lbl.configure(text="v" + CURRENT_VERSION + " // azulyn")
            self.ver_lbl.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-4, in_=self.rain)
        if self._hdr_icon is not None:
            self.rain.create_image(18, 32, image=self._hdr_icon, anchor="w", tags="hdr")
        hw = max(self.rain.winfo_width(), 320)
        hh = T["hdr_h"]
        self.rain.create_line(0, hh - 1, hw, hh - 1, fill=T["border"], tags="hdr")
        if self.theme_name == "osrs":
            # stone header with a gold/bronze double trim, OSRS-style
            self.rain.create_line(0, hh - 4, hw, hh - 4, fill="#ff981f", tags="hdr")
            self.rain.create_line(0, hh - 7, hw, hh - 7, fill="#7a5c2e", tags="hdr")
        if self.theme_name == "rs3":
            # sleek near-black header with a thin gold pinstripe
            self.rain.create_line(0, hh - 4, hw, hh - 4, fill="#f5c542", tags="hdr")
        if self.theme_name == "classic":
            # Win95 caption buttons, inset from the right edge and vertically centered
            by0, by1 = hh // 2 - 10, hh // 2 + 10
            for bx, glyph in ((hw - 66, "_"), (hw - 44, "[]")):
                self.rain.create_rectangle(bx, by0, bx + 20, by1, fill="#c0c0c0", outline="#000000", tags="hdr")
                self.rain.create_text(bx + 10, (by0 + by1) // 2 + 1, text=glyph, font=("Segoe UI", 8, "bold"), fill="#000000", tags="hdr")
            self.rain.create_rectangle(hw - 22, by0, hw - 2, by1, fill="#c0c0c0", outline="#000000", tags="hdr")
            self.rain.create_text(hw - 12, (by0 + by1) // 2 + 1, text="x", font=("Segoe UI", 9, "bold"), fill="#000000", tags="hdr")
        if self.theme_name == "midnight":
            import random as _rnd
            self._stars = []
            for _ in range(90):
                x = _rnd.randrange(0, hw)
                y = _rnd.randrange(4, 54)
                s = _rnd.choice([1, 1, 1, 2])   # mostly 1px, occasional 2px
                c = _rnd.choice(["#ffffff", "#cfd8ff", "#8fa3ff", "#ffffff"])
                sid = self.rain.create_oval(x, y, x + s, y + s, fill=c, outline="", tags="hdr")
                self._stars.append((sid, c))
        else:
            self._stars = []
        if self.theme_name == "midnight":
            # round crescent moon: full circle minus an offset dark circle
            mx, my, mr = hw - 88, 20, 11
            self.rain.create_oval(mx - mr, my - mr, mx + mr, my + mr, fill="#f5f3ce", outline="#e8e0a0", tags="hdr")
            self.rain.create_oval(mx - mr + 7, my - mr - 3, mx + mr + 7, my + mr - 3, fill=T["header"], outline="", tags="hdr")
            if not self._twinkle_job:
                self._start_twinkle()
            else:
                # stars were redrawn with new ids; restart the loop so it
                # animates the current items, not the deleted ones
                self.after_cancel(self._twinkle_job)
                self._twinkle_job = None
                self._start_twinkle()

    def _start_twinkle(self):
        import random
        # a rotating subset of stars blinks fully out and back, on its own phase/speed
        self._twinkle_set = []
        for sid, c in getattr(self, "_stars", []):
            if random.random() < 0.3:
                self._twinkle_set.append([sid, c, random.random() * 6.28, random.uniform(0.08, 0.35)])
        self._twinkle_step()

    def _twinkle_step(self):
        import colorsys, math
        self._twinkle_job = None
        if self.theme_name != "midnight" or not self.rain.winfo_exists():
            return
        bg = self.T["header"]
        br = int(bg[1:3], 16); bgc = int(bg[3:5], 16); bb = int(bg[5:7], 16)
        for entry in self._twinkle_set:
            sid, base, phase, speed = entry
            entry[2] += speed
            t = (math.sin(entry[2]) + 1) / 2  # 0..1 oscillation
            # fade between the star color and the header bg (fully invisible at min)
            r = int(base[1:3], 16); g = int(base[3:5], 16); b = int(base[5:7], 16)
            nr = int(br + (r - br) * t)
            ng = int(bgc + (g - bgc) * t)
            nb = int(bb + (b - bb) * t)
            self.rain.itemconfigure(sid, fill="#%02x%02x%02x" % (nr, ng, nb))
        self._twinkle_job = self.after(40, self._twinkle_step)

    def _build_ui(self):
        self._theme_widgets = []
        self.rain = tk.Canvas(self, height=0, bg="#000000", highlightthickness=0)
        self.rain.pack(fill="x")
        self._hdr_icon = None
        try:
            from PIL import Image, ImageTk
            self._hdr_icon = ImageTk.PhotoImage(Image.open(ICON_PATH).resize((28, 28)))
        except Exception:
            try:
                self._hdr_icon = tk.PhotoImage(file=ICON_PATH)
            except Exception:
                self._hdr_icon = None
        self.title_lbl = tk.Label(self.rain, text="R5_TR41N3R", font=("Consolas", 16, "bold"))
        self.title_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.ver_lbl = tk.Label(self, text="v" + CURRENT_VERSION + " // azulyn", font=("Segoe UI", 8))

        self.card = tk.Frame(self, highlightthickness=1)
        self.card.pack(fill="both", expand=True, padx=14, pady=8)

        boss_row = tk.Frame(self.card)
        boss_row.pack(fill="x", padx=12, pady=(12, 4))
        self.boss_lbl = tk.Label(boss_row, text="BOSS:", font=("Segoe UI", 10, "bold"))
        self.boss_lbl.pack(side="left")
        self.boss_var = tk.StringVar()
        self.boss_combo = ttk.Combobox(boss_row, textvariable=self.boss_var, state="readonly", font=("Segoe UI", 11))
        self.boss_combo.pack(side="left", fill="x", expand=True, padx=(10, 4), ipady=3)
        self.boss_combo.bind("<<ComboboxSelected>>", self.on_boss_selected)
        self.rotation_files = sorted(Path(APPDATA_DIR, "boss_rotations").glob("*.json")) if Path(APPDATA_DIR, "boss_rotations").exists() else []
        names = [f.stem for f in self.rotation_files]
        self.boss_combo["values"] = names
        if names:
            last = ""
            try:
                last = open(last_boss_selected_save).read().strip()
            except Exception:
                pass
            self.boss_var.set(last if last in names else names[0])

        btns = tk.Frame(self.card)
        btns.pack(fill="x", padx=12, pady=10)
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        self.btn_trainer = ttk.Button(btns, text="> START TRAINER", style="Accent.Btn.TButton", command=self.start_trainer)
        self.btn_trainer.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.btn_overlay = ttk.Button(btns, text="> START OVERLAY", style="Accent.Btn.TButton", command=self.start_overlay)
        self.btn_overlay.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.btn_keybinds = ttk.Button(btns, text="EDIT KEYBINDS", style="Btn.TButton", command=self.edit_keybinds)
        self.btn_keybinds.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.btn_config = ttk.Button(btns, text="EDIT CONFIG", style="Btn.TButton", command=self.edit_config)
        self.btn_config.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.btn_scripts = ttk.Button(btns, text="BOSS SCRIPTS FOLDER", style="Btn.TButton", command=self.select_boss_script)
        self.btn_scripts.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)

        srow = tk.Frame(self.card)
        srow.pack(side="bottom", fill="x", padx=12, pady=(8, 10))
        self.status_tag = tk.Label(srow, text="STATUS:", font=("Segoe UI", 9, "bold"))
        self.status_tag.pack(side="left")
        self.status_var = tk.StringVar(value="idle")
        self.status_lbl = tk.Label(srow, textvariable=self.status_var, font=("Segoe UI", 9, "bold"))
        self.status_lbl.pack(side="left", padx=(8, 0))

        links = tk.Frame(self)
        links.pack(fill="x", padx=17, pady=(2, 12))
        links.columnconfigure(0, weight=2)
        links.columnconfigure(1, weight=3)
        links.columnconfigure(2, weight=2)
        links.columnconfigure(3, weight=4)
        links.columnconfigure(4, weight=2)
        links.columnconfigure(5, weight=2)
        self.link_btns = []
        for i, (text, cmd) in enumerate((("UPDATES", self.check_updates), ("YOUTUBE", lambda: self.open_link(YOUTUBE_URL)), ("DISCORD", lambda: self.open_link(DISCORD_URL)), ("BUILD ROT", self.build_rotation), ("THEMES", self.pick_theme), ("DONATE", lambda: self.open_link(DONATE_URL)))):
            b = ttk.Button(links, text=text, style="Link.TButton", command=cmd)
            b.grid(row=0, column=i, sticky="ew", padx=3)
            self.link_btns.append(b)

        # widgets that need live recolor on theme switch
        self._theme_widgets = [
            (self.rain, lambda T: {"bg": T["header"], "height": T["hdr_h"]}),
            (self.title_lbl, lambda T: {"bg": T["header"], "fg": T["header_fg"], "font": (T["font"], 16, "bold"), "text": "R5_TR41N3R" if T["rain"] else "RS TRAINER"}),
            (self.ver_lbl, lambda T: {"bg": T["header"], "fg": T["muted"], "font": (T["font"], 8)}),
            (self.card, lambda T: {"bg": T["panel"], "highlightbackground": "#ffffff" if T["header"] == "#000080" else T["border"]}),
            (self.boss_lbl, lambda T: {"bg": T["panel"], "fg": T["muted"]}),
            (self.status_tag, lambda T: {"bg": T["panel"], "fg": T["faint"]}),
            (self.status_lbl, lambda T: {"bg": T["panel"], "fg": T["fg"]}),
        ]
        for fr in (boss_row, btns, srow, links):
            self._theme_widgets.append((fr, lambda T: {"bg": T["panel"]}))

    def pick_theme(self):
        dlg = tk.Toplevel(self)
        dlg.title("Themes")
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(bg=self.T["panel"])
        tk.Label(dlg, text="SELECT THEME", bg=self.T["panel"], fg=self.T["fg"], font=(self.T["font"], 11, "bold")).pack(padx=16, pady=(14, 8))
        for name in THEMES:
            row = tk.Frame(dlg, bg=self.T["panel"])
            row.pack(fill="x", padx=16, pady=3)
            cur = " [current]" if name == self.theme_name else ""
            tk.Button(row, text=name + cur, bg=self.T["btn_bg"], fg=self.T["fg"], activebackground=self.T["btn_hi"],
                      activeforeground=self.T["fg"], relief="flat", font=(self.T["font"], 10), anchor="w",
                      command=lambda n=name: self._set_theme(n, dlg)).pack(fill="x", ipady=4)
        tk.Button(dlg, text="close", bg=self.T["btn_bg"], fg=self.T["muted"], relief="flat", command=dlg.destroy).pack(pady=(6, 12))

    def _set_theme(self, name, dlg=None):
        self.theme_name = name
        self.T = THEMES[name]
        save_ui_settings({**UI_SETTINGS, "theme": name})
        self._apply_theme()
        if dlg:
            dlg.destroy()
        self._set_status("theme: " + name)

    def _animate_rain(self):
        import random
        if not self.T["rain"]:
            self._rain_job = None
            return
        w = max(self.rain.winfo_width(), 400)
        hh = self.rain.winfo_height() or self.T["hdr_h"]
        rows = max(4, hh // 12)          # fill the taller header top to bottom
        cols = w // 12
        if not self._rain_state or len(self._rain_state) != cols:
            self._rain_state = [random.randint(-rows, 0) for _ in range(cols)]
        self.rain.delete("drop")
        glyphs = "01!?#$%&*+=<>"
        for i, y in enumerate(self._rain_state):
            x = i * 12 + 6
            yy = (y % rows) * (hh / rows)
            self.rain.create_text(x, yy, text=random.choice(glyphs), fill=self.T["muted"], font=("Consolas", 8), tags="drop")
        self._rain_state = [(y + 1) for y in self._rain_state]
        self._rain_job = self.after(150, self._animate_rain)

    def _schedule_meteor(self):
        import random
        # random delay 6-18s between shooting stars
        self._meteor_job = self.after(random.randint(6000, 18000), self._launch_meteor)

    def _launch_meteor(self):
        import random
        self._meteor_job = None
        if self.theme_name != "midnight":
            return
        w = max(self.rain.winfo_width(), 400)
        # spawn fully out of view: either above the top edge or left of the
        # canvas, so the star falls into view instead of popping in
        if random.random() < 0.6:
            x0 = random.randint(-40, int(w * 0.7))
            y0 = random.randint(-24, -6)   # above the header
        else:
            x0 = random.randint(-44, -30)  # left of the header
            y0 = random.randint(-10, 30)
        # generous step budget; the star exits via the out-of-view check below
        self._meteor_step(x0, y0, 200)

    def _meteor_step(self, x, y, steps_left):
        if self.theme_name != "midnight" or not self.rain.winfo_exists():
            return
        self.rain.delete("meteor")
        w = self.rain.winfo_width()
        # only stop when the WHOLE streak (head + tail) is out of view:
        # past the right edge, or below the bottom of the header
        if x - 26 > w + 4 or y - 8 > 56:
            self._schedule_meteor()
            return
        # streak: bright head with a tail trailing behind (opposite the motion vector)
        self.rain.create_line(x, y, x - 26, y - 8, fill="#ffffff", width=1, tags="meteor")
        self.rain.create_line(x - 10, y - 3, x - 26, y - 8, fill="#8fa3ff", width=1, tags="meteor")
        self.rain.create_oval(x - 1, y - 1, x + 2, y + 2, fill="#ffffff", outline="", tags="meteor")
        self._meteor_id = self.after(40, self._meteor_step, x + 9, y + 3, steps_left - 1)

    def _set_status(self, text):
        self.status_var.set(text)

    def _proc_running(self, proc):
        return proc is not None and proc.poll() is None

    def start_trainer(self):
        if self._proc_running(self.trainer_proc):
            self._set_status("trainer already running")
            return
        if not self.boss_var.get():
            messagebox.showinfo("Select a boss", "Choose a boss rotation first.")
            return
        self.trainer_proc = self._launch("trainer")
        self._set_status("trainer running" if self._proc_running(self.trainer_proc) else "trainer failed to start")

    def start_overlay(self):
        if self._proc_running(self.overlay_proc):
            self._set_status("overlay already running")
            return
        self.overlay_proc = self._launch("overlay")
        self._set_status("overlay running" if self._proc_running(self.overlay_proc) else "overlay failed to start")

    def _launch(self, which):
        # resolve the scripts dir relative to this app (works installed,
        # portable from dist_final, and from source)
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)          # ...\RS Trainer or ...\dist_final
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        exe = os.path.join(base, "scripts", "rs_trainer.exe" if which == "trainer" else "rs_overlay.exe")
        if not os.path.exists(exe):
            messagebox.showerror("Launch failed", f"Not found:\n{exe}")
            return None
        args = []
        if which == "trainer":
            # boss_var holds the rotation stem; trainer expects a path to the .json
            boss_dir = os.path.join(APPDATA_DIR, "boss_rotations")
            args = [os.path.join(boss_dir, self.boss_var.get() + ".json")]
        elif which == "overlay":
            # old app passed the boss path to the overlay too
            boss_dir = os.path.join(APPDATA_DIR, "boss_rotations")
            args = [os.path.join(boss_dir, self.boss_var.get() + ".json")]
        try:
            return subprocess.Popen([exe] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(exe))
        except Exception as e:
            messagebox.showerror("Launch failed", f"Failed to launch {exe}:\n{e}")
            return None

    def on_boss_selected(self, event=None):
        try:
            with open(last_boss_selected_save, "w") as f:
                f.write(self.boss_var.get())
        except Exception:
            pass

    def select_boss_script(self):
        boss_dir = os.path.join(APPDATA_DIR, "boss_rotations")
        os.makedirs(boss_dir, exist_ok=True)
        webbrowser.open(boss_dir)

    def edit_keybinds(self):
        # old app launched the key_binds GUI editor next to the app; fall back to notepad
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        kb_exe = os.path.join(base, "key_binds.exe")
        if os.path.exists(kb_exe):
            subprocess.Popen([kb_exe], cwd=base)
        else:
            subprocess.Popen(["notepad.exe", KEYBINDS_FILE])

    def edit_config(self):
        subprocess.Popen(["notepad.exe", CONFIG_FILE])

    def build_rotation(self):
        # keep keybinds ordered, then open the web-based rotation creator
        try:
            reorder_keybinds_json()
        except Exception as e:
            messagebox.showerror("Build rotation", str(e))
            return
        webbrowser.open(ROTATION_CREATOR_URL)
        self._set_status("rotation creator opened in browser")

    def open_link(self, url):
        webbrowser.open(url)

    def check_updates(self):
        try:
            r = requests.get(VERSION_URL, timeout=5)
            data = r.json()
            latest = data.get("version", CURRENT_VERSION)
            if latest != CURRENT_VERSION:
                self._set_status("update available: v" + latest)
                download_url = data.get("download_url")
                if messagebox.askyesno("Update Available",
                                       f"New version {latest} available.\n\nOpen the download page?"):
                    webbrowser.open(download_url if download_url else VERSION_URL)
            else:
                self._set_status("up to date")
        except Exception:
            self._set_status("could not check for updates")

    def on_close(self):
        for job in (self._rain_job, self._meteor_job, self._meteor_id, self._twinkle_job):
            if job:
                try:
                    self.after_cancel(job)
                except Exception:
                    pass
        s = {"win_w": self.winfo_width(), "win_h": self.winfo_height(), "theme": self.theme_name}
        save_ui_settings({**UI_SETTINGS, **s})
        self.destroy()

if __name__ == "__main__":
    App().mainloop()
