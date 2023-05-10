from settings import *
from tetris import Tetris, Text
import sys
import pathlib
import pygame.mixer
import aubio
import numpy as np
from effects import MusicVisuals

# Initialize the music mixer
pygame.mixer.init()

# Load and play the music
music_file = 'sounds/8. Electric Moments.wav'  # Replace with the path to your music file
pygame.mixer.music.load(music_file)
pygame.mixer.music.play()

# Set up aubio to analyze the music
win_s = 1024
hop_s = win_s // 2
aubio_source = aubio.source(music_file, samplerate=0, hop_size=hop_s)
samplerate = aubio_source.samplerate

# Set up the pitch and beat detection
pitch_o = aubio.pitch('default', win_s, hop_s, samplerate)
pitch_o.set_unit('Hz')
pitch_o.set_silence(-40)
tempo_o = aubio.tempo('default', win_s, hop_s, samplerate)


class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('KnotzTertis')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.music_visuals = MusicVisuals(self)
        self.tetris = Tetris(self)
        self.text = Text(self)

    def load_images(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        self.tetris.update()
        self.clock.tick(FPS)
        music_data = self.get_music_data()  # Implement this method to get the music data
        self.music_visuals.update(music_data)

    def get_music_data(self):
        samples, read = aubio_source()
        pitch = pitch_o(samples)[0]
        is_beat = tempo_o(samples)
        return pitch, is_beat

    def draw(self):
        # Analyze the current music frame
        samples, read = aubio_source()
        pitch = pitch_o(samples)[0]
        is_beat = tempo_o(samples)
        # React to pitch and beat
        if is_beat:
            # Do something when a beat is detected (e.g., change the background color)
            pass

        # Create special effects based on the pitch (e.g., animate shapes)
        # ...

        # Draw rest of  game
        self.screen.fill(color = BG_COLOR)
        
        self.screen.fill(color=FIELD_COLOR, rect= (0,0, *FIELD_RES))
        self.music_visuals.draw()
        self.tetris.draw()
        self.text.draw()
        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    app = App()
    app.run()