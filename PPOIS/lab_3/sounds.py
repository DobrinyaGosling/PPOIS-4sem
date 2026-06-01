import pygame
import numpy as np


class SoundManager:
    def __init__(self, music_file="iowa.mp3"):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sounds = {}
        self.music_playing = False
        self.music_file = music_file
        self._create_sounds()
        self._load_music()

    def _create_sounds(self):
        self.sounds["shoot"] = self._generate_shoot_sound()
        self.sounds["hit"] = self._generate_hit_sound()
        self.sounds["explosion"] = self._generate_explosion_sound()

    def _generate_shoot_sound(self):
        sample_rate = 22050
        duration = 0.1
        frequency = 800
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * frequency * t) * (1 - t / duration)
        wave = (wave * 32767).astype(np.int16)

        wave_stereo = np.zeros((samples, 2), dtype=np.int16)
        wave_stereo[:, 0] = wave
        wave_stereo[:, 1] = wave

        sound = pygame.sndarray.make_sound(wave_stereo)
        return sound

    def _generate_hit_sound(self):
        sample_rate = 22050
        duration = 0.2
        frequency = 400
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * frequency * t) * (1 - t / duration)
        wave = (wave * 32767).astype(np.int16)

        wave_stereo = np.zeros((samples, 2), dtype=np.int16)
        wave_stereo[:, 0] = wave
        wave_stereo[:, 1] = wave

        sound = pygame.sndarray.make_sound(wave_stereo)
        return sound

    def _generate_explosion_sound(self):
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)
        noise = np.random.uniform(-1, 1, samples)
        envelope = 1 - t / duration
        wave = noise * envelope

        wave = (wave * 32767).astype(np.int16)

        wave_stereo = np.zeros((samples, 2), dtype=np.int16)
        wave_stereo[:, 0] = wave
        wave_stereo[:, 1] = wave

        sound = pygame.sndarray.make_sound(wave_stereo)
        return sound

    def play_shoot(self):
        if "shoot" in self.sounds:
            pygame.mixer.Channel(0).play(self.sounds["shoot"])

    def play_hit(self):
        if "hit" in self.sounds:
            pygame.mixer.Channel(1).play(self.sounds["hit"])

    def play_explosion(self):
        if "explosion" in self.sounds:
            pygame.mixer.Channel(2).play(self.sounds["explosion"])

    def _load_music(self):
        try:
            pygame.mixer.music.load(self.music_file)
        except (pygame.error, FileNotFoundError):
            pass

    def play_music(self):
        if not self.music_playing:
            try:
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except pygame.error:
                pass

    def stop_music(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
