# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import random

from common import DWTB, DWDriver, random_data_gen, DWMonitor
from systolic_array import SystolicArrayTB

@cocotb.test()
def run_test(dut):
    """Test Main file"""
    tb = SystolicArrayTB(dut)
    yield tb.clk_rst_gen()

    dut.reset <= 1
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    dut.reset <= 0

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)

    yield tb.start()

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
