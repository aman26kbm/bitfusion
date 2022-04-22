# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import random

from common import DWTB, DWDriver, random_data_gen, DWMonitor

def random_int_gen(low, high, dlen):
    while True:
        yield BinaryValue(random.randint(low, high), dlen,
            binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT)

def print_val (x):
    print(x)

class LPMultTB(DWTB):

    def __init__(self, dut):

        DWTB.__init__(self, dut)

        self.dut.in_0 <= 0
        self.dut.in_1 <= 0
        self.dut.shift <= 0
        self.dut.sel <= 0

        self.in_0 = self.dut.in_0
        self.in_0_width = self.dut.IN_0_WIDTH.value
        self.in_0_driver = DWDriver("in_0", self.clk, self.dut.in_0, random_data_gen(self.in_0_width.value))
        self.in_0_mon = DWMonitor("in_0", self.dut.in_0, self.clk, callback=print_val)


        self.in_1 = self.dut.in_1
        self.in_1_width = self.dut.IN_1_WIDTH.value
        self.in_1_driver = DWDriver("in_1", self.clk, self.dut.in_1, random_data_gen(self.in_1_width.value))
        self.in_1_mon = DWMonitor("in_1", self.dut.in_1, self.clk, callback=print_val)

        self.acc_mon = DWMonitor("out", self.dut.out, self.clk, callback=print_val)

        self.mult_out = DWMonitor("mult_out", self.dut.mult_out, self.clk, callback=print_val)

    def start(self):
        self.in_0_driver.start()
        self.in_0_mon.start()
        self.in_1_driver.start()
        self.in_1_mon.start()
        self.acc_mon.start()
        self.mult_out.start()

@cocotb.test()
def run_test(dut):
    """Test Main file"""
    tb = LPMultTB(dut)
    yield tb.clk_rst_gen()

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)

    tb.start()

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
