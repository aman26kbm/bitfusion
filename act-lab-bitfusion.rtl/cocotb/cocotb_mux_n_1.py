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

class MuxNto1(object):
    def __init__(self, dut):
        self.dut = dut
        self.log = self.dut._log
        self.N = (1<<self.dut.LOG2_N.value.integer)
        self.precision = self.dut.WIDTH.value.integer

    @cocotb.coroutine
    def start(self):
        self.log.info('{}:1 Mux'.format(self.N))

        num_tests = 100
        for i in range(num_tests):
            sel = np.random.randint(0, self.N-1)
            np_data_in = np.random.random_integers(0, (1<<self.precision)-1, (self.N))
            data_in = np_array_to_signal(np_data_in, self.precision)

            self.log.debug('Value Sent = {}'.format(data_in))

            self.dut.data_in = data_in
            self.dut.sel = sel

            yield Timer(2)

            exp_out = np_data_in[sel]
            rcv_out = self.dut.data_out.value.integer
            self.log.debug('Input = {}'.format(np_data_in))
            self.log.debug('Output = {}'.format(rcv_out))
            self.log.debug('Expected Output = {}'.format(exp_out))
            assert (rcv_out == exp_out)


@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = MuxNto1(dut)

    yield Timer(2)
    yield tb.start()
