import os
import sys
import string
#masks for registers and immediate
rs_mask = 0b00000011111000000000000000000000
rt_mask = 0b00000000000111110000000000000000
rd_mask = 0b00000000000000001111100000000000
imm_16_mask = 0b00000000000000001111111111111111

reg_map = {  #register hash table
	0:"$zero",
	1:"$at",
	2:"$v0",
	3:"$v1",
	4:"$a0",
	5:"$a1",
	6:"$a2",
	7:"$a3",
	8:"$t0",
	9:"$t1",
	10:"$t2",
	11:"$t3",
	12:"$t4",
	13:"$t5",
	14:"$t6",
	15:"$t7",
	16:"$s0",
	17:"$s1",
	18:"$s2",
	19:"$s3",
	20:"$s4",
	21:"$s5",
	22:"$s6",
	23:"$s7",
	24:"$t8",
	25:"$t9",
	26:"$k0",
	27:"$k1",
	28:"$gp",
	29:"$sp",
	30:"$fp",
	31:"$ra"
}

func_codes = {   #hash table for function codes
	0:"sll",
	2:"srl",
    8:"addi",
    33:"addu",
	32:"add",
	34:"sub",
    35:"subu",
	36:"and",
	37:"or",
	39:"nor",
	42:"slt",
    43:"sltu",
	}

opcodes = {  #hash table for opcodes
	0:"R",
	4:"beq",
	5:"bne",
	8:"addi",
    9:"addiu",
	10:"slti",
    11:"sltiu",
    34:"sub",
    16:"subu",
  	12:"andi",
	13:"ori",
	15:"lui",
    37:"lhu",
    36:"lbu",
	32:"lb",
	35:"lw",
	40:"sb",
    41:"sh",
	43:"sw"
	}

def get_func(inst): #get function code
    var = inst
    func = (var & 0b00000000000000000000000000111111)#using mask and returning value
    # print("func:", func)
    return func

def get_opcode(inst):#get opcode returns opcode
    var = inst
    opcode = (var & 0b11111100000000000000000000000000) >> 26#using mask and returning value
    # print("opcode:",opcode)
    return opcode
def get_imm(inst):
    tmp = inst
    imm = (tmp & imm_16_mask) #using mask and returning value
    return imm
def get_regs(inst): #return register vlaues from instruction by masks.
    tmp = inst

    rt_t = reg_map[(tmp & rt_mask) >> 16]
    # print("rt_t: " + str(rt_t))
    # rt = reg_map[rt_t]

    rs_t = reg_map[(tmp & rs_mask) >> 21]
    # print("rd_t: " + str(rs_t))
    # rs = reg_map[rs_t]
    # print("rs: " + str(rs))
    rd_t = reg_map[(tmp & rd_mask) >> 11]
    # print("rd_t: " + str(rd_t))
    # rd = reg_map[rd_t]
    # print("rd: " + str(rd))
    reg_tuple = (rd_t, rs_t, rt_t)
    return reg_tuple
def twos_complement(val):
    return -(val & 0x8000) | (val & 0x7fff)

def err(line,string,file_name,old_sys): #error function to print and close

    sys.stdout = old_sys # restoring sys.stdout value
    print("cannot disassemble string: " + string + " at line:" + str(line))
    if os.path.exists(file_name):
        os.remove(file_name)
    exit(1)
def is_hex(s):  #check if number is hex by type casting to int and if throw exception it's not
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def branch_is_neg(num):  #check if branch offset is negative
       shift = num >> 15  #shift to last bit
       if(shift == 0): #check last bit
           # print(bin(num) , " is not negative")
           return False

       else:
           # print(bin(num) , " is  negative")
           return True

