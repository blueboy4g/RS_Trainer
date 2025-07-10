import time

import win32con

from scripts.dial_animation import DialAnimation
from config.config import *
from scripts.ability import Ability
import tkinter as tk
import pygame
import threading
import keyboard
import win32gui

import sys
import json



with open(USER_KEYBINDS, "r") as f:
    keybind_config = json.load(f)

with open(USER_CONFIG, "r") as f:
    config = json.load(f)

print(str(keybind_config))

ABILITY_KEYBINDS = keybind_config["ABILITY_KEYBINDS"]

if len(sys.argv) < 2:
    print("Usage: python RS_Trainer.py <config_file>")
    config_file = "C://Users//PC//AppData//Roaming//Azulyn//boss_rotations//azulyn_kerapac_hm_solo_mage_melee_with_ezk.json"
else:
    config_file = sys.argv[1]
    print(f"Using config: {config_file}")

# Example: load the config
with open(config_file, 'r') as f:
    ability_sequence = json.load(f)

is_restart = False

def play_game():
    global running, current_tick, score, missed_abilities, spawned_abilities, tick_bars, key_press_count, new_global_key_events, still_active_global_key_events, is_restart, screen

    # Put everything from initialization to show_results() here
    def make_window_always_on_top():
        hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    # Now you can use `config` in your script
    win_w = int(config["overlay_screen_width"])
    win_h = int(config["overlay_screen_height"])
    if is_restart:
        pass
    else:
        # Initialize Pygame
        pygame.init()
        icon = pygame.image.load("../resources/azulyn_icon.ico")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("RS Trainer (Overlay)")

        # Tkinter is used to center the window on screen
        root = tk.Tk()
        root.withdraw()
        # screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
        # x = round((screen_w - win_w) / 2)
        # y = round((screen_h - win_h) / 2 * 0.8)

        # Create Pygame screen and set window position
        screen = pygame.display.set_mode((win_w, win_h))
        make_window_always_on_top()
        is_restart = True
        #SetWindowPos(pygame.display.get_wm_info()['window'], -1, x, y, 0, 0, 1)

    if (str(config["see_ability_icons"])) == "True" or (str(config["see_ability_icons"])) == "true":
        see_abilities = True
    else:
        see_abilities = False

    if (str(config["see_keybinds"])) == "True" or (str(config["see_keybinds"])) == "true":
        see_keybinds = True
    else:
        see_keybinds = False


    # Game Variables
    press_zone_rect = pygame.Rect(PRESS_ZONE_X, 0, 1, win_h)  # 1 pixel wide with extra height
    tick_bars = []  # Store tick bars

    # Game variables
    running = True
    clock = pygame.time.Clock()
    spawned_abilities = []
    spawned_abilities_queue = []
    current_tick = 0
    next_tick_time = time.time() + TICK_DURATION
    last_tick_time = time.time()  # Track last tick time for debugging
    score = 0
    total_abilities = len(ability_sequence)
    missed_abilities = 0
    last_tick_bar_time = None  # Store last tick bar collision time
    tick_ability_counts = {}
    tick_ability_counts_queue = {}# Dictionary to track abilities stacking per tick
    tick_ability_counts_queue2 = {}# Dictionary to track abilities stacking per tick
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP])
    dial_animation = DialAnimation(win_w // 2 - 25, win_h - 55)
    dial_animation_queue = []  # Queue for animations
    current_animation = None  # Track the currently playing animation
    failed_attempts = 0  # Track failed attempts
    feedback_message = None  # Store feedback message
    feedback_timer = 0  # Timer for feedback message


    key_press_count = 0
    new_global_key_events = []
    still_active_global_key_events = []

    key_combination_map = {
        "SHIFT+1": "!",
        "SHIFT+2": "@",
        "SHIFT+3": "#",
        "SHIFT+4": "$",
        "SHIFT+5": "%",
        "SHIFT+6": "^",
        "SHIFT+7": "&",
        "SHIFT+8": "*",
        "SHIFT+9": "(",
        "SHIFT+0": ")",
        "SHIFT+A": "A",
        "SHIFT+B": "B",
        "SHIFT+C": "C",
        "SHIFT+D": "D",
        "SHIFT+E": "E",
        "SHIFT+F": "F",
        "SHIFT+G": "G",
        "SHIFT+H": "H",
        "SHIFT+I": "I",
        "SHIFT+J": "J",
        "SHIFT+K": "K",
        "SHIFT+L": "L",
        "SHIFT+M": "M",
        "SHIFT+N": "N",
        "SHIFT+O": "O",
        "SHIFT+P": "P",
        "SHIFT+Q": "Q",
        "SHIFT+R": "R",
        "SHIFT+S": "S",
        "SHIFT+T": "T",
        "SHIFT+U": "U",
        "SHIFT+V": "V",
        "SHIFT+W": "W",
        "SHIFT+X": "X",
        "SHIFT+Y": "Y",
        "SHIFT+Z": "Z",

        # Add more mappings as needed
    }

    # Function to get the mapped value
    def get_mapped_key(key):
        for combination, symbol in key_combination_map.items():
            mod, k = combination.split('+')
            if k.lower() == key.lower():
                return symbol
        return key

    #
    def global_key_listener():
        held_keys = set()

        def on_key_event(e):
            global key_press_count, new_global_key_events, new_global_key_events

            key = e.name
            if e.event_type == 'down':
                if key not in held_keys:
                    held_keys.add(key)
                    key_press_count += 1
                    print(f"[GLOBAL] Key pressed once: {key} (Total: {key_press_count})")
                    still_active_global_key_events.append(key)
                    print("Still_active " + str(still_active_global_key_events))
                    new_global_key_events = still_active_global_key_events.copy()

            elif e.event_type == 'up':
                print(f"[GLOBAL] Key released: {key}")
                held_keys.discard(key)
                if key in still_active_global_key_events:
                    still_active_global_key_events.remove(key)
                if key.upper() in still_active_global_key_events:
                    still_active_global_key_events.remove(key.upper())
                # Handle shift key and corresponding symbol keys
                if key == 'shift':
                    for char in '!@#$%^&*()':
                        if char in still_active_global_key_events:
                            still_active_global_key_events.remove(char)
                            held_keys.discard(char)
                    # for combination, symbol in key_combination_map.items():
                    #     mod, k = combination.split('+')
                    #     if mod.lower() == 'shift' and k.lower() in still_active_global_key_events:
                    #         still_active_global_key_events.remove(k.lower())
                else:
                    for combination, symbol in key_combination_map.items():
                        mod, k = combination.split('+')
                        #TODO I removed this as the shiftkey is getting unpressed when you lift another key so shift + f then + g wont work if you lift up f first
                        # if k.lower() == key.lower() and mod.lower() == 'shift' and 'shift' in still_active_global_key_events:
                        #     still_active_global_key_events.remove('shift')
                        #     held_keys.discard('shift')
                    # Remove corresponding symbol when number key is released
                    if key in '1234567890':
                        symbol = key_combination_map.get(f'SHIFT+{key}')
                        if symbol and symbol in still_active_global_key_events:
                            still_active_global_key_events.remove(symbol)
                            held_keys.discard(symbol)
                new_global_key_events = still_active_global_key_events.copy()

        keyboard.hook(on_key_event)

    # Start the global key listener
    threading.Thread(target=global_key_listener, daemon=True).start()

    while running:
        screen.fill((0, 0, 0))  # Clear screen
        mouse_clicked = False  # Track mouse click state
        key_pressed = False  # Track key press state
        dt = clock.tick(60) / 1000.0  # Convert milliseconds to seconds

        # Update animation
        if (str(config["see_global_cooldown_animation"])) == "True" or (str(config["see_global_cooldown_animation"])) == "true":
            dial_animation.update(dt)
            # If no animation is playing, start the next one from the queue
            if current_animation is None and dial_animation_queue:
                current_animation = dial_animation_queue.pop(0)  # Start the next animation
                current_animation.start()  # Ensure it begins playing

            # Update and draw the current animation
            if current_animation:
                current_animation.update(dt)
                if not current_animation.active:
                    current_animation = None  # Move to the next animation when done
            # Draw the current animation
            if current_animation:
                current_animation.draw(screen)

        key_down = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key not in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT]:
                    #print(f"Key pressed: {event.key}")
                    key_pressed = True
                    key_down = event.key
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #print(f"Mouse clicked at {event.pos}")
                mouse_clicked = True

        keys = pygame.key.get_pressed()
        # Check for hits
        if key_down or mouse_clicked or new_global_key_events:
            #print("new_global_key_events:", new_global_key_events)
            #print("Key pressed:", key_down)
            if (str(config["default_exit_button"])).lower() in new_global_key_events or (str(config["default_exit_button"])).upper() in new_global_key_events:
                running = False
            ONE_ABILITY_HIT = False
            for ability in spawned_abilities[:]:
                try:
                    required_keys_pressed = False  # Start with False (assume key is NOT pressed)

                    for k in ability.key:
                        k = k.strip().upper()  # Normalize key formatting
                        required_keys_pressed = all(
                            (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) if k == "SHIFT" else
                            (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) if k in ["CTRL", "LCTRL"] else
                            (keys[pygame.K_LALT] or keys[pygame.K_RALT]) if k == "ALT" else
                            (keys[pygame.K_LEFTBRACKET] if k == "[" else
                             keys[pygame.K_RIGHTBRACKET] if k == "]" else
                             keys[pygame.K_BACKSLASH] if k == "\\" else
                             keys[pygame.K_MINUS] if k == "-" else
                             keys[pygame.K_COMMA] if k == "," else
                             keys[pygame.K_BACKQUOTE] if k == "`" else
                             pygame.mouse.get_pressed()[0] if k == "MOUSE" else
                             keys[getattr(pygame, f'K_F{k[1:]}', None)] if k.startswith("F") and k[1:].isdigit() else
                             keys[getattr(pygame, f'K_{k.lower()}', None)] if getattr(pygame, f'K_{k.lower()}',
                                                                                      None) else False)
                            for k in ability.key
                        )

                    # if not required_keys_pressed:
                        # required_keys_pressed = all(
                        #     (k.lower() == "mouse" and "space" in new_global_key_events) or
                        #     (mapped_key in new_global_key_events) or
                        #     (k.lower() in new_global_key_events) or
                        #     ("shift" in new_global_key_events and k.lower() == "3" and "@" in new_global_key_events) or
                        #     ("ctrl" in new_global_key_events and f"ctrl+{k.lower()}" in key_combination_map and
                        #      key_combination_map[f"ctrl+{k.lower()}"] in new_global_key_events) or
                        #     ("alt" in new_global_key_events and f"alt+{k.lower()}" in key_combination_map and
                        #      key_combination_map[f"alt+{k.lower()}"] in new_global_key_events)
                        #     for k in ability.key
                        # )

                    if required_keys_pressed:
                        new_global_key_events = []

                    for k in ability.key:
                        #print("WE GOT: " + str(k))
                        pass

                    #TODO seems like we get random misses and im not sure why?
                    if required_keys_pressed == False:
                        for k in ability.key:
                            #print("k.lower is " + str(k.lower()))
                            mapped_key = get_mapped_key(k.lower())
                            #print("Mapped key is " + str(mapped_key))
                            required_keys_pressed = False
                            #print("IN LOOP: " + str(k))
                            if k.lower() == "mouse":
                                # if space is in new global key
                                if (str(config["mouse_abilities"])) in new_global_key_events:
                                    required_keys_pressed = True

                            elif mapped_key in new_global_key_events:
                                #print(f"Key {mapped_key} is pressed mapped")
                                required_keys_pressed = True


                            elif k.lower() in new_global_key_events:
                                #print(f"Key {k} is pressed")
                                required_keys_pressed = True

                            # Check for modifier combinations
                            elif "shift" in new_global_key_events and f"shift+{k.lower()}" in key_combination_map:
                                if key_combination_map[f"shift+{k.lower()}"] in new_global_key_events:
                                    print(f"Key {key_combination_map[f'shift+{k.lower()}']} is pressed with SHIFT")
                                    required_keys_pressed = True

                            elif "ctrl" in new_global_key_events and k.lower() == 'lctrl':
                                print(f"Key is pressed with CTRL")
                                required_keys_pressed = True

                            elif "alt" in new_global_key_events and f"alt+{k.lower()}" in key_combination_map:
                                if key_combination_map[f"alt+{k.lower()}"] in new_global_key_events:
                                    print(f"Key {key_combination_map[f'alt+{k.lower()}']} is pressed with ALT")
                                    required_keys_pressed = True
                            elif required_keys_pressed == False:
                                print(f"Key {k} is NOT pressed")
                                required_keys_pressed = False
                                break

                    if required_keys_pressed and press_zone_rect.colliderect(ability.rect):
                        print(f"Hit detected: {ability.ability}")  # Debugging log
                        score += 1
                        spawned_abilities.remove(ability)
                        feedback_message = "Correct"
                        feedback_timer = time.time() + 1  # Show feedback for 1 second
                        failed_attempts = 0  # Reset failed attempts
                        ONE_ABILITY_HIT = True

                        if ability.ability not in EXCLUDED_DIAL_ANIMATIONS:
                            new_animation = DialAnimation(win_w // 2 - 25, win_h - 55)
                            dial_animation_queue.append(new_animation)

                except KeyError:
                    print(f"Warning: Unrecognized ability in ability: {ability.ability}")

            # Check for missed abilities after the loop
            if not ONE_ABILITY_HIT and (key_pressed or mouse_clicked or new_global_key_events):
                if new_global_key_events == ['shift'] or new_global_key_events == ['ctrl'] or new_global_key_events == ['alt']:
                    pass
                else:
                    #print(key_pressed)
                    #print(new_global_key_events)
                    failed_attempts += 1
                    missed_abilities += 1  # Increment missed abilities
                    print("Failed attempts:", failed_attempts)
                    feedback_message = "Wrong!"
                    feedback_timer = time.time() + 1  # Show feedback for 1 second
                    if failed_attempts >= 3:
                        print("Making visible")
                        for ability in spawned_abilities:
                            ability.visible = True  # Show the ability after 3 failed attempts
        #print("ahhhhhhhhhhhhhh" + str(new_global_key_events))
        new_global_key_events = [key for key in new_global_key_events if key.lower() == "shift" or key.lower() == "ctrl" or key.lower() == "alt"]

        # Tick system: Check if it's time for the next tick
        new_global_key_events.clear()
        for key in still_active_global_key_events:
            if key== 'shift' or key == 'ctrl' or key == 'alt':
                pass
            else:
                still_active_global_key_events.remove(key)
        current_time = time.time()
        valid_spawned_abilities = [ability for ability in spawned_abilities if not ability.image == None]
        if current_time >= next_tick_time and not valid_spawned_abilities:
            spawned_abilities.clear()
            print("On tick " + str(current_tick))
            spawned_abilities_queue = []  # Reset queue for new abilities
            actual_tick_duration = current_time - last_tick_time
            last_tick_time = current_time
            current_tick += 1
            #next_tick_time += TICK_DURATION  # Remove tick time so it instant

            future_ticks = [ability["tick"] for ability in ability_sequence if ability["tick"] > current_tick]
            next_ability = min(future_ticks, default=None)

            if next_ability is not None:
                future_future_ticks = [ability["tick"] for ability in ability_sequence if ability["tick"] > next_ability]
                next_next_ability = min(future_future_ticks, default=None)

        for ability in spawned_abilities:
            result = ability.update(dt)
            if result == "missed":
                missed_abilities += 1
            ability.draw(screen)

        for ability in spawned_abilities_queue:
            ability.draw(screen)

        current_time = time.time()
        # if valid_spawned_abilities:
        #     print(str(valid_spawned_abilities[0].image))
        if current_time >= next_tick_time and not valid_spawned_abilities:

            # Spawn abilities based on tick timing
            for ability_data in ability_sequence:
                tick_count = tick_ability_counts.get(current_tick, 0)
                tick_count_queue = tick_ability_counts_queue.get(next_ability, 0)
                tick_count_queue2 = tick_ability_counts_queue2.get(next_next_ability, 0)
                if ability_data["tick"] == current_tick:
                    ability = ability_data["ability"]
                    if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                        key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                        image_path = ABILITY_IMAGES[ability]  # Get mapped image
                        width = ability_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                        # Debug log for missing abilities

                        print(f"Spawning ability: {ability}, Keys: {key}, Tick: {current_tick}, Width: {width}, tick_count: {tick_count}, ABILITY_SPACING_Y: {ABILITY_SPACING_Y}")
                        ability_y = (win_h // 4) + (tick_count * (ABILITY_SPACING_Y))
                        print(f"Ability Y position: {ability_y}")
                        if key == []:
                            key = ["MOUSE"]
                        ability = Ability(
                            ability=ability,
                            key=key,
                            image_path=image_path,
                            start_x=press_zone_rect.x,  # Place ability on press_zone_rect
                            start_y=ability_y,
                            width=width / 2,
                            stationary=True,  # Mark ability as stationary
                            visible=see_abilities,
                            keybinds_visible = see_keybinds
                        )
                        spawned_abilities.append(ability)
                        tick_ability_counts[current_tick] = tick_count + 1
                    else:
                        print(f"Warning: Ability {ability} not found in keybinds or images.")
                        if "Text:" in ability:
                            print("Spawning a text ability")
                            width = ability_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                            ability_y = 0
                            ability = Ability(
                                ability=ability.removeprefix("Text: "),
                                key=ability.removeprefix("Text: "),
                                image_path= "None",
                                start_x=press_zone_rect.x - 10,  # Place ability on press_zone_rect
                                start_y=ability_y,
                                width=width / 2,
                                stationary=True,  # Mark ability as stationary
                                visible=see_abilities,
                                keybinds_visible = see_keybinds,
                                text_color = "red"
                            )
                            spawned_abilities.append(ability)
                            tick_ability_counts[current_tick] = tick_count + 0

                if ability_data["tick"] == next_ability:
                    ability = ability_data["ability"]
                    if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                        key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                        image_path = ABILITY_IMAGES[ability]  # Get mapped image
                        width = ability_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                        # Debug log for missing abilities
                        #print(f"Spawning ability: {ability}, Keys: {key}, Tick: {next_ability}, Width: {width}")

                        ability_y = (win_h // 4) + (tick_count_queue * (ABILITY_SPACING_Y))
                        if key == []:
                            key = ["MOUSE"]
                        ability = Ability(
                            ability=ability,
                            key=key,
                            image_path=image_path,
                            start_x=press_zone_rect.x + ABILITY_SPACING_X,  # Place ability on press_zone_rect
                            start_y=ability_y,
                            width=width / 2,
                            stationary=True,  # Mark ability as stationary
                            visible=see_abilities,
                            keybinds_visible = see_keybinds
                        )
                        spawned_abilities_queue.append(ability)
                        tick_ability_counts_queue[next_ability] = tick_count_queue + 1
                    else:
                        print(f"Warning: Ability {ability} not found in keybinds or images.")
                        if "Text:" in ability:
                            print("Spawning a text ability")
                            width = ability_data.get("width",ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                            ability_y = 0
                            ability = Ability(
                                ability=ability.removeprefix("Text: "),
                                key=ability.removeprefix("Text: "),
                                image_path= "None",
                                start_x=press_zone_rect.x + ABILITY_SPACING_X - 10,  # Place ability on press_zone_rect
                                start_y=ability_y,
                                width=width / 2,
                                stationary=True,  # Mark ability as stationary
                                visible=see_abilities,
                                keybinds_visible = see_keybinds,
                                text_color = "red"
                            )
                            spawned_abilities_queue.append(ability)
                            tick_ability_counts_queue[next_ability] = tick_count_queue + 0

                if ability_data["tick"] == next_next_ability:
                    ability = ability_data["ability"]
                    if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                        key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                        image_path = ABILITY_IMAGES[ability]  # Get mapped image
                        width = ability_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                        # Debug log for missing abilities
                        #print(f"Spawning ability: {ability}, Keys: {key}, Tick: {next_ability}, Width: {width}")

                        ability_y = (win_h // 4) + (tick_count_queue2 * (ABILITY_SPACING_Y))
                        if key == []:
                            key = ["MOUSE"]
                        ability = Ability(
                            ability=ability,
                            key=key,
                            image_path=image_path,
                            start_x=press_zone_rect.x + ABILITY_SPACING_X * 2,  # Place ability on press_zone_rect
                            start_y=ability_y,
                            width=width / 2,
                            stationary=True,  # Mark ability as stationary
                            visible=see_abilities,
                            keybinds_visible = see_keybinds
                        )
                        spawned_abilities_queue.append(ability)
                        tick_ability_counts_queue2[next_next_ability] = tick_count_queue2 + 1
                    else:
                        print(f"Warning: Ability {ability} not found in keybinds or images.")
                        if "Text:" in ability:
                            print("Spawning a text ability")
                            width = ability_data.get("width",ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                            ability_y = 0
                            ability = Ability(
                                ability=ability.removeprefix("Text: "),
                                key=ability.removeprefix("Text: "),
                                image_path= "None",
                                start_x=press_zone_rect.x + ABILITY_SPACING_X * 2 - 10,  # Place ability on press_zone_rect
                                start_y=ability_y,
                                width=width / 2,
                                stationary=True,  # Mark ability as stationary
                                visible=see_abilities,
                                keybinds_visible = see_keybinds,
                                text_color = "red"
                            )
                            spawned_abilities_queue.append(ability)
                            tick_ability_counts_queue2[next_next_ability] = tick_count_queue2 + 0


            #tick_bars.append(TickBar(SCREEN_WIDTH))  # Always spawn from the right side

        # Update and draw abilities
        # for ability in spawned_abilities:
        #     result = ability.update(dt)
        #     if result == "missed":
        #         missed_abilities += 1
        #     ability.draw(screen)
        #
        # for ability in spawned_abilities_queue:
        #     ability.draw(screen)


        # Update and draw tick bars
        for bar in tick_bars:
            bar.update(press_zone_rect, dt)
            bar.draw(screen)

        # Remove expired tick bars and abilities
        tick_bars = [bar for bar in tick_bars if bar.active]
        spawned_abilities = [ability for ability in spawned_abilities if ability.active]

        # Draw pressing zone
        pygame.draw.rect(screen, (0, 0, 0), press_zone_rect)

        # Process events ONCE per frame
        if not pygame.key.get_focused():
            pass

        # Display score and misses
        font = pygame.font.Font(None, 48)
        #score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        #misses_text = font.render(f"Misses: {missed_abilities}", True, (255, 255, 255))
        #screen.blit(score_text, (10, 10))
        #screen.blit(misses_text, (10, 60))

        # Display feedback message
        if feedback_message and time.time() < feedback_timer:
            font = pygame.font.Font(None, 22)
            if (str(config["see_correct_or_incorrect_feedback_message"])) == "True" or (str(config["see_correct_or_incorrect_feedback_message"])) == "true":
                if feedback_message == "Wrong!":
                    feedback_text = font.render(feedback_message, True, (255, 0, 0))
                else:
                    feedback_text = font.render(feedback_message, True, (0, 255, 0))
                screen.blit(feedback_text,(win_w // 2 - feedback_text.get_width() // 2, win_h // 2 - feedback_text.get_height() // 2))
        else:
            feedback_message = None  # Clear feedback message after timer expires

        pygame.display.flip()

        # Check if all abilities have played
        if (current_tick - 15) >= max([n["tick"] for n in ability_sequence]) and not spawned_abilities:
            game_over = True
            running = False  # End game loop

    def show_results(screen, score, total_abilities, missed_abilities):
        accuracy = (score / total_abilities) * 100 if total_abilities > 0 else 0
        font = pygame.font.Font(None, 24)
        screen.fill((0, 0, 0))
        exit_button = (str(config["default_exit_button"])).upper()
        restart_button = (str(config["default_restart_button"])).upper()
        results = [
            "Done!",
            f"Final Score: {score}",
            f"Total Abilities: {total_abilities}",
            f"Missed Abilities: {missed_abilities}",
            f"Accuracy: {score / (total_abilities + missed_abilities) * 100:.2f}%",
            f"Press {exit_button} to exit",
            f"Press {restart_button} to restart"
        ]

        for i, text in enumerate(results):
            rendered_text = font.render(text, True, (255, 255, 255))
            screen.blit(rendered_text, (win_w // 2 - 60, 10 + i * 25))

        pygame.display.flip()

    # Display results
    show_results(screen, score, total_abilities, missed_abilities)

    # Exit or restart screen handling
    # waiting = True
    new_global_key_events.clear()
    still_active_global_key_events.clear()
    # while waiting:
    #     if new_global_key_events != []:
    #         print("new_global_key_events:", new_global_key_events)
    #         if (str(config["default_restart_button"])).lower() in new_global_key_events or (str(config["default_restart_button"])).upper() in new_global_key_events:
    #             print("Restarting game...")
    #             running = True
    #             current_tick = 0
    #             score = 0
    #             missed_abilities = 0
    #             spawned_abilities = []
    #             tick_bars = []
    #             waiting = False
    #             new_global_key_events.clear()
    #             still_active_global_key_events.clear()
    #         elif (str(config["default_exit_button"])).lower() in new_global_key_events or (str(config["default_exit_button"])).upper() in new_global_key_events:
    #             print("Exiting game...")
    #             running = False
    #             waiting = False
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
    #             waiting = False
    #         elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
    #             # Restart the game
    #             running = True
    #             current_tick = 0
    #             score = 0
    #             missed_abilities = 0
    #             spawned_abilities = []
    #             tick_bars = []
    #             waiting = False  # Exit the results screen loop
    #             # Optionally reload the ability sequence or reset other variables if needed


def prompt_restart():
    pygame.event.clear()
    new_global_key_events.clear()
    still_active_global_key_events.clear()
    waiting = True
    while waiting:
        if (str(config["default_restart_button"])).lower() in new_global_key_events or (str(config["default_restart_button"])).upper() in new_global_key_events:
            new_global_key_events.clear()
            still_active_global_key_events.clear()
            return True
        if (str(config["default_exit_button"])).lower() in new_global_key_events or (str(config["default_exit_button"])).upper() in new_global_key_events:
            new_global_key_events.clear()
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                waiting = False


while True:
    play_game()
    if not prompt_restart():
        break
pygame.quit()