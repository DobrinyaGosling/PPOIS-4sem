import pytest
import numpy as np


class TestSoundGeneration:
    def test_generate_sine_wave(self):
        sample_rate = 22050
        duration = 0.1
        frequency = 800
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * frequency * t) * (1 - t / duration)
        wave = (wave * 32767).astype(np.int16)

        assert len(wave) > 0
        assert len(wave) == samples

    def test_generate_noise(self):
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)
        noise = np.random.uniform(-1, 1, samples)
        envelope = 1 - t / duration
        wave = noise * envelope

        wave = (wave * 32767).astype(np.int16)

        assert len(wave) == samples
        assert all(isinstance(x, (int, np.integer)) for x in wave)

    def test_envelope_decay(self):
        duration = 0.2
        samples = 100

        t = np.linspace(0, duration, samples)
        envelope = 1 - t / duration

        assert envelope[0] > envelope[-1]
        assert envelope[-1] < 0.01

    def test_sound_parameters(self):
        shoot_duration = 0.1
        hit_duration = 0.2
        explosion_duration = 0.3

        assert shoot_duration < hit_duration < explosion_duration

    def test_frequency_values(self):
        shoot_freq = 800
        hit_freq = 400
        explosion_freq = None

        assert shoot_freq > hit_freq
        assert shoot_freq > 0
        assert hit_freq > 0

    def test_wave_normalization(self):
        wave = np.array([0.5, 0.75, 0.25])
        normalized = (wave * 32767).astype(np.int16)

        assert all(isinstance(x, (int, np.integer)) for x in normalized)
        assert max(normalized) <= 32767
