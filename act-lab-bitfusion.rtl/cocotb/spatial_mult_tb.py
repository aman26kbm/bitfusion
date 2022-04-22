import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue, BinaryRepresentation
import math
import random
from common import DWTB, DWDriver, random_data_gen, DWMonitor
import swizzle

import numpy as np

class SpatialMult(object):

  def __init__(self, hp, lp):
    self.high_prec = hp
    self.low_prec = lp
    self.b_swizzle = swizzle.get_swizzle(self.high_prec, self.low_prec)
    self.in_width = int(hp * hp / lp)

  def list_to_signal(self, l, precision, repeat, transpose=False):
    """
    converts a list of operands to signals through left shift
    0th operand is MSB
    """

    in_width = self.in_width
    s = 0
    x_width = self.high_prec
    num_x = x_width/precision
    num_y = len(l)/num_x
    repeat = in_width/num_y/num_x/precision

    for j in range(num_y):
      for r in range(repeat):
        for i in range(num_x):
          curr = l[i+j*num_x]
          if curr < 0:
            curr = curr + (1 << precision)
          s = (s << precision) + curr
    return s

  def pre_process_b(self, b, b_prec, a, a_prec):
    """
    pre-processing step for weights
    """
    mode = '{}x{}'.format(a_prec, b_prec)
    sw = self.b_swizzle[mode]
    b_swizzled = [b[i] for i in sw]
    return b_swizzled


  def get_mode(self, a_prec, b_prec):
    """
    Get the mode signal for the multiplier
    Mode at any level is a 2-bit signal that corresponds to {a_high/low, b_high/low}
    The MSB specifies if the 'a' operand is high-precision or low-precision
    The LSB specifies if the 'b' operand is high-precision or low-precision
    """
    lp = self.low_prec
    hp = self.high_prec

    curr_prec = int(hp/2)
    mode = 0
    while curr_prec >= lp:
      mode_a = 0 if a_prec > curr_prec else 1
      mode_b = 0 if b_prec > curr_prec else 1
      mode = (mode_a << 1) + mode_b + (mode << 2)
      curr_prec = int(curr_prec/2)

    return mode

