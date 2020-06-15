"""CPU functionality."""

import sys

INC = 0b01100101  # reg += 1 (increment)
LDI = 0b10000010  # reg = int (register immediate)
PRN = 0b01000111  # print(reg)
HLT = 0b00000001  # halt


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*8
        self.reg = [0]*8  # general-purpose registers
        self.pc = 0  # program counter
        self.mar = None  # Memory address register where reading/writing
        self.mdr = None  # holds value to write/read
        self.fl = []  # holds current flags

    def ram_write(self, address, value):
        self.ram[address] = value
        self.pc += 3

    def ram_read(self, address=False):
        if address.exists() is not False:
            print(self.ram[address])
        else:
            print(self.ram)

    def load(self):
        """Load a program into memory."""
        address = 0
        # For now, we've just hardcoded a program:
        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            print(self.reg[reg_a])
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
            print(self.reg[reg_a])
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
            print(self.reg[reg_a])
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
            print(self.reg[reg_a])
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            # * self.ram_read(self.pc),
            # * self.ram_read(self.pc + 1),
            # * self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram[self.pc]  # instruction register, copy
            # print(f"pc-{self.pc} ir-{ir}")
            if ir == LDI:
                self.mar = self.ram[self.pc+1]
                self.mdr = self.ram[self.pc+2]
                self.reg[self.mar] = self.mdr
                self.pc += 3

            elif ir == PRN:
                self.mar = self.ram[self.pc+1]
                self.mdr = self.reg[self.mar]
                print(self.mdr)
                self.pc += 2

            elif ir == HLT:
                running = False
                self.pc += 1
            else:
                print(f'Unknown instruction {ir} at address {self.mar}')
                sys.exit(1)


cpu = CPU()
cpu.load()
cpu.run()
cpu.alu("MULT", 0, 3)
