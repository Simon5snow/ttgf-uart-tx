from pathlib import Path

dico_instruction = {"jmp" : "2'b01", "set" : "2'b11", "out" : "2'b10"}
dico_register = {"tx":(1, "2'b11"), "n":(9, "2'b10"), "osr":(8, "2'b00"), "x":(3, "2'b01")}

def generate_param():
    with open(Path(__file__).resolve().parent / "param.vh", 'w') as f:
        for instr,value in dico_instruction.items():
            f.write(f"localparam {instr} = {value};\n")
        
        for register,adress in dico_register.items():
            f.write(f"localparam adress_{register} = {adress[1]};\n")
            f.write(f"localparam width_{register} = {adress[0]};\n")




def encode_instruction(instruction, adress_jmp):
    if len(instruction)!=3:
        raise ValueError("BAD FORMAT FOR INSTRUCTION")
    result=0
    opcode = instruction[0]
    adress = instruction[1]
    data = instruction[2]

    if opcode=="out" and adress!="tx":
        raise ValueError("CAN ONLY OUT TX")
    


    if type(opcode)==str and opcode in dico_instruction:
        result += int(dico_instruction[opcode][-1])*2**11+int(dico_instruction[opcode][-2])*2**12
    else:
        raise ValueError("WRONG OPCODE")
    
    if type(adress)==str and adress in dico_register:
        result += int(dico_register[adress][1][-1])*2**9 + int(dico_register[adress][1][-2])*2**10
    else:
        raise ValueError("WRONG REGISTER ADRESS")
    
    if type(data)==int and 0<=data<(2**dico_register[adress][0]):
        result +=data
        return result

    if type(data)==str:
        if (data,) in adress_jmp:
            result += adress_jmp[(data,)]
        else:
            raise ValueError("WRONG JUMPING ADRESS")

    else:
        raise ValueError("INVALID DATA")

    return result


def encode_full_program(list_instruction):
    list_converted_instr=[]
    list_instruction_wo_jmp=[]
    adress_jmp={}
    shifter=0
    for i in range(len(list_instruction)):
        if len(list_instruction[i])==1:
            if list_instruction[i] not in adress_jmp:
                adress_jmp[list_instruction[i]]=i-shifter
                shifter+=1
            else :
                raise ValueError("TWO TIME THE SAME JUMPING LABEL")
        else:
            list_instruction_wo_jmp.append(list_instruction[i])

    if len(list_instruction_wo_jmp)>32:
        raise ValueError("TOO MANY INSTRUCTIONS")

    for instr in list_instruction_wo_jmp:
        list_converted_instr.append(encode_instruction(instr, adress_jmp))

    return list_converted_instr + [0*i for i in range(32-len(list_converted_instr))]

list_O = [("set","tx",0),("set","osr",79), ("set", "n",429), ("set", "x", 7), ("start_loop_1",), ("jmp", "n", "start_loop_1"), ("bitloop1",), ("out", "tx", 1), ("set", "n", 430), ("in_loop_1",), ("jmp", "n", "in_loop_1"), ("jmp", "x", "bitloop1"), ("set", "tx", 1), ("set", "n", 431), ("end_loop_1",), ("jmp", "n", "end_loop_1"), ('infinite_loop',), ("set", "n", 1), ("jmp", "n", "infinite_loop")]