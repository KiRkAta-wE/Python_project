"""Entities module for Space Invaders game."""

import pygame
from imageloader import (
    SPACESHIP, ENEMY, ENEMY2, ENEMY3, ENEMY4, SPECIAL,
    SHIP_LASER, RED_LASER, GREEN_LASER
)
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, FPS
from typing import List, Optional


def collide(obj1: pygame.sprite.Sprite, obj2: pygame.sprite.Sprite) -> bool:
    """Check if two objects collide based on their masks."""
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


class Laser:
    """Represents a laser projectile in the game."""
    
    def __init__(self, x: int, y: int, img: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the laser on the screen."""
        screen.blit(self.img, (self.x, self.y))

    def move(self, vel: int) -> None:
        """Move the laser by a given velocity."""
        self.y += vel

    def off_screen(self) -> bool:
        """Check if the laser is off-screen."""
        return self.y >= SCREEN_HEIGHT or self.y <= 0

    def collision(self, obj: pygame.sprite.Sprite) -> bool:
        """Check if the laser collides with an object."""
        return collide(self, obj)


class Ship(pygame.sprite.Sprite):
    """Base class for all ships (Player and Enemy)."""
    
    COOLDOWN = FPS / 2

    def __init__(self, x: int, y: int, health: int = 100) -> None:
        super().__init__()
        self.image: Optional[pygame.Surface] = None
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.lasers: List[Laser] = []
        self.laser_img: Optional[pygame.Surface] = None
        self.cool_down_counter = 0
        self.powerup_cooldown = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the ship and its lasers."""
        screen.blit(self.image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(screen)

    def cooldown(self) -> None:
        """Handle cooldown for shooting."""
        if self.powerup_cooldown == 0:
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0
            elif self.cool_down_counter > 0:
                self.cool_down_counter += 1
        else:
            self.powerup_cooldown -= 1
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0
            elif self.cool_down_counter > 0:
                self.cool_down_counter += 2

    def shoot(self) -> None:
        """Shoot a laser if cooldown allows."""
        if self.cool_down_counter == 0:
            laser = Laser(
                self.x + self.image.get_width() // 2 - self.laser_img.get_width() // 2,
                self.y,
                self.laser_img
            )
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_height(self) -> int:
        """Return the ship's height."""
        return self.image.get_height()

    def get_width(self) -> int:
        """Return the ship's width."""
        return self.image.get_width()


class Player(Ship):
    """Player-controlled spaceship."""
    
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = SPACESHIP
        self.laser_img = SHIP_LASER
        self.mask = pygame.mask.from_surface(self.image)

    def move_lasers(self, vel: int, objs: list[pygame.sprite.Sprite], specials: List[pygame.sprite.Sprite], score: int) -> int:
        """Move the player's lasers and check for collisions."""
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        score += 10
                for special in specials[:]:
                    if laser.collision(special):
                        specials.remove(special)
                        self.health = min(self.health + 20, self.max_health)
                        self.powerup_cooldown = 10 * FPS
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        score += 100
        return score

    def healthbar(self, screen: pygame.Surface) -> None:
        """Draw the player's health bar."""
        pygame.draw.rect(screen, (255, 0, 0), (10, SCREEN_HEIGHT - 20, SCREEN_WIDTH / 8, 10))
        pygame.draw.rect(screen, (0, 255, 0), (
            10, SCREEN_HEIGHT - 20, (self.health / self.max_health) * SCREEN_WIDTH / 8, 10
        ))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player and health bar."""
        super().draw(screen)
        self.healthbar(screen)


class Enemy(Ship):
    """Enemy spaceship."""
    
    SKINS = {
        "one": (ENEMY, GREEN_LASER),
        "two": (ENEMY2, SHIP_LASER),
        "three": (ENEMY3, RED_LASER),
        "four": (ENEMY4, RED_LASER)
    }

    def __init__(self, x: int, y: int, skin: str) -> None:
        super().__init__(x, y)
        self.image, self.laser_img = self.SKINS[skin]
        self.mask = pygame.mask.from_surface(self.image)

    def move_lasers(self, vel: int, obj: Player) -> None:
        """Move enemy lasers and check for collisions."""
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                if laser in self.lasers:
                    self.lasers.remove(laser)


class Special(Ship):
    """Special ship that moves horizontally across the screen."""
    
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = SPECIAL
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 3

    def move(self) -> None:
        """Move the special ship back and forth."""
        self.x += self.speed
        if self.x >= SCREEN_WIDTH + SCREEN_WIDTH / 2:
            self.speed *= -1
