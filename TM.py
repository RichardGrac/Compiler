class OPCLASS:
    def __init__(self):
        self.opclRR=0
        self.opclRM=1
        self.opclRA=2

class OPCODE:
    def __init__(self):
        self.opHALT=0
        self.opIN=1
        self.opOUT=2
        self.opADD=3
        self.opSUB=4
        self.opMUL=5
        self.opDIV=6
        self.opRRLim=7
        self.opLD=8
        self.opST=9
        self.opRMLim=10
        self.opLDA=11
        self.opLDC=12
        self.opJLT=13
        self.opJLE=14
        self.opJGT=15
        self.opJGE=16
        self.opJEQ=17
        self.opJNE=18
        self.opRALim=19

class STEPRESULT:
    def __init__(self):
        self.srOKAY=0
        self.srHALT=1
        self.srIMEM_ERR=2
        self.srDMEM_ERR=3
        self.srZERODIVIDE=4

class INSTRUCCION:
    def __init__(self,iop2,iarg12,iarg22,iarg32):
        self.iop=iop2
        self.iarg1=iarg12
        self.iarg2=iarg22
        self.iarg3=iarg32

class MACHINE:
    def __init__(self):
        self.IADDR_SIZE = 1024
        self.DADDR_SIZE = 1024
        self.NO_REGS = 8
        self.PC_REG = 7

        self.iMem=[]
        self.dMem=[]
        self.reg=[]
        self.opCodeTab = ["HALT", "IN", "OUT", "ADD", "SUB"
            , "MUL", "DIV", "????", "LD", "ST", "????", "LDA"
            , "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE"
            , "????"]
        self.stepResultTab = ["OK", "Halted", "Instruction Memory Fault",
                              "Data Memory Fault", "Division by 0"]
        self.archivoL = open("code.RJI", "r")

        for i in range(self.IADDR_SIZE):
            self.iMem.append(INSTRUCCION(0,0,0,0))

        for i in range(self.NO_REGS):
           self.reg.append(0)
        self.dMem.append(self.DADDR_SIZE-1)
        for i in range(self.DADDR_SIZE):
           self.dMem.append(0)
        A=OPCODE()
        for i in range(self.IADDR_SIZE):
            self.iMem[i].iop=A.opHALT
            self.iMem[i].iarg1=0
            self.iMem[i].iarg2 = 0
            self.iMem[i].iarg3 = 0

    def opClass(self,c):
        opcodeA=OPCODE()
        opclassB=OPCLASS()
        if(c<= opcodeA.opRRLim):
            return opclassB.opclRR
        elif(c<= opcodeA.opRMLim):
            return opclassB.opclRM
        else:
            return opclassB.opclRA

    def error(self,msg, lineNo, instNo):
        print("Line "+str(lineNo))
        if(instNo >= 0):
            print("(Instruccion "+str(instNo)+")")
        print(" "+str(msg)+"\n")


    def getOpCode(self, opcode):
        for i in range(len(self.opCodeTab)):
            if (self.opCodeTab[i] == opcode):
                return i
        return -1

    def strToNum(self,val):
        if(val.find('.') != -1):
            return float(val)
        return int(val)

    def readInstruction(self):
        op=0
        lineNo = 0

        ophalt=OPCODE()

        for linea in self.archivoL.readlines():
            lineNo += 1
            datos=linea.split(" ")
            loc= int(datos[0])

            if(loc > self.IADDR_SIZE):
                self.error("Location too large "+lineNo,loc)
            op=ophalt.opHALT
            if(self.getOpCode(datos[1])== -1):
                self.error("Ilegal opcode",lineNo,loc)
            else:
                op=self.getOpCode(datos[1])

            arg1=self.strToNum(datos[2])
            arg2=self.strToNum(datos[3])
            arg3=self.strToNum(datos[4])

            if(arg1<0 or arg1>=self.NO_REGS):
                self.error("Bad first register",lineNo,loc)

            if op<7:
                if(arg2<0 or arg2>=self.NO_REGS):
                    self.error("Bad second register",lineNo,loc)
            if(arg3<0 or arg3>=self.NO_REGS):
                self.error("Bad third register",lineNo,loc)
            self.iMem[loc].iop=op
            self.iMem[loc].iarg1=arg1
            self.iMem[loc].iarg2=arg2
            self.iMem[loc].iarg3=arg3

    def stepTM(self):
        pc=self.reg[self.PC_REG]
        opclass=OPCLASS()
        opcode=OPCODE()
        stepresult=STEPRESULT()

        if ((pc < 0) or (pc > self.IADDR_SIZE)):
            return stepresult.srIMEM_ERR

        self.reg[self.PC_REG] = pc + 1
        currentInstruction = self.iMem[pc]

        if(self.opClass(currentInstruction.iop)== opclass.opclRR):
            r=currentInstruction.iarg1
            s=currentInstruction.iarg2
            t=currentInstruction.iarg3
        elif(self.opClass(currentInstruction.iop)==opclass.opclRM):
            r=currentInstruction.iarg1
            s = currentInstruction.iarg3
            m=currentInstruction.iarg2+self.reg[s]
            if((m<0) or (m>self.DADDR_SIZE)):
                return stepresult.srDMEM_ERR
        elif(self.opClass(currentInstruction.iop)==opclass.opclRA):
            r=currentInstruction.iarg1
            s=currentInstruction.iarg3
            m=currentInstruction.iarg2+self.reg[s]

        if(currentInstruction.iop==opcode.opHALT):
            print("HALT:"+str(r)+" "+str(s)+" "+str(t)+"\n")
            return stepresult.srHALT
        elif(currentInstruction.iop==opcode.opIN):
            print("Por favor ingresa el valor para IN:")
            in_line=input()
            try:
                self.reg[r]=self.strToNum(in_line)

            except:
                print("TM Error: Ilegal value")

        elif(currentInstruction.iop==opcode.opOUT):
            print("OUTPUT -> "+ str(self.reg[r]))

        elif(currentInstruction.iop==opcode.opADD):
            self.reg[r]=self.reg[s]+self.reg[t]
        elif(currentInstruction.iop==opcode.opSUB):
            self.reg[r]=self.reg[s]-self.reg[t]
        elif(currentInstruction.iop==opcode.opMUL):
            self.reg[r]=self.reg[s]*self.reg[t]
        elif(currentInstruction.iop==opcode.opDIV):
            if(self.reg[t]!=0):
                self.reg[r]=self.reg[s]/self.reg[t]
            else:
                return stepresult.srZERODIVIDE
        elif(currentInstruction.iop==opcode.opLD):
            self.reg[r]=self.dMem[m]
        elif(currentInstruction.iop==opcode.opST):
            self.dMem[m]=self.reg[r]
        elif(currentInstruction.iop==opcode.opLDA):
            self.reg[r]=m
        elif(currentInstruction.iop==opcode.opLDC):
            self.reg[r]=currentInstruction.iarg2
        elif(currentInstruction.iop==opcode.opJLT):
            if(self.reg[r]<0):
                self.reg[self.PC_REG]=m
        elif(currentInstruction.iop==opcode.opJLE):
            if(self.reg[r]<=0):
                self.reg[self.PC_REG]=m
        elif(currentInstruction.iop==opcode.opJGT):
            if(self.reg[r]>0):
                self.reg[self.PC_REG]=m
        elif(currentInstruction.iop==opcode.opJGE):
            if(self.reg[r]>=0):
                self.reg[self.PC_REG]=m
        elif(currentInstruction.iop==opcode.opJEQ):
            if(self.reg[r]==0):
                self.reg[self.PC_REG]=m
        elif(currentInstruction.iop==opcode.opJNE):
            if(self.reg[r]!=0):
                self.reg[self.PC_REG]=m
        return stepresult.srOKAY

    def Run(self):
        a=STEPRESULT()
        stepResult=a.srOKAY
        while stepResult == a.srOKAY:
            stepResult=self.stepTM()


maquina= MACHINE()
maquina.readInstruction()
maquina.Run()

