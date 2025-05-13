import json

with open("Config.json", "r") as f:
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
prefix="Ability_Icons/30px-"
ABILITY_IMAGES = {ability: f"{prefix}{ability}.png" for ability in config["ABILITY_KEYBINDS"]}


