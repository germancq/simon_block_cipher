#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 03.10.2025
# Last Modified Date: 03.10.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import os
import random
import sys

import cocotb
import numpy as np
import simon
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20


def setup_dut(dut, plaintext, key):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.rq_data.value = 0
    dut.block_i.value = plaintext
    dut.key.value = key
    dut.enc_dec.value = 0


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    random.seed(index)

    N = dut.N.value
    M = dut.M.value

    key = random.getrandbits(M * N)
    plaintext = random.getrandbits(2 * N)
    simon_cipher_sw = simon.SIMON(2 * N, M * N)
    simon_cipher_sw.key_schedule(key)

    setup_dut(dut, plaintext, key)
    dut.rst.value = 1
    await n_cycles_clock(dut, 10)
    dut.rst.value = 0
    dut.rq_data.value = 1

    while dut.end_signal.value == 0:
        await n_cycles_clock(dut, 1)

    expected_result = simon_cipher_sw.encrypt(plaintext)

    assert (
        dut.block_o.value == expected_result
    ), f"ERROR expected result = {hex(expected_result)}, calculated = {hex(dut.block_o.value)}"
