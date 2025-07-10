import time

from config.config import *
from scripts.dial_animation import DialAnimation
from scripts.ability import Ability, TickBar
import pygame
import tkinter as tk

import sys
import json
from config.config import USER_KEYBINDS


def show_error_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)
    root.destroy()  # Destroy the root window after the popup

try:
    with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
        config = json.load(f)
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

ABILITY_KEYBINDS = config["ABILITY_KEYBINDS"]

if len(sys.argv) < 2:
    print("Usage: python RS_Trainer.py <config_file>")
    config_file = "C://Users//PC//AppData//Roaming//Azulyn//boss_rotations//telos_necro.json"
else:
    config_file = sys.argv[1]
    print(f"Using config: {config_file}")

try:
    with open(config_file, "r", encoding="utf-8") as f:
        ability_sequence = json.load(f)
except json.JSONDecodeError as e:
    error_message = (
        f"Error: Your .JSON file is not formatted correctly.\n"
        f"Fix it at: '{config_file}'\n"
        f"Line {e.lineno}, Column {e.colno}.\n"
        f"Message: {e.msg}"
    )
    show_error_popup(error_message)
    sys.exit(1)
except FileNotFoundError:
    error_message = f"Error: The file '{config_file}' was not found."
    show_error_popup(error_message)
    sys.exit(1)

# Now you can use `config` in your script

# Initialize Pygame
pygame.init()
pygame.display.set_caption("RS Trainer")
icon = pygame.image.load("../resources/azulyn_icon.ico")
pygame.display.set_icon(icon)

# Tkinter is used to center the window on screen
root = tk.Tk()
root.withdraw()
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
win_w, win_h = 800, 600
x = round((screen_w - win_w) / 2)
y = round((screen_h - win_h) / 2 * 0.8)

# Create Pygame screen and set window position
screen = pygame.display.set_mode((win_w, win_h))
#SetWindowPos(pygame.display.get_wm_info()['window'], -1, x, y, 0, 0, 1)



# Game Variables
press_zone_rect = pygame.Rect(PRESS_ZONE_X, (SCREEN_HEIGHT // 2) - 225, 1, 450)  # 1 pixel wide with extra height
tick_bars = []  # Store tick bars

# Load ability sequences
# with open("Boss_Rotations/Vernyx.json") as f:
#     ability_sequence = json.load(f)

# Game variables
running = True
clock = pygame.time.Clock()
spawned_abilities = []
current_tick = 0
next_tick_time = time.time() + TICK_DURATION
last_tick_time = time.time()  # Track last tick time for debugging
score = 0
total_abilities = len(ability_sequence)
missed_abilities = 0
last_tick_bar_time = None  # Store last tick bar collision time
tick_ability_counts = {}  # Dictionary to track abilities stacking per tick
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP])
dial_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
dial_animation_queue = []  # Queue for animations
current_animation = None  # Track the currently playing animation

