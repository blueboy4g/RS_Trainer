import subprocess
import threading
import webbrowser
from tkinter import filedialog
from tkinter import ttk

import requests

from config.config import *
from order_key_binds import reorder_keybinds_json

# ----------------- Config -----------------
CURRENT_VERSION = "1.1.1"
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
BOSS_SCRIPT_LIST_FILE = os.path.join(APPDATA_DIR, "boss_script_list.json")
BOSS_SCRIPT_DISPLAY_FILE = os.path.join(APPDATA_DIR, "boss_script_display.json")
from pathlib import Path

APPDATA_BOSS_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "Azulyn" / "boss_rotations"
SOURCE_BOSS_DIR = Path("boss_rotations")
APPDATA_BOSS_DIR.mkdir(parents=True, exist_ok=True)

BOSS_FILE = os.path.join(APPDATA_BOSS_DIR, "azulyn_telos_2499_necro.json")

ICON_PATH = "Resources/azulyn_icon.ico"
# ------------------------------------------

with open("config/keybinds.json", "r", encoding="utf-8") as f:
    print("Loading default keybinds from: ", "config/keybinds.json")
    default_keybinds = json.load(f)

# Check for missing keys under "ABILITY_KEYBINDS"
missing_keybinds = {key: value for key, value in default_keybinds["ABILITY_KEYBINDS"].items() if
                    key not in keybind_config["ABILITY_KEYBINDS"]}

if missing_keybinds:
    # Add missing keys to "ABILITY_KEYBINDS"
    keybind_config["ABILITY_KEYBINDS"].update(missing_keybinds)

    # Save the updated user keybinds without reformatting other entries
    with open(USER_KEYBINDS, "w", encoding="utf-8") as f:
        json.dump(keybind_config, f, indent=4, separators=(',', ': '))
    print(f"Added missing keybinds under 'ABILITY_KEYBINDS': {missing_keybinds}")
else:
    print("All keybinds under 'ABILITY_KEYBINDS' are already present.")

if not os.path.exists(BUILD_ROTATION_FILE):
    if os.path.exists(DEFAULT_BUILD_ROTATION_FILE):
        shutil.copy(DEFAULT_BUILD_ROTATION_FILE, BUILD_ROTATION_FILE)

for boss_file in SOURCE_BOSS_DIR.glob("*.json"):
    target = APPDATA_BOSS_DIR / boss_file.name
    if not target.exists():
        shutil.copy(boss_file, target)


def check_for_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        notes = data.get("notes", "")
        if latest_version != CURRENT_VERSION:
            if messagebox.askyesno("Update Available",
                                   f"New version {latest_version} available:\n\n{notes}\n\nDownload now?"):
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
            # TODO: THIS VARIABLE IS NOT BEING USED!
            process = subprocess.Popen(
                [full_path] + args,
                cwd=os.path.dirname(full_path),
                stdout=subprocess.PIPE if log_output else None,
                stderr=subprocess.STDOUT if log_output else None,
                text=True
            )
            # if log_output:
            #     log_text.delete("1.0", tk.END)
            #     for line in process.stdout:
            #         log_text.insert(tk.END, line)
            #         log_text.see(tk.END)
            #     process.wait()
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


