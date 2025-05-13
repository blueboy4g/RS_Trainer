import time

import win32con

from Scripts.DialAnimation import DialAnimation
from Config import *
from Scripts.Ability import Ability
import tkinter as tk
import pygame
import threading
import keyboard
import win32gui

import sys
import json
with open("../Config.json", "r") as f:
    config = json.load(f)

ABILITY_KEYBINDS = config["ABILITY_KEYBINDS"]


if len(sys.argv) < 2:
    print("Usage: python RS_Trainer.py <config_file>")
    sys.exit(1)

config_file = sys.argv[1]
print(f"Using config: {config_file}")

# Example: load the config
with open(config_file, 'r') as f:
    note_sequence = json.load(f)

# Now you can use `config` in your script

# Initialize Pygame
pygame.init()
pygame.display.set_caption("RS Trainer")

# Tkinter is used to center the window on screen
root = tk.Tk()
root.withdraw()
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
win_w, win_h = 800, 200
x = round((screen_w - win_w) / 2)
y = round((screen_h - win_h) / 2 * 0.8)

# Create Pygame screen and set window position
screen = pygame.display.set_mode((win_w, win_h))
#SetWindowPos(pygame.display.get_wm_info()['window'], -1, x, y, 0, 0, 1)

see_notes=True

# Game Variables
press_zone_rect = pygame.Rect(PRESS_ZONE_X, (SCREEN_HEIGHT // 2) - 450, 1, 450)  # 1 pixel wide with extra height
tick_bars = []  # Store tick bars

# Game variables
running = True
clock = pygame.time.Clock()
spawned_notes = []
spawned_notes_queue = []
current_tick = 0
next_tick_time = time.time() + TICK_DURATION
last_tick_time = time.time()  # Track last tick time for debugging
score = 0
total_notes = len(note_sequence)
missed_notes = 0
last_tick_bar_time = None  # Store last tick bar collision time
tick_note_counts = {}
tick_note_counts_queue = {}# Dictionary to track notes stacking per tick
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP])
dial_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
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
        global key_press_count, new_global_key_events, still_active_global_key_events

        key = e.name
        if e.event_type == 'down':
            if key not in held_keys:
                held_keys.add(key)
                key_press_count += 1
                print(f"[GLOBAL] Key pressed once: {key} (Total: {key_press_count})")
                still_active_global_key_events.append(key)
                print(still_active_global_key_events)
                new_global_key_events = still_active_global_key_events.copy()

        elif e.event_type == 'up':
            print(f"[GLOBAL] Key released: {key}")
            held_keys.discard(key)
            if key in still_active_global_key_events:
                still_active_global_key_events.remove(key)
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
                    if k.lower() == key.lower() and mod.lower() == 'shift' and 'shift' in still_active_global_key_events:
                        still_active_global_key_events.remove('shift')
                        held_keys.discard('shift')
                # Remove corresponding symbol when number key is released
                if key in '1234567890':
                    symbol = key_combination_map.get(f'SHIFT+{key}')
                    if symbol and symbol in still_active_global_key_events:
                        still_active_global_key_events.remove(symbol)
                        held_keys.discard(symbol)
            new_global_key_events = still_active_global_key_events.copy()

    keyboard.hook(on_key_event)

def make_window_always_on_top():
    hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
make_window_always_on_top()
# Start the global key listener
threading.Thread(target=global_key_listener, daemon=True).start()

