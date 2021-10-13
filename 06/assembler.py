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
        C_COMMAND for 'dest' = comp; jump
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
        instruction = line.lstrip()        # No leading spaces
        if instruction[:2] == "//":        # Full line comment
            return None
        instruction = line.split('//')[0]  # Remove in-line comments
        instruction = instruction.strip()  # No leading and trailing spaces
        if len(instruction) == 0:          # Empty line (?)
            return None
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

    def reset_parser(self, filename):
        self.fin = open(filename, 'r')           # create a fileobject
        self.current_line = self.fin.readline()  # read the 1st line


class Code:
    """
    Translates Hack assembly language mnemonics into binary codes.
    """

    def __init__(self):
        # 8 possible 'destination' field combinations
        # self.d_to_binary = {"M": "100", "D": "010", "MD": "110",
        #                     "A": "001", "AM": "101", "AD": "011",
        #                     "AMD": "111", "NULL": "000"}
        self.d_to_binary = {"M": "001", "D": "010", "MD": "011",
                            "A": "100", "AM": "101", "AD": "110",
                            "AMD": "111", "NULL": "000"}

        # 28 possibilities for the 'comp' mnemonic in the C-command
        self.c_to_binary = {"0": "0101010", "1": "0111111",
                            "-1": "0111010", "D": "0001100", "A": "0110000",
                            "!D": "0001101", "!A": "0110001", "-D": "0001111",
                            "-A": "0110011", "D+1": "0011111",
                            "A+1": "0110111", "D-1": "0001110",
                            "A-1": "0110010", "D+A": "0000010",
                            "D-A": "0010011", "A-D": "0000111",
                            "D&A": "0000000", "D|A": "0010101",
                            "M": "1110000", "!M": "1110001", "-M": "1110011",
                            "M+1": "1110111", "M-1": "1110010",
                            "D+M": "1000010", "D-M": "1010011",
                            "M-D": "1000111", "D&M": "1000000",
                            "D|M": "1010101"}

        self.j_to_binary = {"NULL": "000", "JGT": "001", "JEQ": "010",
                            "JGE": "011", "JLT": "100", "JNE": "101",
                            "JLE": "110", "JMP": "111"}
        # self.j_to_binary = {"NULL": "000", "JGT": "100", "JEQ": "010",
        #                     "JGE": "110", "JLT": "001", "JNE": "101",
        #                     "JLE": "011", "JMP": "111"}


    def dest(self, mnemonic):
        """
        Returns the binary code of the 'dest' mnemonic.

        :param mnemonic:  string
        :return:           string
        """
        return self.d_to_binary[mnemonic]

    def comp(self, mnemonic):
        """
        Returns the binary code of the 'comp' mnemonic.

        :param mnemonic:  string
        :return:           string
        """
        return self.c_to_binary[mnemonic]

    def jump(self, mnemonic):
        """
        Returns the binary code of the 'jump' mnemonic.

        :param mnemonic:  string
        :return:           string
        """
        return self.j_to_binary[mnemonic]

class SymbolTable:
    """
    3 types of symbols: predefined symbols, labels, and variables.
    Variable: represents a memory location where programmer wants to maintain
              values; live in RAM.
    Label:    represent destinations of goto instructions
    Pre-defined symbol: represent special memory locations

    """

    def __init__(self):
        # Initialization
        # Initialize the symbol table with all the predeﬁned symbols and their
        # pre - allocated RAM addresses, according to section 6.2.3,
        # self.table = {"SP": str(bin(0)), "LCL": str(bin(1)),
        #               "ARG": str(bin(2)), "THIS" :str(bin(3)),
        #               "THAT":str(bin(4)),
        #               "R0": str(bin(0)), "R1": str(bin(1)),
        #               "R2": str(bin(2)), "R3": str(bin(3)),
        #               "R4": str(bin(4)), "R5": str(bin(5)),
        #               "R6": str(bin(6)), "R7": str(bin(7)),
        #               "R8": str(bin(8)), "R9": str(bin(9)),
        #               "R10": str(bin(10)), "R11": str(bin(11)),
        #               "R12": str(bin(12)), "R13": str(bin(13)),
        #               "R14": str(bin(14)), "R15": str(bin(15)),
        #               "SCREEN": str(bin(16384)),
        #               "KBD": str(bin(24576))}

        # Initialize the symbol table and add the pre-defined symbols.
        self.symbols = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
                        "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5,
                        "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10,
                        "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
                        "SCREEN": 16384, "KBD": 24576}
        # Keep track of the current loc in memory (instructions and vars)
        self.ROM_address = 0
        self.RAM_address = 16

    def add_entry(self, symbol, address):
        """
        Adds the pair (symbol, address) to the table.

        :param symbol:   string
        :param address:  int, in decimal
        :return:
        """
        self.symbols[symbol] = address

    def contains(self, symbol):
        """
        Does the symbol table contain the given symbol?

        :param symbol:  string
        :return:        True if contains, False otherwise.
        """
        return symbol in self.symbols

    def get_address(self, symbol):
        """
        Return the address associated with the symbol

        :param symbol: string
        :return:       int, in decimal
        """
        return self.symbols[symbol]

    def inc_ROM(self):
        self.ROM_address += 1

    def inc_RAM(self):
        self.RAM_address += 1

    def get_ROM(self):
        return self.ROM_address

    def get_RAM(self):
        return self.RAM_address


