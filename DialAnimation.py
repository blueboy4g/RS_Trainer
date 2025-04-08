import pygame
import time
import math

class DialAnimation:
    def __init__(self, x, y, size=50, duration_ticks=3):
        """Create a dial animation that lasts for 'duration_ticks' ticks."""
        self.x = x
        self.y = y
        self.size = size
        self.angle = 270  # Start at 270° (pointing up)
        self.start_time = None  # Will be set when animation starts
        self.duration_seconds = duration_ticks * 0.6  # 3 ticks * 0.6s per tick = 1.8s
        self.active = False  # Track if animation is currently running

    def start(self):
        """Start the animation when it is dequeued."""
        self.start_time = time.time()
        self.active = True

    def update(self, dt):
        """Update the animation rotation."""
        if not self.active or self.start_time is None:
            return

        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.duration_seconds:
            self.active = False  # Mark animation as complete
            return

        # Rotate smoothly, completing 360° in `duration_seconds`
        self.angle = 270 + (elapsed_time / self.duration_seconds) * 360  # Always starts & ends vertical

    def draw(self, screen):
        """Draw the dial animation."""
        if not self.active:
            return

        # Draw square background
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.size, self.size), border_radius=10)

        # Calculate dial position
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        radius = self.size // 2 - 5
        end_x = center_x + math.cos(math.radians(self.angle)) * radius
        end_y = center_y + math.sin(math.radians(self.angle)) * radius

        # Draw rotating dial
        pygame.draw.line(screen, (255, 255, 255), (center_x, center_y), (end_x, end_y), 4)
