from settings import *
import random

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_tetro_pos = vec(pos) + NEXT_TETRO_POS_OFFSET
        self.alive= True

        color = COLORS[self.tetromino.shape]

        super().__init__(tetromino.tetris.sprite_group)
        self.image = pg.Surface([TILE_SIZE, TILE_SIZE])
        pg.draw.rect(self.image, color, (1, 1, TILE_SIZE-2, TILE_SIZE-2), border_radius= 8)
        self.rect = self.image.get_rect()
    
        self.sfx_image = self.image.copy() #creates a copy of the current image of the block to be manipulated for the special effect.
        self.sfx_image.set_alpha(110) #sets transparency of the special effect
        self.sfx_speed = random.uniform(0.2, 0.6) #speed of the special effect is set randomly between 0.2 and 0.6
        self.sfx_cycles = random.randrange(6, 8) #how many "cycles" the special effect will run for.
        self.cycle_counter = 0
    
    def sfx_end_time(self):
        #increments the cycle counter each time an animation trigger occurs.
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter += 1
            if self.cycle_counter > self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        self.image = self.sfx_image #replaces the current image of the block (self.image) with the special effects image
        self.pos.y -= self.sfx_speed #moves the block upwards by reducing its y-position
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self.sfx_speed) #rotates the block image

    #Update pixel position for user to see/drawing objects on the screen
    def  updatePixelPosition(self):
            #If self.tetromino.current is False, pos will be set to self.next_pos, and if it is True, pos will be set to self.pos
            pos = [self.next_tetro_pos, self.pos][self.tetromino.current]
            self.rect.topleft = pos * TILE_SIZE #Convert from grid to pixel coord

    def update(self):
        self. updatePixelPosition()
        self.isAlive()

    def isCollide(self, pos):
        x, y = int(pos.x), int(pos.y)
        #Origin point (0,0) of the coordinate system is usually at the top left corner of the screen
        #If the block's y position is greater than or equal to the field height, it means the block has moved past the bottom boundary of the game field.
        if 0<=x<FIELD_W and y<FIELD_H and (
            y<0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True
    
    def rotate(self, pivit_pos):
        translated= self.pos - pivit_pos #translate point so that the pivot point is at the origin (0,0)
        rotated= translated.rotate(90)
        return rotated + pivit_pos
    
    def isAlive(self):
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()

class Tetromino:
    def __init__(self, tetris, current=True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.blocks= [Block(self,pos) for pos in TETROMINOES[self.shape]]
        self.landing=False
        self.current=current
    
    def rotate(self):
        pivot_pos= self.blocks[0].pos
        newBlockPosition= [block.rotate(pivot_pos) for block in self.blocks] #For each block in the tetromino, it calls the rotate function
        if not self.isCollide(newBlockPosition):
            for i, block in enumerate(self.blocks): #i is the index of the block in self.blocks and block is the value at that index
                block.pos= newBlockPosition[i]

    def move(self, direction):
        moveDirection = MOVE_DIRECTIONS[direction]
        newBlockPositions=[]
        for block in self.blocks:
            newBlockPositions.append(block.pos + moveDirection)
        isCollide= self.isCollide(newBlockPositions)

        if not isCollide:
            for block in self.blocks:
                block.pos += moveDirection
        elif direction == 'down':
            self.landing = True
    
    def isCollide(self, blockPositions):
        #Call collision check for each block
        #Return any(map(Block.isCollide, self.blocks, block_positions))
        for block, newPosition in zip(self.blocks, blockPositions): #(block1, pos1), (block2, pos2), (block3, pos3)
            if block.isCollide(newPosition):
                return True
        return False

    def update(self):
        self.move(direction='down')