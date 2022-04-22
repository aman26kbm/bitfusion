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
        self.dut.loop_wr_v <= 0
        self.dut.loop_wr_max_iter <= 0

    def get_addr(self, idx, stride):
        tmp = 0
        for i in range(len(idx)):
            tmp += idx[i] * stride[i]
        return tmp

    def print_controller_state(self):

        state = self.dut.state.value.integer
        if state == 0:
            state_msg = 'IDLE State'
        elif state == 1:
            state_msg = 'BUSY State'
        else:
            state_msg = 'STALL State'

        loop_max_count = self.dut.loop_rd_max.value
        rd_ptr = self.dut.iter_rd_ptr.value
        iter_rd_data = self.dut.iter_rd_data.value

        self.log.debug('{0:<20}'.format(state_msg))
        self.log.debug('LOOP PTR :{0:<20}'.format(rd_ptr))
        self.log.debug('LOOP MAX: {0:<20}'.format(loop_max_count))
        self.log.debug('LOOP ITER:{0:<20}'.format(iter_rd_data))

    @cocotb.coroutine
    def test(self):
        self.log.info('Controller TB')
        re_clk = RisingEdge(self.clk)
        yield re_clk

        count_len = np.random.randint(3, 6)
        max_count = []
        loop_count = []
        for c in range(count_len):
            max_count.append(np.random.randint(1, 4))
            loop_count.append(0)
        self.log.info('Testing {}'.format(max_count))

        useful_cycles = 1
        loop_offset = []
        loop_stride = []
        for c in max_count:
          loop_offset.append(0)
          loop_stride.append(useful_cycles)
          useful_cycles *= (c+1)

        expected_cycles = 1
        for c in max_count:
            expected_cycles = 2 + (c+1) * expected_cycles
        expected_cycles -= (len(max_count)+1)

        for i in range (len(max_count)):
            self.dut.loop_wr_v <= 1
            self.dut.loop_wr_max_iter <= max_count[i]
            self.dut.loop_wr_max_iter <= max_count[i]
            yield re_clk
            self.dut.loop_wr_v <= 0

        self.dut.start <= 1
        yield re_clk
        self.dut.start <= 0
        self.log.debug('*'*50)
        self.log.debug('Starting the FSM')
        self.log.debug('*'*50)


        total_cycles = 0

        read_idx = []

        addr = 0

        total_cycles = 0
        addr = 0
        prev_addr = 0
        prev_loop_offset = 0
        while not self.dut.done.value.integer == 1:
            self.log.debug('*'*50)
            self.print_controller_state()
            self.log.debug('*'*50)
            yield re_clk
            total_cycles += 1
            offset_index = self.dut.offset_index.value.integer
            if self.dut.offset_index_valid.value.integer == 1:
                if offset_index == 0:
                    addr += loop_stride[0]
                else:
                    loop_offset[offset_index] += loop_stride[offset_index]
                    addr = loop_offset[offset_index]
                    prev_loop_offset = loop_offset[offset_index]
                # Check if address are incrementing correctly
                assert addr == prev_addr + 1
                prev_addr = addr
            elif self.dut.state.value.integer == 3:
                loop_offset[offset_index] = prev_loop_offset

        yield re_clk
        self.log.info('Total Cycles: {0}; Useful Cycles: {1}'.format(total_cycles, useful_cycles))
        self.log.info('Expected Cycles: {0}'.format(expected_cycles))
        assert expected_cycles == total_cycles


@cocotb.test()
def run_test(dut):
    """Test Main file"""
    # dut._log.logger.setLevel(1)
    tb = ControllerTB(dut)
    yield tb.clk_rst_gen()
    for i in range(10):
        yield tb.test()
