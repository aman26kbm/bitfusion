# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random

from common import DWTB, DWDriver, random_data_gen, DWMonitor
import swizzle
from spatial_mult_tb import SpatialMultTB

random.seed(0)

def random_int_gen(low, high, dlen):
    while True:
        yield BinaryValue(random.randint(low, high), dlen)

def print_val (x):
    print(x)

@cocotb.test()
def run_test(dut):
    """Test Main file"""
    dut._log.logger.setLevel(1)
    tb = SpatialMultTB(dut)
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
