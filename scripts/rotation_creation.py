import os
import re
import difflib
import json
import shutil

from config.config import USER_KEYBINDS

APP_NAME = "Azulyn"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
BUILD_ROTATION_FILE = os.path.join(APPDATA_DIR, "build_rotation.txt")
DEFAULT_BUILD_ROTATION_FILE = os.path.join("config", "build_rotation.txt")

if not os.path.exists(BUILD_ROTATION_FILE):
    if os.path.exists(DEFAULT_BUILD_ROTATION_FILE):
        shutil.copy(DEFAULT_BUILD_ROTATION_FILE, BUILD_ROTATION_FILE)


with open(USER_KEYBINDS, "r") as f:
    config = json.load(f)

ABILITY_KEYBINDS = config["ABILITY_KEYBINDS"]

try:
    with open(BUILD_ROTATION_FILE, "r", encoding="utf-8") as f:
        text = f.read()
except:
    with open(BUILD_ROTATION_FILE, "r", encoding="utf-8") as f:
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
    "natty": "Natural_Instinct",
    "eof": "Essence_of_Finality",
    "asfix": "Asphyxiate",
    "ioh": "Ingenuity_of_the_humans",
    "magma": "Magma_Tempest",
    "tc": "Target_Cycle",
    "balista": "Unload",
    "prismofrestoration": "Prism_of_Restoration",
    "zerk": "Berserk",
    "cane": "Hurricane",
    "dba": "Dragon_Battleaxe",
    "lengmh": "Dark_Shard_Of_Leng",
    "lengoh": "Dark_Sliver_Of_Leng",
    "gbarge": "Greater_Barge",
}

IGNORED_EMOJI_NAMES = {
    "deathguard90",
    "omniguard",
    "dragonclaw"
}


#text = "<:surge:535533810004262912> + <:deathskulls:1159434663903899728> → <:bloat:1159433682403201044> → <:soulsap:1137809140476031057> → <:touchofdeath:1137809175980810380> → <:deathguard90:1138809243143766118> <:eofspec:1257438999794946099> → <:soulsap:1137809140476031057> → <:omniguard:1138809234922934282> <:spec:537340400273195028> → <:necroauto:1137809137401602109>"

# Start tick value
tick = 4
result = []

# Prepare list of all ability names for fuzzy matching
ability_names = list(ABILITY_KEYBINDS.keys())

# Split by → to indicate +3 ticks
sections = re.split(r"→", text)

for section in sections:
    section = section.strip()
    parts = section.split()

    for part in parts:
        # Tick adjustment like '2t'
        tick_match = re.match(r"^(\d{1,2})t$", part.lower())
        if tick_match:
            tick += int(tick_match.group(1))
            continue

        # Handle emoji matches
        matches = re.findall(r"<:([a-zA-Z0-9_]+):\d+>", part)
        for raw_name in matches:
            key = raw_name.lower()
            if key in IGNORED_EMOJI_NAMES:
                print(f"Skipping ignored emoji: {key}")
                continue

            if key in EMOJI_NAME_OVERRIDES:
                best_match = EMOJI_NAME_OVERRIDES[key]
            else:
                simplified = [a.lower().replace("_", "") for a in ability_names]
                close_matches = difflib.get_close_matches(key.replace("_", ""), simplified, n=1, cutoff=0.6)
                if close_matches:
                    matched = close_matches[0]
                    best_match = next(a for a in ability_names if a.lower().replace("_", "") == matched)
                else:
                    print(f"Could not match emoji name: {raw_name}")
                    continue

            result.append({"tick": tick, "ability": best_match})

    # After each → section, increment tick by 3 (unless overridden by Nt)
    tick += 3


# for entry in result:
#     print(json.dumps(entry))
print(json.dumps(result, indent=2))

# for ability in ABILITY_KEYBINDS:
#     if ability not in ABILITY_IMAGES:
#         print(f"Missing image for ability: {ability}")