// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
//    @0     // Set R0 to value2.
//    D=A
//    @R0
//    M=D
    
//    @5     // Set R1 to value. 
//    D=A
//    @R1
//    M=D 
    
    // Edge cases: If R0 or R1 is 0, set R2 to 0 and exit.
    @R0    
    D=M
    @R2TOZERO
    D;JEQ
    
    @R1    
    D=M
    @R2TOZERO
    D;JEQ
    
    // Main
    
    @R0
    D=M    // D <- R0
    
    @R2    
    M=D    // R2 <- R0
    
    @R1    // Decrement R1 by 1.
    M=M-1  
    D=M
    
    @END
    D;JLE  // Exit if D <= 0
    
    // Loop that repeats addition
    
(ADD)

    @R0
    D=M
    
    @R2
    M=M+D
 
    @R1     
    M=M-1  
    D=M
    
    @END
    D;JLE
    
    @ADD
    0;JMP
    
    // Edge cases: sets R2 to 0.
    
(R2TOZERO)
    
    @R2
    M=0    
    
(END)

    @END
    0;JMP         // Infinite loop
    
