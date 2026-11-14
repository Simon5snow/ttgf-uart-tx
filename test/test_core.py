from __future__ import annotations

import cocotb
from cocotb.simtime import get_sim_time
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge, ClockCycles, ValueChange, First
import encoder
import random


CLOCK_CYCLE = 50e6
PERIOD_CLOCK_ps = round((1/CLOCK_CYCLE)*1e12)

o_to_send_1 = ["O","K"]
o_to_send_2 = ["K", "O"]

list_O_1 = [("set","tx",0),("set","osr",ord(o_to_send_1[0])), ("set", "n",429), ("set", "x", 7), ("start_loop_1",), ("jmp", "n", "start_loop_1"), ("bitloop1",), ("out", "tx", 1), ("set", "n", 430), ("in_loop_1",), ("jmp", "n", "in_loop_1"), ("jmp", "x", "bitloop1"), ("set", "tx", 1), ("set", "n", 431), ("end_loop_1",), ("jmp", "n", "end_loop_1"), ("set","tx",0),("set","osr",ord(o_to_send_1[1])), ("set", "n",429), ("set", "x", 7), ("start_loop_2",), ("jmp", "n", "start_loop_2"), ("bitloop2",), ("out", "tx", 1), ("set", "n", 430), ("in_loop_2",), ("jmp", "n", "in_loop_2"), ("jmp", "x", "bitloop2"), ("set", "tx", 1), ("set", "n", 431), ("end_loop_2",), ("jmp", "n", "end_loop_2"), ('infinite_loop',), ("set", "n", 1), ("jmp", "n", "infinite_loop"), ]
list_O_2 = [("set","tx",0),("set","osr",ord(o_to_send_2[0])), ("set", "n",429), ("set", "x", 7), ("start_loop_1",), ("jmp", "n", "start_loop_1"), ("bitloop1",), ("out", "tx", 1), ("set", "n", 430), ("in_loop_1",), ("jmp", "n", "in_loop_1"), ("jmp", "x", "bitloop1"), ("set", "tx", 1), ("set", "n", 431), ("end_loop_1",), ("jmp", "n", "end_loop_1"),("set", "tx", 1), ("set", "n", 428), ("set", "x", 1), ("set", "x", 3), ("set", "x", 4), ("mid_loop",), ("jmp", "n", "mid_loop"), ("set","tx",0),("set","osr",ord(o_to_send_2[1])), ("set", "n",429), ("set", "x", 7), ("start_loop_2",), ("jmp", "n", "start_loop_2"), ("bitloop2",), ("out", "tx", 1), ("set", "n", 430), ("in_loop_2",), ("jmp", "n", "in_loop_2"), ("jmp", "x", "bitloop2"), ("set", "tx", 1), ("set", "n", 431), ("end_loop_2",), ("jmp", "n", "end_loop_2"), ('infinite_loop',), ("set", "n", 1), ("jmp", "n", "infinite_loop"), ]
list_instr_1 = encoder.encode_full_program(list_O_1)
list_instr_2 = encoder.encode_full_program(list_O_2)

    
@cocotb.test(timeout_time=(len(o_to_send_1)+1)*434*10*PERIOD_CLOCK_ps, timeout_unit="ps")
async def load_and_run(tb):

    tb.loading.value = 0
    tb.strobe.value = 0
    tb.ena.value = 1

    Clock(tb.clk, PERIOD_CLOCK_ps, "ps").start()
    Load = cocotb.start_soon(load_imem(tb, list_instr_1))
    cocotb.start_soon(test_timing(tb))

    Receive = cocotb.start_soon(receive_value(tb, o_to_send_1))

    await Receive

@cocotb.test(timeout_time=(3*len(o_to_send_1)+1)*434*10*PERIOD_CLOCK_ps, timeout_unit="ps")
async def test_strobe_parasite(tb):

    tb.ena.value = 1

    Clock(tb.clk, PERIOD_CLOCK_ps, "ps").start()
    Load = cocotb.start_soon(load_imem(tb, list_instr_1))
    Receive = cocotb.start_soon(receive_value(tb, o_to_send_1))

    await FallingEdge(tb.tx)

    for i in range(5):
        await Timer(PERIOD_CLOCK_ps+random.randint(0,PERIOD_CLOCK_ps), "ps")
        tb.strobe.value=1
        tb.instr_to_load.value = random.randint(1,500) ##garantie différent car l'opcode 00 n'existe pas
        await Timer(PERIOD_CLOCK_ps+1, "ps")
        tb.strobe.value=0
        await Timer(PERIOD_CLOCK_ps*5, "ps")

    await Receive

    await FallingEdge(tb.clk)
    tb.rst_n.value = 0
    await FallingEdge(tb.clk)
    tb.rst_n.value = 1

    Receive2 = cocotb.start_soon(receive_value(tb, o_to_send_1))

    await Receive2
    

