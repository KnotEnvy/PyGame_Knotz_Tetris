import pygame as pg
import numpy as np
from numba import njit
from settings import *

class MusicVisuals:
    def __init__(self, app):
        self.app = app
        self.width, self.height = app.screen.get_size()
        self.gradient_surface = self.generate_gradient_surface()

    @staticmethod
    def generate_gradient_surface():
        size = max(WIN_RES)
        size = int(size)
        gradient_surface = pg.Surface(WIN_RES, pg.SRCALPHA)
        for i in range(0, size, 2):
            pg.draw.circle(gradient_surface, (0, 0, 0, 255 - (i * 255 // size)), (size // 2, size // 2), size // 2 - i, 1)
        return gradient_surface

    def update(self, music_data):
        self.pitch, self.is_beat = music_data

    def draw(self):
        radius = int(self.pitch / 2000 * max(WIN_RES) // 2)
        if self.is_beat:
            color = (np.random.randint(50, 256), np.random.randint(50, 256), np.random.randint(50, 256))
            self.app.screen.fill(color)
        gradient_surface = pg.transform.scale(self.gradient_surface, (radius * 2, radius * 2))
        gradient_rect = gradient_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.app.screen.blit(gradient_surface, gradient_rect)