if __name__ == '__main__':

    code = Code()                  # translate mnemonics to binary
    symbol_table = SymbolTable()   # create and maintain the symbol table
    asm_file = "Rect.asm"

    # FIRST PASS: Add LABEL symbols, e.g.: @LABEL_SYMBOL.
    #             Go through the entire program, line by line, and build
    #             the symbol table without generating the code.
    parser = Parser(asm_file)

    while parser.has_more_commands():
        line = parser.get_current_line()
        instruction = parser.get_instruction(line)
        if instruction:
            type = parser.instruction_type(instruction)
            if type == "A_COMMAND" or type == "C_COMMAND":
                # Add 1 to ROM address when A- or C-command is encountered.
                symbol_table.inc_ROM()
            elif type == "L_COMMAND":
                symbol = parser.symbol(instruction, type)
                symbol_table.add_entry(symbol, symbol_table.get_ROM())

        parser.advance()

    # for key in symbol_table.symbols:
    #     print(key, symbol_table.get_address(key))

    # SECOND PASS: Add VARIABLE symbols.
    #              Go through the entire program. Each time a symbolic
    #              A-instruction is encoutered, @Xxx, where Xxx is a symbol,
    #              look up Xxx in symbol table.
    #              If the symbol is found, replace it with its numeric meaning
    #              and complete the command's translation.
    #              If the symbol is not found in the table, then it must
    #              represent a new variable. Add the pair (Xxx, n) to the
    #              symbol table, where n is the next available RAM address.
    #              Complete the command's translation.
    parser.reset_parser(asm_file)

    while parser.has_more_commands():
        line = parser.get_current_line()
        instruction = parser.get_instruction(line)
        if instruction:
            type = parser.instruction_type(instruction)
            if type == "A_COMMAND":
                symbol = parser.symbol(instruction, type)
                if not symbol.isdecimal():  # symbol is a variable symbol
                    if not symbol_table.contains(symbol):
                        symbol_table.add_entry(symbol, symbol_table.get_RAM())
                        symbol_table.inc_RAM()
        parser.advance()

    # for key in symbol_table.symbols:
    #     print(key, symbol_table.get_address(key))

    L_JUST = 20
    # 1. Open an output file.
    hack_file = asm_file[:-3] + "hack"
    fout = open(hack_file, "a")
    # 2. Iterate assembly instructions (lines)

    # For each C-instruction, concatenate the translated binary codes of the
    # instruction fields into a single 16-bit word.

    # For each A-instruction of type @Xxx, the program translates the
    # decimal constant returned by the parser into its binary representation
    # and writes the resulting 16-bit word into the prog.hack file.

    parser.reset_parser(asm_file)
    while parser.has_more_commands():
        line = parser.get_current_line()
        instruction = parser.get_instruction(line)
        if instruction:
            type = parser.instruction_type(instruction)
            if type == "A_COMMAND":
                symbol = parser.symbol(instruction, type)
                if not symbol.isdecimal(): # identifier, get address
                    symbol = symbol_table.get_address(symbol)
                symbol = str(bin(int(symbol)))[2:]  # remove '0b'
                symbol = symbol.zfill(15)  # 15-bit address value
                # symbol = list(symbol)
                # out_arr = list()
                # out_arr.extend(symbol[:3])  # add the first 3 bits
                # out_arr.append(" ")  # put a separator
                # count = 0
                # for i in range(3,
                #                len(symbol)):  # every 4 bits, separate
                #     if count == 4:
                #         out_arr.extend([" ", symbol[i]])
                #         count = 1
                #     else:
                #         out_arr.append(symbol[i])
                #         count += 1
                # symbol = "".join(out_arr)
                # output = '{}'.format(instruction.ljust(L_JUST))
                # fout.write(output)
                output = '0{}'.format(symbol)
                fout.write(output)
                fout.write('\n')
            # elif type == "L_COMMAND":
            #     symbol = parser.symbol(instruction, type)
            #     # output = '{} type: {}, symbol: {}'.format(
            #     # instruction.ljust(L_JUST), type, symbol)
            #     # fout.write(output)
            #     # fout.write('\n')
            #     output = '{}'.format(instruction.ljust(L_JUST))
            #     fout.write(output)
            #     output = '{}'.format(symbol)
            #     fout.write(output)
            #     fout.write('\n')
            elif type == "C_COMMAND":
                dest = parser.dest(instruction)
                comp = parser.comp(instruction)
                jump = parser.jump(instruction)

                d = code.dest(dest)
                c = code.comp(comp)
                j = code.jump(jump)

                # 3. C-instruction. Concatenate the translated binary codes
                # of the instruction fields into a single 16-bit word.
                #    A-instruction. Translate the decimal constant returned
                # by the parser into its binary representation.

                # output = '{}'.format(instruction.ljust(L_JUST))
                # fout.write(output)
                # output = '111{} {} {}{} {}{}'.format(c[0], c[1:5],
                #                                      c[5:], d[:2],
                #                                      d[2:], j)
                output = '111{}{}{}{}{}{}'.format(c[0], c[1:5],
                                                     c[5:], d[:2],
                                                     d[2:], j)
                # 4. Write the resulting 16-bit word into the 'Prog.hack'
                # file
                fout.write(output)
                fout.write('\n')

        parser.advance()

    fout.close()