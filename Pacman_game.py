import pygame
from Event_loop import EventLoop
from Ghost import Ghost
from Maze import Maze
from Pacman import PacMan
from Lives_status import PacManCounter
from Score import ScoreController, LevelTransition
from Sound_manager import SoundManager
from Menu import Menu, HighScoreScreen
from Intro import Intro


class PacManPortalGame:
    """Contains the main logic and methods
    for the running and updating of the PacMan portal game"""

    BLACK_BG = (0, 0, 0)
    START_EVENT = pygame.USEREVENT + 1
    REBUILD_EVENT = pygame.USEREVENT + 2
    LEVEL_TRANSITION_EVENT = pygame.USEREVENT + 3

    def __init__(self):
        pygame.init()
        pygame.mixer.music.load('sounds/bg-music.wav')
        self.screen = pygame.display.set_mode(
            (800, 600)
        )
        pygame.display.set_caption('PacMan Portal')
        self.clock = pygame.time.Clock()
        self.score_keeper = ScoreController(screen=self.screen,
                                            sb_pos=((self.screen.get_width() // 5),
                                                    (self.screen.get_height() * 0.965)),
                                            items_image='cherry.png',
                                            itc_pos=(int(self.screen.get_width() * 0.6),
                                                     self.screen.get_height() * 0.965))
        self.maze = Maze(screen=self.screen, maze_map_file='maze_map.txt')
        self.life_counter = PacManCounter(screen=self.screen, ct_pos=((self.screen.get_width() // 3),
                                                                      (self.screen.get_height() * 0.965)),
                                          images_size=(self.maze.block_size, self.maze.block_size))
        self.level_transition = LevelTransition(screen=self.screen, score_controller=self.score_keeper)
        self.game_over = True
        self.pause = False
        self.player = PacMan(screen=self.screen, maze=self.maze)
        self.ghosts = pygame.sprite.Group()
        self.ghost_sound_manager = SoundManager(sound_files=['ghost-blue.wav', 'pacman_eatghost.wav', 'ghost-std.wav'],
                                                keys=['blue', 'eaten', 'std'],
                                                channel=Ghost.GHOST_AUDIO_CHANNEL)
        self.ghost_active_interval = 2500
        self.ghosts_to_activate = None
        self.first_ghost = None
        self.other_ghosts = []
        self.spawn_ghosts()
        self.actions = {PacManPortalGame.START_EVENT: self.init_ghosts,
                        PacManPortalGame.REBUILD_EVENT: self.rebuild_maze,
                        PacManPortalGame.LEVEL_TRANSITION_EVENT: self.next_level}

    def init_ghosts(self):
        """kick start the ghost AI over a period of time"""
        if not self.first_ghost.state['enabled']:
            self.first_ghost.enable()
            self.ghosts_to_activate = self.other_ghosts.copy()
            pygame.time.set_timer(PacManPortalGame.START_EVENT, 0)  # disable timer repeat
            pygame.time.set_timer(PacManPortalGame.START_EVENT, self.ghost_active_interval)
        else:
            try:
                g = self.ghosts_to_activate.pop()
                g.enable()
            except IndexError:
                pygame.time.set_timer(PacManPortalGame.START_EVENT, 0)  # disable timer repeat

    def spawn_ghosts(self):
        """Create all ghosts at their starting positions"""
        files = ['ghost-pink.png', 'ghost-lblue.png', 'ghost-orange.png', 'ghost-red.png']
        idx = 0
        while len(self.maze.ghost_spawn) > 0:
            spawn_info = self.maze.ghost_spawn.pop()
            g = Ghost(screen=self.screen, maze=self.maze, target=self.player,
                      spawn_info=spawn_info, ghost_file=files[idx], sound_manager=self.ghost_sound_manager)
            if files[idx] == 'ghost-red.png':
                self.first_ghost = g    # red ghost should be first
            else:
                self.other_ghosts.append(g)
            self.ghosts.add(g)
            idx = (idx + 1) % len(files)

    def next_level(self):
        """Increment the game level and then continue the game"""
        pygame.time.set_timer(PacManPortalGame.LEVEL_TRANSITION_EVENT, 0)  # reset timer
        self.player.clear_portals()
        self.score_keeper.increment_level()
        self.rebuild_maze()

    def rebuild_maze(self):
        """Resets the maze to its initial state if the game is still active"""
        if self.life_counter.lives > 0:
            for g in self.ghosts:
                if g.state['enabled']:
                    g.disable()
            self.maze.build_maze()
            self.player.reset_position()
            for g in self.ghosts:
                g.reset_position()
            if self.player.dead:
                self.player.revive()
            if self.pause:
                self.pause = False
            self.level_transition.set_show_transition()
        else:
            self.game_over = True
        pygame.time.set_timer(PacManPortalGame.REBUILD_EVENT, 0)    # disable timer repeat

    def check_player(self):
        """Check the player to see if they have been hit by an enemy, or if they have consumed pellets/fruit"""
        n_score, n_fruits, power = self.player.eat()
        self.score_keeper.add_score(score=n_score, items=n_fruits if n_fruits > 0 else None)
        if power:
            for g in self.ghosts:
                g.begin_blue_state()
        ghost_collide = pygame.sprite.spritecollideany(self.player, self.ghosts)
        if ghost_collide and ghost_collide.state['blue']:
            ghost_collide.set_eaten()
            self.score_keeper.add_score(200)
        elif ghost_collide and not (self.player.dead or ghost_collide.state['return']):
            self.life_counter.decrement()
            self.player.clear_portals()
            self.player.set_death()
            for g in self.ghosts:
                if g.state['enabled']:   # disable any ghosts
                    g.disable()
            pygame.time.set_timer(PacManPortalGame.START_EVENT, 0)  # cancel start event
            pygame.time.set_timer(PacManPortalGame.REBUILD_EVENT, 4000)
        elif not self.maze.pellets_left() and not self.pause:
            pygame.mixer.stop()
            self.pause = True
            pygame.time.set_timer(PacManPortalGame.LEVEL_TRANSITION_EVENT, 1000)

    def update_screen(self):
        """Update the game screen"""
        if not self.level_transition.transition_show:
            self.screen.fill(PacManPortalGame.BLACK_BG)
            self.check_player()
            self.maze.blit()
            if not self.pause:
                self.ghosts.update()
                self.player.update()
                self.maze.teleport.check_teleport(self.player.rect)     # teleport player/projectiles
            for g in self.ghosts:
                if self.score_keeper.level > 3:
                    if not g.state['speed_boost']:
                        g.increase_speed()
                    self.maze.teleport.check_teleport(g.rect)   # teleport ghosts
                g.blit()
            self.player.blit()
            self.score_keeper.blit()
            self.life_counter.blit()
        elif self.player.dead:
            self.player.update()
            self.player.blit()
        else:
            self.level_transition.draw()
            # if transition just finished, init ghosts
            if not self.level_transition.transition_show:
                self.init_ghosts()
        pygame.display.flip()

    def run(self):
        """Run the game application, starting from the menu"""
        menu = Menu(self.screen)
        hs_screen = HighScoreScreen(self.screen, self.score_keeper)
        intro_seq = Intro(self.screen)
        e_loop = EventLoop(loop_running=True, actions={pygame.MOUSEBUTTONDOWN: menu.check_buttons})

        while e_loop.loop_running:
            self.clock.tick(60)  # 60 fps limit
            e_loop.check_events()
            self.screen.fill(PacManPortalGame.BLACK_BG)
            if not menu.hs_screen:
                intro_seq.update()  # display intro/menu
                intro_seq.blit()
                menu.update()
                menu.blit()
            else:
                hs_screen.blit()    # display highs score screen
                hs_screen.check_done()
            if menu.ready_to_play:
                pygame.mixer.music.stop()   # stop menu music
                self.play_game()    # player selected play, so run game
                for g in self.ghosts:
                    g.reset_speed()
                menu.ready_to_play = False
                self.score_keeper.save_high_scores()    # save high scores only on complete play
                hs_screen.prep_images()     # update high scores page
                hs_screen.position()
            elif not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)     # music loop
            pygame.display.flip()

    def play_game(self):
        """Run the game's event loop, using an EventLoop object"""
        e_loop = EventLoop(loop_running=True, actions={**self.player.event_map, **self.actions})
        # game init signal
        # pygame.time.set_timer(PacManPortalGame.START_EVENT, self.level_transition.transition_time)
        self.level_transition.set_show_transition()
        self.game_over = False
        if self.player.dead:
            self.player.revive()
            self.score_keeper.reset_level()
            self.life_counter.reset_counter()
            self.rebuild_maze()

        while e_loop.loop_running:
            self.clock.tick(60)  # 60 fps limit
            e_loop.check_events()
            self.update_screen()
            if self.game_over:
                pygame.mixer.stop()
                self.score_keeper.reset_level()
                e_loop.loop_running = False


if __name__ == '__main__':
    game = PacManPortalGame()
    game.run()