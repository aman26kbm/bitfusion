# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random

import swizzle

from common import DWTB, DWDriver, random_data_gen, DWMonitor
from temporal_mult_tb import TemporalMultTB

random.seed(0)

def random_int_gen(low, high, dlen):
    while True:
        yield BinaryValue(random.randint(low, high), dlen)

@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = TemporalMultTB(dut, signed=True)
    yield tb.clk_rst_gen()

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)

    yield tb.start()

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
