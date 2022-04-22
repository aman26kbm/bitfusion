# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random
import numpy as np

from common import DWTB, DWDriver, random_data_gen, DWMonitor
import swizzle
from spatial_mult_tb import SpatialMultTB

random.seed(0)

def np_array_to_signal(arr, precision):
    b = BinaryValue(value=0, bits=precision*len(arr))
    for i in range(len(arr)):
        hi = (len(arr)-i)*precision-1
        lo = (len(arr)-i-1)*precision
        tmp = arr[i]
        if tmp < 0:
            val = bin(tmp + (1<<precision))[2:]
            val_ext = (precision-len(val))*'1'+val
        else:
            val = bin(tmp)[2:]
            val_ext = (precision-len(val))*'0' + val
        b[lo:hi] = val_ext
    return b

class SelGen(object):
    def __init__(self, dut):
        self.dut = dut
        self.log = self.dut._log
        self.num_banks = self.dut.NUM_BANKS.value.integer
        self.bank_id = self.dut.BANK_ID.value.integer
        self.max_mode = int(math.log(self.num_banks) / math.log(2)) + 1
        self.addr_range = 1 << self.dut.ADDR_WIDTH.value.integer

    @cocotb.coroutine
    def start(self):
        self.log.info('Sel Gen Test')
        self.log.info('Num Banks: {}'.format(self.num_banks))
        self.log.info('Bank ID: {}'.format(self.bank_id))
        self.log.info('Num Modes: {}'.format(self.max_mode))

        for i in range(self.max_mode):
            addr_range = self.addr_range / (1<<i)

            for a in range(addr_range):
                self.dut.addr <= a
                self.dut.precision_mode <= i
                yield Timer(2)
                self.log.info('Mode: {}, Address: {}, Sel Output: {}'.format(i, a, self.dut.sel.value.integer))



@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = SelGen(dut)

    yield Timer(2)
    yield tb.start()