def main():
    old_sys = sys.stdout # save previous stdout
    sys.stdout = open('%s' % sys.argv[1].replace('.obj','.s'), 'w') #open file to write output
    with open(sys.argv[1], 'r') as fi: # open file without worrying about closing it
        counter = 0    #counters for line numbers
        counter2 =0
        label_dict = {}

        file_name = sys.argv[1]  #save file name from input

        for l in fi:  #looping first time to get do error checking and
            hex = l.rstrip("\n\r") #get only the number without \n and \r
            if( is_hex(l) == False): #check if hex
                err(counter2,l,file_name.replace('.obj','.s'),old_sys)
            # print(len(hex))
            if (len(hex) !=8): #check length
                err(counter2, l, file_name.replace('.obj', '.s'), old_sys)
            opc = get_opcode(int(l,16))
            if opc not in opcodes: #check if opcode included
                err(counter2, l, file_name.replace('.obj', '.s'),old_sys)

            imm = get_imm(int(l,16)) #get imm to check branches
            if( opc == 4 or opc ==5): #if branch instruction check if neg and calculate where address should be.
                if (branch_is_neg(imm)):
                    offset = twos_complement(imm)  #get twos complement if < 0
                    # print("twos complement: " + str(offset))
                    final = counter2 * 4 +( offset * 4) +4
                    ine_res = counter2 + offset
                    if(ine_res <0):
                        ine_res +=1
                    # print (str(offset))
                    res = 'Address_{:04x}'.format(final) #format address correctly.
                    r = label_dict.get(ine_res, None)  #store in hash table if it doesnt exist there
                    if(r == None):
                     label_dict[ine_res] = res

                else:
                    final2 = (imm * 4) + (counter2 * 4) +4
                    line_res = (final2/4)
                    # print( " hello " + str(line_res))
                    # print(str(imm))
                    res = 'Address_{:04x}'.format(final2)
                    r = label_dict.get(line_res, None)
                    if (r == None):
                     label_dict[line_res] = res
                    # print(str(res))


            counter2+=1 #new page
        fi.seek(0) #after being done reset file cursor

        for line in fi:

           hex = int(line,16)  #store file name
           op = get_opcode(hex)  #get opcode
           func = get_func(hex)  #get function code
           regs = get_regs(hex)  #get register values
           imm = get_imm(hex)   #get immediate value
           shamt = (hex & 0b00000000000000000000011111000000) >> 6 # use mask to get the right value and shift

           r = label_dict.get(counter, None)  #check if current line has address to be printing and print it.
           if(r != None):
               print(label_dict[counter])

           if (op == 0 ):
               if func not in func_codes:  #check if func exists. error checking
                   sys.stdout = old_sys
                   print(" func error at line:" + str(counter ) + "func code:" + func)
               else: # if op ==0  then print according to function code
                   if (func == 32 or func == 33 or func == 36 or func == 39  or func == 37 or func == 34 or func == 35 or func == 42 or func == 43 ):
                       print(func_codes[func] + " " + regs[0] + ", " + regs[1] + ", " +regs[2] )
                   elif( func == 0 or func == 2):
                       print(func_codes[func] + " " + regs[0] + ", " + regs[2]+ ", "+ str(shamt))
           elif (op == 4 or op == 5):#branch
               if(branch_is_neg(imm)):
                    offset = twos_complement(imm)
                    final =  counter*4 + offset*4 +4
                    # print (str(offset))
                    res = '{:04x}'.format(final)
                    # print (str(res))
                    print(opcodes[op] + " "  + regs[1] + ", " + regs[2] + ", Address_" + str(res))
               else:
                   final2 = (imm*4) + (counter*4) +4
                   # print(str(imm))
                   res = '{:04x}'.format(final2)
                   print(opcodes[op] + " " + regs[1] + ", " + regs[2] + ", Address_" + str(res))
           elif ( op == 15):# immediate
               res = '{:02x}'.format(imm)
               print(opcodes[op] + " " + regs[2] + ", "  + str(imm))
           elif ( op == 42  ):
               print(func_codes[func] + " " + regs[0] + ", " + regs[1] + ", " + regs[2])
           elif ( op == 40 or op == 41 or op == 43 or op == 35 ):
               print(opcodes[op] + " " + regs[2] + "," + " " +  str(imm) + "(" + regs[1] + ")")
           elif ( op == 36 or op == 37  ):
               print(opcodes[op] + " " + regs[2] + "," + " " + str(imm) + "(" + regs[1] + ")")

           elif ( op == 13 or op == 14 or  op == 12 or op == 8):
               print(opcodes[op] + " " + regs[2] + ", " + regs[1] + ", " + str(imm))
           counter += 1

if __name__ == "__main__":
    main()