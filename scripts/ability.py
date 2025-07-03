import time

import pygame
import os

from config.config import ABILITY_SPEED

last_tick_bar_time = None  # Initialize tick timing

class GameObject:
    """Base class for moving objects (TickBar & Ability)"""
    def __init__(self, x, y, width, height, speed, color=(200, 200, 200)):
        self.rect = pygame.Rect(x, y, width, height)  # Use a rect for movement
        self.speed = speed  # Movement speed
        self.active = True  # Determines if the object is still in play
        self.color = color  # Default color for rendering

    def update(self, dt):
        """Moves the object left"""
        self.rect.x -= self.speed * dt

        # Deactivate if out of bounds
        if self.rect.right < 0:
            self.active = False

    def draw(self, screen):
        """Draws the object as a rectangle"""
        pygame.draw.rect(screen, self.color, self.rect)


class TickBar(GameObject):
    """A visual tick marker that moves across the screen"""

    pygame.font.init()  # Ensure font system is initialized
    tick_times = [.6]  # Shared list to track tick times
    NUM_TICKS_TO_AVERAGE = 10  # Moving average size
    font = pygame.font.Font(None, 36)  # UI font for displaying average tick time

    def __init__(self, x):
        super().__init__(x, 0, 2, pygame.display.get_surface().get_height(), ABILITY_SPEED, (50, 50, 50))
        self.collided = False  # Detects collision once

    def update(self, press_zone_rect, dt):
        """Moves TickBar & checks for press zone collision"""
        super().update(dt)  # Move as a GameObject

        if not self.collided and press_zone_rect.colliderect(self.rect):
            self.collided = True  # Mark as collided
            global last_tick_bar_time
            current_time = time.time()

            # Calculate time since last tick bar
            if last_tick_bar_time is not None:
                time_since_last_tick = current_time - last_tick_bar_time

                # Store tick duration & maintain a fixed size list
                TickBar.tick_times.append(time_since_last_tick)
                if len(TickBar.tick_times) > TickBar.NUM_TICKS_TO_AVERAGE:
                    TickBar.tick_times.pop(0)  # Remove oldest tick time

            last_tick_bar_time = current_time  # Update last collision time

    def draw(self, screen):
        """Draw the TickBar and the Average Tick Time UI"""
        super().draw(screen)  # Draw tick bar

        # Compute and display the average tick time
        if TickBar.tick_times:
            avg_tick_time = sum(TickBar.tick_times) / len(TickBar.tick_times)
            avg_tick_text = TickBar.font.render(f"Avg Tick Time: {avg_tick_time:.3f}s", True, (255, 255, 255))
            screen.blit(avg_tick_text, (10, 50))  # Position the text on screen


class Ability(GameObject):
    """Represents a falling ability that must be pressed"""
    def __init__(self, ability, key, image_path, start_x, start_y, width=75, stationary=False, visible=True, keybinds_visible=True, text_color = ""):
        super().__init__(start_x, start_y, width, width, ABILITY_SPEED)
        print(str(ability))
        self.ability = ability  # Store ability name
        self.key = key if isinstance(key, list) else [key]  # Ensure key is list
        self.is_click_ability = "MOUSE" in self.key  # Determine if it's a click ability
        self.font = pygame.font.Font(None, 24)
        self.stationary = stationary  # Flag to indicate if the ability is stationary
        self.visible = visible  # Flag to control visibility
        self.keybinds_visible = keybinds_visible
        self.text_color = text_color  # Color for keybind text

        # Load image safely
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path)
        else:
            print(f"Warning: Failed to load image {image_path}")
            self.image = None

    def update(self, dt):
        """Moves the ability if it's not stationary"""
        if not self.stationary:
            super().update(dt)

    def draw(self, screen):
        """Draws the ability and key label if visible"""
        if self.visible:
            if self.image:
                self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
                screen.blit(self.image, self.rect)
            else:
                pass

        # Draw key label
        if self.keybinds_visible:
            #TODO show the keybinds
            key_label = "CLICK" if self.is_click_ability else " + ".join(self.key)
            if self.text_color == "red":
                text_surface = self.font.render(key_label, True, (255, 0, 0))
            else:
                text_surface = self.font.render(key_label, True, (255, 255, 255))
            text_x = self.rect.x + (self.rect.width // 4)
            text_y = max(10, self.rect.y - 22)  # Prevents text from going off-screen
            screen.blit(text_surface, (text_x, text_y))
        else:
            pass