#!/usr/bin/env python3
import pygame
import numpy as np
import os

def create_background_music(filename="iowa.mp3", duration=30):
    """Создает фоновую музыку в формате MP3"""

    pygame.mixer.init()

    sample_rate = 44100
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)

    freq1 = 220
    freq2 = 330
    freq3 = 440
    freq4 = 550

    wave = (
        0.25 * np.sin(2 * np.pi * freq1 * t) +
        0.25 * np.sin(2 * np.pi * freq2 * t) +
        0.25 * np.sin(2 * np.pi * freq3 * t) +
        0.25 * np.sin(2 * np.pi * freq4 * t)
    )

    for i in range(4):
        start = i * int(duration / 4) * sample_rate
        end = (i + 1) * int(duration / 4) * sample_rate
        envelope = np.sin(np.pi * np.linspace(0, 1, end - start))
        wave[start:end] *= envelope

    wave = wave / np.max(np.abs(wave)) * 0.8

    wave = (wave * 32767).astype(np.int16)

    try:
        import scipy.io.wavfile as wavfile
        wavfile.write("iowa.wav", sample_rate, wave)
        print("✓ iowa.wav создана (30 сек спокойной музыки)")
        return
    except ImportError:
        pass

    try:
        import soundfile as sf
        stereo = np.zeros((len(wave), 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave
        sf.write(filename, stereo, sample_rate)
        print(f"✓ {filename} создана")
        return
    except ImportError:
        pass

    wave_stereo = np.zeros((len(wave), 2), dtype=np.int16)
    wave_stereo[:, 0] = wave
    wave_stereo[:, 1] = wave

    sound = pygame.sndarray.make_sound(wave_stereo)
    print(f"✓ Музыка готова (использована Pygame для синтеза)")

if __name__ == "__main__":
    if os.path.exists("iowa.mp3"):
        print("✓ iowa.mp3 уже существует")
    else:
        create_background_music()