class SpatialMultTB(DWTB):

    def __init__(self, dut, signed=False):
        DWTB.__init__(self, dut)

        dut.a <= 0
        dut.b <= 0
        dut.mode <= 0
        if signed:
            dut.prev_level_mode <= 0

        self.signed = signed

        self.high_prec = int(dut.PRECISION.value)
        self.low_prec  = int(dut.L_PRECISION.value)

        self.spatial_mult = SpatialMult(self.high_prec, self.low_prec)
        self.b_swizzle = self.spatial_mult.b_swizzle

        self.num_prec = int(math.log(self.high_prec/self.low_prec) / math.log(2)) + 1
        self.precision = int(dut.PRECISION.value)

        self.expected_outputs = None
        self.expected_inputs = {'a': None, 'b': None}

    def get_inputs(self, precision, count):
        """
        Generate random inputs
        """
        op = []
        if self.signed != True:
            for i in range(count):
                op.append(random.randint(0, (1<<precision)-1))
        else:
            for i in range(count):
                op.append(random.randint(-1*(1<<precision-1), (1<<precision-1)-1))
        return op


    @cocotb.coroutine
    def start (self):
        self.dut._log.info('Highest supported precision: {}'.format(self.high_prec))
        self.dut._log.info('Lowest  supported precision: {}'.format(self.low_prec))
        self.dut._log.info('Number of levels           : {}'.format(int(self.dut.NUM_LEVELS.value)))
        num_prec = self.num_prec
        num_modes = num_prec * num_prec
        self.dut._log.info('Number of modes            : {}'.format(num_modes))

        for i in range(1000):
            a_prec = (1 << random.randint(0, num_prec-1)) * self.low_prec
            b_prec = (1 << random.randint(0, num_prec-1)) * self.low_prec
            self.dut._log.debug('Op A precision: {}; Op B precision: {}'.format(a_prec, b_prec))
            mode = self.spatial_mult.get_mode(a_prec, b_prec)
            self.dut.mode <= mode
            self.dut._log.debug('Mode {}'.format(mode))

            count = self.precision * self.precision / (a_prec * b_prec)
            a_in = self.get_inputs(a_prec, count)
            b_in = self.get_inputs(b_prec, count)

            self.dut._log.debug('A: {}'.format(a_in))
            self.dut._log.debug('B: {}'.format(b_in))

            assert len(a_in) == len(b_in)

            expected_out = 0
            for i in range(len(a_in)):
                expected_out += a_in[i] * b_in[i]

            # Pre-processing B
            b_swizzled = self.spatial_mult.pre_process_b(b_in, b_prec, a_in, a_prec)

            a_repeat = int(self.dut.PRECISION.value) / b_prec
            b_repeat = int(self.dut.PRECISION.value) / a_prec
            # Convert list of operands to signal
            a = self.spatial_mult.list_to_signal(a_in, a_prec, a_repeat)
            b = self.spatial_mult.list_to_signal(b_swizzled, b_prec, b_repeat, True)

            self.dut.a <= a
            self.dut.b <= b

            yield(RisingEdge(self.clk))

            self.dut._log.debug('Got : {}'.format(self.dut.out.value))

            if self.signed:
                received_output = self.dut.out.value.signed_integer
            else:
                received_output = self.dut.out.value

            if int(received_output != expected_out):
            # if True:
                self.dut._log.info('A_precision: {}'.format(a_prec))
                self.dut._log.info('B_precision: {}'.format(b_prec))

                self.dut._log.info('A: {}'.format(a_in))
                self.dut._log.info('B: {}'.format(b_in))

                self.dut._log.info('Expected output: {}'.format(expected_out))
                self.dut._log.info('Received output: {}'.format(received_output))

                self.expected_out = self.get_expected_outputs(a_in, a_prec, b_in, b_prec, mode)
                self.check_received_vs_expected()

                raise TestFailure()

    def reduce_expected_outputs(self, out, prec, mode):

        prev_precision = prec
        current_precision = prec * 2

        previous_level = self.get_level(prev_precision)
        current_level = self.get_level(current_precision)
        out[current_level] = []

        irange = int(self.high_prec // prec)
        jrange = int(self.high_prec // prec)


        div = 4**(self.num_prec - current_level-2)
        curr_mode = int(mode / div)
        print(bin(curr_mode), bin(mode), div)

        # Generate weights for adding partial products
        a_mode = int(curr_mode / 2) % 2
        b_mode = curr_mode % 2
        weight = [1, 1, 1, 1]
        for ii in [1, 0]:
            for jj in [1, 0]:
                a_shift = (1 - b_mode) * ii * prec
                b_shift = (1 - a_mode) * jj * prec
                shift = a_shift + b_shift
                idx = jj + 2 * ii
                weight[idx] = 2**shift

        self.fancy_printer(weight)

        # Set the previous output to the previous level output
        prev_out = out[previous_level]

        # Generate weights for adding partial products
        for i in reversed(range(irange//2)):
            for j in reversed(range(jrange//2)):
                tmp = 0
                for ii in [1, 0]:
                    i_idx = ii + 2 * i
                    for jj in [1, 0]:
                        j_idx = jj + 2 * j
                        o_idx = j_idx + jrange * i_idx
                        idx = jj + 2 * ii
                        tmp += prev_out[o_idx] * weight[idx]
                out[current_level].insert(0, tmp)

        print('Output at level {}:'.format(current_level))
        self.fancy_printer(out[current_level])

        if prec < self.high_prec / 2:
            return self.reduce_expected_outputs(out, prec*2, mode)
        else:
            return out

    def get_level(self, prec):
        return int(math.log(self.high_prec / prec) / math.log(2))

    def fancy_printer(self, data, rev=False):
        """
        Fancy printer
        """
        xdim = int(math.sqrt(len(data)))
        ydim = int(len(data)/xdim)

        for i in reversed(range(ydim)):
            for j in reversed(range(xdim)):
                if rev:
                    idx = i + xdim * j
                else:
                    idx = j + xdim * i
                print '{:>6}'.format(data[idx]),
                if j!=0:
                    print ' | ',
            print
            if i != 0:
                print '-'*6*xdim + '-'*5*(xdim-1)
        print


    def get_expected_outputs(self, a, a_prec, b, b_prec, mode):
        """
        Print the expected inputs at each level
        """
        a_repeat = int(b_prec // self.low_prec)
        b_repeat = int(a_prec // self.low_prec)
        a_new = np.empty((self.high_prec//self.low_prec * self.high_prec//self.low_prec), dtype=np.int)
        b_new = np.empty((self.high_prec//self.low_prec * self.high_prec//self.low_prec), dtype=np.int)

        imax = self.high_prec // b_prec
        kmax = b_prec // self.low_prec
        jmax = self.high_prec // a_prec
        lmax = a_prec // self.low_prec
        for i in range(imax):
            for k in range(kmax):
                for j in range(jmax):
                    idx = len(a) - (i * self.high_prec // a_prec + j) - 1
                    tmp = a[idx]
                    for l in range(lmax):
                        mult = 2 ** (self.low_prec * l)
                        val = int(a[idx] // mult) % (2 ** self.low_prec)
                        if l == (a_prec // self.low_prec) - 1 and a[idx] < 0:
                            val -= int(2**self.low_prec)
                        new_idx = l + lmax * (j + jmax * (k + kmax * i))
                        a_new[new_idx] = val

        self.expected_inputs['a'] = a_new

        imax = self.high_prec // b_prec
        lmax = b_prec // self.low_prec
        jmax = self.high_prec // a_prec
        kmax = a_prec // self.low_prec
        for i in range(imax):
            for l in range(lmax):
                mult = 2 ** (self.low_prec * l)
                for j in range(jmax):
                    idx = len(a) - (i * self.high_prec // a_prec + j) - 1
                    for k in range(kmax):
                        val = int(b[idx] // mult) % (2 ** self.low_prec)
                        if l == (b_prec // self.low_prec) - 1 and b[idx] < 0:
                            val -= 2**self.low_prec
                        new_idx = k + kmax * (j + jmax * (l + lmax * i))
                        b_new[new_idx] = val

        self.expected_inputs['b'] = b_new

        irange = int(self.high_prec // self.low_prec)
        jrange = int(self.high_prec // self.low_prec)

        print('A')
        self.fancy_printer(a_new, rev=False)
        print('B')
        self.fancy_printer(b_new, rev=False)


        current_level = self.get_level(self.low_prec)
        out = {}
        out[current_level] = []

        for i in reversed(range(irange)):
            for j in reversed(range(jrange)):
                idx = j + jrange * i
                o = a_new[idx] * b_new[idx]
                out[current_level].insert(0, o)

        print('A x B')
        self.fancy_printer(out[current_level])

        prec = self.low_prec
        self.reduce_expected_outputs(out, prec, mode)

        return out

    def get_scope(self, i, j, scope=None, level=0, op='a', max_level=None):
        if scope is None:
            scope = self.dut
        if max_level is None:
            max_level = int(math.log(self.high_prec // self.low_prec) / math.log(2))

        if level < max_level:
            mult = 2**(self.num_prec-level-2)
            mult_i = int(i / mult)
            mult_j = int(j / mult)
            mult_ID = mult_j + 2 * mult_i
            if mult_ID == 0:
                return self.get_scope(i%mult, j%mult, scope=scope.LP_MULT_INST.m0, level=level+1, op=op, max_level=max_level)
            elif mult_ID == 1:
                return self.get_scope(i%mult, j%mult, scope=scope.LP_MULT_INST.m1, level=level+1, op=op, max_level=max_level)
            elif mult_ID == 2:
                return self.get_scope(i%mult, j%mult, scope=scope.LP_MULT_INST.m2, level=level+1, op=op, max_level=max_level)
            else:
                    return self.get_scope(i%mult, j%mult, scope=scope.LP_MULT_INST.m3, level=level+1, op=op, max_level=max_level)
        else:
            return scope

    def slice(self, xval, xlen):
        ret = []
        for i in range(xlen):
            ret.append(xval % (1<<self.low_prec))
            xval = int(xval // (1<<self.low_prec))
        return ret


    def check_received_vs_expected(self, scope=None, level=0, i_base=0, j_base=0):
        """
        Generate Warnings when the error detected
        args:
            scope: required to traverse the multiplier's hierarchy
            level: current level of hierarchy. 0 means top level
        """
        if scope is None:
            scope = self.dut

        if level == 0:
            self.dut._log.warn('Checking Inputs')
            a_val = self.dut.a.value.signed_integer
            a_len = (self.high_prec // self.low_prec) ** 2
            received_a = []
            received_b = []
            for i in range(self.high_prec // self.low_prec):
                for j in range(self.high_prec // self.low_prec):
                    received_a.append(self.get_scope(i, j).a_signed.value.signed_integer)
                    received_b.append(self.get_scope(i, j).b_signed.value.signed_integer)
            self.dut._log.warn('Received A:')
            self.fancy_printer(received_a)
            self.dut._log.warn('Expected A:')
            self.fancy_printer(self.expected_inputs['a'])
            self.dut._log.warn('Received B:')
            self.fancy_printer(received_b)
            self.dut._log.warn('Expected B:')
            self.fancy_printer(self.expected_inputs['b'])

            for i in reversed(range(self.high_prec // self.low_prec)):
                for j in reversed(range(self.high_prec // self.low_prec)):
                    print int(self.get_scope(i, j).B_SIGN_EXTEND.value),
                print

            for l in reversed(range(self.num_prec)):
                print('Level = {}'.format(l))
                for i in reversed(range(self.high_prec // self.low_prec // (2**l))):
                    for j in reversed(range(self.high_prec // self.low_prec // (2**l))):
                        # print int(self.get_scope(i * (2**l), j * (2**l), max_level=self.num_prec-l-1).b_signed.value.signed_integer), ' ',
                        print int(self.get_scope(i * (2**l), j * (2**l), max_level=self.num_prec-l-1).b_mode.value), ' ',
                    print

            for i in range(len(received_a)):
                assert received_a[i] == self.expected_inputs['a'][i]

        self.dut._log.warn("*"*50)
        self.dut._log.warn("level={}".format(level))
        xdim = ydim = 2**level
        self.dut._log.warn("Expected output at this level = {}".format(self.expected_out[level][i_base * xdim + j_base]))
        # self.dut._log.warn("Len(Output) at this level = {}".format(len(self.expected_out[level])))
        # self.dut._log.warn("xdim = {}, ydim = {}".format(xdim, ydim))

        # More than one level
        if (2**(level+1)) * self.low_prec < self.high_prec:
            # self.dut._log.warn('NEXT: A = {}, B = {}, mode: {}, out: {}'.format(scope.a, scope.b, scope.mode, scope.out.value.signed_integer))
            self.dut._log.warn('Received Output: {}'.format(scope.out.value.signed_integer))
            # self.dut._log.warn('current level mode = {}'.format(scope.LP_MULT_INST.curr_level_mode))
            # self.dut._log.warn('lower level mode = {}'.format(scope.LP_MULT_INST.NEXT_LEVEL.lower_level_mode))
            # if level != 0:
                # self.dut._log.warn('previous level mode = {}'.format(scope.prev_level_mode))
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m3, level=level+1, i_base=i_base*2+1, j_base=j_base*2+1)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m2, level=level+1, i_base=i_base*2+0, j_base=j_base*2+1)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m1, level=level+1, i_base=i_base*2+1, j_base=j_base*2+0)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m0, level=level+1, i_base=i_base*2+0, j_base=j_base*2+0)
        # One level above last
        elif (2**(level+1)) * self.low_prec == self.high_prec:
            # self.dut._log.warn('current level mode = {}'.format(scope.LP_MULT_INST.curr_level_mode))
            # if level != 0:
                # self.dut._log.warn('previous level mode = {}'.format(scope.prev_level_mode))
            # self.dut._log.warn('LAST: A = {}, B = {}, mode: {}, out: {}'.format(scope.a, scope.b, scope.mode, scope.out.value.signed_integer))
            self.dut._log.warn('Received Output: {}'.format(scope.out.value.signed_integer))
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m3, level=level+1, i_base=i_base*2+1, j_base=j_base*2+1)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m2, level=level+1, i_base=i_base*2+0, j_base=j_base*2+1)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m1, level=level+1, i_base=i_base*2+1, j_base=j_base*2+0)
            self.check_received_vs_expected(scope=scope.LP_MULT_INST.m0, level=level+1, i_base=i_base*2+0, j_base=j_base*2+0)
        # last level
        else:
            self.dut._log.warn('Received Output: {}'.format(scope.out.value.signed_integer))
            self.dut._log.warn('A = {}, B = {}, prev_level_mode: {}, out: {}'.format(scope.a_signed.value.signed_integer, scope.b_signed.value.signed_integer, scope.prev_level_mode, scope.out.value.signed_integer))

