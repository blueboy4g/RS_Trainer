import pygame

# Initialize Pygame
pygame.init()

# Create Window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Mouse Test")

# Main Loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen
    pygame.display.flip()  # Update screen

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse Button {event.button} clicked at {event.pos}")

pygame.quit()
