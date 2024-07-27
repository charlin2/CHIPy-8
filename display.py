import pygame

class Display:
    OFF = (0, 0, 0)
    ON = (3, 150, 30)
    WIDTH = 64
    HEIGHT = 32
    SCALE = 20
    
    def __init__(self):
        self.window = pygame.display.set_mode((Display.WIDTH * Display.SCALE, Display.HEIGHT * Display.SCALE)) 
        
        self.screen = pygame.Surface((Display.WIDTH, Display.HEIGHT))
        
        self.clear()        
        
    def clear(self):
        self.screen.fill(Display.OFF)        