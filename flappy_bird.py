"""
The flappy bird game using the NEAT algorithm
"""

from distutils.command.config import config
from hashlib import algorithms_available
import pygame
import random
import os
import time
import neat
import pickle


pygame.font.init() # initialize font


WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 50)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg.png")).convert_alpha(),(600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha())

gen = 0

class Bird:
    """
    Flappy Bird class
    """

    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        X is starting x position (int)
        y is starting y pos (int)
        No return value
        """
        self.x = x
        self.y = self.tilt = 0 # degree of tilt

        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        Make flappy  bird jump
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make flappy bird move
        """    
        self.tick_count += 1

        displacement = self.vel*(self.tick_count) + 0.5 * (3) * (self.tick_count)**2 # displacement calculation

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        if displacement < 0:
            displacement += 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50: # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: #tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        """
        draw flappy bird on pygame window
        """
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*4 +1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # if flappy bird is nose diving there should not be flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        #get the maask
        return pygame.mask.from_surface(self.img)

class Pipe():
    """
    represents pipe object
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        """
        self.x = x
        self.height = 0

        #where top and bottom of pipe is
        self.top = 0
        self.bottom = 0
    
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()
    
    def set_height(self):
        """
        set the height of the pipe from the top of the screen
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        Move pipe base on velocity
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw the top and bottom of the pipe
        """

        #draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))

        #draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird, win):
        """
        returns if point has been collided with
        return bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True
        
        return False

class Base:
    """
    Represents the moving floor
    """

    VEL = 5
    WIDTH =base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialise object
        """

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        movee floor to make it as if scrolling
        return none
        """

        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, win):
        """
        draw the floor
        return none
        """

        win.blit(self.IMG, (self.x1, self.y)),
        win.blit(self.IMG, (self.x2, self.y))
    
def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    return none

    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen,  pipe_ind):
    """
    draw the window for the main loop
    return none
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw linnes from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x +pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x +pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
            # draw bird
        bird.draw(win) 

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generation
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def eval_genomes(genomes, config):
    """
    Runs simulation of current population of birdies
    """

    global WIN, gen
    win = WIN
    gen += 1

    # start creating lists holding the genome itself
    # the ANN associated with the genome
    # and bird object

    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0 # begin with zero fitness
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
    
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
    
        for x, bird in enumerate(birds): # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe locatio and botom pipe location
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5: #we use a tahn activation function so result will be between
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this to gie reward for each pipe pass
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

    # break if score gets large eniugh
    '''if score > 20:
       pickle.dump(nets[0],open("best.pickle", "wb"))
       break'''

def run(config_file):
    """
    run NEAT

    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

    p = neat.Population(config) # Create the population, which is the top-level object for a NET run

    # Add a stdout reporter to shiw progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointers)

    # Run for up to 50 generations
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Deternimne path to config file. Path manipulation
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
