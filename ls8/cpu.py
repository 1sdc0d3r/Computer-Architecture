"""CPU functionality."""

import sys
import glob
# from pynput.keyboard import keyboard

# path = './'

# files = [f for f in glob.glob(path + "**/", recursive=True)]
# for f in files:
#     print(f)

INC = 0b01100101  # reg += 1 (increment)
DEC = 0b01100110  # decrement from reg
LDI = 0b10000010  # reg = int (register immediate)
PRN = 0b01000111  # print
HLT = 0b00000001  # halt
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100  # jump pc to register
JEQ = 0b01010101  # JMP if equal flag is set
JNE = 0b01010110  # JMP if equal flag is not set

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
CMP = 0b10100111  # compare and set flags
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100  # shift left
SHR = 0b10101101  # shift right
MOD = 0b10100100  # modulo


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8  # general-purpose registers
        # R5 reserved for interrupt mask (IM)
        # R6 reserved for interrupt status(IS)
        # R7 reserved for stack pointer(SP)
        self.reg[7] = int("F4", 16)
        self.sp = self.reg[7]  # Stack Pointer
        self.pc = 0  # program counter
        self.mar = None  # Memory address register where reading/writing
        self.mdr = None  # Memory Data Register holds value to write/read
        self.fl = {}  # holds current flags
        self.fl["E"] = 0
        self.fl["L"] = 0
        self.fl["G"] = 0
        """Interput Vector Table"""
        self.ram[int("FF", 16)] = "I7"
        self.ram[int("FE", 16)] = "I6"
        self.ram[int("FD", 16)] = "I5"
        self.ram[int("FC", 16)] = "I4"
        self.ram[int("FB", 16)] = "I3"
        self.ram[int("FA", 16)] = "I2"
        self.ram[int("F9", 16)] = "I1"
        self.ram[int("F8", 16)] = "I0"
        """Interput Vector Table"""
        self.dispatch_table = {}
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[ADD] = self.alu
        self.dispatch_table[SUB] = self.alu
        self.dispatch_table[MUL] = self.alu
        self.dispatch_table[DIV] = self.alu
        self.dispatch_table[CMP] = self.alu
        self.dispatch_table[AND] = self.alu
        self.dispatch_table[OR] = self.alu
        self.dispatch_table[XOR] = self.alu
        self.dispatch_table[NOT] = self.alu
        self.dispatch_table[SHL] = self.alu
        self.dispatch_table[SHR] = self.alu
        self.dispatch_table[MOD] = self.alu
        self.dispatch_table[PUSH] = self.handle_PUSH
        self.dispatch_table[POP] = self.handle_POP
        self.dispatch_table[CALL] = self.handle_CALL
        self.dispatch_table[RET] = self.handle_RET
        self.dispatch_table[JMP] = self.handle_JMP
        self.dispatch_table[JEQ] = self.handle_JEQ
        self.dispatch_table[JNE] = self.handle_JNE

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
        # file = "mult.ls8"
        # file = "stack.ls8"
        # file = "call.ls8"
        file = "sctest.ls8"
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
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        reg_b = self.reg[self.ram_read(self.pc + 2)]

        def CMP_handler():
            self.fl["L"] = 0
            self.fl["E"] = 0
            self.fl["G"] = 0
            if reg_a < reg_b:
                self.fl["L"] = 1
            elif reg_a == reg_b:
                self.fl["E"] = 1
            else:
                self.fl["G"] = 1

        def ADD_handler():
            reg_a += reg_b

        def SUB_handler():
            reg_a -= reg_b

        def MUL_handler():
            reg_a *= reg_b

        def DIV_handler():
            reg_a /= reg_b

        def AND_handler():
            reg_a = reg_a & reg_b

        def OR_handler():
            reg_a = reg_a | reg_b

        def XOR_handler():
            reg_a = reg_a ^ reg_b

        def NOT_handler():
            # ? WHY NONETYPE??
            reg_a = ~reg_a

        def SHL_handler():
            reg_a = reg_a << reg_b

        def SHR_handler():
            reg_a = reg_a >> reg_b

        def MOD_handler():
            if reg_b == 0:
                print("The world just exploded! You can't divide by 0...")
                self.handle_HLT()
            else:
                reg_a = reg_a % reg_b

        branch_table = {
            ADD: ADD_handler,
            SUB: SUB_handler,
            MUL: MUL_handler,
            DIV: DIV_handler,
            CMP: CMP_handler,
            AND: AND_handler,
            OR: OR_handler,
            XOR: XOR_handler,
            NOT: NOT_handler,
            SHL: SHL_handler,
            SHR: SHR_handler,
            MOD: MOD_handler,

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
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def handle_INC(self):
        self.mar = self.ram[self.pc+1]
        self.reg[self.mar] = self.reg[self.mar] + 1
        self.pc += 2

    def handle_PUSH(self, data=None):
        self.sp -= 1
        self.mar = self.sp
        if data is None:
            self.mdr = self.reg[self.ram[self.pc+1]]
            self.pc += 2
        else:
            self.mdr = data
        self.ram[self.mar] = self.mdr

    def handle_POP(self):
        self.mar = self.ram[self.pc+1]
        self.mdr = self.ram[self.sp]
        self.reg[self.mar] = self.mdr
        self.sp += 1
        self.pc += 2

    def handle_CALL(self):
        self.handle_PUSH(self.pc+2)
        self.mar = self.reg[self.ram[self.pc+1]]
        self.pc = self.mar

    def handle_RET(self):
        self.mar = self.ram[self.sp]
        self.pc = self.mar

    def handle_JMP(self):
        self.mar = self.ram[self.pc+1]
        self.pc = self.reg[self.mar]

    def handle_JEQ(self):
        if self.fl["E"] == 1:
            self.handle_JMP()
        else:
            self.pc += 2

    def handle_JNE(self):
        if self.fl["E"] == 0:
            self.handle_JMP()
        else:
            self.pc += 2

    def handle_LDI(self):
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
        # print(self.ram_read())
        sys.exit(0)

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram_read(self.pc)  # instruction register, copy
            # print(f"pc-{self.pc} ir-{ir} {ir[:1]}")

            # if self.pc > 25:
            #     self.reg[6] = 1
            # if self.reg[6] == 1:
            #     print("INTERUPT")
            #     break

            if ir in self.dispatch_table:
                # print(bin(ir))
                self.dispatch_table[ir]()
            # elif int(ir, 2)[2] == 1:
                # self.alu()

            else:
                print(
                    f'Unknown instruction {ir}({bin(ir)}) on pc-{self.pc} at address {self.mar}. registers={self.reg}')
                sys.exit(1)


cpu = CPU()
# cpu.load()
# cpu.run()
# print(cpu.ram_read())


bit1 = 0b10101010
bit2 = 0b00001111
bit3 = 10
bit4 = 3
# ----------
# 0b00001010
#    `MOD`


def OR_handler():
    print("OR")


def AND_handler(bit1, bit2, bit3, bit4):
    return ~bit3


print(AND_handler(bit1, bit2, bit3, bit4))
