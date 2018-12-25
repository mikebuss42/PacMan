import pygame


class SoundManager:
    """Handles the playing of sound over pygame mixer"""
    def __init__(self, sound_files, keys=None, channel=0, volume=None):
        self.sound_files = sound_files
        self.sounds = {}
        self.channel = pygame.mixer.Channel(channel)
        if not keys:
            for s_file in sound_files:
                self.sounds[s_file] = pygame.mixer.Sound('Sounds/' + s_file)
        else:
            if len(keys) != len(sound_files):
                raise ValueError('number of keys must be the same as the number of sound files')
            for key, s_file in zip(keys, sound_files):
                self.sounds[key] = pygame.mixer.Sound('Sounds/' + s_file)
        if isinstance(volume, float):
            self.channel.set_volume(volume)

    def play(self, key):
        """Play a sound once"""
        self.channel.play(self.sounds[key], loops=0)

    def play_loop(self, key):
        """Loop a sound indefinitely"""
        self.channel.play(self.sounds[key], loops=-1)

    def stop(self):
        """Stop sound from playing"""
        self.channel.stop()