import sys
import re


class CPU:
    def __init__(self, program, verbosity=0):         # Construct a new CPU
        self.pc = 0             #: Program Counter
        self.ir = None          #: Instruction Register - currently running instruction

        self.ram = [0] * 256    #: Init as array of zeros
        self.reg = [0] * 8      #: Register fixed number
        
        self.fl = NOP           #: Flags
        self.alu_op = 0         #: Is this an alu operation?
        self.set_pc = 0         #: Is this an operation that sets the pc?

        self.mar = [0] * 8      #: Memory Address Reader

        self.running = 0        #: Running?
        self.verbose = int(verbosity)        #: Verbosity?
        self.french = 0         #: French Finish Mode?

        self.opcodes = {
            # HLT: self.HLT,
            # NOP: self.NOP,
            # LDI: self.LDI,
            PRN: self.PRN,
            POP: self.POP,
            PUSH: self.PUSH,
            END: self.END,
        }
        self.jumpcodes = {
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE
        }

        self.alucodes = { MUL, CMP, ADD, SUB }
        
        self.program = program
        self.load(self.program)
    
    def load(self, proggy):
        # Load a program into memory. First method called from ls8
        address = 0     
        with open(proggy, 'r') as program:
            for line in program:
                short_line = line[:8]
                strip = re.sub(r'(?m)^ *#.*\n?', '', str(short_line))
                if len(strip) > 0 and strip is not "\n":
                    command = int(strip, 2)
                    if self.verbose >= 3:
                        print('\nCMD:', bin(command))
                    self.ram_write(address, command)
                    address += 1
        self.run()

    # Arithmatic and logic unit ALU
    def alu(self, operation, reg_a, reg_b):
        if operation == ADD:     #: Add
            if self.verbose >= 1:
                print(f"Adding reg {reg_a} and reg {reg_b}")
            self.reg[reg_a] += self.reg[reg_b]

        elif operation == SUB:   #: Sub
            if self.verbose >= 1:
                print(f"Subtracting reg {reg_b} from reg {reg_a}")
            self.reg[reg_a] -= self.reg[reg_b]
        
        elif operation == CMP:   #: Compare, if equal, set E to 1
            if self.verbose >= 1:
                print(f"\n CMP Comparing reg {reg_b} to reg {reg_a}")

            if self.reg[reg_a] < self.reg[reg_b]:
                if self.verbose >= 1:
                    print("Less than")
                self.fl = FLLS
                
            elif self.reg[reg_a] > self.reg[reg_b]:
                if self.verbose >= 1:
                    print("Greater than")
                self.fl = FLGR

            elif self.reg[reg_a] == self.reg[reg_b]:
                if self.verbose >= 1:
                    print("Equal")
                self.fl = FLEQ

        elif operation == MUL:     #: Mult
            print("Multi triggers")
            if self.verbose >= 1:
                print(f"Multiplying reg {reg_a} and reg {reg_b}")
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, counter):        #: Read the ram
        return self.ram[counter]
    
    def ram_write(self, address, payload):       #: Write the ram
        if self.verbose >= 3:
            print(f" RAM_WRITE address:{address} command:{bin(payload)}")
        self.ram[address] = payload

    def HLT(self, reg=0, reg_b=0):
        if self.french == 1:
            print("\nL' HALTE")
        else:
            print("\nHALT")
        self.END()

    def END(self):
        if self.french == 1:
            print("\n\n\n   FIN\n\n\n")
        else:
            print("\n    END OF PROGRAM\n")
        exit(1)
    
    def NOP(self, op_a, op_b):
        print(f"\n NOP: {op_a}:{op_b}")

    def NOT(self, op_a, op_b):
        opa = self.ram[pc + 1]
        self.reg[opa] = ~self.reg[opa]
        pc += 2

    def LDI(self, op_a, op_b):
        if self.verbose >= 3:
            print(f"\n LDI register set: {op_a}:{op_b}")
        self.reg[op_a] = op_b

    def PRN(self, register, op_b):
        if self.verbose >= 3:
            print(f"\n PRN Print at register {register}: {self.reg[register]}")
        print(self.reg[register])

    def POP(self, op_a, op_b):
        pass

    def PUSH(self, op_a, op_b):
        pass

    def JMP(self, register, reg_b):
        if self.verbose >= 2:
            print(f"\n JNE Jump to {self.reg[register]}")
        self.pc = self.reg[register]

    def JEQ(self, register, reg_b):
        if self.verbose >= 2:
            print(f"\n JNE Jump to {self.reg[register]} if equal {self.fl}")
        if self.fl is FLEQ:
            self.pc = self.reg[register]
        else:
            self.pc += 2
    
    def JNE(self, register, reg_b):
        if self.verbose >= 2:
            print(f"\n JNE Jump to {self.reg[register]} if not equal {self.fl}")
        if self.fl is not FLEQ:
            self.pc = self.reg[register]
        else:
            self.pc += 2

    def trace(self):
        print("\n\n >>> BEGIN TRACE ======================")
        print(f"PC: %s | %02X %02X %02X %02X | Flags: %02X " % (
            self.pc,                    #: 0
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2),
            self.ram_read(self.pc + 3),
            self.fl,                 #: Flags, might be doing this wrong
            #self.ie,           #: Might have something to do with interrupts
        ), end=' \n')

        print("\nREGISTERS:")
        for i in range(8):
            if self.reg[i] > 0:
                print(f"R{i}: %s" % self.reg[i], end="\n")
        print("\n")

    def run(self):
        self.running = 1
        self.french = 1

        # If verbosity 1+, trace the first op
        if self.verbose >= 1:
            self.trace()

        while self.running == 1:
            self.ir = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)
            check_end = self.ram_read(self.pc + 3)

            if self.ir in self.alucodes:
                self.alu(self.ir, op_a, op_b)
                self.pc += 3

            if self.ir in self.opcodes.keys():
                self.opcodes[self.ir](op_a, op_b)
                self.pc += 2
            
            if self.ir in self.jumpcodes.keys():
                self.jumpcodes[self.ir](op_a, op_b)

            if self.ir == LDI:
                # print("This is an LDI")
                self.LDI(op_a, op_b)
                self.pc += 3

            if self.ir == NOP:
                self.NOP(op_a, op_b)
                self.pc += 1

            if op_b == HLT and check_end == 0:
                self.HLT()

            if op_a == HLT and op_b == 0:
                self.HLT()

            if self.ir == HLT:
                self.HLT()

            if self.pc >= (len(self.ram) - 1):
                self.running = 0
                self.END()

            # If verbosity 1+, trace every operation
            if self.verbose == 1:
                self.trace()
            if self.verbose >= 2:
                self.trace()
                print('  self.ir: ', bin(self.ir))
                print('  op_a: ', bin(op_a))
                print('  op_b: ', bin(op_b))
                print('  check_end: ', bin(check_end))
                # print(f"{self.opcodes[self.ir].__name__}  op_a: {bin(op_a)}  op_b: {bin(op_b)}")

        self.running = 0