# Main Game Loop
while running:
    screen.fill((0, 0, 0))  # Clear screen
    mouse_clicked = False  # Track mouse click state
    #dt = clock.tick(30) / 100.0
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(f"Key pressed: {event.key}")

            # Add new animation to the queue
            #new_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
            #dial_animation_queue.append(new_animation)  # Queue it instead of playing immediately


        elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse clicked at {event.pos}")
                mouse_clicked = True


    # Tick system: Check if it's time for the next tick
    current_time = time.time()
    if current_time >= next_tick_time:
        actual_tick_duration = current_time - last_tick_time
        #print(f"Tick {current_tick + 1}: {actual_tick_duration:.6f} seconds since last tick")

        last_tick_time = current_time
        current_tick += 1
        next_tick_time += TICK_DURATION  # Add 0.6s to next tick

        # Spawn abilities based on tick timing
        for ability_data in ability_sequence:
            if ability_data["tick"] == current_tick:
                ability = ability_data["ability"]

                # if current_tick == 1:
                #     added_x_spacing = 50
                #     pass
                # else:
                #     added_x_spacing = 0

                if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                    key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                    image_path = ABILITY_IMAGES[ability]  # Get mapped image
                    width = ability_data.get("width", 75)  # Default width to 75 if not provided

                    # Debug log for missing abilities
                    print(f"Spawning ability: {ability}, Keys: {key}, Tick: {current_tick}, Width: {width}")

                    tick_count = tick_ability_counts.get(current_tick, 0)
                    ability_y = (SCREEN_HEIGHT // 4) + (tick_count * ABILITY_SPACING_Y)
                    if key == []:
                        key = ["MOUSE"]
                    ability = Ability(
                        ability=ability,
                        key=key,
                        image_path=image_path,
                        start_x=SCREEN_WIDTH, #+ added_x_spacing,
                        start_y=ability_y,
                        width=width  # Pass custom width
                    )
                    spawned_abilities.append(ability)
                    tick_ability_counts[current_tick] = tick_count + 1

        tick_bars.append(TickBar(SCREEN_WIDTH))  # Always spawn from the right side

    # Update and draw abilities
    for ability in spawned_abilities:
        result = ability.update(dt)
        if result == "missed":
            missed_abilities += 1
        ability.draw(screen)

    # Update and draw tick bars
    for bar in tick_bars:
        bar.update(press_zone_rect, dt)
        bar.draw(screen)

    # Remove expired tick bars and abilities
    tick_bars = [bar for bar in tick_bars if bar.active]
    spawned_abilities = [ability for ability in spawned_abilities if ability.active]

    # Draw pressing zone
    pygame.draw.rect(screen, (255, 0, 0), press_zone_rect)

    keys = pygame.key.get_pressed()

    # Process events ONCE per frame
    if not pygame.key.get_focused():
        #print("⚠️ WARNING: Pygame window is NOT focused! Click inside the window.")
        pass
    # Check for hits
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
                     keys[getattr(pygame, f'K_{k.lower()}', None)] if getattr(pygame, f'K_{k.lower()}', None) else False)
                    for k in ability.key
                )

            # ✅ **Check if the ability’s ability should trigger the dial animation**
            if required_keys_pressed and press_zone_rect.colliderect(ability.rect):
                print(f"Hit detected: {ability.ability}")  # Debugging log
                score += 1
                spawned_abilities.remove(ability)

                # ✅ **Only add animation if the ability is NOT in the exclusion list**
                if ability.ability not in EXCLUDED_DIAL_ANIMATIONS:
                    new_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
                    dial_animation_queue.append(new_animation)

        except KeyError:
            print(f"Warning: Unrecognized ability in ability: {ability.ability}")

    # Display score
    font = pygame.font.Font(None, 48)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    #clock.tick(30)  # 60 FPS

    # Check if all abilities have played
    if (current_tick - 15) >= max([n["tick"] for n in ability_sequence]) and not spawned_abilities:
        game_over = True
        running = False  # End game loop


# Show results screen
def show_results(screen, score, total_abilities, missed_abilities):
    accuracy = (score / total_abilities) * 100 if total_abilities > 0 else 0
    font = pygame.font.Font(None, 48)
    screen.fill((0, 0, 0))

    results = [
        f"Game Over!",
        f"Final Score: {score}",
        f"Total Abilities: {total_abilities}",
        f"Missed Abilities: {missed_abilities}",
        f"Accuracy: {accuracy:.2f}%",
        "Press ESC to exit"
    ]

    for i, text in enumerate(results):
        rendered_text = font.render(text, True, (255, 255, 255))
        screen.blit(rendered_text, (SCREEN_WIDTH // 2 - 150, 200 + i * 50))

    pygame.display.flip()

# Display results
show_results(screen, score, total_abilities, missed_abilities)

# Exit screen handling
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            waiting = False

pygame.quit()