while running:
    screen.fill((0, 0, 0))  # Clear screen
    mouse_clicked = False  # Track mouse click state
    key_pressed = False  # Track key press state
    dt = clock.tick(60) / 1000.0  # Convert milliseconds to seconds

    # Update animation
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
                print(f"Key pressed: {event.key}")
                key_pressed = True
                key_down = event.key
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at {event.pos}")
            mouse_clicked = True

    keys = pygame.key.get_pressed()
    # Check for hits
    if key_down or mouse_clicked or new_global_key_events:
        print("new_global_key_events:", new_global_key_events)
        print("Key pressed:", key_down)
        ONE_NOTE_HIT = False
        for note in spawned_notes[:]:
            try:
                required_keys_pressed = False  # Start with False (assume key is NOT pressed)

                for k in note.key:
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
                        for k in note.key
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
                    #     for k in note.key
                    # )

                if required_keys_pressed:
                    new_global_key_events = []

                for k in note.key:
                    print("WE GOT: " + str(k))

                #TODO seems like we get random misses and im not sure why?
                if required_keys_pressed == False:
                    for k in note.key:
                        print("k.lower is " + str(k.lower()))
                        mapped_key = get_mapped_key(k.lower())
                        print("Mapped key is " + str(mapped_key))
                        required_keys_pressed = False
                        print("IN LOOP: " + str(k))
                        if k.lower() == "mouse":
                            # if space is in new global key
                            if "space" in new_global_key_events:
                                required_keys_pressed = True

                        elif mapped_key in new_global_key_events:
                            print(f"Key {mapped_key} is pressed mapped")
                            required_keys_pressed = True


                        elif k.lower() in new_global_key_events:
                            print(f"Key {k} is pressed")
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

                if required_keys_pressed and press_zone_rect.colliderect(note.rect):
                    print(f"Hit detected: {note.ability}")  # Debugging log
                    score += 1
                    spawned_notes.remove(note)
                    feedback_message = "Correct"
                    feedback_timer = time.time() + 1  # Show feedback for 1 second
                    failed_attempts = 0  # Reset failed attempts
                    ONE_NOTE_HIT = True

                    if note.ability not in EXCLUDED_DIAL_ANIMATIONS:
                        new_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
                        dial_animation_queue.append(new_animation)

            except KeyError:
                print(f"Warning: Unrecognized ability in note: {note.ability}")

        # Check for missed notes after the loop
        if not ONE_NOTE_HIT and (key_pressed or mouse_clicked or new_global_key_events):
            if new_global_key_events == ['shift'] or new_global_key_events == ['ctrl'] or new_global_key_events == ['alt']:
                pass
            else:
                print(key_pressed)
                print(new_global_key_events)
                failed_attempts += 1
                missed_notes += 1  # Increment missed notes
                print("Failed attempts:", failed_attempts)
                feedback_message = "Wrong!"
                feedback_timer = time.time() + 1  # Show feedback for 1 second
                if failed_attempts >= 3:
                    print("Making visible")
                    for note in spawned_notes:
                        note.visible = True  # Show the note after 3 failed attempts
    new_global_key_events.clear()

    # Tick system: Check if it's time for the next tick
    current_time = time.time()
    if current_time >= next_tick_time and not spawned_notes:
        print("On tick " + str(current_tick))
        spawned_notes_queue = []  # Reset queue for new notes
        actual_tick_duration = current_time - last_tick_time
        last_tick_time = current_time
        current_tick += 1
        #next_tick_time += TICK_DURATION  # Remove tick time so it instant

        future_ticks = [note["tick"] for note in note_sequence if note["tick"] > current_tick]
        next_note = min(future_ticks, default=None)

    for note in spawned_notes:
        result = note.update(dt)
        if result == "missed":
            missed_notes += 1
        note.draw(screen)

    for note in spawned_notes_queue:
        note.draw(screen)

    current_time = time.time()
    if current_time >= next_tick_time and not spawned_notes:

        # Spawn notes based on tick timing
        for note_data in note_sequence:
            tick_count = tick_note_counts.get(current_tick, 0)
            tick_count_queue = tick_note_counts_queue.get(next_note, 0)
            if note_data["tick"] == current_tick:
                ability = note_data["ability"]
                if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                    key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                    image_path = ABILITY_IMAGES[ability]  # Get mapped image
                    width = note_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                    # Debug log for missing notes

                    print(f"Spawning note: {ability}, Keys: {key}, Tick: {current_tick}, Width: {width}, tick_count: {tick_count}, NOTE_SPACING_Y: {NOTE_SPACING_Y}")
                    note_y = (SCREEN_HEIGHT // 24) + (tick_count * (NOTE_SPACING_Y - 20))
                    if key == []:
                        key = ["MOUSE"]
                    note = Ability(
                        ability=ability,
                        key=key,
                        image_path=image_path,
                        start_x=press_zone_rect.x,  # Place note on press_zone_rect
                        start_y=note_y,
                        width=width / 2,
                        stationary=True,  # Mark note as stationary
                        visible=see_notes
                    )
                    spawned_notes.append(note)
                    tick_note_counts[current_tick] = tick_count + 1

            if note_data["tick"] == next_note:
                ability = note_data["ability"]
                if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                    key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                    image_path = ABILITY_IMAGES[ability]  # Get mapped image
                    width = note_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided
                    # Debug log for missing notes
                    #print(f"Spawning note: {ability}, Keys: {key}, Tick: {next_note}, Width: {width}")

                    note_y = (SCREEN_HEIGHT // 24) + (tick_count_queue * (NOTE_SPACING_Y - 20))
                    if key == []:
                        key = ["MOUSE"]
                    note = Ability(
                        ability=ability,
                        key=key,
                        image_path=image_path,
                        start_x=press_zone_rect.x + 350,  # Place note on press_zone_rect
                        start_y=note_y,
                        width=width / 2,
                        stationary=True,  # Mark note as stationary
                        visible=see_notes
                    )
                    spawned_notes_queue.append(note)
                    tick_note_counts_queue[next_note] = tick_count_queue + 1


        #tick_bars.append(TickBar(SCREEN_WIDTH))  # Always spawn from the right side

    # Update and draw notes
    # for note in spawned_notes:
    #     result = note.update(dt)
    #     if result == "missed":
    #         missed_notes += 1
    #     note.draw(screen)
    #
    # for note in spawned_notes_queue:
    #     note.draw(screen)


    # Update and draw tick bars
    for bar in tick_bars:
        bar.update(press_zone_rect, dt)
        bar.draw(screen)

    # Remove expired tick bars and notes
    tick_bars = [bar for bar in tick_bars if bar.active]
    spawned_notes = [note for note in spawned_notes if note.active]

    # Draw pressing zone
    pygame.draw.rect(screen, (255, 0, 0), press_zone_rect)

    # Process events ONCE per frame
    if not pygame.key.get_focused():
        pass

    # Display score and misses
    font = pygame.font.Font(None, 48)
    #score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    #misses_text = font.render(f"Misses: {missed_notes}", True, (255, 255, 255))
    #screen.blit(score_text, (10, 10))
    #screen.blit(misses_text, (10, 60))

    # Display feedback message
    if feedback_message and time.time() < feedback_timer:
        font = pygame.font.Font(None, 22)
        if feedback_message == "Wrong!":
            feedback_text = font.render(feedback_message, True, (255, 0, 0))
        else:
            feedback_text = font.render(feedback_message, True, (0, 255, 0))
        screen.blit(feedback_text,
                    (win_w // 2 - feedback_text.get_width() // 2, win_h // 2 - feedback_text.get_height() // 2))
    else:
        feedback_message = None  # Clear feedback message after timer expires

    pygame.display.flip()

    # Check if all notes have played
    if (current_tick - 15) >= max([n["tick"] for n in note_sequence]) and not spawned_notes:
        game_over = True
        running = False  # End game loop

def show_results(screen, score, total_notes, missed_notes):
    accuracy = (score / total_notes) * 100 if total_notes > 0 else 0
    font = pygame.font.Font(None, 24)
    screen.fill((0, 0, 0))

    results = [
        "Done!",
        f"Final Score: {score}",
        f"Total Notes: {total_notes}",
        f"Missed Notes: {missed_notes}",
        f"Accuracy: {score / (total_notes + missed_notes) * 100:.2f}%",
        "Press ESC to exit",
        "Press R to restart"
    ]

    for i, text in enumerate(results):
        rendered_text = font.render(text, True, (255, 255, 255))
        screen.blit(rendered_text, (SCREEN_WIDTH // 2 - 150, 10 + i * 25))

    pygame.display.flip()

# Display results
show_results(screen, score, total_notes, missed_notes)

# Exit or restart screen handling
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            waiting = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Restart the game
            running = True
            current_tick = 0
            score = 0
            missed_notes = 0
            spawned_notes = []
            tick_bars = []
            waiting = False  # Exit the results screen loop
            # Optionally reload the note sequence or reset other variables if needed

pygame.quit()
