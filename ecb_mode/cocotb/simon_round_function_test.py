#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon_round_function_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 01.10.2025
# Last Modified Date: 01.10.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import os
import random
import sys

import cocotb
import numpy as np
import simon
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    random.seed(index)

    N = int(dut.N.value)
    M = 3
    if N == 16:
        M = 4

    simon_cipher_sw = simon.SIMON(2 * N, M * N)
    x_generated = random.getrandbits(N)
    y_generated = random.getrandbits(N)
    k_generated = random.getrandbits(N)

    dut.x.value = x_generated
    dut.y.value = y_generated
    dut.k.value = k_generated

    await Timer(10, units="ns")

    expected_f_circ = simon_cipher_sw.f_circular(x_generated)
    expected_x_new, expected_y_new = simon_cipher_sw.round_function(
        x_generated, y_generated, k_generated
    )

    assert (
        dut.f_circ.value == expected_f_circ
    ), f"ERROR with f_circ, with N = {N}, expected_value = {expected_f_circ} and calculated = {dut.f_circ.value}"

    assert (
        dut.x_new.value == expected_x_new
    ), f"ERROR with x_new, with N = {N}, expected_value = {expected_x_new} and calculated = {dut.x_new.value}"

    assert (
        dut.y_new.value == expected_y_new
    ), f"ERROR with y_new, with N = {N}, expected_value = {expected_y_new} and calculated = {dut.y_new.value}"
