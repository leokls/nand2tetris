"""
Symbol-less assembler assumes that program.hack contains no symbols:
(a) In all address commands of type @Xxx, the Xxx constants are decimal nums;
(b) The input file contains no label commands of type (Xxx).
"""

class Parser:
    def __init__(self, filename):
        """
        Opens the input file/stream and gets ready to parse it.
        :param filename:  text file containing Assembly instructions.
        """
        self.fin = open(filename, 'r')  # create a fileobject
        self.current_line = self.fin.readline()

    def get_current_line(self):
        return self.current_line

    def has_more_commands(self):
        """
        :return: False if the file has reached EOF,
                 True otherwise.
        """
        if self.current_line == "":  # returns "" on EOF
            self.fin.close()
            return False
        return True

    def advance(self):
        """
        Reads the next command from the input and makes it the current
        command. Should be called only if hasMoreCommands() is true.
        Initially there is no current command.

        """
        self.current_line = self.fin.readline()

    def instruction_type(self, line):  # command_type
        """
        Assumes that line has been modified by extract_command(self, line).

        Returns the type of the current command:

        A_COMMAND for @Xxx where Xxx is either a symbol or a decimal number,
        C_COMMAND for dest = comp; jump
        L_COMMAND(actually, pseudo-command) for (Xxx) where Xxx is a symbol.

        EMPTY_LINE for empty line
        """
        if line == '':
            return "EMPTY_LINE"
        if line[0] == '@':
            return "A_COMMAND"
        elif line[0] == '(' and line[-1] == ')':
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def get_instruction(self, line):
        """
        Removes the whitespace, comments and the end-of-the-line character
        from the command.

        :return: string
        """
        instruction = line.lstrip()           # No leading spaces
        if instruction[:2] == "//":           # Full line comment
            return None
        instruction = line.split('//')[0]     # No comments
        instruction = instruction.strip()     # No leading and trailing spaces
        return instruction

    def symbol(self, line, type):
        """
        Assumes that line has been modified by extract_command(self, line).
        Assumes that line is of type A_COMMAND or L_COMMAND.

        Returns the symbol or decimal Xxx of the current command @Xxx
        or (Xxx). Should be called only when commandType() is
        A_COMMAND or L_COMMAND.

        :return: string
        """
        if type == "A_COMMAND":
            return line[1:]
        elif type == "L_COMMAND":
            return line[1:-1]

    def dest(self, line):
        if "=" in line:
            return line.split("=")[0]
        else:
            return "NULL"

    def comp(self, line):
        """
        """
        if "=" in line:  # command contains destination
            return line.split("=")[1].split(";")[0]
        else:            # command does not contain destination
            return line.split(";")[0]

    def jump(self, line):
        if ";" in line:  # command contains jump
            return line.split(";")[1]
        else:
            return "NULL"


class Code:
    """
    Translates Hack assembly language mnemonics into binary codes.
    """

    def __init__(self):
        # 8 possible 'destination' field combinations
        self.d_to_binary = {"M": "001", "D": "010", "MD": "011",
                                 "A": "100", "AM": "101", "AD": "110",
                                 "AMD": "111", "NULL": "000"}

        # 28 possibilities for the 'comp' mnemonic in the C-command
        self.c_to_binary = {"0": "0101010", "1": "0111111",
                         "-1": "0111010", "D": "0001100", "A": "0110000",
                         "!D": "0001101", "!A": "0110001", "-D": "0001111",
                         "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
                         "D-1": "0001110", "A-1": "0110010", "D+A": "0000010",
                         "D-A": "0010011", "A-D": "0000111", "D&A": "0000000",
                         "D|A": "0010101", "M": "1110000", "!M": "1110001",
                         "-M": "1110011", "M+1": "1110111", "M-1": "1110010",
                         "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
                         "D&M": "1000000", "D|M": "1010101"}

        self.j_to_binary = {"NULL": "000", "JGT": "100", "JEQ": "010",
                            "JGE": "110", "JLT": "001", "JNE": "101",
                            "JLE": "011", "JMP": "111"}


    def dest(self, mnemonic):
        """
        Returns the binary code of the 'dest' mnemonic.

        :param mneomonic:  string
        :return:           string
        """
        return self.d_to_binary[mnemonic]

    def comp(self, mnemonic):
        """
        Returns the binary code of the 'comp' mnemonic.

        :param mneomonic:  string
        :return:           string
        """
        return self.c_to_binary[mnemonic]

    def jump(self, mnemonic):
        """
        Returns the binary code of the 'jump' mnemonic.

        :param mneomonic:  string
        :return:           string
        """
        return self.j_to_binary[mnemonic]

