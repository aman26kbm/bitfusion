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
np.random.seed(0)

def signal_to_np_array(signal, precision, signed=False):
    arr = np.empty((signal._bits / precision))
    for i in range(len(arr)):
        hi = (len(arr)-i)*precision-1
        lo = (len(arr)-i-1)*precision
        arr[i] = signal[lo:hi].integer
        if signed and arr[i] > (1<<(precision-1)):
          arr[i] -= 1<<precision
    return arr

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

class SpatialMultMux(object):
    def __init__(self, dut):
        self.dut = dut
        self.log = self.dut._log
        self.precision = self.dut.PRECISION.value.integer
        self.num_banks = self.dut.NUM_BANKS.value.integer
        self.num_precision_modes = int(math.log(self.num_banks) / math.log(2)) + 1

    @cocotb.coroutine
    def start(self):
        self.log.info('Spatial Mult Mux Test')

        for i in range(self.num_precision_modes):
          addr_range = self.num_banks >> i
          for a in range(addr_range):
            din = np.random.random_integers(0, (1<<self.precision)-1, (self.num_banks))
            dout = np.empty((self.num_banks))
            self.dut.data_in <= np_array_to_signal(din, self.precision)
            self.dut.precision_mode <= i
            self.dut.addr <= a
            for b in range(self.num_banks):
              idx = (a << i) + (b / (1<<(self.num_precision_modes - i - 1))),
              dout[b] = din[idx]
            yield Timer(2)

            rcv_dout = signal_to_np_array(self.dut.data_out.value, self.precision)
            for ii in range(len(dout)):
                assert dout[ii] == rcv_dout[ii]


@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = SpatialMultMux(dut)

    yield Timer(2)
    yield tb.start()
