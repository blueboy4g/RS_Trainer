import pygame
import threading
import keyboard
import win32gui
import win32con

key_press_count = 0

def global_key_listener():
    def on_key_event(e):
        global key_press_count
        if e.event_type == 'down':
            key_press_count += 1
            print(f"[GLOBAL] Key pressed: {e.name} (Total: {key_press_count})")
    keyboard.hook(on_key_event)
    keyboard.wait('esc')

def make_window_always_on_top():
    hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# Start the global key listener
threading.Thread(target=global_key_listener, daemon=True).start()

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Global Keys + Always On Top")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Ensure the window stays on top
make_window_always_on_top()

running = True
while running:
    screen.fill((10, 10, 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display count
    text = font.render(f"Global key presses: {key_press_count}", True, (200, 200, 200))
    screen.blit(text, (50, 180))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
