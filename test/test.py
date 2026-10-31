# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge

BAUD_RATE = 115200
BIT_CYCLE = int(1e9//BAUD_RATE)
test = [0x55,0xA3, 0x00, 0xFF, 0x01]


TIMEOUT_TIME= (len(test)+1)*90+200


@cocotb.test(timeout_time=TIMEOUT_TIME, timeout_unit="us")
async def test_project(tb):
    tb._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    tb.clk.value = 0
    tb.ui_in.value = 0x00
    tb.uio_in.value = 0x00

    Clock(tb.clk, 20, "ns").start()    
    cocotb.start_soon(give_values(tb))

    test = [0x55,0xA3, 0x00, 0xFF, 0x01]


    for k in range(len(test)):    
        result=0

        await FallingEdge(tb.tx)
        await Timer(BIT_CYCLE//2, unit="ns")
        assert tb.tx.value==0, f"out= {int(tb.tx.value)}"
        for i in range(8):
            
            await Timer(BIT_CYCLE, unit="ns")
            result += (int(tb.tx.value)*(2**i))
            tb._log.info(f"Reçu {int(tb.tx.value)}")

        assert result == test[k], f"reçu {result:#04x}, attendu {test[k]:#04x}"
        
        await Timer(BIT_CYCLE, unit="ns")
        assert tb.tx.value==1, f"out= {int(tb.tx.value)}"





async def give_values(tb):

    
    await FallingEdge(tb.clk)
    tb.rst_n.value = 0
    await FallingEdge(tb.clk)
    tb.rst_n.value = 1

    test = [0x55,0xA3, 0x00, 0xFF, 0x01]

    for k in range(len(test)):
        await FallingEdge(tb.busy)
        
        tb.ui_in.value = test[k]
        tb.uio_in.value = 1
        await RisingEdge(tb.clk)
        await FallingEdge(tb.clk)
        tb.uio_in.value = 0
