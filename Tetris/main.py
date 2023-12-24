from settings import *
from tetris import Tetris, Text, Button
from tetromino import Tetromino, Block
import pygame.freetype as ft
import sys

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        self.font = ft.Font(FONT_PATH)
        self.screen = pg.display.set_mode(WIN_RES)
        self.sprite_group = pg.sprite.Group()
        self.clock = pg.time.Clock()
        self.setTimer()
        self.tetris = Tetris(self)
        self.tetromino= Tetromino(self)
        self.text= Text(self, self.tetris)
        self.fade_surface = pg.Surface(WIN_RES)
        self.fade_alpha = 0
        self.fade_in = False
        self.fade_out = False
        self.yesButton = Button(WIN_W * 0.3, WIN_H * 0.7, 120, 80, 'Yes', text_color=(255, 255, 255), function=self.reset)
        self.noButton = Button(WIN_W * 0.6, WIN_H * 0.7, 120, 80, 'No', text_color=(255, 255, 255), function=pg.quit)   
        self.buttons = [self.yesButton, self.noButton]
        self.running = True

    #defines a custom event, self.user_event, and sets up a timer for it.
    def setTimer(self):
        self.user_event = pg.USEREVENT + 0 #will appear after a set period of time
        self.fast_user_event = pg.USEREVENT + 1 #when user press down key
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL) #sets up a timer for the event I defined.
        #after ANIM_TIME_INTERVAL milliseconds, the event will be added to the event queue. (in checkEvent() method)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        self.tetris.update()
        self.clock.tick(FPS)
        if self.fade_out:
            self.fade_alpha += FADE_SPEED  #Increase alpha to fade out
            if self.fade_alpha >= 150:
                self.fade_alpha = 150  #Ensure the opacity doesn't go above the maximum
                self.fade_out = False #Stop fading out when fully opaque

    def draw(self):
        self.screen.fill(color=FIELD_COLOR)
        self.tetris.draw()
        self.text.draw()
        #Apply fade effect
        self.fade_surface.fill((0, 0, 0))  # use any color you want for the fade
        self.fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.fade_surface, (0, 0))
        #Draw buttons and text after the fade effect
        if self.fade_alpha == 150:
            for button in self.buttons:
                button.draw(self.screen)
            self.font.render_to(self.screen, (WIN_W * 0.09, WIN_H * 0.2),
                    text='Game Over', fgcolor='white', size=TILE_SIZE * 2)
            self.font.render_to(self.screen, (WIN_W * 0.18, WIN_H * 0.5),
                    text='Play Again?', fgcolor='white',
                    size=TILE_SIZE * 1.4)
        pg.display.flip()

    #Continuously runs in the game loop, checking and handling all events in Pygame's event queue.
    def checkEvent(self):
        self.anim_trigger = False #all movement of game would occur according to value of trigger. Resets the animation trigger flag for each new frame
        #at the start of each frame (or event cycle), this flag is reset to False, meaning that no animation event has yet occurred for this frame.
        #Then, as the events for this frame are processed in the loop, if an event of type self.user_event is found (which was set up by the timer to be triggered every ANIM_TIME_INTERVAL milliseconds), the self.anim_trigger flag is set to True. 
        #This indicates that the animation event has occurred for this frame.
        self.fast_anim_trigger = False 
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN: 
                #Keyboard key has been pressed down.
                self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.pos.collidepoint(pg.mouse.get_pos()):
                        button.click()

    def reset(self):
        self.tetris.game_over=False
        self.fade_alpha=0
        self.__init__()
        self.tetris = Tetris(self)
        self.tetromino=Tetromino(self)

    
    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.checkEvent()
            self.update()
            self.draw()
        pg.quit()
        sys.exit()

if __name__ == '__main__':
    app = App()
    app.run()