# * **immediate**: takes a constant integer value as an argument
# * **register**: takes a register number as an argument
# ## Instruction Layout
# `AABCDDDD`
# * `AA` Number of operands for this opcode, 0-2
# * `B` 1 if this is an ALU operation
# * `C` 1 if this instruction sets the PC
# * `DDDD` Instruction identifier
HLT = 0b1           #: HALT
END = 0b11111111    #: END

# 2 opcodes
# ALU op
# does not set pc
MYSTERY = 0b11101101

# 2 operand
LDI = 0b10000010    #: LDI register immediate set value of reg to an int
# Writes or reads from memory
LD = 0b10000011     #: Loads RegA with val at RegB
ST = 0b10000100     #: Store value in registerB in the address stored in registerA. 

# 1 operand
PRN = 0b01000111    #: Print decimal
PRA = 0b01001000    #: Pseudo-instruction, Print alpha character value stored in the given register.
# stack
POP = 0b01000110    #: Pop off register
PUSH = 0b01000101   #: Push on register
# Cool new commands
JMP = 0b01010100    #: Jump jump, kriss kross will make ya
JEQ = 0b01010101    #: Jump, if equal, to address
JNE = 0b01010110    #: Jump, if not equal, to address
CALL = 0b01010000   #: Call register, Calls a subroutine (function) at the address stored in the register.

NOP = 0b0           #: No Operation, do nothing with this instruction

# 0 operand
# Flag bits 
FLLS = 0b00000100     #: Less than
FLGR = 0b00000010     #: Greater than
FLEQ = 0b00000001     #: Equal to

RET = 0b00010001    #: RETURn, return from subroutine.


NOT = 0b01101001    #: NOT, 1 operand. Perform a bitwise-NOT on the value in a register.
# ALU Ops
MUL = 0b10100010    #: Multiply
OR = 0b10101010     #: OR
CMP = 0b10100111    #: Compare the values of two registers
ADD = 0b10100000    #: Add
SUB = 0b10100001    #: Subtract

