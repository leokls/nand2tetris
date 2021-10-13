// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(START)
    @0
    D=A
    @R0
    M=D       // R0 holds the value of 0, 16384 + R0 will be serviced next.
    
    @24576    // RAM[24576] holds the ASCII-value of the pressed key. 
    D=M
    @BLACKSCREEN
    D;JNE
    @WHITESCREEN
    0;JMP

(BLACKSCREEN)    
    @R0       
    D=M
    @SCREEN   // Starts at 16384 and will service the next 8191 bytes.
    A=A+D     // Go to the next unserviced memory location.
    M=-1      // All 16 bits are set to 1, i.e., to the color BLACK.  
    
    @R0
    M=M+1     // Keep track of the serviced memory locations. 
    
    @8191
    D=A-D    
    @BLACKSCREEN
    D;JGT     // If 8191 - serviced byte # > 0, goto BLACKSCREEN
    
    @START
    0; JMP    // Otherwise, goto START
    
(WHITESCREEN)
    @R0       
    D=M
    @SCREEN   // Starts at 16384 and will service the next 8191 bytes.
    A=A+D     // Go to the next unserviced memory location.
    M=0       // All 16 bits are set to 0, i.e., to the color WHITE.      
    
    @R0
    M=M+1     // Keep track of the serviced memory locations. 
    
    @8191
    D=A-D    
    @WHITESCREEN
    D;JGT     // If 8191 - serviced byte # > 0, goto BLACKSCREEN
    
    @START
    0; JMP    // Otherwise, goto START
    
    

