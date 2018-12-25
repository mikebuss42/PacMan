import pygame
from Image_manager import ImageManager
from Score import ScoreBoard


class SimpleAnimation(pygame.sprite.Sprite):
    """A class for presenting a basic animation with little to no special logic"""
    def __init__(self, screen, sprite_sheet, sheet_offsets, pos=(0, 0), resize=None,
                 detail=None, frame_delay=None, flip=False):
        super().__init__()
        self.screen = screen
        if not resize:
            resize = (self.screen.get_height() // 10, self.screen.get_height() // 10)
        self.image_manager = ImageManager(sprite_sheet, sheet=True, pos_offsets=sheet_offsets,
                                          resize=resize, animation_delay=frame_delay)
        if flip:
            self.image_manager.flip()
        self.image, self.rect = self.image_manager.get_image()
        if detail:
            self.detail_piece = ImageManager(detail, sheet=True, pos_offsets=sheet_offsets,
                                             resize=resize).all_images()[0]     # grab first image in detail sheet
            if flip:
                self.image_manager.flip()
            self.image.blit(self.detail_piece, (0, 0))  # combine detail
        else:
            self.detail_piece = None
        self.rect.centerx, self.rect.centery = pos

    def update(self):
        """Update to the next image in the animation"""
        self.image = self.image_manager.next_image()
        if self.detail_piece:
            self.image.blit(self.detail_piece, (0, 0))     # combine detail

    def blit(self):
        """Blit the current image to the screen"""
        self.screen.blit(self.image, self.rect)


class TitleCard(pygame.sprite.Sprite):
    """Displays a single line of text as a large title card"""
    def __init__(self, screen, text,  pos=(0, 0), color=ScoreBoard.SCORE_WHITE, size=42):
        super().__init__()
        self.screen = screen
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(None, size)
        self.image = None
        self.rect = None
        self.pos = pos
        self.prep_image()

    def position(self, n_pos=None):
        """set the position of the title card"""
        if not n_pos:
            self.rect.centerx, self.rect.centery = self.pos
        else:
            self.rect.centerx, self.rect.centery = n_pos

    def prep_image(self):
        """Render the text as an image to be displayed"""
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.position()

    def blit(self):
        """Blit the title card to the screen"""
        self.screen.blit(self.image, self.rect)


class GhostIntro:
    """Displays an introduction title card and sprite for a given ghost"""
    def __init__(self, screen, g_file, name):
        self.screen = screen
        self.title_card = TitleCard(screen, name, pos=(screen.get_width() // 2, screen.get_height() // 2))
        self.ghost = SimpleAnimation(screen, g_file, sheet_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                     pos=(self.title_card.rect.right + self.title_card.rect.width // 2,
                                          screen.get_height() // 2),
                                     detail='ghost-eyes.png',
                                     frame_delay=150)

    def update(self):
        """Update ghost animations in title card"""
        self.ghost.update()

    def blit(self):
        """Blit the components of the ghost intro to the screen"""
        self.title_card.blit()
        self.ghost.blit()


class ChaseScene:
    """Displays a chase scene moving from left to right across the screen, or flipped from right to left"""
    def __init__(self, screen, chasers, chased, reverse=False, speed=5, chaser_detail=None, chased_detail=None):
        self.screen = screen
        self.chasers = []
        self.chased = []
        self.x_start = 0 if not reverse else screen.get_width()
        self.speed = speed if not reverse else -speed
        self.chaser_positions = []
        self.chased_positions = []
        self.y_pos = (screen.get_height() // 2)
        x_offset = self.x_start
        for chaser in chasers:
            self.chaser_positions.append(x_offset)
            animation = SimpleAnimation(screen, chaser, sheet_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        pos=(x_offset, self.y_pos),
                                        detail=chaser_detail,
                                        frame_delay=150,
                                        flip=reverse)
            x_offset += int(animation.rect.width * 1.5)
            self.chasers.append(animation)
        x_offset += (self.speed * 2)
        for target in chased:
            self.chased_positions.append(x_offset)
            animation = SimpleAnimation(screen, target, sheet_offsets=[(0, 0, 32, 32),
                                                                       (32, 0, 32, 32),
                                                                       (0, 32, 32, 32),
                                                                       (32, 32, 32, 32),
                                                                       (0, 64, 32, 32)],
                                        pos=(x_offset, self.y_pos),
                                        detail=chased_detail,
                                        frame_delay=150,
                                        flip=reverse)
            x_offset += int(animation.rect.width * 1.5)
            self.chased.append(animation)

    def reset_positions(self):
        """Reset the chasers and the chased to their start positions"""
        for chaser, c_offset in zip(self.chasers, self.chaser_positions):
            chaser.rect.centerx, chaser.rect.centery = c_offset, self.y_pos
        for target, t_offset in zip(self.chased, self.chased_positions):
            target.rect.centerx, target.rect.centery = t_offset, self.y_pos

    def update(self):
        """Update the chase scene so that is moves across the screen"""
        for chaser in self.chasers:
            chaser.rect.centerx += self.speed
            chaser.update()
        for target in self.chased:
            target.rect.centerx += self.speed
            target.update()

    def blit(self):
        """Blit all the components of the scene to the screen"""
        for chaser in self.chasers:
            chaser.blit()
        for target in self.chased:
            target.blit()


class Intro:
    """Handles the display and continuation of an introductory cut-scene"""
    def __init__(self, screen):
        self.screen = screen
        self.ghost_intros = [
            ChaseScene(screen, chasers=['ghost-red.png', 'ghost-pink.png',
                                        'ghost-lblue.png', 'ghost-orange.png'],
                       chased=['pacman-horiz.png'], chaser_detail='ghost-eyes.png'),
            ChaseScene(screen, chasers=['ghost-ppellet.png', 'ghost-ppellet.png',
                                        'ghost-ppellet.png', 'ghost-ppellet.png'],
                       chased=['pacman-horiz.png'], reverse=True),
            GhostIntro(screen, 'ghost-red.png', 'Blinky'),
            GhostIntro(screen, 'ghost-pink.png', 'Pinky'),
            GhostIntro(screen, 'ghost-lblue.png', 'Inky'),
            GhostIntro(screen, 'ghost-orange.png', 'Clyde')
        ]
        self.run = set()
        self.intro_index = 0
        self.last_intro_start = None
        self.intro_time = 5000  # time to display in milliseconds

    def update(self):
        """Progress the intro sequence"""
        if not self.last_intro_start:
            self.last_intro_start = pygame.time.get_ticks()
        elif abs(self.last_intro_start - pygame.time.get_ticks()) > self.intro_time:
            self.run.add(self.intro_index)
            self.intro_index = (self.intro_index + 1) % len(self.ghost_intros)
            self.last_intro_start = pygame.time.get_ticks()
        if self.intro_index in (0, 1) and self.intro_index in self.run:
            self.ghost_intros[self.intro_index].reset_positions()
            self.run.remove(self.intro_index)
        self.ghost_intros[self.intro_index].update()

    def blit(self):
        """Blit the intro sequence to the screen"""
        self.ghost_intros[self.intro_index].blit()