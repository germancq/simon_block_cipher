#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon_encrypt_test.py
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
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20


def setup_dut(dut, plaintext, simon_cipher_sw):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.start.value = 0
    dut.blk_i.value = plaintext
    for i in range(0, simon_cipher_sw.T):
        dut.round_keys[i].value = simon_cipher_sw.round_keys[i]


async def rst_function_test(dut):
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"
    await n_cycles_clock(dut, 10)
    assert int(dut.current_state.value) == int(
        dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"

    assert dut.rk_counter_dout.value == 0, f"ERROR IDLE in counter"
    assert dut.x_reg_dout.value == 0, f"ERROR IDLE in x_reg register"
    assert dut.y_reg_dout.value == 0, f"ERROR IDLE in y_reg register"


async def load_plaintext_test(dut, plaintext, simon_sw):
    # preambule in simon_sw
    y = plaintext & ((2**simon_sw.n) - 1)
    x = (plaintext >> simon_sw.n) & ((2**simon_sw.n) - 1)
    ############################################

    dut.rst.value = 0
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"

    dut.start.value = 1
    await n_cycles_clock(dut, 1)

    assert int(dut.current_state.value) == int(
        dut.LOAD_PLAINTEXT.value
    ), f"ERROR STATE IN LOAD_PLAINTEXT, STATE={dut.current_state.value}"

    await n_cycles_clock(dut, 1)

    assert (
        dut.x_reg_dout.value == x
    ), f"ERROR LOAD_PLAINTEXT in x_reg register, expected {hex(x)}, calculated = {hex(dut.x_reg_dout.value)}"

    assert (
        dut.y_reg_dout.value == y
    ), f"ERROR LOAD_PLAINTEXT in y_reg register, expected {hex(y)}, calculated = {hex(dut.y_reg_dout.value)}"


async def encrypt_loop_test(dut, plaintext, simon_sw):

    i = 0

    y_sw = plaintext & ((2**simon_sw.n) - 1)
    x_sw = (plaintext >> simon_sw.n) & ((2**simon_sw.n) - 1)

    while True:

        x_sw, y_sw = simon_sw.round_function(
            x_sw, y_sw, simon_sw.round_keys[i])

        print("ciclo {}".format(i))

        assert int(dut.current_state.value) == int(
            dut.ROUND_FUNCTION.value
        ), f"ERROR STATE IN ROUND_FUNCTION, STATE={dut.current_state.value}"

        await n_cycles_clock(dut, 1)

        assert (
            dut.x_reg_dout.value == x_sw
        ), f"ERROR ROUND_FUNCTION in x_reg register, expected {hex(x_sw)}, calculated = {hex(dut.x_reg_dout.value)}"

        assert (
            dut.y_reg_dout.value == y_sw
        ), f"ERROR ROUND_FUNCTION in y_reg register, expected {hex(y_sw)}, calculated = {hex(dut.y_reg_dout.value)}"

        assert int(dut.current_state.value) == int(
            dut.ICR_COUNTER.value
        ), f"ERROR STATE IN ICR_COUNTER, STATE={dut.current_state.value}"

        await n_cycles_clock(dut, 1)

        assert int(dut.current_state.value) == int(
            dut.CHECK_COUNTER.value
        ), f"ERROR STATE IN CHECK_COUNTER, STATE={dut.current_state.value}"

        i = i + 1

        if i == dut.T.value:
            return

        await n_cycles_clock(dut, 1)


async def end_state_function_test(dut, expected_result):
    await n_cycles_clock(dut, 1)

    assert int(dut.current_state.value) == int(
        dut.END_STATE.value
    ), f"ERROR STATE IN END, STATE={dut.current_state.value}"

    assert dut.end_signal.value == 1, f"ERROR in end_round signal"

    assert (
        dut.blk_o.value == expected_result
    ), f"ERROR result, expected={hex(expected_result)}, calculated = {hex(dut.blk_o.value)}"


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    random.seed(index)

    N = int(dut.N.value)
    M = int(dut.M.value)
    T = int(dut.T.value)

    key = random.getrandbits(M * N)
    plaintext = random.getrandbits(2 * N)
    simon_cipher_sw = simon.SIMON(2 * N, M * N)
    simon_cipher_sw.key_schedule(key)

    setup_dut(dut, plaintext, simon_cipher_sw)

    await rst_function_test(dut)
    await load_plaintext_test(dut, plaintext, simon_cipher_sw)
    await encrypt_loop_test(dut, plaintext, simon_cipher_sw)

    expected_result = simon_cipher_sw.encrypt(plaintext)
    await end_state_function_test(dut, expected_result)
