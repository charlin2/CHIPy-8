from random import randint
import pygame
from display import Display
from font import Font
from pygame.locals import *

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
        self.key = [0] * 16
        
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

        elif b3 == 0x3:
            # 3XNN: skip if VX == NN
            val = (b1 << 4) + b0
            if self.V[b2] == val:
                self.PC += 2

        elif b3 == 0x4:
            # 4XNN: skip if VX != NN
            val = (b1 << 4) + b0
            if self.V[b2] != val:
                self.PC += 2
                
        elif b3 == 0x5:
            # 5XY0: skip if VX == VY
            if self.V[b2] == self.V[b1]:
                self.PC += 2
            
        elif b3 == 0x6:
            # 6XNN: set register VX to NN
            self.V[b2] = (b1 << 4) + b0
                        
        elif b3 == 0x7:
            # 7XNN: add value NN to VX
            self.V[b2] += (b1 << 4) + b0
        
        elif b3 == 0x8:
            # 8XY0: set VX = VY
            if b0 == 0:
                self.V[b2] = self.V[b1]
                
            # 8XY1: VX = VX | VY (OR)
            elif b0 == 1:
                self.V[b2] |= self.V[b1]
                
            # 8XY2: VX = VX & VY (AND)
            elif b0 == 2:
                self.V[b2] &= self.V[b1]
                
            # 8XY3: VX = VX ^ VY (XOR)
            elif b0 == 3:
                self.V[b2] ^= self.V[b1]
                
            # 8XY4: VX = (VX + VY) % 0xFF
            elif b0 == 4:
                self.V[0xF] = 0
                sum = self.V[b2] + self.V[b1]
                
                # Overflow case
                if sum > 0xFF:
                    self.V[0xF] = 1
                    sum %= 0xFF
                self.V[b2] = sum

            # 8XY5: VX = VX - VY
            elif b0 == 5:
                self.V[0xF] = 1
                diff = self.V[b2] - self.V[b1]
                if diff < 0:
                    self.V[0xF] = 0
                    diff %= 0xFF
                self.V[b2] = diff
 
            # 8XY6: VX >>= 1
            elif b0 == 6:
                # self.V[b2] = self.V[b1]  # optional 'old style'
                self.V[0xF] = self.V[b2] & 0x1
                self.V[b2] >>= 1
 
            # 8XY7: VX = VY - VX
            elif b0 == 7:
                self.V[0xF] = 1
                diff = self.V[b1] - self.V[b2]
                if diff < 0:
                    self.V[0xF] = 0
                    diff %= 0xFF
                self.V[b2] = diff
            
            # 8XYE: VX <<= 1
            elif b0 == 0xE:
                # self.V[b2] = self.V[b1]  # optional 'old style'
                # TODO: get MSB from VX
                msb = self.V[b2]
                for _ in range(7):
                    msb >>= 1
                self.V[0xF] = msb
                self.V[b2] <<= 1
                    
        elif b3 == 0x9:
            # 9XY0: skip if VX != VY
            if self.V[b2] != self.V[b1]:
                self.PC += 2
        
        elif b3 == 0xA:
            # ANNN: set index register I to NNN
            self.I = (b2 << 8) + (b1 << 4) + b0
        
        elif b3 == 0xB:
            # BNNN: jump with offset
            self.PC = (b2 << 8) + (b1 << 4) + b0 + self.V[0]
            self.PC -= 2
        
        elif b3 == 0xC:
            # CXNN: generate random number, & with NN, put result in VX
            self.V[b2] = randint(0, 255) & ((b1 << 4) + b0)
        
        elif b3 == 0xD:
            # DXYN: draw sprite at VX, VY with height N
            self.draw(b2, b1, b0)
            
        elif b3 == 0xE:
            # EX9E: skip if key == VX
            if b0 == 0xE:
                if self.key[self.V[b2]]:
                    self.PC += 2
        
            # EXA1: skip if key != VX
            elif b0 == 0x1:
                if not self.key[self.V[b2]]:
                    self.PC += 2
            
        elif b3 == 0xF:
            if b1 == 0x0:
                # FX07: set VX = delay_timer
                if b0 == 0x7:
                    self.V[b2] = self.delay_timer
                
                # FX0A: get key press
                if b0 == 0xA:
                    if any(self.key):
                       for i, pressed in enumerate(self.key):
                           if pressed:
                               self.V[b2] = i
                    else:
                        self.PC -= 2 
            
            elif b1 == 0x1:
                # FX15: delay_timer = VX
                if b0 == 0x5:
                    self.delay_timer = self.V[b2]
                
                # FX18: sound_timer = VX
                elif b0 == 0x8:
                    self.sound_timer = self.V[b2]
                
                # FX1E: I += VX
                elif b0 == 0xE:
                    self.I += self.V[b2]
                
            # FX29: I = font address of VX
            elif b1 == 0x2:
                self.I = self.V[b2] * 5
                
            # FX33: convert Vx to decimal and store digits in memory at I
            elif b1 == 0x3:
                decimal = self.V[b2]
                i = 2
                while decimal > 0:
                    self.memory[self.I + i] = decimal % 10
                    decimal //= 10
                    i -= 1
                while i >= 0:
                    self.memory[self.I + i] = 0
                    i -= 1
            
            # FX55: load variable registers into memory 
            elif b1 == 0x5:
                for i, val in enumerate(self.V[:b2 + 1]):
                    self.memory[self.I + i] = val
            
            # FX65: load memory into variable registers
            elif b1 == 0x6:
                for i, val in enumerate(self.memory[self.I : self.I + b2 + 1]):
                    self.V[i] = val
                
        self.PC += 2
    
    def draw(self, b2, b1, n):
        self.V[0xF] = 0
        x = self.V[b2] % 64
        y = self.V[b1] % 32
        
        for i in range(n):
            sprite_line = self.memory[self.I + i]
            if y + i < Display.HEIGHT:
                for j in range(8):
                    if x + j < Display.WIDTH:
                        newBit = ((0x1 << (7 - j)) & sprite_line) >> (7 - j)
                        pixel = newBit ^ (self.display.screen.get_at((x + j, y + i)) == Display.WHITE)
                        if self.display.screen.get_at((x + j, y + i)) == pygame.Color(255, 255, 255) and newBit == 1:
                            self.V[0xF] = 1
                        self.display.screen.set_at((x + j, y + i), Display.WHITE if pixel else Display.BLACK)
    
    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as rom:
            rom_data = rom.read()
            for i, byte in enumerate(rom_data):
                self.memory[0x200 + i] = byte

    def start_game(self):
        self.started = True
        while self.started:
            self.listen()
                    
            opcode = (self.memory[self.PC] << 8) + self.memory[self.PC + 1]
            
            print(hex(self.memory[self.PC]), hex(self.memory[self.PC + 1]))
            
            self.decode(opcode)
            
            scaled_screen = pygame.transform.scale(self.display.screen, (Display.WIDTH * Display.SCALE, Display.HEIGHT * Display.SCALE))
            self.display.window.blit(scaled_screen, (0, 0))
            
            pygame.display.flip()
            
            pygame.time.wait(3)
            
    def listen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.started = False

            elif event.type == pygame.KEYDOWN:
                if event.key == K_1:
                    self.key[0x1] = 1
                elif event.key == K_2:
                    self.key[0x2] = 1
                elif event.key == K_3:
                    self.key[0x3] = 1
                elif event.key == K_4:
                    self.key[0xC] = 1
                elif event.key == K_q:
                    self.key[0x4] = 1
                elif event.key == K_w:
                    self.key[0x5] = 1
                elif event.key == K_e:
                    self.key[0x6] = 1
                elif event.key == K_r:
                    self.key[0xD] = 1
                elif event.key == K_a:
                    self.key[0x7] = 1
                elif event.key == K_s:
                    self.key[0x8] = 1
                elif event.key == K_d:
                    self.key[0x9] = 1
                elif event.key == K_f:
                    self.key[0xE] = 1
                elif event.key == K_z:
                    self.key[0xA] = 1
                elif event.key == K_x:
                    self.key[0x0] = 1
                elif event.key == K_c:
                    self.key[0xB] = 1
                elif event.key == K_v:
                    self.key[0xF] = 1
                    
            elif event.type == KEYUP:
                if event.key == K_1:
                    self.key[0x1] = 0
                elif event.key == K_2:
                    self.key[0x2] = 0
                elif event.key == K_3:
                    self.key[0x3] = 0
                elif event.key == K_4:
                    self.key[0xC] = 0
                elif event.key == K_q:
                    self.key[0x4] = 0
                elif event.key == K_w:
                    self.key[0x5] = 0
                elif event.key == K_e:
                    self.key[0x6] = 0
                elif event.key == K_r:
                    self.key[0xD] = 0
                elif event.key == K_a:
                    self.key[0x7] = 0
                elif event.key == K_s:
                    self.key[0x8] = 0
                elif event.key == K_d:
                    self.key[0x9] = 0
                elif event.key == K_f:
                    self.key[0xE] = 0
                elif event.key == K_z:
                    self.key[0xA] = 0
                elif event.key == K_x:
                    self.key[0x0] = 0
                elif event.key == K_c:
                    self.key[0xB] = 0
                elif event.key == K_v:
                    self.key[0xF] = 0