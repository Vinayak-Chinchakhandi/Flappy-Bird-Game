import pygame
import random
import os
import sys
import re

# Initialize Pygame
pygame.init()

# Get screen resolution
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)  # 80% of the screen width
SCREEN_HEIGHT = int(info.current_h * 0.8)  # 80% of the screen height

# Game constants
PIPE_WIDTH = 50
PIPE_GAP = 200
BIRD_WIDTH = 70
BIRD_HEIGHT = 55
GRAVITY = 0.5
FLAP_STRENGTH = 10
SPEED = 2.8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)
BUTTON_HOVER_COLOR = (0, 200, 255)
ERROR_COLOR = (255, 0, 0)

# Load assets
bird_img = pygame.image.load("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/bird image.png")
background_img = pygame.image.load("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/background image.jpg")
pipe_img = pygame.image.load("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/tree image.jpeg")
flap_sound = pygame.mixer.Sound("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/flap sound.mp3")
hit_sound = pygame.mixer.Sound("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/hit sound.mp3")
point_sound = pygame.mixer.Sound("C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/pass sound.mp3")

# Scale images to fit the screen size
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
bird_img = pygame.transform.scale(bird_img, (BIRD_WIDTH, BIRD_HEIGHT))
pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, SCREEN_HEIGHT // 2))

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load font
font = pygame.font.Font(None, 48)

# User-related variables
current_user = ""
high_scores = {}

# High scores file path
high_scores_file = "C:/Users/vinay/OneDrive/Desktop/Vinayak/PROJECTS/Flappy bird/d.txt"

# Load high scores from file
if os.path.exists(high_scores_file):
    with open(high_scores_file, "r") as f:
        for line in f:
            # Skip empty lines and ensure the line contains exactly 3 parts
            line = line.strip()
            if line:
                parts = line.split(":")
                if len(parts) == 3:
                    name, score, password = parts
                    high_scores[name] = {"score": int(score), "password": password}
                else:
                    print(f"Skipping invalid line in file: {line}")


def save_high_scores():
    """Save high scores to file."""
    with open(high_scores_file, "w") as f:
        for name, data in high_scores.items():
            f.write(f"{name}:{data['score']}:{data['password']}\n")

def draw_bird(x, y):
    screen.blit(bird_img, (x, y))

def draw_pipe(x, pipe_height):
    # Draw the inverted top pipe
    top_pipe = pygame.transform.flip(pipe_img, False, True)
    screen.blit(top_pipe, (x, pipe_height - pipe_img.get_height()))
    # Draw the bottom pipe
    screen.blit(pipe_img, (x, pipe_height + PIPE_GAP))

def check_collision(bird_rect, pipes):
    if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
        return True
    for pipe in pipes:
        if bird_rect.colliderect(pipe[0]) or bird_rect.colliderect(pipe[1]):
            hit_sound.play()  # Play collision sound
            return True
    return False

def generate_pipes(x):
    pipe_height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
    top_pipe = pygame.Rect(x, pipe_height - pipe_img.get_height(), PIPE_WIDTH, pipe_img.get_height())
    bottom_pipe = pygame.Rect(x, pipe_height + PIPE_GAP, PIPE_WIDTH, pipe_img.get_height())
    return (top_pipe, bottom_pipe)

def display_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def display_high_score():
    if current_user in high_scores:
        high_score_text = font.render(f"High Score: {high_scores[current_user]['score']}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH - 300, 10))

def render_button(text, rect, mouse_pos, action=None):
    # Check if mouse is over the button
    is_hovered = rect.collidepoint(mouse_pos)

    # Draw button
    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR, rect)

    # Render button text
    button_text = font.render(text, True, WHITE)
    text_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, text_rect)

    return is_hovered

