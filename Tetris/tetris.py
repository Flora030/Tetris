import pygame as pg
from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft

class Button:
    def __init__(self, x, y, width, height, text=None, color=(73, 73, 73), text_color=(255, 255, 255), highlight_color=(189,189,189), function=None, params=None):
        self.font = ft.Font(FONT_PATH)
        self.image = pg.Surface((width, height))
        self.pos = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.highlight_color = highlight_color
        self.function = function
        self.params = params
        self.highlighted = False

    def update(self, mouse):
        if self.pos.collidepoint(mouse):
            self.highlighted = True
        else:
            self.highlighted = False

    def draw(self, window):
        if self.highlighted:
            self.image.fill(self.highlight_color)
        else:
            self.image.fill(self.color)
        window.blit(self.image, self.pos)
        if self.text:
            # Render the text to a new Surface, so we can get its dimensions
            text_surface, text_rect = self.font.render(text=self.text, fgcolor='white', size=TILE_SIZE/2)
            # Center the text_rect within the button's rect
            text_rect.center = self.pos.center
            # Now blit the text_surface at the position of text_rect
            window.blit(text_surface, text_rect)

    def click(self):
        if self.params:
            self.function(*self.params)
        elif self.function:
            self.function()
        else:
            pass

class Text:
    def __init__(self, app, tetris):
        self.app = app
        self.tetris = tetris
        self.font = ft.Font(FONT_PATH)

    def getColor(self):
        time = pg.time.get_ticks() * 0.001
        n_sin = lambda t: (math.sin(t) * 0.5 + 0.5) * 255
        return n_sin(time * 0.5), n_sin(time * 0.2), n_sin(time * 0.9)

    def draw(self):
        self.font.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02),
                            text='TETRIS', fgcolor=self.getColor(),
                            size=TILE_SIZE * 1.65, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.65, WIN_H * 0.22),
                            text='next', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67),
                            text='score', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.77, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}', fgcolor='white',
                            size=TILE_SIZE * 1.8)
        
class Tetris:

    def __init__(self, app):
        self.font = ft.Font(FONT_PATH)
        self.sprite_group = pg.sprite.Group()
        self.text = Text(app, self)
        self.app = app
        self.tetromino = Tetromino(self)
        self.field_array = self.makeBackgroundGrid()
        self.score= 0
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}
        self.speed_up= False
        self.game_over = False
        self.next_tetromino= Tetromino(self, current=False) #creating the next tetromino (Tetris piece) that will appear after the current one is placed on the field
        #current=False parameter means that this new Tetromino is not the one currently controlled by the player, but the upcoming one.
    
    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1): #Range(start, stop, step) iterates from bottom to top
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x] #Row is initially the same as y but when a full line is found, the row doesn't decrease, 
                #so the lines above are "shifted" down by copying to the next row.
                if self.field_array[y][x]: #If the column in the current row (self.field_array[y][x]) is occupied by a block,
                    #it moves the block down to the current row
                    self.field_array[row][x].pos = vec(x, y) #updates the block's position to match the new row
            #Checks if the row is full
            if sum(map(bool, self.field_array[y])) < FIELD_W: #if it is not full
                row -= 1
            else:
                #Removes the row by setting all the blocks in the row to not alive
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0
                self.full_lines += 1

    def getScore(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0

    def makeBackgroundGrid(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def addBlockToTracker(self):
        for block in self.tetromino.blocks:
            x, y= int(block.pos.x), int(block.pos.y)
            self.field_array[y][x]= block #block represents a single block

    def drawBackgroundGrid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black', (x*TILE_SIZE, y*TILE_SIZE,TILE_SIZE,TILE_SIZE),1)
    
    def control(self,pressed_key):
        if pressed_key == pg.K_LEFT and self.game_over == False:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT and self.game_over == False:
            self.tetromino.move(direction="right")
        elif pressed_key == pg.K_UP and self.game_over == False:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN and self.game_over == False:
            self.speed_up= True

    def blockArrayTracker(self):
        if self.tetromino.landing:
            self.addBlockToTracker()
            self.checkGameOver()
            if self.game_over == False:
                self.next_tetromino.current=True
                self.tetromino = self.next_tetromino #gives user new block
                self.next_tetromino= Tetromino(self, current=False)
            self.speed_up= False

    def update(self):
        if self.speed_up:
            trigger = self.app.fast_anim_trigger
        else:
            trigger = self.app.anim_trigger
        if trigger:
            self.tetromino.update() #updates the current tetromino. Presumably, this moves the tetromino down the field 
            #or responds to user inputs to move or rotate it.
            self.blockArrayTracker() #checks if the tetromino has landed. 
            #If it has, a new tetromino is created.
            self.check_full_lines()
            self.getScore()
        self.sprite_group.update()
    
    def checkGameOver(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            if y<=0:  #If the position in the field array where the new Tetromino is being spawned is not empty
                self.game_over = True
                self.app.fade_out = True
                return

    def draw(self):
        self.drawBackgroundGrid()
        self.sprite_group.draw(self.app.screen)
    
