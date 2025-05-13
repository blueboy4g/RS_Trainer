import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys

import requests
import webbrowser

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version.json"

def check_for_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        notes = data.get("notes", "")

        if latest_version != CURRENT_VERSION:
            message = f"A new version ({latest_version}) is available!\n\nChanges:\n{notes}\n\nDownload now?"
            if messagebox.askyesno("Update Available", message):
                webbrowser.open(download_url)
        else:
            messagebox.showinfo("No Update", f"You are running the latest version ({CURRENT_VERSION}).")

    except Exception as e:
        messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{e}")


CONFIG_SAVE_FILE = "Config/last_config.txt"
CONFIG_SAVE_FILE2 = "Config/last_config2.txt"

def load_last_used_config():
    if os.path.exists(CONFIG_SAVE_FILE):
        with open(CONFIG_SAVE_FILE, 'r') as f:
            return f.read().strip()
    return "Boss_Rotations/Telos_Necro.json"

def load_last_used_config2():
    if os.path.exists(CONFIG_SAVE_FILE2):
        with open(CONFIG_SAVE_FILE2, 'r') as f:
            return f.read().strip()
    return "PVM_Discord.txt"

def save_current_config():
    with open(CONFIG_SAVE_FILE, 'w') as f:
        f.write(config_path.get())

def start_script(exe_path, log_output=False, args=None):
    full_path = os.path.abspath(exe_path)
    script_dir = os.path.dirname(full_path)
    args = args or []

    def run():
        try:
            process = subprocess.Popen(
                [full_path] + args,
                cwd=script_dir,
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

    editor = get_default_editor()
    try:
        subprocess.Popen([editor, filepath])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file with {editor}:\n{e}")

def get_default_editor():
    return os.environ.get("EDITOR", "notepad")

def browse_config_file():
    file_path = filedialog.askopenfilename(
        title="Select Config File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if file_path:
        config_path.set(file_path)
        save_current_config()

def open_current_config():
    open_file_editor(config_path.get())

def open_key_bind_config():
    open_file_editor(key_bind_config.get())

def open_txt_file():
    file_path = filedialog.askopenfilename(
        title="Select TXT File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        open_file_editor(file_path)

def open_rotation_txt():
    open_file_editor(config_path2.get())

def browse_rotation_file():
    file_path = filedialog.askopenfilename(
        initialdir="Boss_Rotations",
        title="Select Rotation File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if file_path:
        # Make path relative to current working directory
        rel_path = os.path.relpath(file_path)
        config_path.set(rel_path)
        save_current_config()

# ✅ Tkinter Setup
root = tk.Tk()
root.title("Runescape Trainer")
root.iconbitmap("Resources/azulyn_icon.ico")  # ✅ Set your icon here

# ✅ Track config file path
config_path = tk.StringVar(value=load_last_used_config())
config_path2 = tk.StringVar(value=load_last_used_config2())
key_bind_config = tk.StringVar(value="Config.json")

# --- Script Buttons ---
tk.Button(root, text="Start RS Trainer", command=lambda: start_script("RS_Trainer.exe", args=[config_path.get()])).pack(pady=5)
tk.Button(root, text="Start RS Overlay", command=lambda: start_script("RS_Overlay.exe", args=[config_path.get()])).pack(pady=5)

# --- Rotation Builder ---
tk.Label(root, text="Current Rotation:").pack()
tk.Entry(root, textvariable=config_path, width=50).pack(padx=10)
tk.Button(root, text="Browse Rotation File", command=browse_rotation_file).pack(pady=5)

tk.Button(root, text="Build Rotation", command=lambda: start_script("Rotation_Creation.exe", log_output=True)).pack(pady=5)

# --- Config Controls ---
tk.Label(root, text="Rotation Path:").pack()
tk.Entry(root, textvariable=config_path2, width=50).pack(padx=10)
# tk.Button(root, text="Browse Config File", command=browse_config_file).pack(pady=5)
tk.Button(root, text="Edit Rotation", command=open_rotation_txt).pack(pady=5)

tk.Button(root, text="Edit Keybinds", command=open_key_bind_config).pack(pady=5)
# tk.Button(root, text="Open TXT File to Edit", command=open_txt_file).pack(pady=5)
# --- Log Output Area ---
tk.Label(root, text="Build Rotation Log:").pack()
log_text = tk.Text(root, height=10, width=70, wrap=tk.WORD)
log_text.pack(padx=10, pady=5)

# --- Clear Log Button ---
tk.Button(root, text="Clear Log", command=lambda: log_text.delete("1.0", tk.END)).pack(pady=5)
tk.Label(root, text=f"Current Version: {CURRENT_VERSION}").pack(pady=2)
tk.Button(root, text="Check for Updates", command=check_for_update).pack(pady=5)

root.mainloop()
