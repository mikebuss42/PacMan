import pygame
from Score import ScoreBoard
from Image_manager import ImageManager


class ImageRow:
    """Display an image in a row which can be changed"""
    def __init__(self, screen, img, count, label, pos=(0, 0), color=ScoreBoard.SCORE_WHITE):
        self.screen = screen
        if isinstance(img, str):
            self.image = pygame.image.load('images/' + img)
        else:
            self.image = img
        self.image_count = None
        self.image_rects = None
        self.color = color
        self.font = pygame.font.SysFont(None, 36)
        self.text = label
        self.text_image = None
        self.text_image_rect = None
        self.pos = pos
        self.update(count)

    def position(self):
        """Set the image row to its default position"""
        self.text_image_rect.centerx, self.text_image_rect.centery = self.pos
        x_pos = self.text_image_rect.centerx + int(self.text_image_rect.width * 0.75)
        for rect in self.image_rects:
            rect.centerx, rect.centery = x_pos, self.pos[1]
            x_pos += rect.width

    def render_text(self):
        """Render the text as an image to be displayed"""
        self.text_image = self.font.render(self.text, True, self.color)
        self.text_image_rect = self.text_image.get_rect()

    def update(self, n_count):
        """Set a new item count, create rectangles for each, render text and position everything"""
        self.image_count = n_count
        self.image_rects = []
        rect = self.image.get_rect()
        for i in range(n_count):
            self.image_rects.append(rect.copy())
        self.render_text()
        self.position()

    def blit(self):
        """Blit the image row display to the screen"""
        self.screen.blit(self.text_image, self.text_image_rect)
        for rect in self.image_rects:
            self.screen.blit(self.image, rect)


class PacManCounter:
    """Tracks player lives and displays them to the player"""
    def __init__(self, screen, initial_count=3, ct_pos=(0, 0), images_size=(32, 32)):
        self.screen = screen
        self.max_lives = initial_count
        self.lives = initial_count
        sheet_images = ImageManager('pacman-horiz.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                 (32, 0, 32, 32),
                                                                                 (0, 32, 32, 32),
                                                                                 (32, 32, 32, 32),
                                                                                 (0, 64, 32, 32)],
                                    resize=images_size).all_images()
        life_image = sheet_images[-1]  # get last image from the sprite sheet
        self.life_display = ImageRow(screen, life_image, initial_count, 'Lives', ct_pos)

    def decrement(self):
        """Decrement the lives counter and update the display"""
        self.lives -= 1
        self.life_display.update(self.lives)

    def reset_counter(self):
        """Reset the lives counter and update the display"""
        self.lives = self.max_lives
        self.life_display.update(self.lives)

    def blit(self):
        """Blit the counter display to the screen"""
        self.life_display.blit()