import os
import shutil
import json
import sys
import platform

APP_NAME = "Azulyn"
if platform.system() == "Windows":
    APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
else:
    APPDATA_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)
USER_KEYBINDS = os.path.join(APPDATA_DIR, "keybinds.json")
print(str(USER_KEYBINDS))

# Handle base dir for bundled vs. dev mode
if getattr(sys, 'frozen', False):
    try:
        BASE_DIR = sys._MEIPASS
    except Exception:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# print(str(BASE_DIR))
DEFAULT_KEYBINDS = os.path.join(BASE_DIR, "keybinds.json")

if not os.path.exists(USER_KEYBINDS):
    if os.path.exists(DEFAULT_KEYBINDS):
        shutil.copy(DEFAULT_KEYBINDS, USER_KEYBINDS)
    else:
        raise FileNotFoundError("Default keybinds.json not found in bundled resources.")


with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
    config = json.load(f)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
PRESS_ZONE_X = 100  # Position where notes should be pressed... note its 10 pixels wide as well -> we need to move 10 pixels in .6 seconds?

TICK_DURATION = 0.6  # Each tick is 600ms
NOTE_SPEED = 100  # Pixels per tick?
ABILITY_DEFAULT_WIDTH = 75  # Default width of ability images
NOTE_SPACING_Y = 100  # Space between stacked notes


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
#TODO ?
prefix="ability_icons/30px-"
ABILITY_IMAGES = {ability: f"{prefix}{ability}.png" for ability in config["ABILITY_KEYBINDS"]}

