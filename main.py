import random  # Standard library imports first
import pygame  # Third-party imports second
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, ENEMY_SPEED, FPS, MAX_LVL, LASER_VEL
from imageloader import ICON, BACKGROUND
from entities import Player, Enemy, Special, collide

pygame.init()  # Initialize pygame

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
pygame.display.set_icon(ICON)

# Initialize player
player = Player(x=370, y=500)

def main(high_score: int) -> None:
    """
    Main game loop.
    """
    running: bool = True
    clock = pygame.time.Clock()
    lives: int = 5
    level: int = 0
    score: int = 0
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 60)
    enemies: list[Enemy] = []
    specials: list[Special] = []
    wave_length: int = 10
    lost: bool = False
    lost_counter: int = 0
    background_movement: float = 0.0

    def redraw_window() -> None:
        """
        Draw elements on the screen
        """
        nonlocal background_movement
        screen.fill((0, 0, 0))
        screen.blit(BACKGROUND, (0, background_movement))
        screen.blit(BACKGROUND, (0, -SCREEN_HEIGHT + background_movement))
        background_movement += 0.5
        if background_movement == SCREEN_HEIGHT:
            background_movement = 0

        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        screen.blit(lives_label, (10, 10))
        level_label = main_font.render(
            f"Level: {level} (Max)" if level == MAX_LVL else f"Level: {level}",
            True,
            (255, 255, 255),
        )
        screen.blit(level_label, (SCREEN_WIDTH - 10 - level_label.get_width(), 10))
        score_label = main_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_label, (10, 20 + lives_label.get_height()))

        for enemy in enemies:
            enemy.draw(screen)

        for special in specials:
            special.draw(screen)

        player.draw(screen)

        if lost:
            lost_label = lost_font.render("You Lost!!", True, (255, 255, 255))
            screen.blit(lost_label, (SCREEN_WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # pylint: disable=no-member
                if score > high_score:
                    with open("highscore.txt", "w", encoding="utf-8") as f:
                        f.write(str(score))
                running = False

        if lives <= 0 or player.health <= 0:
            lost = True

        if lost:
            if lost_counter > FPS * 2:
                if score > high_score:
                    with open("highscore.txt", "w", encoding="utf-8") as f:
                        f.write(str(score))
                running = False
            else:
                lost_counter += 1
                continue

        if not enemies:
            if level < MAX_LVL:
                level += 1
                wave_length += 2
            for _ in range(wave_length):
                enemy = Enemy(
                    random.randrange(50, SCREEN_WIDTH - 100),
                    random.randrange(-3000, -100),
                    random.choice(["one", "two", "three", "four"]),
                )
                enemies.append(enemy)

        if not specials and random.randrange(0, 15 * FPS) == 1:
            specials.append(Special(x=-100, y=SCREEN_HEIGHT / 3))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - PLAYER_SPEED > 0:  # pylint: disable=no-member
            player.x -= PLAYER_SPEED
        if keys[pygame.K_d] and player.x + PLAYER_SPEED + player.get_width() < SCREEN_WIDTH:  # pylint: disable=no-member
            player.x += PLAYER_SPEED
        if keys[pygame.K_w] and player.y - PLAYER_SPEED > 0:  # pylint: disable=no-member
            player.y -= PLAYER_SPEED
        if keys[pygame.K_s] and player.y + PLAYER_SPEED + player.get_height() < SCREEN_HEIGHT:  # pylint: disable=no-member
            player.y += PLAYER_SPEED
        if keys[pygame.K_SPACE]:  # pylint: disable=no-member
            player.shoot()

        score = player.move_lasers(-LASER_VEL, enemies, specials, score)

        for special in specials[:]:
            special.move()
            if special.x < -100:
                specials.remove(special)
            elif collide(special, player):
                specials.remove(special)
                player.health -= 20

        for enemy in enemies[:]:
            enemy.y += ENEMY_SPEED + 0.05 * level
            enemy.move_lasers(LASER_VEL, player)

            if random.randrange(0, 4 * FPS) == 1:
                enemy.shoot()

            if collide(player, enemy):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > SCREEN_HEIGHT:
                lives -= 1
                enemies.remove(enemy)


def main_menu() -> None:
    """
    Main menu where it shows the high score
    """
    try:
        with open("highscore.txt", "r", encoding="utf-8") as f:
            high_score: int = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        high_score = 0
        with open("highscore.txt", "w", encoding="utf-8") as f:
            f.write("0")

    score_font = pygame.font.SysFont("comicsans", 30)
    title_font = pygame.font.SysFont("comicsans", 50)

    run: bool = True
    while run:
        screen.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press mouse button to start...", True, (255, 255, 255))
        high_score_label = score_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(high_score_label, (SCREEN_WIDTH / 2 - high_score_label.get_width() / 2, 50))
        screen.blit(title_label, (SCREEN_WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # pylint: disable=no-member
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # pylint: disable=no-member
                main(high_score)
                with open("highscore.txt", "r", encoding="utf-8") as f:
                    high_score = int(f.read().strip())

    pygame.quit()


main_menu()
