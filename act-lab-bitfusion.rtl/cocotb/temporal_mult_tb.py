import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random
from common import DWTB, DWDriver, random_data_gen, DWMonitor
import swizzle

import numpy as np

class TemporalMultTB(DWTB):

    def __init__(self, dut, signed=False):
        DWTB.__init__(self, dut)

        dut.a <= 0
        dut.b <= 0
        dut.a_sign_mode <= 0
        dut.b_sign_mode <= 0

        dut.sel <= 1

        dut.shift <= 0

        self.a_prec = int(dut.A_WIDTH.value)
        self.b_prec = int(dut.B_WIDTH.value)

        self.max_precision = int(dut.MAX_PRECISION.value.integer)

        self.log = self.dut._log
        self.log.info('Testing temporal multiplier with {0}-bit x {1}-bit low precision multiplier'.format(self.a_prec, self.b_prec))
        self.log.info('Max precision supported: {0}-bit'.format(self.max_precision))

    def get_inputs(self, precision):
        """
        Generate random inputs
        """
        return random.randint(-1*(1<<precision-1), (1<<precision-1)-1)

    @cocotb.coroutine
    def start (self):
        self.dut._log.info('Highest supported precision: {}'.format(self.max_precision))
        self.dut._log.info('Lowest supported precision for A: {}'.format(self.a_prec))
        self.dut._log.info('Lowest supported precision for B: {}'.format(self.b_prec))
        num_a_modes = int(math.log(self.max_precision // self.a_prec) / math.log(2)) + 1
        num_b_modes = int(math.log(self.max_precision // self.b_prec) / math.log(2)) + 1
        num_modes = num_a_modes * num_b_modes
        self.dut._log.info('Number of a modes          : {}'.format(num_a_modes))
        self.dut._log.info('Number of b modes          : {}'.format(num_b_modes))
        self.dut._log.info('Number of modes            : {}'.format(num_modes))
        modes = []
        for i in range(num_a_modes):
            a_prec = (2**i)*self.a_prec
            for j in range(num_b_modes):
                b_prec = (2**j)*self.b_prec
                modes.append((a_prec, b_prec))

        for test in range(1000):
            mode_idx = random.randint(0, num_modes-1)
            a_prec, b_prec = modes[mode_idx]
            self.log.debug('Op A precision: {}; Op B precision: {}'.format(a_prec, b_prec))
            a = self.get_inputs(a_prec)
            b = self.get_inputs(b_prec)
            self.log.debug('A : {}; B : {}'.format(a, b))

            a_cycles = int(a_prec // self.a_prec)
            b_cycles = int(b_prec // self.b_prec)
            num_cycles = a_cycles * b_cycles

            if test == 0:
                sel = 1
                prev_expected_output = 0
            else:
                sel = random.randint(0, 1)
                prev_expected_output = expected_output

            if sel == 0:
                expected_output += a * b
            else:
                expected_output = a * b

            # minimum precision out of a and b
            min_prec = min(self.a_prec, self.b_prec)
            self.log.debug('Multiplying {0} x {1}'.format(a, b))
            self.log.debug('Precision: {0}-bit x {1}-bit'.format(a_prec, b_prec))
            if sel == 0:
                op = 'MACC'
            else:
                op = 'MULT'
            self.log.debug('Op: {}'.format(op))
            self.log.debug('Expected output: {0}'.format(expected_output))

            for i in range(a_cycles):
                i_mult = 2**(i*self.a_prec)
                a_slice = int(a // i_mult) % (2**self.a_prec)
                if i == a_cycles - 1 and a < 0:
                    a_slice -= 2**self.a_prec
                    a_mode = 1
                else:
                    a_mode = 0
                for j in range(b_cycles):
                    j_mult = 2**(j*self.b_prec)
                    b_slice = int(b // j_mult) % (2**self.b_prec)
                    if j == b_cycles - 1 and b < 0:
                        b_slice -= 2**self.b_prec
                        b_mode = 1
                    else:
                        b_mode = 0

                    if i!=0 or j!=0:
                        sel = 0

                    a_shift = i * int(self.a_prec // min(self.a_prec, b_prec))
                    b_shift = j * int(self.b_prec // min(self.a_prec, b_prec))
                    shift = a_shift + b_shift

                    self.dut.shift <= shift

                    self.dut.sel <= sel
                    self.dut.a <= a_slice
                    self.dut.a_sign_mode <= a_mode
                    self.dut.b <= b_slice
                    self.dut.b_sign_mode <= b_mode

                    expected_slice_output = a_slice * b_slice

                    yield RisingEdge(self.dut.clk)

                    received_slice_output = self.dut.mult_out.value.signed_integer
                    if received_slice_output != expected_slice_output:
                        self.log.warn('Expected A: {}, B: {}'.format(a_slice, b_slice))
                        self.log.warn('Received A: {}, B: {}'.format(self.dut.a.value.signed_integer, self.dut.b.value.signed_integer))
                        self.log.warn('Mode A: {}, B: {}'.format(self.dut.a_sign_mode.value.integer, self.dut.b_sign_mode.value.integer))
                        self.log.warn('Extended A: {}, B: {}'.format(self.dut.a_extended.value.signed_integer, self.dut.b_extended.value))
                        self.log.warn('Mult A: {}, B: {}'.format(self.dut.signed_mult_inst.in_0.value.signed_integer, self.dut.signed_mult_inst.in_1.value.signed_integer))
                        self.log.warn('Received: {}, Expected: {}'.format(received_slice_output, expected_slice_output))
                    assert received_slice_output == expected_slice_output

                    if i == 0 and j == 0:
                        received_output = self.dut.out.value.signed_integer
                        assert prev_expected_output == received_output