@cocotb.test(timeout_time=(3*len(o_to_send_1)+1)*434*10*PERIOD_CLOCK_ps, timeout_unit="ps")
async def reload_test(tb):

    tb.ena.value = 1

    Clock(tb.clk, PERIOD_CLOCK_ps, "ps").start()
    cocotb.start_soon(load_imem(tb, list_instr_1))

    await FallingEdge(tb.tx)

    tb.strobe.value = 1
    await Timer(PERIOD_CLOCK_ps+10, "ps")
    tb.strobe.value = 0
    await Timer(PERIOD_CLOCK_ps*5, "ps")


    cocotb.start_soon(load_imem(tb, list_instr_2,rst_n=False))


    Receive = cocotb.start_soon(receive_value(tb, o_to_send_2))

    await Receive

async def test_timing(tb): ##test timing regarde si la transition est correcte lorsque que l'on envoie deux octets d'affilé mais renvoie une erreur si on les envoie avec undélai il faudrait l'activer qu'à certain moment lors des envois.
    await RisingEdge(tb.rst_n)
    await FallingEdge(tb.tx)


    t_debut = get_sim_time(unit="ps")
    while True:
        await ValueChange(tb.tx)
        assert ((get_sim_time(unit="ps")-t_debut))%(434*PERIOD_CLOCK_ps)==0, f"BAD TIMING, erreur dans la trame {((get_sim_time(unit="ps")-t_debut)/PERIOD_CLOCK_ps)//4340+1} bit {((((get_sim_time(unit="ps")-t_debut)/PERIOD_CLOCK_ps)%4340)//434)} counter {(get_sim_time(unit="ps")-t_debut)}"

async def receive_value(tb, o_to_send):
    
    for k in range(len(o_to_send)): 
        result=0   
        await FallingEdge(tb.tx)

        await ClockCycles(signal=tb.clk, num_cycles=217, rising=False)
        assert int(tb.tx.value)==0, f"TX= {int(tb.tx.value)}"
        
        
        for i in range(8):
            await ClockCycles(signal=tb.clk, num_cycles=434, rising=False)
            result += int(tb.tx.value)*2**i
        assert result ==ord(o_to_send[k]), f"reçu : {result}, attendu : {ord(o_to_send[k])}"
        
        await ClockCycles(signal=tb.clk, num_cycles=434, rising=False)
        assert int(tb.tx.value)==1, "TX pas à 1"

        test_falling = FallingEdge(tb.tx)
        test_length = ClockCycles(signal=tb.clk, num_cycles=217, rising=False) ##les 2 tests ne peuvent arriver en même temps car il se déclenche lors de front différents de l'horloge. 
        res = await First(test_falling, test_length)
        assert res==test_length, f"erreur de timing sur le bit final, trame {k+1}"

async def load_imem(tb, mots, rst_n=True):

    if rst_n:
        await FallingEdge(tb.clk)
        tb.rst_n.value = 0    
        await FallingEdge(tb.clk)
        tb.rst_n.value = 1

    tb.loading.value = 1

    
    for i in range(len(mots)):
        tb.instr_to_load.value = mots[i]
        tb.strobe.value = 1
        await Timer(PERIOD_CLOCK_ps+random.randint(0,1000), "ps")
        tb.strobe.value = 0
        await Timer(PERIOD_CLOCK_ps*5+random.randint(0,1500), "ps")


    await Timer(PERIOD_CLOCK_ps*5+random.randint(0,1500), "ps")
    tb.loading.value = 0
    start = get_sim_time(unit="ps")
    await FallingEdge(tb.tx)
    assert 2<=(get_sim_time(unit="ps")-start)/PERIOD_CLOCK_ps<=3, f"L'écart est {(get_sim_time(unit="ps")-start)/PERIOD_CLOCK_ps} c'est en dehors des bornes"
