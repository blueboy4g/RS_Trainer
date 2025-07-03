import os
import shutil
import json
import sys
import tkinter as tk
from tkinter import messagebox


APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)
USER_KEYBINDS = os.path.join(APPDATA_DIR, "keybinds.json")
USER_CONFIG = os.path.join(APPDATA_DIR, "config.json")

# PyInstaller-safe way to locate bundled files
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_KEYBINDS_IN_APP = os.path.join(BASE_DIR, "config", "keybinds.json")
DEFAULT_CONFIG_IN_APP = os.path.join(BASE_DIR, "config", "config.json")
DEFAULT_KEYBINDS = os.path.join(BASE_DIR, "", "keybinds.json")
DEFAULT_CONFIG = os.path.join(BASE_DIR, "", "config.json")

if not os.path.exists(USER_KEYBINDS):
    if os.path.exists(DEFAULT_KEYBINDS_IN_APP):
        shutil.copy(DEFAULT_KEYBINDS_IN_APP, USER_KEYBINDS)
    else:
        if os.path.exists(DEFAULT_KEYBINDS):
            shutil.copy(DEFAULT_KEYBINDS, USER_KEYBINDS)
        else:
            print("file not found at ", DEFAULT_KEYBINDS_IN_APP)
            raise FileNotFoundError("Default keybinds.json not found in bundled resources.")

if not os.path.exists(USER_CONFIG):
    if os.path.exists(DEFAULT_CONFIG_IN_APP):
        shutil.copy(DEFAULT_CONFIG_IN_APP, USER_CONFIG)
    else:
        if os.path.exists(DEFAULT_CONFIG):
            shutil.copy(DEFAULT_CONFIG, USER_CONFIG)
        else:
            print("file not found at ", DEFAULT_CONFIG_IN_APP)
            raise FileNotFoundError("Default config.json not found in bundled resources.")

def show_error_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)
    root.destroy()  # Destroy the root window after the popup

try:
    with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
        keybind_config = json.load(f)
except json.JSONDecodeError as e:
    error_message = (
        f"Error: Your .JSON file is not formatted correctly.\n"
        f"Fix it at: '{USER_KEYBINDS}'\n"
        f"Line {e.lineno}, Column {e.colno}.\n"
        f"Message: {e.msg}"
    )
    show_error_popup(error_message)
    sys.exit(1)
except FileNotFoundError:
    error_message = f"Error: The file '{USER_KEYBINDS}' was not found."
    show_error_popup(error_message)
    sys.exit(1)

# Ensure "ABILITY_KEYBINDS" exists in user_keybinds
keybind_config["ABILITY_KEYBINDS"] = keybind_config.get("ABILITY_KEYBINDS", {})

try:
    with open(USER_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
except json.JSONDecodeError as e:
    error_message = (
        f"Error: Your .JSON file is not formatted correctly.\n"
        f"Fix it at: '{USER_CONFIG}'\n"
        f"Line {e.lineno}, Column {e.colno}.\n"
        f"Message: {e.msg}"
    )
    show_error_popup(error_message)
    sys.exit(1)
except FileNotFoundError:
    error_message = f"Error: The file '{USER_CONFIG}' was not found."
    show_error_popup(error_message)
    sys.exit(1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
PRESS_ZONE_X = 0  # Position where abilities should be pressed...  its 10 pixels wide as well -> we need to move 10 pixels in .6 seconds?

TICK_DURATION = float(config["tick_duration"])  # Each tick in game is .6
tick_speed_mod = .6 / TICK_DURATION
ABILITY_SPEED = 100 * tick_speed_mod # Pixels per tick?
ABILITY_DEFAULT_WIDTH = (int(config["ability_icon_size"]))
ABILITY_SPACING_Y = (int(config["ability_spacing_y_dir"]))  # Space between stacked abilities
ABILITY_SPACING_X = (int(config["ability_spacing_x_dir"]))  # Space between abilities in x direction

# Abilities that should NOT trigger the dial animation
EXCLUDED_DIAL_ANIMATIONS = {"Surge", "Dive", "Bladed_Dive", "Escape", "Eat_Food",
                            "Powerburst_of_vitality", "Move", "Adrenaline_potion",
                            "Disruption_Shield", "Spellbook_Swap", "Exsanguinate",
                            "Incite_Fear", "Temporal_Anomaly", "Vengeance", "Target_Cycle",
                            "Smoke_Cloud", "Blood_Barrage","Vulnerability_bomb", "Royal_Crossbow",
                            "Noxious_Scythe", "Fractured_Staff_Of_Armadyl", "Soulbound_Lantern", "Omni_Guard",
                            "Death_Guard", "Skull_Lantern", "Roar_Of_Awakening", "Ode_To_Deceit",
                            "Dark_Shard_Of_Leng", "Dark_Sliver_Of_Leng", "Dragon_Battleaxe"}


# Ability to Image Mapping
prefix="../ability_icons/30px-"
ABILITY_IMAGES = {ability: f"{prefix}{ability}.png" for ability in keybind_config["ABILITY_KEYBINDS"]}

