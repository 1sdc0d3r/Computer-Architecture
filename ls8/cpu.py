"""CPU functionality."""

import sys
import glob

# path = './'

# files = [f for f in glob.glob(path + "**/", recursive=True)]
# for f in files:
#     print(f)

INC = 0b01100101  # reg += 1 (increment)
LDI = 0b10000010  # reg = int (register immediate)
PRN = 0b01000111  # print(reg)
HLT = 0b00000001  # halt

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8  # general-purpose registers
        self.pc = 0  # program counter
        self.mar = None  # Memory address register where reading/writing
        self.mdr = None  # holds value to write/read
        self.fl = []  # holds current flags
        self.dispatch_table = {}
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[ADD] = self.alu
        self.dispatch_table[SUB] = self.alu
        self.dispatch_table[MUL] = self.alu
        self.dispatch_table[DIV] = self.alu

    def ram_write(self, address, value):
        self.ram[address] = value
        self.pc += 3

    def ram_read(self, address=False):
        if address is not False:
            return self.ram[address]
        else:
            return self.ram

    def load(self):
        """Load a program into memory."""
        basePath = './examples/'
        file = "print8.ls8"
        if len(sys.argv) > 1:
            file = sys.argv[1]
        address = 0

        with open(basePath + file, "r") as f:
            for line in f:
                line = line.split("#")

                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                # print(v)
                self.ram[address] = v
                address += 1

    def alu(self, op=None, reg_a=None, reg_b=None):
        """ALU operations."""
        op = self.ram_read(self.pc)
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        def ADD_handler():
            self.reg[reg_a] += self.reg[reg_b]

        def SUB_handler():
            self.reg[reg_a] -= self.reg[reg_b]

        def MUL_handler():
            self.reg[reg_a] *= self.reg[reg_b]

        def DIV_handler():
            self.reg[reg_a] /= self.reg[reg_b]

        branch_table = {
            ADD: ADD_handler,
            SUB: SUB_handler,
            MUL: MUL_handler,
            DIV: DIV_handler
        }

        if op in branch_table:
            branch_table[op]()
            self.pc += 3
        else:
            raise Exception(
                f"Unsupported ALU operation {op} on pc-{self.pc} at address {reg_a} and {reg_b}")

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

        # print()
    def handle_LDI(self):
        # self.mar = self.r[self.pc+1]
        self.mar = self.ram_read(self.pc+1)
        self.mdr = self.ram_read(self.pc+2)
        self.reg[self.mar] = self.mdr
        self.pc += 3

    def handle_PRN(self):
        self.mar = self.ram_read(self.pc+1)
        self.mdr = self.reg[self.mar]
        print(self.mdr)
        self.pc += 2

    def handle_HLT(self):
        self.pc += 1
        sys.exit(0)

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram_read(self.pc)  # instruction register, copy
            # print(f"pc-{self.pc} ir-{ir}")

            # branch_table = {
            #     ADD: self.alu,
            #     SUB: self.alu,
            #     MUL: self.alu,
            #     DIV: self.alu
            # }

            if ir in self.dispatch_table:
                self.dispatch_table[ir]()
            elif ir in [ADD, SUB, MUL, DIV]:
                print(ir, True)
            else:
                print(cpu.reg)

                print(
                    f'Unknown instruction {ir} on pc-{self.pc} at address {self.mar}')
                sys.exit(1)


cpu = CPU()
cpu.load()
# cpu.ram_read()
cpu.run()
