import pygame as pg
import numpy as np
from numba import njit, prange

@njit(parallel=True)
def update_field(field, smoke_texture):
    texture_size = smoke_texture.shape[0]
    for y in prange(texture_size, field.shape[0] - texture_size):
        for x in prange(texture_size, field.shape[1] - texture_size):
            field[y:y + texture_size, x:x + texture_size] += smoke_texture


class MusicVisuals:
    def __init__(self, app):
        self.app = app
        self.width, self.height = app.screen.get_size()
        self.field = np.zeros((self.height, self.width), dtype=np.float32)
        self.smoke_texture = self.generate_smoke_texture()

    @staticmethod
    @njit(fastmath=True)
    def generate_smoke_texture():
        size = 100
        texture = np.zeros((size, size), dtype=np.float32)
        for y in range(size):
            for x in range(size):
                dx, dy = x - size // 2, y - size // 2
                distance = np.sqrt(dx * dx + dy * dy)
                value = np.exp(-distance * distance / (2 * size * size / 16))
                texture[y, x] = value
        return texture

    # @njit(parallel=True)
    # def update_field(self, field, smoke_texture):
    #     texture_size = smoke_texture.shape[0]
    #     for y in prange(texture_size, field.shape[0] - texture_size):
    #         for x in prange(texture_size, field.shape[1] - texture_size):
    #             field[y:y + texture_size, x:x + texture_size] += smoke_texture

    def update(self, music_data):
        pitch, is_beat = music_data

        # If there's a beat, add smoke particles
        if is_beat:
            particles = np.random.randint(10, 20)  # You can adjust the number of particles
            for _ in range(particles):
                x = np.random.randint(0, self.width - self.smoke_texture.shape[1])
                y = np.random.randint(0, self.height - self.smoke_texture.shape[0])
                intensity = pitch / 1000  # You can adjust the intensity based on pitch
                self.field[y:y+self.smoke_texture.shape[0], x:x+self.smoke_texture.shape[1]] += self.smoke_texture * intensity

        # Update the field using Numba
        update_field(self.field, self.smoke_texture)

        # Apply decay to the field
        self.field *= 0.99

    def draw(self):
        # Render the smoke effect on the app.screen
        smoke_surface = pg.surfarray.make_surface(self.field)
        self.app.screen.blit(smoke_surface, (0, 0))



