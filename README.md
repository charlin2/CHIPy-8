# CHIPy-8

This is my attempt at a CHIP-8 emulator written in Python using PyGame for the display.

## Background
CHIP-8 is a programming language originally developed for 8-bit microcomputers in the 70's.  Since CHIP-8 is a language and not the hardware itself, the goal of this project is to emulate the environments that CHIP-8 would run on, and also be able to interpret the language by implementing the CHIP-8 instruction set (opcodes).

I began this project after a wave of nostalgia from using emulators to play GBA, SNES, and NDS games led me to the EmuDev subreddit.  Per popular recommendation from the subreddit, I chose CHIP-8 as introductory project to the world of emulation.

## Resources
I mainly used [this guide from Tobias Langhoff](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/) and also cross referenced with [Cowgod's guide](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM).  Since I was not familiar with PyGame before developing this project, I referenced [this repo](https://github.com/ThibaultNocchi/MyChip8Emulator) to get started.