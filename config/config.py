import json
import os
import shutil
from pathlib import Path

DEFAULT_BINDS = {
"ABILITY_KEYBINDS": {
  "Royal_Crossbow": [],
  "Noxious_Scythe": [],
  "Fractured_Staff_Of_Armadyl": [],
  "Soulbound_Lantern": [],
  "Omni_Guard": [],
  "Death_Guard": [],
  "Skull_Lantern": [],
  "Roar_Of_Awakening": [],
  "Ode_To_Deceit": [],
  "Dark_Shard_Of_Leng": [],
  "Dark_Sliver_Of_Leng": [],

  "Move": ["MOUSE"],
  "Powerburst_of_vitality": [],
  "Demon_Slayer": [],
  "Dive": [],
  "Dragon_Slayer": [],
  "Eat_Food": [],
  "Escape": [],
  "Essence_of_Finality": [],
  "Limitless": [],
  "Onslaught": [],
  "Quiver_ammo_slot_1": [],
  "Quiver_ammo_slot_2": [],
  "Reprisal": [],
  "Sacrifice": [],
  "Shatter": [],
  "Storm_Shards": [],
  "Tuska's_Wrath": [],
  "Undead_Slayer": [],
  "Weapon_Special_Attack": [],
  "Adrenaline_potion": [],
  "Target_Cycle": [],
  "Vulnerability_bomb": [],

  "Asphyxiate": [],
  "Chain": [],
  "Combust": [],
  "Concentrated_Blast": [],
  "Corruption_Blast": [],
  "Deep_Impact": [],
  "Detonate": [],
  "Dragon_Breath": [],
  "Greater_Chain": [],
  "Greater_Concentrated_Blast": [],
  "Greater_Sonic_Wave": [],
  "Greater_Sunshine": [],
  "Horror": [],
  "Impact": [],
  "Magma_Tempest": [],
  "Metamorphosis": [],
  "Omnipower": [],
  "Shock": [],
  "Smoke_Tendrils": [],
  "Sonic_Wave": [],
  "Sunshine": [],
  "Surge": [],
  "Tsunami": [],
  "Wild_Magic": [],
  "Wrack": [],
  "Wrack_and_Ruin": [],

  "Exsanguinate": [],
  "Incite_Fear": [],
  "Temporal_Anomaly": [],
  "Disruption_Shield": [],
  "Vengeance": [],
  "Smoke_Cloud": [],
  "Blood_Barrage": [],
  "Intercept": [],
  "Spellbook_Swap": [],
  "Animate_Dead": [],

  "Anticipation": [],
  "Barricade": [],
  "Bash": [],
  "Cease": [],
  "Debilitate": [],
  "Devotion": [],
  "Divert": [],
  "Freedom": [],
  "Ice_Asylum": [],
  "Immortality": [],
  "Ingenuity_of_the_Humans": [],
  "Natural_Instinct": [],
  "Preparation": [],
  "Provoke": [],
  "Reflect": [],
  "Rejuvenate": [],
  "Resonance": [],
  "Revenge": [],

  "Assault": [],
  "Backhand": [],
  "Balanced_Strike": [],
  "Barge": [],
  "Berserk": [],
  "Bladed_Dive": [],
  "Blood_Tendrils": [],
  "Chaos_Roar": [],
  "Cleave": [],
  "Decimate": [],
  "Destroy": [],
  "Dismember": [],
  "Flurry": [],
  "Forceful_Backhand": [],
  "Frenzy": [],
  "Fury": [],
  "Greater_Barge": [],
  "Greater_Flurry": [],
  "Greater_Fury": [],
  "Havoc": [],
  "Hurricane": [],
  "Kick": [],
  "Massacre": [],
  "Meteor_Strike": [],
  "Overpower": [],
  "Pulverise": [],
  "Punish": [],
  "Quake": [],
  "Sever": [],
  "Slaughter": [],
  "Slice": [],
  "Smash": [],
  "Stomp": [],

  "Binding_Shot": [],
  "Bombardment": [],
  "Corruption_Shot": [],
  "Dazing_Shot": [],
  "Deadshot": [],
  "Death's_Swiftness": [],
  "Demoralise": [],
  "Fragmentation_Shot": [],
  "Greater_Dazing_Shot": [],
  "Greater_Death's_Swiftness": [],
  "Greater_Ricochet": [],
  "Incendiary_Shot": [],
  "Needle_Strike": [],
  "Piercing_Shot": [],
  "Rapid_Fire": [],
  "Ricochet": [],
  "Rout": [],
  "Salt_the_Wound": [],
  "Shadow_Tendrils": [],
  "Snap_Shot": [],
  "Snipe": [],
  "Tight_Bindings": [],
  "Unload": [],

  "Bloat": [],
  "Blood_Siphon": [],
  "Command_Phantom_Guardian": [],
  "Command_Putrid_Zombie": [],
  "Command_Skeleton_Warrior": [],
  "Command_Vengeful_Ghost": [],
  "Conjure_Phantom_Guardian": [],
  "Conjure_Putrid_Zombie": [],
  "Conjure_Skeleton_Warrior": [],
  "Conjure_Undead_Army": [],
  "Conjure_Vengeful_Ghost": [],
  "Death_Skulls": [],
  "Finger_of_Death": [],
  "Living_Death": [],
  "Necromancy": [],
  "Soul_Sap": [],
  "Soul_Strike": [],
  "Spectral_Scythe": [],
  "Spectral_Scythe_2": [],
  "Spectral_Scythe_3": [],
  "Touch_of_Death": [],
  "Volley_of_Souls": [],
  "Life_Transfer": [],
  "Threads_of_Fate": [],
  "Invoke_Lord_of_Bones": [],
  "Invoke_Death": [],
  "Darkness": [],
  "Split_Soul": [],
  "Death_Spark": []
    }
}

import os
import shutil
import json
import sys

def ensure_keybinds_file_exists():
  config_file = Path("config/keybinds.json")
  if not config_file.exists():
    print("Keybinds file does not exist. Creating a new one...")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
      json.dump(DEFAULT_BINDS, f, indent=2, encoding="utf-8")
  else:
    # print("Keybinds file already exists. No action taken.")
    pass

ensure_keybinds_file_exists()

APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
USER_KEYBINDS = os.path.join(APPDATA_DIR, "keybinds.json")

# PyInstaller-safe way to locate bundled files
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_KEYBINDS = os.path.join(BASE_DIR, "config", "keybinds.json")


if not os.path.exists(USER_KEYBINDS):
    if os.path.exists(DEFAULT_KEYBINDS):
        shutil.copy(DEFAULT_KEYBINDS, USER_KEYBINDS)
    else:
        raise FileNotFoundError("Default keybinds.json not found in bundled resources.")


with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
    config = json.load(f)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
                            "Dark_Shard_Of_Leng", "Dark_Sliver_Of_Leng",}


# Ability to Image Mapping
prefix="../ability_icons/30px-"
ABILITY_IMAGES = {ability: f"{prefix}{ability}.png" for ability in config["ABILITY_KEYBINDS"]}

