import pygame
from Pacman import PacMan
from Intro import TitleCard


class Button:
    """Represents a click-able button style text, with altering text color"""
    def __init__(self, screen, msg, size=26, pos=(0, 0), text_color=(255, 255, 255), alt_color=(0, 255, 0)):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        # Dimensions and properties of the button
        self.text_color = text_color
        self.alt_color = alt_color
        self.font = pygame.font.SysFont(None, size)
        self.pos = pos

        # Prep button message
        self.msg = msg
        self.msg_image, self.msg_image_rect = None, None
        self.prep_msg(self.text_color)

    def check_button(self, mouse_x, mouse_y):
        """Check if the given button has been pressed"""
        if self.msg_image_rect.collidepoint(mouse_x, mouse_y):
            return True
        else:
            return False

    def alter_text_color(self, mouse_x, mouse_y):
        """Change text color if the mouse coordinates collide with the button"""
        if self.check_button(mouse_x, mouse_y):
            self.prep_msg(self.alt_color)
        else:
            self.prep_msg(self.text_color)

    def prep_msg(self, color):
        """Turn msg into a rendered image and center it on the button"""
        self.msg_image = self.font.render(self.msg, True, color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.centerx, self.msg_image_rect.centery = self.pos

    def blit(self):
        """blit message to the screen"""
        self.screen.blit(self.msg_image, self.msg_image_rect)


class HighScoreScreen:
    """Displays high score data to the screen"""
    def __init__(self, screen, score_controller, size=26, background=(0, 0, 0)):
        self.screen = screen
        self.score_controller = score_controller
        self.back_button = Button(screen, 'Back', pos=(int(screen.get_width() * 0.25), int(screen.get_height() * 0.9)),
                                  alt_color=PacMan.PAC_YELLOW)
        self.font = pygame.font.SysFont(None, size)
        self.images = []
        self.active = False
        self.background = background
        self.prep_images()
        self.position()

    def position(self):
        """Position display elements on the screen"""
        y_offset = int(self.screen.get_height() * 0.1)
        for image in self.images:
            image[1].centerx = int(self.screen.get_width() * 0.5)
            image[1].centery = y_offset
            y_offset += int(image[1].height * 2)

    def check_done(self):
        """Check if the back button has been pressed"""
        self.back_button.alter_text_color(*pygame.mouse.get_pos())
        self.active = not self.back_button.check_button(*pygame.mouse.get_pos())

    def prep_images(self):
        """Render all scores as displayable images"""
        self.images.clear()
        for num, score in enumerate(self.score_controller.high_scores):
            image = self.font.render('#' + str(num + 1) + ' :  ' + str(score), True, (255, 255, 255))
            rect = image.get_rect()
            self.images.append([image, rect])

    def blit(self):
        """Blit all score displays to the screen"""
        for image in self.images:
            self.screen.blit(*image)
        self.back_button.blit()


class Menu:
    """Handles the menu screen, and choices made by the user"""
    def __init__(self, screen):
        self.screen = screen
        self.title = TitleCard(screen, 'Pacman P0rtal', pos=(int(screen.get_width() * 0.5),
                                                             int(screen.get_height() * 0.15)))

        self.play_button = Button(screen, 'Play Game', pos=(int(screen.get_width() * 0.5),
                                                            int(screen.get_height() * 0.8)),
                                  alt_color=PacMan.PAC_YELLOW)
        self.high_scores_button = Button(screen, 'High Scores', pos=(int(screen.get_width() * 0.5),
                                                                     int(screen.get_height() * 0.9)),
                                         alt_color=PacMan.PAC_YELLOW)
        self.hs_screen = False
        self.ready_to_play = False

    def check_buttons(self):
        """Set flags based on whether the play button or the high score screen button has been pressed"""
        self.ready_to_play = self.play_button.check_button(*pygame.mouse.get_pos())
        self.hs_screen = self.high_scores_button.check_button(*pygame.mouse.get_pos())

    def update(self):
        """Update any changing features of the menu"""
        self.play_button.alter_text_color(*pygame.mouse.get_pos())
        self.high_scores_button.alter_text_color(*pygame.mouse.get_pos())

    def blit(self):
        """Blit all display elements to the screen"""
        self.title.blit()
        self.play_button.blit()
        self.high_scores_button.blit()