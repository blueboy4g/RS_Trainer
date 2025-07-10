import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import os
import sys
import requests
import webbrowser

from config.config import *

# ----------------- Config -----------------
CURRENT_VERSION = "1.1.0"
VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version.json"

APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

last_boss_selected_save = os.path.join(APPDATA_DIR, "last_boss_selected.txt")
last_rotation_selected_save = os.path.join(APPDATA_DIR, "last_rotation_selected.txt")
KEYBINDS_FILE = os.path.join(APPDATA_DIR, "keybinds.json")
BUILD_ROTATION_FILE = os.path.join(APPDATA_DIR, "build_rotation.txt")
DEFAULT_BUILD_ROTATION_FILE = os.path.join("config", "build_rotation.txt")
from pathlib import Path

APPDATA_BOSS_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "Azulyn" / "boss_rotations"
SOURCE_BOSS_DIR = Path("boss_rotations")
APPDATA_BOSS_DIR.mkdir(parents=True, exist_ok=True)

BOSS_FILE = os.path.join(APPDATA_BOSS_DIR, "demo.json")

ICON_PATH = "Resources/azulyn_builder_icon.ico"
# ------------------------------------------

if not os.path.exists(BUILD_ROTATION_FILE):
    if os.path.exists(DEFAULT_BUILD_ROTATION_FILE):
        shutil.copy(DEFAULT_BUILD_ROTATION_FILE, BUILD_ROTATION_FILE)

for file in SOURCE_BOSS_DIR.glob("*.json"):
    target = APPDATA_BOSS_DIR / file.name
    if not target.exists():
        shutil.copy(file, target)

def check_for_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        notes = data.get("notes", "")
        if latest_version != CURRENT_VERSION:
            if messagebox.askyesno("Update Available", f"New version {latest_version} available:\n\n{notes}\n\nDownload now?"):
                webbrowser.open(download_url)
        else:
            messagebox.showinfo("No Update", f"You're running the latest version ({CURRENT_VERSION})")
    except Exception as e:
        messagebox.showerror("Update Check Failed", str(e))

def load_last_used_boss():
    if os.path.exists(last_boss_selected_save):
        with open(last_boss_selected_save, 'r') as f:
            return f.read().strip()
    return BOSS_FILE

def load_last_pvm_rot():
    if os.path.exists(last_rotation_selected_save):
        with open(last_rotation_selected_save, 'r') as f:
            return f.read().strip()
    return BUILD_ROTATION_FILE

def save_current_config():
    with open(last_boss_selected_save, 'w') as f:
        f.write(last_used_boss.get())

def start_script(exe_path, log_output=False, args=None):
    full_path = os.path.abspath(exe_path)
    args = args or []
    def run():
        try:
            process = subprocess.Popen(
                [full_path] + args,
                cwd=os.path.dirname(full_path),
                stdout=subprocess.PIPE if log_output else None,
                stderr=subprocess.STDOUT if log_output else None,
                text=True
            )
            if log_output:
                log_text.delete("1.0", tk.END)
                for line in process.stdout:
                    log_text.insert(tk.END, line)
                    log_text.see(tk.END)
                process.wait()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {exe_path}:\n{e}")
    threading.Thread(target=run).start()

def open_file_editor(filepath):
    if not os.path.isfile(filepath):
        messagebox.showerror("Error", f"File not found: {filepath}")
        return
    subprocess.Popen([get_default_editor(), filepath])

def get_default_editor():
    return os.environ.get("EDITOR", "notepad")

# def browse_rotation_file():
#     file_path = filedialog.askopenfilename(
#         initialdir=str(APPDATA_BOSS_DIR),
#         title="Select Rotation File",
#         filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
#     )
#     if file_path:
#         last_used_boss.set(file_path)
#         last_used_boss_trimmed_string = last_used_boss.get().split("/")[-1].split("\\")[-1]
#         last_used_boss_trimmed_string = last_used_boss_trimmed_string.replace(".json", "")
#         last_used_boss_trimmed.set(last_used_boss_trimmed_string)
#         save_current_config()

def open_donation():
    webbrowser.open("https://buymeacoffee.com/azulyn")

def open_discord():
    webbrowser.open("https://discord.gg/Sp7Sh52B")

def open_youtube():
    webbrowser.open("https://www.youtube.com/@Azulyn1")

# --------------- UI Setup ----------------
root = tk.Tk()
root.title("RuneScape Trainer Rotation Builder")
root.geometry("475x340")
root.iconbitmap(ICON_PATH)