class SymbolTable:
    def __init__(self):
        self.predefined_symbols = {"SP": str(bin(0)), "LCL": str(bin(1)),
                                   "ARG": str(bin(2)), "THIS" :str(bin(3)),
                                   "THAT":str(bin(4)),
                                   "R0": str(bin(0)), "R1": str(bin(1)),
                                   "R2": str(bin(2)), "R3": str(bin(3)),
                                   "R4": str(bin(4)), "R5": str(bin(5)),
                                   "R6": str(bin(6)), "R7": str(bin(7)),
                                   "R8": str(bin(8)), "R9": str(bin(9)),
                                   "R10": str(bin(10)), "R11": str(bin(11)),
                                   "R12": str(bin(12)), "R13": str(bin(13)),
                                   "R14": str(bin(14)), "R15": str(bin(15)),
                                   "SCREEN": str(bin(16384)),
                                   "KBD": str(bin(24576))}


if __name__ == '__main__':

    L_JUST = 20

    program = Parser("Add.asm")
    code = Code()

    # 1. Open an output file.
    fout = open('Add.hack', "a")
    # 2. Iterate assembly instructions (lines)

    # For each C-instruction, concatenate the translated binary codes of the
    # instruction fields into a single 16-bit word.

    # For each A-instruction of type @Xxx, the program translates the
    # decimal constant returned by the parser into its binary representation
    # and writes the resulting 16-bit word into the prog.hack file.

    while program.has_more_commands():
        line = program.get_current_line()
        instruction = program.get_instruction(line)
        if instruction:
            type = program.instruction_type(instruction)
            if type == "A_COMMAND":
                symbol = program.symbol(instruction, type)
                 if symbol.isdecimal():  # not identifier, convert to binary
                    symbol = str(bin(int(symbol)))[2:]  # remove '0b'
                    symbol = symbol.zfill(15)       # 15-bit address value
                    symbol = list(symbol)
                    out_arr = list()
                    out_arr.extend(symbol[:3])      # add the first 3 bits
                    out_arr.append(" ")             # put a separator
                    count = 0
                    for i in range(3, len(symbol)): # every 4 bits, separate
                        if count == 4:
                            out_arr.extend([" ", symbol[i]])
                            count = 1
                        else:
                            out_arr.append(symbol[i])
                            count += 1
                    symbol = "".join(out_arr)
                output = '{}'.format(instruction.ljust(L_JUST))
                fout.write(output)
                output = '0{}'.format(symbol)
                fout.write(output)
                fout.write('\n')
            elif type == "L_COMMAND":
                symbol = program.symbol(instruction, type)
                    output = '{}'.format(instruction.ljust(L_JUST))
                fout.write(output)
                output = '{}'.format(symbol)
                fout.write(output)
                fout.write('\n')
            elif type == "C_COMMAND":
                dest = program.dest(instruction)
                comp = program.comp(instruction)
                jump = program.jump(instruction)

                d = code.dest(dest)
                c = code.comp(comp)
                j = code.jump(jump)

                # 3. C-instruction. Concatenate the translated binary codes
                # of the instruction fields into a single 16-bit word.
                #    A-instruction. Translate the decimal constant returned
                # by the parser into its binary representation.

                output = '{}'.format(instruction.ljust(L_JUST))
                fout.write(output)
                output = '111{} {} {}{} {}{}'.format(c[0], c[1:5],
                                                     c[5:], d[:2],
                                                     d[2:], j)
                # 4. Write the resulting 16-bit word into the 'Prog.hack' file
                fout.write(output)
                fout.write('\n')

        program.advance()

    fout.close()

