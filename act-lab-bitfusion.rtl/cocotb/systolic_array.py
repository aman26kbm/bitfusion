# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import random

from common import DWTB, DWDriver, random_data_gen, DWValidMonitor, ceilAByB, FIFO, np_array_to_signal
from spatial_mult_tb import SpatialMult

import math
import numpy as np

random.seed(0)
np.random.seed(0)

class SystolicArray(object):

    def __init__(self, hp, lp, N, M):
        self.high_prec = hp
        self.low_prec = lp
        self.N = N
        self.M = M
        self.spatial_mult = SpatialMult(self.high_prec, self.low_prec)
        self.wgt_swizzle = self.spatial_mult.b_swizzle

    def get_input_activations(self, prec, count):
        inputs = []
        for j in range(count):
            inputs.append(random.randint(-1*(1<<(prec-1)), 1<<(prec-1)-1))
        return inputs

    def get_input_weights(self, prec, count):
        weights = []
        for i in range(count):
            weights.append(random.randint(-1*(1<<(prec-1)), 1<<(prec-1)-1))
        return weights


class SystolicArrayTB(DWTB):

    def __init__(self, dut):
        DWTB.__init__(self, dut)
        self.high_prec = self.dut.PMAX.value.integer
        self.low_prec = self.dut.PMIN.value.integer
        self.N = self.dut.ARRAY_N.value.integer
        self.M = self.dut.ARRAY_M.value.integer
        self.num_prec = int(math.log(self.high_prec/self.low_prec) / math.log(2)) + 1
        self.systolic_array = SystolicArray(self.high_prec, self.low_prec, self.N, self.M)
        self.wgt_swizzle = self.systolic_array.spatial_mult.b_swizzle

        self.dut.activation_in <= 0;
        self.dut.weight_in <= 0;
        self.dut.acc_clear <= 1;
        self.dut.out_valid <= 0;

        self.dut.mode <= 0;

        self.act_out_mon = DWValidMonitor('Activation Out Monitor', self.dut.activation_out, self.dut.activation_valid, self.dut.clk, callback=self.push_rcv_out)

        self.rcv_fifo = FIFO(10000, BinaryValue)
        self.exp_fifo = FIFO(10000, BinaryValue)

    def push_rcv_out (self, data):
        valid = self.dut.systolic_out_valid.value.integer
        accumulate_prec = self.dut.ACCUMULATOR_WIDTH.value.integer
        max_val = (1<<accumulate_prec)
        for i in range(self.M):
            if valid == (1<<i):
                mult = (1 << (i*accumulate_prec))
                val = int(data/mult) % max_val
                if val > (max_val >> 1):
                    val -= max_val
                self.rcv_fifo.push(val)

    def get_mode(self, a_prec, b_prec):
        return self.systolic_array.spatial_mult.get_mode(a_prec, b_prec)

    def get_input_activations(self, prec, count):
        return self.systolic_array.get_input_activations(prec, count)

    def get_input_weights(self, prec, count):
        return self.systolic_array.get_input_weights(prec, count)

    def activation_repeat(self, l, l_prec, other_prec, num):
      """
      Takes an array of inputs and transforms it as follows:
      Each row has num_consecutive = high_prec/l_prec elements
      Each column has other_prec/l_prec elements,
      """
      num_op = len(l) / num
      num_consecutive = self.high_prec / l_prec
      num_strided = num_op / num_consecutive
      num_repeat = other_prec / self.low_prec

      out_arr = np.empty(len(l) * num_repeat)

      idx = 0
      for k in range(num):
        for j in range(num_strided):
          for r in range(num_repeat):
            for i in range(num_consecutive):
              curr = l[i+j*num_consecutive +k*num_consecutive * num_strided]
              out_arr[idx] = curr
              idx += 1
              # print curr,
            # print
        # print

      return out_arr

    def weight_repeat(self, l, l_prec, other_prec, num):
      """
      Takes an array of inputs and transforms it as follows:
      Each row has num_consecutive = high_prec/l_prec elements
      Each column has other_prec/l_prec elements,
      """
      num_op = len(l) / num
      num_consecutive = self.high_prec / l_prec
      num_strided = num_op / num_consecutive
      num_repeat = other_prec / self.low_prec

      out_arr = np.empty(len(l) * num_repeat)

      idx = 0
      mode = "{}x{}".format(other_prec, l_prec)
      sw = self.wgt_swizzle[mode]
      for k in range(num):
          for i in sw:
            curr = l[i + k * num_consecutive * self.high_prec / other_prec]
            out_arr[idx] = curr
            idx += 1
            # print curr,
          # print

      return out_arr

    @cocotb.coroutine
    def feed_data(self, act, act_prec, wgt, wgt_prec):

        for oc in range(act.shape[0]):
            for ic in range(act.shape[1]):

                # print 'Getting Activations: '
                _a = np_array_to_signal(self.activation_repeat(act[oc, ic, :], act_prec, wgt_prec, self.N), act_prec)
                # print 'Getting Weights: '
                # print wgt[oc, ic, :]
                _w = np_array_to_signal(self.weight_repeat(wgt[oc, ic, :], wgt_prec, act_prec, self.N * self.M), wgt_prec)

                self.dut.acc_clear <= 0
                self.dut.activation_in <= _a
                self.dut.weight_in <= _w

                if ic == act.shape[1] - 1 and self.dut.out_valid.value != 1:
                    self.dut.out_valid <= 1

                if ic == 0 and self.dut.acc_clear.value != 1:
                    self.dut.acc_clear <= 1

                yield RisingEdge(self.dut.clk)

                self.dut.out_valid <= 0
                self.dut.acc_clear <= 0


    def get_expected_output(self, act_in, wgt_in):
        assert len(act_in) == self.N
        assert len(wgt_in) == self.N * self.M

        tmp = 0
        for o in range(self.M):
          tmp = tmp << self.high_prec * 2
          for i in range(self.N):
            a_idx = i
            w_idx = o * self.N + i
            tmp += act_in[a_idx] * wgt_in[w_idx]

        return tmp

    def convert_fc_systolic(self, act, act_prec, wgt, wgt_prec):

        ops_per_cycle = self.high_prec * self.high_prec / (act_prec * wgt_prec)
        _NO, _NI = wgt.shape
        _N, _M = self.N * ops_per_cycle, self.M

        exp_out = np.empty((_NO, 1))
        for i in range(_NO):
            exp_out[(i, 0)] = np.dot(act[:, 0], wgt[i, :])


        imax = ceilAByB(_NI, _N * 1) + _N - 1 + _M - 1
        jmax = ceilAByB(_NO, _M)
        act_out = np.empty((jmax, imax, _N * 1), dtype=np.int32)
        wgt_out = np.empty((jmax, imax, _N * _M * 1), dtype=np.int32)

        # print act_out.shape, wgt_out.shape

        # if (act_prec < self.high_prec or wgt_prec < self.high_prec):
          # print jmax, imax

        for j in range(jmax):
            for i in range(imax):
                for ii in range(_N * 1):
                    idx = ((i-ii)*_N + ii, 0)
                    if idx[0] < 0 or idx[0] >= _NI or j >= ceilAByB(_NO, _M):
                        act_out[j, i, ii] = 0
                    else:
                        act_out[j, i, ii] = act[idx]

                for jj in range(_M):
                    for ii in range(_N * 1):
                        idx = (j*_M + jj, (i-ii-jj)*_N+ii)
                        if idx[0] < 0 or idx[0] >= _NO or idx[1] < 0 or idx[1] >= _NI:
                            wgt_out[j, i, ii + _N * jj] = 0
                            tmp = 0
                        else:
                            wgt_out[j, i, ii + _N * jj] = wgt[idx]
                            tmp = wgt[idx]
                        # print 'i: {}, jj: {} , ii: {}: W[{}, {}] = {}'.format(i, jj, ii, idx[1], idx[0], tmp)
                        # print '(i - ii - jj) * _N: {}'.format((i - ii - jj) * _N)

        # if (act_prec < self.high_prec or wgt_prec < self.high_prec):
          # print act_out, wgt_out

        return act_out, wgt_out, exp_out


    @cocotb.coroutine
    def start(self):
        self.dut._log.info('Highest supported precision: {}'.format(self.high_prec))
        self.dut._log.info('Lowest  supported precision: {}'.format(self.low_prec))
        self.dut._log.info('Systolic array dimensions  : {} x {}'.format(self.N, self.M))

        self.act_out_mon.start()

        num_tests = 10
        for i in range(num_tests):
            act_prec = (1 << random.randint(0, self.num_prec-1)) * self.low_prec
            wgt_prec = (1 << random.randint(0, self.num_prec-1)) * self.low_prec
            self.dut._log.info('Op A precision: {}; Op B precision: {}'.format(act_prec, wgt_prec))
            mode = self.get_mode(act_prec, wgt_prec)

            act_min = -1 * (1 << (act_prec-1))
            act_max = (1 << (act_prec-1)) - 1

            wgt_min = -1 * (1 << (wgt_prec-1))
            wgt_max = (1 << (wgt_prec-1)) - 1

            _NI = random.randint(1, 256)
            _NO = random.randint(1, 256)
            # _NI = 16
            # _NO = 16
            # _NI = 800
            # _NO = 800
            self.dut._log.info('FC dimensions: {} x {}'.format(_NI, _NO))
            act = np.random.random_integers(act_min, act_max, (_NI, 1))
            wgt = np.random.random_integers(wgt_min, wgt_max, (_NO, _NI))
            act_in, wgt_in, exp_out_list = self.convert_fc_systolic(act, act_prec, wgt, wgt_prec)

            # print act
            # print wgt

            # print act_in
            # print wgt_in

            for d in exp_out_list:
                self.exp_fifo.push(d[0])

            for i in range(ceilAByB(len(exp_out_list), self.M) * self.M - len(exp_out_list)):
                self.exp_fifo.push(0)

            self.dut.mode <= mode
            yield self.feed_data(act_in, act_prec, wgt_in, wgt_prec)

            yield RisingEdge(self.clk)

            while self.rcv_fifo.count < self.exp_fifo.count:
                yield RisingEdge(self.clk)

            oc = 0
            while not self.rcv_fifo.empty:
                rcv_out = self.rcv_fifo.pop()
                exp_out = self.exp_fifo.pop()
                if rcv_out != exp_out:
                    print 'Output number {}'.format(oc)
                    print '*'*50
                    print 'Activations: \n{}'.format(act[:])
                    # print 'Activations: \n{}'.format(act_in[oc,:,:])
                    print '*'*50
                    print '*'*50
                    print 'Weights: \n{}'.format(wgt[oc, :])
                    # print 'Weights: \n{}'.format(wgt_in[oc, :, :])
                    print '*'*50
                    print '*'*50
                    # print 'Expected Output: \n{}'.format(exp_out_list[oc])
                    print 'Expected Output: \n{}'.format(exp_out)
                    print 'Received Output: \n{}'.format(rcv_out)
                    print '*'*50
                    print exp_out
                    print rcv_out

                    print 'Expected accumulator inputs: '
                    for i in range(ceilAByB(act.shape[0], self.N)):
                        # for ii in range(self.N):
                        hi = (i+1)*self.N
                        lo = i*self.N
                        a_vec = act[lo:hi][:, 0]
                        w_vec = wgt[oc, lo:hi]
                        print a_vec
                        print w_vec
                        print np.dot(a_vec, w_vec)
                    assert rcv_out == exp_out
                oc += 1


        while not self.rcv_fifo.empty:
            rcv_out = self.rcv_fifo.pop()
            exp_out = self.exp_fifo.pop()
            print(rcv_out, exp_out)
            if rcv_out != exp_out:
                print 'fail'
