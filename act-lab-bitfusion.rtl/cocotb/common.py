import random

import cocotb
from cocotb.clock import Clock
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.monitors import Monitor
from cocotb.binary import BinaryValue, BinaryRepresentation
from cocotb.regression import TestFactory
from cocotb.scoreboard import Scoreboard
from cocotb.result import TestFailure, TestSuccess
from cocotb.log import SimLog

import math
import numpy as np


# ========================
def signal_to_np_array(signal, precision, signed=False):
    arr = np.empty((signal._bits / precision))
    for i in range(len(arr)):
        hi = (len(arr)-i)*precision-1
        lo = (len(arr)-i-1)*precision
        arr[i] = signal[lo:hi].integer
        if signed and arr[i] > (1<<(precision-1)):
          arr[i] -= 1<<precision
    return arr

# ========================
def np_array_to_signal(arr, precision):
    b = BinaryValue(value=0, bits=precision*len(arr))
    for i in range(len(arr)):
        hi = (len(arr)-i)*precision-1
        lo = (len(arr)-i-1)*precision
        tmp = int(arr[i])
        if tmp < 0:
            val = bin(tmp + (1<<precision))[2:]
            val_ext = (precision-len(val))*'1'+val
        else:
            val = bin(tmp)[2:]
            val_ext = (precision-len(val))*'0' + val
        b[lo:hi] = val_ext
    return b

# ========================
def ceilAByB(a, b):
    return int(math.ceil(a/float(b)))

# ========================
def random_op_gen(op_list):
    while True:
        yield op_list[random.randint(0, len(op_list)-1)]

# ========================
def random_data_gen(dlen):
    while True:
        # yield BinaryValue(random.randrange(-(1<<10), 1<<10-1, 1), dlen, binaryRepresentation=BinaryRepresentation.SIGNED_MAGNITUDE)
        yield BinaryValue(random.randint(-(1<<5),(1<<5)), dlen, binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT)

# ========================
def zero_gen():
    while True:
        yield 0

# ========================
class DWValidMonitor(Monitor):
    """Observes single input DUT when valid is high."""
    def __init__(self, name, signal, valid, clock, callback=None, event=None):
        self.name = name
        self.signal = signal
        self.valid = valid
        self.clock = clock
        Monitor.__init__(self, callback, event)
        self._log = SimLog("%s.%s" % (self.__class__.__name__, self.name))
        self.started = False

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    @coroutine
    def _monitor_recv(self):
        clkedge = RisingEdge(self.clock)

        while True:
            # Capture signal at rising edge of clock
            yield clkedge
            if self.started and self.valid.value.integer == 1:
                self._recv(self.signal.value.signed_integer)
                self._log.debug('Monitor {}: Got: {}'.format(self.name, self.signal.value.signed_integer))


# ========================

# ========================
class DWMonitor(Monitor):
    """Observes single input or output of DUT."""
    def __init__(self, name, signal, clock, callback=None, event=None):
        self.name = name
        self.signal = signal
        self.valid = False
        self.clock = clock
        Monitor.__init__(self, callback, event)
        self._log = SimLog("%s.%s" % (self.__class__.__name__, self.name))

    def start(self):
        self.valid = True

    def stop(self):
        self.valid = False

    @coroutine
    def _monitor_recv(self):
        clkedge = RisingEdge(self.clock)

        while True:
            # Capture signal at rising edge of clock
            yield clkedge
            if (self.valid):
                self._recv(self.signal.value.signed_integer)
                self._log.debug('Monitor {}: Got: {}'.format(self.name, self.signal.value.signed_integer))

# ========================
class DWDriver(object):
    def __init__(self, name, clk, signal, generator):
        self._clk = clk
        self._signal = signal
        self._generator = generator
        self._generate_fork = None

    @cocotb.coroutine
    def generate(self):
        while True:
            yield RisingEdge(self._clk)
            self._signal <= next(self._generator)

    def start(self):
        self._generate_fork = cocotb.fork(self.generate())

    def stop(self):
        if self._generate_fork is not None:
            self._generate_fork.kill()
            self._generate_fork = None

# ========================
class DWTB(object):
    def __init__(self, dut):
        """
        Setup testbench
        """

        self._log = SimLog("%s" % (self.__class__.__name__))
        self._log.info('Starting Test')

        # Dut
        self.dut = dut

        # clock and reset
        self.clk = dut.clk
        self.rst = dut.reset

    @cocotb.coroutine
    def clk_rst_gen(self):
        cocotb.fork(Clock(self.dut.clk, 10).start())
        yield self.apply_reset()

    @cocotb.coroutine
    def apply_reset(self):
        self.rst <= 1
        yield RisingEdge(self.clk)
        self.rst <= 0
        yield RisingEdge(self.clk)


# ========================
class FIFO(object):

  def __init__(self, size, dtype=np.int):
    self.mem = np.empty(size, dtype)
    self.rd_ptr = 0
    self.wr_ptr = 0
    self.size = size
    self.count = 0

  def push (self, data):
    self.mem[self.wr_ptr] = data
    self.wr_ptr = (self.wr_ptr + 1) % self.size
    self.count += 1

  def pop (self):
    ret = self.mem[self.rd_ptr]
    self.rd_ptr = (self.rd_ptr + 1) % self.size
    self.count -= 1
    return ret

  @property
  def empty(self):
    return self.count == 0

  @property
  def full(self):
    return self.count == self.size
