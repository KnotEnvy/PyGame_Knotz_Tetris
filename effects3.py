import taichi as ti
from settings import *
import numba
import numpy as np



ti.init(arch=ti.cuda)  # Use GPU for computation

# Define the data structures for Taichi
field = ti.field(dtype=ti.f32)
smoke_texture = ti.field(dtype=ti.f32)

# Use the shape of the Pygame screen for the field
ti.root.dense(ti.ij, (FIELD_H, FIELD_W)).place(field)

# The smoke texture will be a 100x100 field
ti.root.dense(ti.ij, (100, 500)).place(smoke_texture)

@ti.kernel
def generate_smoke_texture():
    size = 100
    for y in range(size):
        for x in range(size):
            dx, dy = x - size // 2, y - size // 2
            distance = ti.sqrt(dx * dx + dy * dy)
            value = ti.exp(-distance * distance / (2 * size * size / 16))
            smoke_texture[y, x] = value

@ti.kernel
def update_field(field: ti.template(), smoke_texture: ti.template(), x: ti.i32, y: ti.i32, intensity: ti.f32):
    texture_size = smoke_texture.shape[0]
    for i in range(texture_size):
        for j in range(texture_size):
            field[y+i, x+j] += smoke_texture[i, j] * intensity


@ti.kernel
def decay_field():
    for y in range(field.shape[0]):
        for x in range(field.shape[1]):
            field[y, x] *= 0.99

class MusicVisuals:
    def __init__(self, app):
        self.app = app
        self.width, self.height = app.screen.get_size()
        generate_smoke_texture()

    def update(self, music_data):
        pitch, is_beat = music_data

        # If there's a beat, add smoke particles
        if is_beat:
            particles = np.random.randint(10, 20)  # You can adjust the number of particles
            for _ in range(particles):
                x = np.random.randint(0, self.width - smoke_texture.shape[1])
                y = np.random.randint(0, self.height - smoke_texture.shape[0])
                intensity = pitch / 1000  # You can adjust the intensity based on pitch
                update_field(field, smoke_texture, x, y, intensity)

        # Apply decay to the field
        decay_field()


    def draw(self):
        # Convert the field values to the 0-255 range
        smoke_array = np.clip(field.to_numpy() * 255, 0, 255).astype(np.uint8)

        # Create a 3D array with the smoke values in the red and green channels
        smoke_array_rgb = np.zeros((smoke_array.shape[0], smoke_array.shape[1], 3), dtype=np.uint8)
        smoke_array_rgb[..., 0] = smoke_array
        smoke_array_rgb[..., 1] = smoke_array

        # Create the Pygame surface
        smoke_surface = pg.surfarray.make_surface(smoke_array_rgb)

        # Draw the smoke effect on the app.screen
        self.app.screen.blit(smoke_surface, (0, 0))



