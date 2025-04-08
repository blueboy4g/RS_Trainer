import json
import time

from DialAnimation import DialAnimation
from TestConfig import *
from TestNote import Note, TickBar
import pygame
import tkinter as tk

# TODO get tons of images from in-game

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Guitar Hero Trainer")

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

# Load note sequences
with open("Vernyx.json") as f:
    note_sequence = json.load(f)

# Game variables
running = True
clock = pygame.time.Clock()
spawned_notes = []
current_tick = 0
next_tick_time = time.time() + TICK_DURATION
last_tick_time = time.time()  # Track last tick time for debugging
score = 0
total_notes = len(note_sequence)
missed_notes = 0
last_tick_bar_time = None  # Store last tick bar collision time
tick_note_counts = {}  # Dictionary to track notes stacking per tick
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

        # Spawn notes based on tick timing
        # Spawn notes based on tick timing
        # Spawn notes based on tick timing
        for note_data in note_sequence:
            if note_data["tick"] == current_tick:
                ability = note_data["ability"]

                # if current_tick == 1:
                #     added_x_spacing = 50
                #     pass
                # else:
                #     added_x_spacing = 0

                if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                    key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                    image_path = ABILITY_IMAGES[ability]  # Get mapped image
                    width = note_data.get("width", ABILITY_DEFAULT_WIDTH)  # Default width to 75 if not provided

                    # Debug log for missing notes
                    print(f"Spawning note: {ability}, Keys: {key}, Tick: {current_tick}, Width: {width}")

                    tick_count = tick_note_counts.get(current_tick, 0)
                    note_y = (SCREEN_HEIGHT // 4) + (tick_count * NOTE_SPACING_Y)
                    if key == []:
                        key = ["MOUSE"]
                    note = Note(
                        ability=ability,
                        key=key,
                        image_path=image_path,
                        start_x=SCREEN_WIDTH, #+ added_x_spacing,
                        start_y=note_y,
                        width=width  # Pass custom width
                    )
                    spawned_notes.append(note)
                    tick_note_counts[current_tick] = tick_count + 1

        tick_bars.append(TickBar(SCREEN_WIDTH))  # Always spawn from the right side

    # Update and draw notes
    for note in spawned_notes:
        result = note.update(dt)
        if result == "missed":
            missed_notes += 1
        note.draw(screen)

    # Update and draw tick bars
    for bar in tick_bars:
        bar.update(press_zone_rect, dt)
        bar.draw(screen)

    # Remove expired tick bars and notes
    tick_bars = [bar for bar in tick_bars if bar.active]
    spawned_notes = [note for note in spawned_notes if note.active]

    # Draw pressing zone
    pygame.draw.rect(screen, (255, 0, 0), press_zone_rect)

    keys = pygame.key.get_pressed()

    # Process events ONCE per frame
    if not pygame.key.get_focused():
        #print("⚠️ WARNING: Pygame window is NOT focused! Click inside the window.")
        pass
    # Check for hits
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
                     keys[getattr(pygame, f'K_{k.lower()}', None)] if getattr(pygame, f'K_{k.lower()}', None) else False)
                    for k in note.key
                )

            # ✅ **Check if the note’s ability should trigger the dial animation**
            if required_keys_pressed and press_zone_rect.colliderect(note.rect):
                print(f"Hit detected: {note.ability}")  # Debugging log
                score += 1
                spawned_notes.remove(note)

                # ✅ **Only add animation if the ability is NOT in the exclusion list**
                if note.ability not in EXCLUDED_DIAL_ANIMATIONS:
                    new_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
                    dial_animation_queue.append(new_animation)

        except KeyError:
            print(f"Warning: Unrecognized ability in note: {note.ability}")

    # Display score
    font = pygame.font.Font(None, 48)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    #clock.tick(30)  # 60 FPS

    # Check if all notes have played
    if (current_tick - 15) >= max([n["tick"] for n in note_sequence]) and not spawned_notes:
        game_over = True
        running = False  # End game loop


# Show results screen
def show_results(screen, score, total_notes, missed_notes):
    accuracy = (score / total_notes) * 100 if total_notes > 0 else 0
    font = pygame.font.Font(None, 48)
    screen.fill((0, 0, 0))

    results = [
        f"Game Over!",
        f"Final Score: {score}",
        f"Total Notes: {total_notes}",
        f"Missed Notes: {missed_notes}",
        f"Accuracy: {accuracy:.2f}%",
        "Press ESC to exit"
    ]

    for i, text in enumerate(results):
        rendered_text = font.render(text, True, (255, 255, 255))
        screen.blit(rendered_text, (SCREEN_WIDTH // 2 - 150, 200 + i * 50))

    pygame.display.flip()

# Display results
show_results(screen, score, total_notes, missed_notes)

# Exit screen handling
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            waiting = False

pygame.quit()
