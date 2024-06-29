import pygame
from display import Display
from font import Font

pygame.init()

class Chip8:
    def __init__(self):
        self.speed = 1024
        self.memory = [0] * 0xFFF
        self.stack = []
        self.PC = 0x200
        self.display = Display()
        self.V = [0] * 0x10
        self.I = 0
        self.delay_timer = 0
        self.sound_timer = 0
        
        # load fonts into first slots
        for i, val in enumerate(Font.FONT):
            self.memory[i] = val

    def decode(self, opcode):
        # Bitmask and right shift to get single digit
        b0 = opcode & 0x000F
        b1 = (opcode & 0x00F0) >> 4
        b2 = (opcode & 0x0F00) >> 8
        b3 = (opcode & 0xF000) >> 12
        
        # opcodes starting with 0
        if b3 == 0x0:
            # 00E0: clear screen
            if b0 == 0x0:
                self.display.clear()
            # 00EE: return from subroutine
            elif b0 == 0xE:
                self.PC = self.stack.pop()
        
        elif b3 == 0x1:
            # 1NNN: jump - set PC to NNN
            # Shift digits back into place
            self.PC = (b2 << 8) + (b1 << 4) + b0
            self.PC -= 2 # Offset PC increment
        
        elif b3 == 0x2:
            # 2NNN: jump to subroutine
            self.stack.append(self.PC)
            self.PC = (b2 << 8) + (b1 << 4) + b0 
            self.PC -= 2 # Offset PC increment

        elif b3 == 0x6:
            # 6XNN: set register VX to NN
            self.V[b2] = (b1 << 4) + b0
                        
        elif b3 == 0x7:
            # 7XNN: add value NN to VX
            self.V[b2] += (b1 << 4) + b0
        
        elif b3 == 0xA:
            # ANNN: set index register I to NNN
            self.I = (b2 << 8) + (b1 << 4) + b0
        
        elif b3 == 0xD:
            # DXYN: draw sprite at VX, VY with height N
            self.draw(b2, b1, b0)
        
        self.PC += 2
    
    # def draw(self, b2, b1, n):
    #     self.V[0xF] = 0
    #     x = self.V[b2] % 64
    #     y = self.V[b1] % 32
        
    #     for i in range(n):
    #         sprite_line = self.memory[self.I + i]
    #         if y + i < Display.HEIGHT:
    #             for j in range(8):
    #                 if x + j < Display.WIDTH:
    #                     pixel = (sprite_line >> (7 - j)) & 0x1
    #                     if self.display.screen.get_at((x + j, y + i)) == pygame.Color(255, 255, 255):
    #                         self.V[0xF] = 1
    #                     self.display.screen.set_at((x + j, y + i), Display.WHITE if pixel else Display.WHITE)
    
    def draw(self, b2, b1, b0):
        self.V[0xF] = 0 	# V[0xF] stores 0 by default, and 1 if during the instruction we erase a pixel (setting it to black, or 0)

        for i in range(b0): 	# For each line of our sprite

            line = self.memory[self.I+i] 	# We are reading the sprite starting from the I adress and increasing it for each line
            currentY = self.V[b1] + i 		# We set the initial Y axis position to the one given by V[Y] and we add to it the i counter to get the current line position

            if currentY < Display.HEIGHT: 	# If we are in available height of the screen

                for j in range(8): 	# A sprite is 8 bits in width

                    currentX = self.V[b2] + j 	# Sets the current X position to the value given by V[X] and adding the j counter value

                    if currentX < Display.WIDTH: 	# If we are in available width of the screen

                        mask = 0x1 << (7-j) 										# Mask to be used to retrieve the wanted bit in the line (which is a byte). If I want the MSB bit, j is at 0, so we get a mask of 0b10000000. Applying it with a bitwise AND and shifting will get us our bit.
                        newBit = (mask & line) >> (7-j) 							# Getting the bit by applying the mask, and shifting it back to the LSB position
                        result = newBit ^ (self.display.screen.get_at((currentX, currentY)) == Display.WHITE) 	# A new pixel is decided by doing a XOR between the current state of the pixel, and the value wanted by the sprite
                        self.display.screen.set_at((currentX, currentY), Display.WHITE if result else Display.BLACK) 			# We set the result of the XOR to the screen

                        if(self.display.screen.get_at((currentX, currentY)) == Display.BLACK and newBit == 1): 	# If we erased it (with a XOR, it happens when the pixel is erased and we wanted to apply a value of 1)
                            self.V[0xF] = 1 		

    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as rom:
            rom_data = rom.read()
            for i, byte in enumerate(rom_data):
                self.memory[0x200 + i] = byte

    def start_game(self):
        started = True
        while started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    started = False
                    
            self.display.screen.set_at((16, 16), Display.WHITE)
            
            opcode = (self.memory[self.PC] << 8) + self.memory[self.PC + 1]
            
            print(hex(self.memory[self.PC]), hex(self.memory[self.PC + 1]))
            
            self.decode(opcode)
            
            scaled_screen = pygame.transform.scale(self.display.screen, (Display.WIDTH * Display.SCALE, Display.HEIGHT * Display.SCALE))
            self.display.window.blit(scaled_screen, (0, 0))
            
            pygame.display.flip()
            
            pygame.time.wait(10)
            
chip8 = Chip8()
chip8.load_rom("IBM Logo.ch8")
chip8.start_game()
