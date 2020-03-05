"""CPU functionality."""

import sys

MUL = 0b10100010
ADD = 0b10100000
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
PSH = 0b01000101
POP = 0b01000110
CAL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
PRA = 0b01001000
NOT = 0b01101001
INC = 0b01100101
XOR = 0b10101011
AND = 0b10101000
# 2 opcodes
# ALU op
# does not set pc
# MYST = 0b11101101 # This shouldn't be right

code = "10000010\n00000001\n01001101\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n01100101\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01111001\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01110101\n01001000\n00000001\n10000010\n00000001\n01110010\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01100011\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01110010\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101101\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n00101001\n10000010\n00000010\n00111111\n10101000\n00000001\n00000010\n10000010\n00000010\n00011101\n10101011\n00000001\n00000010\n01001000\n00000001\n10000010\n00000001\n11111111\n10000010\n00000010\n00100101\n10101000\n00000001\n00000010\n10000010\n00000010\n00010101\n10101011\n00000001\n00000010\n01001000\n00000001\n10000010\n00000001\n00100101\n10000010\n00000010\n10110000\n10101000\n00000001\n00000010\n10000010\n00000010\n00011001\n10101011\n00000001\n00000010\n01001000\n00000001\n00000001"
list = code.split('\n')

new_list = []
for byte in list:
    new_list.append(int(byte, 2))


class CPU:
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

    def load(self):
        address = 0

        program = new_list

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, opa, opb, opc=None):
        if op == "ADD":
            self.reg[opa] += self.reg[opb]

        elif op == "MUL":
            self.reg[opa] *= self.reg[opb]

        elif op == 'EQ':
            if opa == opb:
                return(0b00000001)
            elif opa < opb:
                return(0b00000100)
            elif opa > opb:
                return(0b00000010)

        elif op == "XOR":
            print('self.reg[opa]^self.reg[opb]: ', self.reg[opa], self.reg[opb])
            comp = self.reg[opa]^self.reg[opb]
            return comp

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %s" % self.reg[i], end='')

        print()

    def ram_read(self, loc):
        return self.ram[loc]

    def ram_write(self, loc, val):
        self.ram[loc] = val

    def run(self):
        pc = self.pc
        SP = 0xF3
        FL = 0b00000000

        while True:
            IR = self.ram[pc]
            # self.trace()
            if IR == HLT:
                break
            elif IR == LDI:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                pc += 3
                self.reg[opa] = opb

            elif IR == PRN:
                reg_loc = self.ram[pc + 1]
                print(self.reg[reg_loc])
                pc += 2

            elif IR == ADD:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                self.alu('ADD', opa, opb)
                pc += 3

            elif IR == MUL:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                self.alu('MUL', opa, opb)
                pc += 3

            elif IR == PSH:
                opa = self.ram[pc + 1]
                self.ram[SP] = self.reg[opa]
                SP -= 1
                pc += 2

            elif IR == POP:
                opa = self.ram[pc + 1]
                SP += 1
                self.reg[opa] = self.ram[SP]
                pc += 2

            elif IR == CAL:
                opa = self.ram[pc + 1]
                self.ram[SP] = pc + 2
                SP -= 1
                pc = self.reg[opa]

            elif IR == RET:
                SP += 1
                pc = self.ram[SP]

            elif IR == CMP:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                rega = self.reg[opa]
                regb = self.reg[opb]
                FL = self.alu('EQ', rega, regb)
                pc += 3
        
            elif IR == JMP:
                opa = self.ram[pc + 1]
                pc = self.reg[opa]

            elif IR == JEQ:
                opa = self.ram[pc + 1]
                if FL == 1:
                    pc = self.reg[opa]
                else:
                    pc += 2

            elif IR == JNE:
                opa = self.ram[pc + 1]
                if FL != 1:
                    pc = self.reg[opa]
                else:
                    pc += 2

            elif IR == PRA:
                opa = self.ram[pc + 1]
                rega = self.reg[opa]
                print(" > ", chr(rega))
                
                pc += 2

            elif IR == NOT:
                opa = self.ram[pc + 1]
                self.reg[opa] = ~self.reg[opa]
                pc += 2

            elif IR == AND:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                self.reg[opa] = self.reg[opa] & self.reg[opb]
                pc += 3

            elif IR == XOR:
                opa = self.ram[pc + 1]
                opb = self.ram[pc + 2]
                self.reg[opa] = self.reg[opa] ^ self.reg[opb]
                pc += 3

            elif IR == INC:
                opa = self.ram[pc + 1]
                self.reg[opa] += 1
                pc += 2

            # elif IR == MYST:
            #     opa = self.ram[pc + 1]
            #     opb = self.ram[pc + 2]
            #     opc = self.ram[pc + 3]
            #     self.alu('MYST', opa, opb, opc)
            #     print("Myst op")
            #     pc += 4



cpu = CPU()
cpu.load()
cpu.run()
