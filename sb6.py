import pygame
import os

pygame.init()

# Lijst van .wav bestanden
sound_files = [f for f in os.listdir('C:/Sounds') if f.endswith('.wav')]

# Scherm instellen - niet fullscreen maar resizable
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Soundboard")

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Geluiden laden
sounds = {}
for file in sound_files:
    sounds[file] = pygame.mixer.Sound(os.path.join('C:/Sounds', file))

# Knoppen en scrollbar
buttons = []
button_size = 160  # Vierkante knoppen
gap = 10  # Afstand tussen knoppen
min_buttons_per_row = 2  # Minimum aantal knoppen per rij
max_buttons_per_row = 5  # Maximum aantal knoppen per rij
row_gap = 10  # Afstand tussen rijen

font = pygame.font.Font(None, 24)  # Font voor tekstmeting

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width = font.size(word)[0]
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        if len(' '.join(current_line)) > 30:  # Na 30 tekens nieuwe regel
            lines.append(' '.join(current_line))
            current_line = []
            current_width = 0

    if current_line:
        lines.append(' '.join(current_line))
    return lines

def update_buttons(screen_width):
    buttons.clear()
    available_width = screen_width - 20  # 20 voor de scrollbar en wat margin
    buttons_per_row = max(min_buttons_per_row, min(max_buttons_per_row, available_width // (button_size + gap)))
    effective_button_size = (available_width - (buttons_per_row - 1) * gap) // buttons_per_row
    
    for i, file in enumerate(sound_files):
        wrapped_lines = wrap_text(file, font, effective_button_size - 10)  # 10 voor wat marge
        col = i % buttons_per_row
        row = i // buttons_per_row
        height = button_size + (len(wrapped_lines) - 1) * font.get_linesize()  # Pas hoogte aan voor meerdere regels
        button = pygame.Rect(10 + col * (effective_button_size + gap), 
                             10 + row * (height + row_gap), 
                             effective_button_size, height)
        buttons.append((button, wrapped_lines))

    return buttons_per_row

buttons_per_row = update_buttons(screen.get_width())

# Scrollbaar gebied
scroll_rect = pygame.Rect(0, 0, screen.get_width() - 20, screen.get_height() - 20)
scroll_offset = 0
max_scroll = 0

# Scrollbar
scrollbar_width = 10
scrollbar = pygame.Rect(screen.get_width() - scrollbar_width, 0, scrollbar_width, screen.get_height())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Controleer alleen op MOUSEBUTTONDOWN, niet op scrollen
            if event.button == 1:  # Alleen linkerklik
                for button, wrapped_lines in buttons:
                    adjusted_button = button.move(0, -scroll_offset)
                    if adjusted_button.collidepoint(event.pos):
                        full_name = ' '.join(wrapped_lines)
                        if full_name in sounds:
                            sounds[full_name].play()
                        else:
                            print(f"Geluid niet gevonden voor: {full_name}")
        elif event.type == pygame.MOUSEBUTTONUP:  # Scrollen events
            if event.button == 4:  # Muiswiel omhoog
                scroll_offset = max(0, scroll_offset - 50)  # Scroll omhoog
            elif event.button == 5:  # Muiswiel omlaag
                scroll_offset = min(max_scroll, scroll_offset + 50)  # Scroll omlaag
        elif event.type == pygame.VIDEORESIZE:
            # Scherm grootte aanpassen
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            scroll_rect.width = screen.get_width() - 20
            scroll_rect.height = screen.get_height() - 20
            scrollbar.x = screen.get_width() - scrollbar_width
            scrollbar.height = screen.get_height()
            buttons_per_row = update_buttons(screen.get_width())
            # Bereken max_scroll na het bijwerken van de knoppen
            max_scroll = max(0, sum(button[0].height + row_gap for button in buttons) - scroll_rect.height)

    screen.fill(WHITE)  # Zorg ervoor dat het scherm wordt gevuld met wit
    
    # Teken knoppen
    for button, wrapped_lines in buttons:
        adjusted_button = button.move(0, -scroll_offset)
        if scroll_rect.colliderect(adjusted_button):  # Alleen zichtbare knoppen tekenen
            pygame.draw.rect(screen, BLACK, adjusted_button, 1)
            for i, line in enumerate(wrapped_lines):
                text = font.render(line, True, BLACK)
                screen.blit(text, (adjusted_button.left + 5, adjusted_button.top + 5 + i * font.get_linesize()))

    # Teken scrollbar
    pygame.draw.rect(screen, GRAY, scrollbar)
    if max_scroll > 0:  # Voorkom deling door nul
        handle_height = max(20, int(scrollbar.height * (scroll_rect.height / (max_scroll + scroll_rect.height))))
        handle_y = scrollbar.top + (scroll_offset / max_scroll) * (scrollbar.height - handle_height)
        pygame.draw.rect(screen, BLACK, (scrollbar.left, handle_y, scrollbar_width, handle_height))

    pygame.display.flip()

pygame.quit()
