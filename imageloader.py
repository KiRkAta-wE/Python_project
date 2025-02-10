"""
Модул за зареждане на изображенията на играта
"""

import os  # Standard imports should come first
import pygame  # Third-party imports should come after standard imports
from settings import SCREEN_WIDTH, SCREEN_HEIGHT  # Local imports come last

# Load images
ICON = pygame.image.load(os.path.join("assets", "main.png"))
ENEMY = pygame.image.load(os.path.join("assets", "izrod_green.png"))
ENEMY2 = pygame.image.load(os.path.join("assets", "izrod_blue.png"))
ENEMY3 = pygame.image.load(os.path.join("assets", "izrod_red.png"))
ENEMY4 = pygame.image.load(os.path.join("assets", "izrod_orange.png"))
SPECIAL = pygame.image.load(os.path.join("assets", "ufo.png"))
SPACESHIP = pygame.image.load(os.path.join("assets", "spaceship.png"))
SHIP_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))

# Преоразмеряваме background-a така че да fit-ва във екрана
BACKGROUND = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "background.png")),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)