# Dark button styling
style = ttk.Style()
style.theme_use("default")
style.configure("Dark.TButton", foreground="white", background="#444", padding=6)
style.map("Dark.TButton", background=[("active", "#555")])

last_used_boss = tk.StringVar(value=load_last_used_boss())
last_used_pvm_rot = tk.StringVar(value=load_last_pvm_rot())
key_bind_config = tk.StringVar(value=KEYBINDS_FILE)


ascii_title = r"""
   _____               .__                
  /  _  \ __________ __|  | ___.__. ____  
 /  /_\  \\___   /  |  \  |<   |  |/    \ 
/    |    \/    /|  |  /  |_\___  |   |  \
\____|__  /_____ \____/|____/ ____|___|  /
        \/      \/          \/         \/ 
"""

# Layout Frames
top_frame = tk.Frame(root)
top_frame.pack(pady=5, fill="x")

# tk.Label(
#     top_frame,
#     text='RuneScape Trainer',
#     font='Helvetica 12 bold',
#     foreground="black",
# ).pack(pady=0)

left = tk.Frame(top_frame)
right = tk.Frame(top_frame)
left.pack(side="left", padx=5, expand=True, fill="both")
right.pack(side="right", padx=5, expand=True, fill="both")

log_frame = tk.Frame(root)
log_frame.pack(pady=0, fill="both")

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=(15, 0))

footer = tk.Frame(root)
footer.pack(side="right", pady=(20, 0))

# ttk.Button(left, text="Start RS Overlay", style="Gray.TButton",
#            command=lambda: start_script("scripts/RS_Overlay.exe", args=[last_used_boss.get()])).pack(pady=2, fill="x")
# ttk.Button(left, text="Edit Keybinds", style="Gray.TButton",
#            command=lambda: open_file_editor(key_bind_config.get())).pack(pady=2, fill="x")

# tk.Label(left, text="Current Boss:").pack(pady=(5, 2))
#
# last_used_boss_trimmed = last_used_boss.get().split("/")[-1].split("\\")[-1]
# last_used_boss_trimmed = last_used_boss_trimmed.replace(".json", "")
# last_used_boss_trimmed = tk.StringVar(value=last_used_boss_trimmed)
# tk.Entry(left, textvariable=last_used_boss_trimmed, width=40).pack()

# ttk.Button(right, text="Start RS Trainer", style="Gray.TButton",
#            command=lambda: start_script("scripts/RS_Trainer.exe", args=[last_used_boss.get()])).pack(pady=2, fill="x")
# ttk.Button(right, text="Select Boss Script", style="Gray.TButton",
#            command=browse_rotation_file).pack(pady=2, fill="x")

#trim everything but the .json name at the end
last_used_pvm_rot_trimmed = last_used_pvm_rot.get().split("/")[-1].split("\\")[-1]
#trim everything the .json name at the end
last_used_pvm_rot_trimmed = last_used_pvm_rot_trimmed.replace(".txt", "")
last_used_pvm_rot_trimmed = tk.StringVar(value=last_used_pvm_rot_trimmed)

# tk.Label(log_frame, text="Rotation Path:").pack(pady=(0, 2))
# tk.Entry(log_frame, textvariable=last_used_pvm_rot_trimmed, width=40).pack()

# Log Output
tk.Label(log_frame, text="Build Rotation Log:").pack()
log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
log_text.pack(padx=5, pady=(0, 2))

ttk.Button(log_frame, text="Build Rotation", style="Gray.TButton",
           command=lambda: start_script("scripts/rotation_creation.exe", log_output=True)).pack(pady=2, fill="x")

ttk.Button(log_frame, text="Edit Build Rotation File", style="Gray.TButton",
           command=lambda: open_file_editor(last_used_pvm_rot.get())).pack(pady=2, fill="x")

ttk.Button(bottom_frame, text="Clear Log", style="Gray.TButton",
           command=lambda: log_text.delete("1.0", tk.END)).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Check for Updates", style="Gray.TButton",
           command=check_for_update).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Azulyn Youtube", style="Gray.TButton",
           command=open_youtube).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Azulyn Discord", style="Gray.TButton",
           command=open_discord).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Donate", style="Gray.TButton",
           command=open_donation).pack(side="left", padx=5, pady=1)

# tk.Label(
#     footer,
#     text=ascii_title,
#     font=("Courier", 3),
#     justify="right",
#     anchor="w",
#     foreground="blue",
# ).pack(side="left", padx=5, pady=0)

tk.Label(footer, font=("Courier", 8), text=f"Current Version: {CURRENT_VERSION}").pack(side="right", padx=5, pady=0)


root.mainloop()
