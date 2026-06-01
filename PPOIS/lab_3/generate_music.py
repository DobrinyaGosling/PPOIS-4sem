import pygame
import numpy as np
import os

def generate_iowa_music():
    if os.path.exists("iowa.mp3"):
        print("✓ iowa.mp3 уже существует")
        return

    pygame.mixer.init()

    sample_rate = 44100
    duration = 10
    samples = int(sample_rate * duration)

    t = np.linspace(0, duration, samples)

    freq1 = 440
    freq2 = 330
    freq3 = 280

    wave = (
        0.3 * np.sin(2 * np.pi * freq1 * t) +
        0.2 * np.sin(2 * np.pi * freq2 * t) +
        0.2 * np.sin(2 * np.pi * freq3 * t)
    )

    envelope = np.sin(np.pi * t / duration)
    wave = wave * envelope

    wave = (wave * 32767).astype(np.int16)

    wave_stereo = np.zeros((samples, 2), dtype=np.int16)
    wave_stereo[:, 0] = wave
    wave_stereo[:, 1] = wave

    sound = pygame.sndarray.make_sound(wave_stereo)
    pygame.mixer.music.load(sound)

    try:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.Sound("iowa.wav").play()
    except:
        pass


if __name__ == "__main__":
    generate_iowa_music()
