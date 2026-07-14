import tkinter as tk
from tkinter import filedialog
import random

WIDTH, HEIGHT = 64, 32
SCALE = 10
FONTSET = [
    0xF0,0x90,0x90,0x90,0xF0,
    0x20,0x60,0x20,0x20,0x70,
    0xF0,0x10,0xF0,0x80,0xF0,
    0xF0,0x10,0xF0,0x10,0xF0,
    0x90,0x90,0xF0,0x10,0x10,
    0xF0,0x80,0xF0,0x10,0xF0,
    0xF0,0x80,0xF0,0x90,0xF0,
    0xF0,0x10,0x20,0x40,0x40,
    0xF0,0x90,0xF0,0x90,0xF0,
    0xF0,0x90,0xF0,0x10,0xF0,
    0xF0,0x90,0xF0,0x90,0x90,
    0xE0,0x90,0xE0,0x90,0xE0,
    0xF0,0x80,0x80,0x80,0xF0,
    0xE0,0x90,0x90,0x90,0xE0,
    0xF0,0x80,0xF0,0x80,0xF0,
    0xF0,0x80,0xF0,0x80,0x80
]

class Chip8:
    def __init__(self):
        self.memory = [0]*4096
        self.V = [0]*16
        self.I = 0
        self.pc = 0x200
        self.stack = []
        self.display = [[0]*WIDTH for _ in range(HEIGHT)]
        self.delay = 0
        self.sound = 0
        self.keys = [0]*16
        self.draw_flag = False
        for i, b in enumerate(FONTSET):
            self.memory[i] = b

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom = f.read()
        self.memory = [0]*4096
        for i, b in enumerate(FONTSET):
            self.memory[i] = b
        for i, b in enumerate(rom[:4096-0x200]):
            self.memory[0x200+i] = b
        self.pc = 0x200

    def cycle(self):
        if self.pc >= 4095:
            return
        op = (self.memory[self.pc] << 8) | self.memory[self.pc+1]
        self.pc += 2
        x = (op & 0x0F00) >> 8
        y = (op & 0x00F0) >> 4
        n = op & 0x000F
        kk = op & 0x00FF
        nnn = op & 0x0FFF

        if op == 0x00E0:
            self.display = [[0]*WIDTH for _ in range(HEIGHT)]
            self.draw_flag = True
        elif op == 0x00EE:
            if self.stack:
                self.pc = self.stack.pop()
        elif (op & 0xF000) == 0x1000:
            self.pc = nnn
        elif (op & 0xF000) == 0x2000:
            self.stack.append(self.pc)
            self.pc = nnn
        elif (op & 0xF000) == 0x3000:
            if self.V[x] == kk:
                self.pc += 2
        elif (op & 0xF000) == 0x4000:
            if self.V[x] != kk:
                self.pc += 2
        elif (op & 0xF000) == 0x6000:
            self.V[x] = kk
        elif (op & 0xF000) == 0x7000:
            self.V[x] = (self.V[x] + kk) & 0xFF
        elif (op & 0xF000) == 0xA000:
            self.I = nnn
        elif (op & 0xF000) == 0xD000:
            self.V[0xF] = 0
            for row in range(n):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col):
                        px = (self.V[x] + col) % WIDTH
                        py = (self.V[y] + row) % HEIGHT
                        if self.display[py][px]:
                            self.V[0xF] = 1
                        self.display[py][px] ^= 1
            self.draw_flag = True

class App:
    def __init__(self, root):
        self.root = root
        root.title("DeepSeek CHIP-8 EMU")
        root.configure(bg="#081a33")
        self.chip = Chip8()
        self.canvas = tk.Canvas(root, width=WIDTH*SCALE, height=HEIGHT*SCALE, bg="black")
        self.canvas.pack(pady=10)
        tk.Button(root, text="LOAD ROM", command=self.load_rom, bg="black", fg="#33ccff").pack()
        self.root.after(16, self.loop)

    def load_rom(self):
        path = filedialog.askopenfilename()
        if path:
            self.chip.load_rom(path)

    def draw(self):
        self.canvas.delete("all")
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.chip.display[y][x]:
                    self.canvas.create_rectangle(x*SCALE, y*SCALE, (x+1)*SCALE, (y+1)*SCALE, fill="#33ccff", outline="")

    def loop(self):
        for _ in range(10):
            self.chip.cycle()
        self.draw()
        self.root.after(16, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
