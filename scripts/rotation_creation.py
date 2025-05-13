import os
import re
import difflib
import json
import shutil

from config.config import USER_KEYBINDS, ensure_keybinds_file_exists

APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
PVM_DISCORD_FILE = os.path.join(APPDATA_DIR, "pvm_discord.txt")
DEFAULT_PVM_DISCORD_PATH = os.path.join("config", "pvm_discord.txt")

if not os.path.exists(PVM_DISCORD_FILE):
    if os.path.exists(DEFAULT_PVM_DISCORD_PATH):
        shutil.copy(DEFAULT_PVM_DISCORD_PATH, PVM_DISCORD_FILE)

ensure_keybinds_file_exists()  # Make sure the file exists in AppData

with open(USER_KEYBINDS, "r") as f:
    config = json.load(f)

ABILITY_KEYBINDS = config["ABILITY_KEYBINDS"]

try:
    with open(PVM_DISCORD_FILE, "r", encoding="utf-8") as f:
        text = f.read()
except:
    with open(PVM_DISCORD_FILE, "r", encoding="utf-8") as f:
        text = f.read()

ALIASES = {
    "(tc)": "<:Target_Cycle:000000000000000000>",  # Replace with actual emoji ID if needed
    "(r)": "<:Smoke_Cloud:000000000000000000>",     # Example replacement
}


# Replace aliases
for alias, replacement in ALIASES.items():
    text = text.replace(alias, replacement)


# Hardcoded emoji name overrides
EMOJI_NAME_OVERRIDES = {
    "spec": "Weapon_Special_Attack",
    "eofspec": "Essence_of_Finality",
    "necroauto": "Necromancy",
    "adrenrenewal": "Adrenaline_potion",
    "gconc": "Greater_Concentrated_Blast",
    "wm": "Wild_Magic",
    "anti": "Anticipation",
    "deto": "Detonate",
    "fsoa": "Fractured_Staff_Of_Armadyl",
    "gsunshine": "Greater_Sunshine",
    "deathspark": "Death_Spark",
    "nat": "Natural_Instinct",
    "anticlearheaded": "Anticipation",
    "res": "Resonance",
    "prep": "Preparation",
    "meta": "Metamorphosis",
    "bd": "Bladed Dive",
    "natty": "Natrual Instinct",
    "eof": "Essence_of_Finality",
    "asfix": "Asphyxiate",
    "ioh": "Ingenuity_of_the_humans",
    "magma": "Magma_Tempest",
    "tc": "Target_Cycle",
    "balista": "Unload",
    "prismofrestoration": "Prism_of_Restoration",
    "zerk": "Berserk",

}

IGNORED_EMOJI_NAMES = {
    "deathguard90",
    "omniguard",
}


#text = "<:surge:535533810004262912> + <:deathskulls:1159434663903899728> → <:bloat:1159433682403201044> → <:soulsap:1137809140476031057> → <:touchofdeath:1137809175980810380> → <:deathguard90:1138809243143766118> <:eofspec:1257438999794946099> → <:soulsap:1137809140476031057> → <:omniguard:1138809234922934282> <:spec:537340400273195028> → <:necroauto:1137809137401602109>"

# Start tick value
tick = 4
result = []

# Prepare list of all ability names for fuzzy matching
ability_names = list(ABILITY_KEYBINDS.keys())

# Split the input string by '→'
chunks = text.split("→")
for chunk in chunks:
    parts = chunk.strip().split("+")
    for part in parts:
        matches = re.findall(r"<:([a-zA-Z0-9_]+):\d+>", part)
        for raw_name in matches:
            key = raw_name.lower()
            if key in IGNORED_EMOJI_NAMES:
                print(f" Skipping ignored emoji: {key}")
                continue
            # Check hardcoded overrides first
            if key in EMOJI_NAME_OVERRIDES:
                best_match = EMOJI_NAME_OVERRIDES[key]
            else:
                # Fuzzy match fallback
                simplified_ability_names = [a.lower().replace("_", "") for a in ability_names]
                close_matches = difflib.get_close_matches(key.replace("_", ""), simplified_ability_names, n=1, cutoff=0.6)

                if close_matches:
                    matched_lower = close_matches[0]
                    # Map back to original-cased name
                    best_match = next(name for name in ability_names if name.lower().replace("_", "") == matched_lower)
                else:
                    print(f" Could not match emoji name: {raw_name}")
                    continue

            result.append({"tick": tick, "ability": best_match})
    tick += 3  # Increase tick every time we see →

# for entry in result:
#     print(json.dumps(entry))
print(json.dumps(result, indent=2))

# for ability in ABILITY_KEYBINDS:
#     if ability not in ABILITY_IMAGES:
#         print(f"Missing image for ability: {ability}")