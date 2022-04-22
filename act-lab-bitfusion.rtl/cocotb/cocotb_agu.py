import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random
import numpy as np

from common import DWTB, DWDriver, random_data_gen, DWMonitor, np_array_to_signal, signal_to_np_array
import swizzle
from spatial_mult_tb import SpatialMultTB

random.seed(0)
np.random.seed(0)

class ControllerTB(DWTB):
    def __init__(self, dut):
        DWTB.__init__(self, dut)
        self.log = self.dut._log

        self.dut.start <= 0
        self.dut.reset <= 0

    @cocotb.coroutine
    def test(self):
        yield RisingEdge(self.clk)


@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = ControllerTB(dut)
    yield tb.clk_rst_gen()
    for i in range(10):
        yield tb.test()