def login_page():
    """Display the login page."""
    global current_user
    
    # Define dimensions for UI elements
    input_box_width, input_box_height = 300, 60
    password_box_width, password_box_height = 300, 60
    button_width, button_height = 300, 60
    radio_size = 30

    # Offset to move content slightly above center
    vertical_offset = -100

    input_box = pygame.Rect(
        SCREEN_WIDTH // 2 - input_box_width // 2,
        SCREEN_HEIGHT // 2 - 30 + vertical_offset,
        input_box_width,
        input_box_height
    )
    password_box = pygame.Rect(
        SCREEN_WIDTH // 2 - password_box_width // 2,
        SCREEN_HEIGHT // 2 + 80 + vertical_offset,
        password_box_width,
        password_box_height
    )
    start_button = pygame.Rect(
        SCREEN_WIDTH // 2 - button_width // 2,
        SCREEN_HEIGHT // 2 + 200 + vertical_offset,
        button_width,
        button_height
    )
    new_user_radio = pygame.Rect(
        SCREEN_WIDTH // 2 - button_width // 2 + 10,
        SCREEN_HEIGHT // 2 + 160 + vertical_offset,
        radio_size,
        radio_size
    )

    active_name = False
    active_password = False
    user_text = ""
    password_text = ""
    placeholder_name = "Name"
    placeholder_password = "Password"
    error_message = ""
    is_new_user = False

    while True:
        screen.blit(background_img, (0, 0))

        # Render input box
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if active_name else BUTTON_COLOR, input_box, 2)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if active_password else BUTTON_COLOR, password_box, 2)

        # Display name and password
        if user_text == "" and not active_name:
            name_surface = font.render(placeholder_name, True, (180, 180, 180))
        else:
            name_surface = font.render(user_text, True, WHITE)

        if password_text == "" and not active_password:
            password_surface = font.render(placeholder_password, True, (180, 180, 180))
        else:
            password_surface = font.render("*" * len(password_text), True, WHITE)

        screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))
        screen.blit(password_surface, (password_box.x + 10, password_box.y + 10))

        # Render start button and new user radio
        mouse_pos = pygame.mouse.get_pos()
        start_hovered = render_button("Start", start_button, mouse_pos)

        # Draw radio button for new user
        pygame.draw.circle(screen, BUTTON_COLOR, (new_user_radio.centerx, new_user_radio.centery), 15)
        if is_new_user:
            pygame.draw.circle(screen, BUTTON_HOVER_COLOR, (new_user_radio.centerx, new_user_radio.centery), 15)

        # Render "New User" text beside the radio button
        new_user_text = font.render("New User", True, WHITE)
        screen.blit(new_user_text, (new_user_radio.x + 40, new_user_radio.y))

        # Display error message if any
        if error_message:
            error_text = font.render(error_message, True, ERROR_COLOR)
            screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 50))  # Top-center position

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active_name = True
                else:
                    active_name = False

                if password_box.collidepoint(event.pos):
                    active_password = True
                else:
                    active_password = False

                if new_user_radio.collidepoint(event.pos):
                    is_new_user = not is_new_user

                if start_hovered and user_text.strip() and password_text.strip():
                    # Check if name is valid
                    if not re.match("^[A-Za-z]*$", user_text):
                        error_message = "Name should only contain letters"
                        continue

                    if is_new_user:
                        if user_text.strip() in high_scores:
                            error_message = "User already exists, try a different name"
                        else:
                            high_scores[user_text.strip()] = {"score": 0, "password": password_text.strip()}
                            current_user = user_text.strip()
                            error_message = ""
                            save_high_scores()
                            return
                    else:
                        if user_text.strip() in high_scores and high_scores[user_text.strip()]["password"] == password_text.strip():
                            current_user = user_text.strip()
                            error_message = ""
                            return
                        else:
                            error_message = "Incorrect username or password"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if active_name:
                        user_text = user_text[:-1]
                    elif active_password:
                        password_text = password_text[:-1]
                else:
                    if active_name:
                        user_text += event.unicode
                    elif active_password:
                        password_text += event.unicode

def game_over_page(score):
    """Display the game-over page."""
    hit_sound.play() 
    global high_scores
    if score > high_scores[current_user]['score']:
        high_scores[current_user]['score'] = score
        save_high_scores()

    while True:
        screen.blit(background_img, (0, 0))

        # Display Game Over message
        game_over_text = font.render("Game Over", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 4))

        # Display current and highest scores
        score_text = font.render(f"Your Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_scores[current_user]['score']}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 3))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 3 + 50))

        # Create buttons
        play_again_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60)
        exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 60)

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Draw and render buttons
        play_again_hovered = render_button("Restart", play_again_button, mouse_pos)
        exit_hovered = render_button("Exit", exit_button, mouse_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_hovered:
                    main()  # Restart the game
                if exit_hovered:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

def main():
    global SPEED, GRAVITY
    bird_x, bird_y = 100, SCREEN_HEIGHT // 2
    bird_velocity = 0
    score = 0

    pipes = [generate_pipes(SCREEN_WIDTH + i * 200) for i in range(5)]

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = -FLAP_STRENGTH
                    flap_sound.play()

        bird_velocity += GRAVITY
        bird_y += bird_velocity
        bird_rect = pygame.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)

        draw_bird(bird_x, bird_y)

        for i, pipe in enumerate(pipes):
            pipe[0].x -= SPEED
            pipe[1].x -= SPEED
            draw_pipe(pipe[0].x, pipe[0].y + pipe_img.get_height())

            if pipe[0].x + PIPE_WIDTH < 0:
                pipes[i] = generate_pipes(SCREEN_WIDTH)
                score += 1
                point_sound.play()

        if check_collision(bird_rect, pipes):
            game_over_page(score)

        display_score(score)
        display_high_score()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    login_page()
    main()