def browse_rotation_file():
    file_path = filedialog.askopenfilename(
        initialdir=str(APPDATA_BOSS_DIR),
        title="Select Rotation File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if file_path:
        last_used_boss.set(file_path)
        last_used_boss_trimmed_string = last_used_boss.get().split("/")[-1].split("\\")[-1]
        last_used_boss_trimmed_string = last_used_boss_trimmed_string.replace(".json", "")
        last_used_boss_trimmed.set(last_used_boss_trimmed_string)
        save_current_config()


def open_donation():
    webbrowser.open("https://buymeacoffee.com/azulyn")


def open_discord():
    webbrowser.open("https://discord.gg/Sp7Sh52B")


def open_rotation():
    webbrowser.open("https://blueboy4g.github.io/RS_Rotation_Creator/")


def open_youtube():
    webbrowser.open("https://www.youtube.com/@Azulyn1")


def format_filename_for_display(filename):
    """Convert filename to display format: remove underscores and capitalize words"""
    name = filename.replace(".json", "").replace("_", " ")
    return " ".join(word.capitalize() for word in name.split())


def load_boss_script_list():
    """Load the boss script list from JSON file"""
    if os.path.exists(BOSS_SCRIPT_LIST_FILE):
        try:
            with open(BOSS_SCRIPT_LIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []
    return []


def save_boss_script_list(script_list):
    """Save the boss script list to JSON file"""
    try:
        with open(BOSS_SCRIPT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(script_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save boss script list: {e}")


def load_boss_script_display_list():
    """Load the display list (scripts that should be shown to user)"""
    if os.path.exists(BOSS_SCRIPT_DISPLAY_FILE):
        try:
            with open(BOSS_SCRIPT_DISPLAY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []
    return []


def save_boss_script_display_list(display_list):
    """Save the display list to JSON file"""
    try:
        with open(BOSS_SCRIPT_DISPLAY_FILE, 'w', encoding='utf-8') as f:
            json.dump(display_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save boss script display list: {e}")


def validate_and_clean_script_list():
    """Check if files in the list exist and remove non-existent ones"""
    script_list = load_boss_script_list()
    valid_scripts = []

    for script_path in script_list:
        if os.path.exists(script_path):
            valid_scripts.append(script_path)

    # Add default boss rotation files from APPDATA_BOSS_DIR if not already in list
    for boss_script_file in APPDATA_BOSS_DIR.glob("*.json"):
        file_path = str(boss_script_file)
        if file_path not in valid_scripts:
            valid_scripts.append(file_path)

    # Save the cleaned list
    save_boss_script_list(valid_scripts)
    return valid_scripts


def clean_existing_display_list():
    """Check if files in the display list exist and remove non-existent ones"""
    display_list = load_boss_script_display_list()
    valid_scripts = []

    for script_path in display_list:
        if os.path.exists(script_path):
            valid_scripts.append(script_path)

    # Only save if there were changes
    if len(valid_scripts) != len(display_list):
        save_boss_script_display_list(valid_scripts)
    
    return valid_scripts


def check_and_add_new_default_scripts():
    """Check for new default scripts in APPDATA_BOSS_DIR and add them to the list"""
    current_scripts = load_boss_script_list()
    new_scripts = []
    
    # Check for new default scripts in the Azulyn boss_rotations folder
    for new_script_file in APPDATA_BOSS_DIR.glob("*.json"):
        file_path = str(new_script_file)
        if file_path not in current_scripts:
            current_scripts.append(file_path)
            filename = os.path.basename(file_path)
            display_name = format_filename_for_display(filename)
            new_scripts.append((file_path, display_name))  # Return both path and display name
    
    # Save the updated list if new scripts were found
    if new_scripts:
        save_boss_script_list(current_scripts)
    
    return current_scripts, new_scripts


def refresh_display_list_only():
    """Clean existing display scripts without checking for new ones"""
    # Get the current display list and clean it
    current_display_list = load_boss_script_display_list()
    valid_display_scripts = []
    
    # Clean up any non-existent files from display list
    for script_path in current_display_list:
        if os.path.exists(script_path):
            valid_display_scripts.append(script_path)
    
    # Save cleaned display list if there were changes
    if len(valid_display_scripts) != len(current_display_list):
        save_boss_script_display_list(valid_display_scripts)
    
    return valid_display_scripts


def check_for_new_scripts_and_update_display():
    """Check for new default scripts and add them to display list"""
    # Check for new default scripts (this updates the complete script list only)
    all_scripts, new_scripts = check_and_add_new_default_scripts()
    
    # Only add truly NEW scripts to the display list
    if new_scripts:
        current_display_list = load_boss_script_display_list()
        # new_scripts contains tuples of (file_path, display_name)
        for file_path, display_name in new_scripts:
            # Only add if it's not already in display list
            if file_path not in current_display_list:
                current_display_list.append(file_path)
        
        # Save the updated display list since we added new scripts
        save_boss_script_display_list(current_display_list)
        return current_display_list, new_scripts
    
    return load_boss_script_display_list(), []


def initialize_boss_script_list():
    """Initialize boss script list on program startup"""
    # Initialize the complete script list (for detection purposes)
    complete_list = validate_and_clean_script_list()
    
    # Initialize the display list if it doesn't exist
    if not os.path.exists(BOSS_SCRIPT_DISPLAY_FILE):
        # First time - copy all default scripts to display list
        save_boss_script_display_list(complete_list.copy())
    
    return complete_list


def reload_default_scripts():
    """Reload default scripts and reset the list"""
    try:
        # Get all default scripts from the boss_rotations directory
        default_scripts = []
        for default_script_file in APPDATA_BOSS_DIR.glob("*.json"):
            default_scripts.append(str(default_script_file))
        
        # Save only the default scripts
        save_boss_script_list(default_scripts)
        return default_scripts
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reload default scripts: {e}")
        return []


def load_custom_display_names():
    """Load custom display names from JSON file"""
    custom_names_file = os.path.join(APPDATA_DIR, "boss_script_custom_names.json")
    if os.path.exists(custom_names_file):
        try:
            with open(custom_names_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def save_custom_display_names(custom_names):
    """Save custom display names to JSON file"""
    custom_names_file = os.path.join(APPDATA_DIR, "boss_script_custom_names.json")
    try:
        with open(custom_names_file, 'w', encoding='utf-8') as f:
            json.dump(custom_names, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save custom names: {e}")


def get_display_name(script_path, custom_names):
    """Get display name for a script (custom name if exists, otherwise formatted filename)"""
    if script_path in custom_names:
        return custom_names[script_path]
    else:
        filename = os.path.basename(script_path)
        return format_filename_for_display(filename)


def open_boss_script_selection():
    """Open the boss script selection window"""
    selection_window = tk.Toplevel(root)
    selection_window.withdraw()  # Hide window initially to fix the issue of it appearing in the wrong spot briefly
    selection_window.title("Select Boss Script")
    selection_window.geometry("500x450")
    selection_window.resizable(False, False)
    selection_window.transient(root)

    # Title label
    title_label = tk.Label(selection_window, text="Choose a boss script or load your own",
                           font=("Arial", 12))
    title_label.pack(pady=10)

    # Frame for listbox and scrollbar
    list_frame = tk.Frame(selection_window)
    list_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Listbox with scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    script_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
    script_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=script_listbox.yview)

    # Store the actual file paths and custom names
    script_paths = []
    custom_names = load_custom_display_names()

    def refresh_script_list():
        """Refresh the script list display (without checking for new scripts)"""
        nonlocal script_paths, custom_names
        script_listbox.delete(0, tk.END)
        
        # Get the current display list (this is what the user should see)
        script_paths = load_boss_script_display_list()
        
        # Clean up any non-existent files from display list and track removed ones
        valid_scripts = []
        removed_scripts = []
        
        for script_path in script_paths:
            if os.path.exists(script_path):
                valid_scripts.append(script_path)
            else:
                # Track removed scripts for notification
                filename = os.path.basename(script_path)
                display_name = format_filename_for_display(filename)
                removed_scripts.append(display_name)
        
        # Save cleaned display list if there were changes
        if len(valid_scripts) != len(script_paths):
            save_boss_script_display_list(valid_scripts)
            script_paths = valid_scripts
            
            # Notify user about removed scripts
            if removed_scripts:
                if len(removed_scripts) == 1:
                    message = f"The following boss script file was not found and has been removed from the list:\n\n• {removed_scripts[0]}\n\nThe file may have been deleted or moved."
                    title = "Script File Missing"
                else:
                    script_list = "\n".join(f"• {name}" for name in removed_scripts)
                    message = f"The following boss script files were not found and have been removed from the list:\n\n{script_list}\n\nThe files may have been deleted or moved."
                    title = "Script Files Missing"
                
                messagebox.showwarning(title, message)
        
        custom_names = load_custom_display_names()

        for script_path in script_paths:
            display_name = get_display_name(script_path, custom_names)
            script_listbox.insert(tk.END, display_name)

    def check_for_new_scripts_on_startup():
        """Check for new default scripts only when window is first opened"""
        nonlocal script_paths, custom_names
        
        # Get current state
        current_complete_list = load_boss_script_list()
        current_display_list = load_boss_script_display_list()
        
        # Find truly NEW scripts (exist on disk but not in complete list)
        new_scripts = []
        scripts_added_to_complete = False
        
        for new_script_file in APPDATA_BOSS_DIR.glob("*.json"):
            file_path = str(new_script_file)
            if file_path not in current_complete_list:
                # This is a truly new script
                current_complete_list.append(file_path)
                scripts_added_to_complete = True
                
                filename = os.path.basename(file_path)
                display_name = format_filename_for_display(filename)
                new_scripts.append((file_path, display_name))
                
                # Add to display list too (since it's new)
                if file_path not in current_display_list:
                    current_display_list.append(file_path)
        
        # Save updates if there were changes
        if scripts_added_to_complete:
            save_boss_script_list(current_complete_list)
            save_boss_script_display_list(current_display_list)
            script_paths = current_display_list
        
        # Show notification if new scripts were found
        if new_scripts:
            # Extract display names from the tuples
            display_names = [display_name for file_path, display_name in new_scripts]
            
            if len(display_names) == 1:
                message = f"New default boss script found and added:\n\n• {display_names[0]}"
                title = "New Script Added"
            else:
                script_list = "\n".join(f"• {name}" for name in display_names)
                message = f"New default boss scripts found and added:\n\n{script_list}"
                title = "New Scripts Added"
            
            messagebox.showinfo(title, message)

    def load_selected_script():
        """Load the selected script"""
        selection = script_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a boss script to load.")
            return

        selected_index = selection[0]
        selected_path = script_paths[selected_index]

        # Update the main window variables
        last_used_boss.set(selected_path)
        last_used_boss_trimmed_string = os.path.basename(selected_path).replace(".json", "")
        last_used_boss_trimmed.set(last_used_boss_trimmed_string)

        # Save current config
        save_current_config()

        selection_window.destroy()
        display_name = get_display_name(selected_path, custom_names)
        messagebox.showinfo("Success", f"Boss script loaded: {display_name}")

    def rename_selected_script():
        """Rename the selected script in the list"""
        selection = script_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a boss script to rename.")
            return

        selected_index = selection[0]
        selected_path = script_paths[selected_index]
        current_display_name = get_display_name(selected_path, custom_names)

        # Create rename dialog
        rename_dialog = tk.Toplevel(selection_window)
        rename_dialog.title("Rename Script")
        rename_dialog.geometry("400x150")
        rename_dialog.resizable(False, False)
        rename_dialog.transient(selection_window)
        rename_dialog.grab_set()

        # Center the dialog
        rename_dialog.geometry("+%d+%d" % (selection_window.winfo_rootx() + 50, selection_window.winfo_rooty() + 100))

        tk.Label(rename_dialog, text="Enter new name for the script:", font=("Arial", 10)).pack(pady=10)
        
        name_entry = tk.Entry(rename_dialog, width=50, font=("Arial", 10))
        name_entry.pack(pady=5)
        name_entry.insert(0, current_display_name)
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        def confirm_rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Invalid Name", "Please enter a valid name.")
                return

            # Update custom names
            custom_names[selected_path] = new_name
            save_custom_display_names(custom_names)
            
            # Refresh the list
            refresh_script_list()
            
            # Reselect the renamed item
            try:
                script_listbox.selection_set(selected_index)
                script_listbox.see(selected_index)
            except (tk.TclError, IndexError):
                pass
            
            rename_dialog.destroy()

        def cancel_rename():
            rename_dialog.destroy()

        # Buttons
        button_frame = tk.Frame(rename_dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Confirm", command=confirm_rename).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_rename).pack(side="left", padx=5)

        # Bind Enter key to confirm
        rename_dialog.bind('<Return>', lambda e: confirm_rename())

    def browse_for_script():
        """Browse for a new script file"""
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = filedialog.askopenfilename(
            initialdir=downloads_folder,
            title="Select Boss Script File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            # Validate the file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Basic JSON validation

                # Add to both script list and display list if not already present
                current_scripts = load_boss_script_list()
                if file_path not in current_scripts:
                    current_scripts.append(file_path)
                    save_boss_script_list(current_scripts)
                
                # Also add to display list
                current_display_scripts = load_boss_script_display_list()
                if file_path not in current_display_scripts:
                    current_display_scripts.append(file_path)
                    save_boss_script_display_list(current_display_scripts)

                refresh_script_list()

                # Select the newly added script
                try:
                    index = script_paths.index(file_path)
                    script_listbox.selection_set(index)
                    script_listbox.see(index)
                except ValueError:
                    pass

            except (json.JSONDecodeError, Exception) as e:
                messagebox.showerror("Invalid File", f"The selected file is not a valid JSON file:\n{e}")

    def remove_selected_script():
        """Remove selected script from the list"""
        nonlocal custom_names
        selection = script_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a boss script to remove.")
            return

        selected_index = selection[0]
        selected_path = script_paths[selected_index]
        display_name = get_display_name(selected_path, custom_names)

        if messagebox.askyesno("Confirm Removal",
                               f"Remove '{display_name}' from the list?\n\nThe file will not be deleted."):
            # Remove from display list (this is what the user sees)
            current_display_scripts = load_boss_script_display_list()
            if selected_path in current_display_scripts:
                current_display_scripts.remove(selected_path)
                save_boss_script_display_list(current_display_scripts)

            # Also remove custom name if exists
            if selected_path in custom_names:
                del custom_names[selected_path]
                save_custom_display_names(custom_names)

            refresh_script_list()

    def reload_defaults():
        """Reload default scripts and reset the list"""
        if messagebox.askyesno("Confirm Reset", 
                              "This will reload the default scripts and undo all changes to the list.\n\nContinue?"):
            # Reload default scripts in both files
            default_scripts = reload_default_scripts()
            
            # Reset display list to only show default scripts
            save_boss_script_display_list(default_scripts.copy())
            
            # Clear custom names
            save_custom_display_names({})
            
            refresh_script_list()
            messagebox.showinfo("Success", "Default scripts reloaded successfully.")

    # Bottom frame for reload button
    bottom_frame = tk.Frame(selection_window)
    bottom_frame.pack(fill="x", padx=20, pady=(0, 10))

    # Reload button (bottom left with icon)
    reload_button = ttk.Button(bottom_frame, text="🔄", width=3, command=reload_defaults)
    reload_button.pack(side="left")

    # Add tooltip for reload button
    def create_tooltip(widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tooltip, text=text, background="lightyellow",
                             relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event): # TODO: THIS PARAMETER IS NOT BEING USED!
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    create_tooltip(reload_button, "Reload default scripts and undo all changes to the list")

    # Button frame for main action buttons
    button_frame = tk.Frame(selection_window)
    button_frame.pack(pady=10)

    # Action buttons
    load_button = ttk.Button(button_frame, text="Load", command=load_selected_script)
    load_button.pack(side="left", padx=5)

    rename_button = ttk.Button(button_frame, text="Rename", command=rename_selected_script)
    rename_button.pack(side="left", padx=5)

    browse_button = ttk.Button(button_frame, text="Browse", command=browse_for_script)
    browse_button.pack(side="left", padx=5)

    remove_button = ttk.Button(button_frame, text="Remove", command=remove_selected_script)
    remove_button.pack(side="left", padx=5)

    # Add tooltips
    create_tooltip(rename_button, "Rename the selected item, not the file")
    create_tooltip(remove_button, "Remove selected script. The file is not deleted.")

    # Cancel button
    cancel_button = ttk.Button(selection_window, text="Cancel",
                               command=selection_window.destroy)
    cancel_button.pack(pady=10)

    # Check for new scripts on startup (only when window is first opened)
    check_for_new_scripts_on_startup()
    
    # Initialize the list
    refresh_script_list()

    # Select current boss if it's in the list
    current_boss_path = last_used_boss.get()
    if current_boss_path in script_paths:
        try:
            index = script_paths.index(current_boss_path)
            script_listbox.selection_set(index)
            script_listbox.see(index)
        except ValueError:
            pass

    # Center the window and show it
    center_window(selection_window)
    selection_window.deiconify()  # Show the window
    selection_window.grab_set()  # Make window modal


# --------------- UI Setup ----------------
def center_window(window):
    # ensure accurate window dimensions by updating idle tasks
    window.update_idletasks()

    # get window dimensions
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate coordinates for centering
    x_coordinate = (screen_width // 2) - (window_width // 2)
    y_coordinate = (screen_height // 2) - (window_height // 2)

    # set the window geometry
    window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

reorder_keybinds_json()

# Initialize boss script list on startup
initialize_boss_script_list()

root = tk.Tk()
root.title("RuneScape Trainer")
root.geometry("450x220")
root.iconbitmap(ICON_PATH)

# centralize window
center_window(root)

# Dark button styling
style = ttk.Style()
style.theme_use("default")
style.configure("Dark.TButton", foreground="white", background="#444", padding=6)
style.map("Dark.TButton", background=[("active", "#555")])

last_used_boss = tk.StringVar(value=load_last_used_boss())
last_used_pvm_rot = tk.StringVar(value=load_last_pvm_rot())
key_bind_config = tk.StringVar(value=KEYBINDS_FILE)
config_file = tk.StringVar(value=CONFIG_FILE)

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
bottom_frame.pack(pady=(5, 0))

footer = tk.Frame(root)
footer.pack(side="right", pady=(10, 0))

ttk.Button(left, text="Start RS Overlay", style="Gray.TButton",
           command=lambda: start_script("scripts/RS_Overlay.exe", args=[last_used_boss.get()])).pack(pady=2, fill="x")
ttk.Button(left, text="Edit Keybinds", style="Gray.TButton",
           command=lambda: start_script("key_binds.exe")).pack(pady=2, fill="x")
# ttk.Button(left, text="Build Rotation", style="Gray.TButton",
#            command=lambda: start_script("scripts/rotation_creation.exe", log_output=True)).pack(pady=2, fill="x")

tk.Label(log_frame, text="Current Boss:").pack(pady=(0, 2))

last_used_boss_trimmed = last_used_boss.get().split("/")[-1].split("\\")[-1]
last_used_boss_trimmed = last_used_boss_trimmed.replace(".json", "")
last_used_boss_trimmed = tk.StringVar(value=last_used_boss_trimmed)
tk.Entry(log_frame, textvariable=last_used_boss_trimmed, width=40).pack()
ttk.Button(log_frame, text="Select Boss Script", style="Gray.TButton",
           command=open_boss_script_selection).pack(pady=10, padx=30, fill="x")

ttk.Button(right, text="Start RS Trainer", style="Gray.TButton",
           command=lambda: start_script("scripts/RS_Trainer.exe", args=[last_used_boss.get()])).pack(pady=2, fill="x")
ttk.Button(right, text="Edit Config", style="Gray.TButton",
           command=lambda: open_file_editor(config_file.get())).pack(pady=2, fill="x")
# ttk.Button(right, text="Build Rotation File", style="Gray.TButton",
#            command=lambda: open_file_editor(last_used_pvm_rot.get())).pack(pady=2, fill="x")

# trim everything but the .json name at the end
last_used_pvm_rot_trimmed = last_used_pvm_rot.get().split("/")[-1].split("\\")[-1]
# trim everything the .json name at the end
last_used_pvm_rot_trimmed = last_used_pvm_rot_trimmed.replace(".txt", "")
last_used_pvm_rot_trimmed = tk.StringVar(value=last_used_pvm_rot_trimmed)

# tk.Label(right, text="Rotation Path:").pack(pady=(5, 2))
# tk.Entry(right, textvariable=last_used_pvm_rot_trimmed, width=40).pack()

# Log Output
# tk.Label(log_frame, text="Build Rotation Log:").pack()
# log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
# log_text.pack(padx=5, pady=(0, 2))

# ttk.Button(bottom_frame, text="Clear Log", style="Gray.TButton",
#            command=lambda: log_text.delete("1.0", tk.END)).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Check for Updates", style="Gray.TButton",
           command=check_for_update).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Youtube", style="Gray.TButton",
           command=open_youtube).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Discord", style="Gray.TButton",
           command=open_discord).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Build a Rotation", style="Gray.TButton",
           command=open_rotation).pack(side="left", padx=5, pady=1)
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
