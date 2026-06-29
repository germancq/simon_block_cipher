#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon_key_schedule_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 02.10.2025
# Last Modified Date: 02.10.2025
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

Z_sw = [
    0b01100111000011010100100010111110110011100001101010010001011111,
    0b01011010000110010011111011100010101101000011001001111101110001,
    0b11001101101001111110001000010100011001001011000000111011110101,
    0b11110000101100111001010001001000000111101001100011010111011011,
    0b11110111001001010011000011101000000100011011010110011110001011,
]


def setup_dut(dut, key, Z):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.start.value = 0
    dut.key.value = key
    dut.Z.value = Z


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
    assert dut.reg_aux_dout.value == 0, f"ERROR IDLE in aux register"
    for i in range(0, dut.T.value):
        assert dut.round_keys[i].value == 0, f"ERROR RST in round key {i}"


async def preambule_test(dut, simon_sw, key):
    # preambule in simon_sw
    for i in range(0, simon_sw.T):
        simon_sw.round_keys.insert(i, 0)

    for i in range(0, simon_sw.m):
        rk = (key >> ((simon_sw.n) * i)) & ((2 ** (simon_sw.n)) - 1)
        simon_sw.round_keys[i] = rk
    ############################################

    dut.rst.value = 0
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"

    dut.start.value = 1
    await n_cycles_clock(dut, 1)

    assert int(dut.current_state.value) == int(
        dut.PREAMBULE.value
    ), f"ERROR STATE IN PREAMBULE, STATE={dut.current_state.value}"

    await n_cycles_clock(dut, 1)

    for i in range(0, dut.M.value):
        assert (
            dut.round_keys[i].value == simon_sw.round_keys[i]
        ), f"ERROR in RK{i}, expected = {hex(simon_sw.round_keys[i])}, calculated = {hex(dut.round_keys[i].value)} "


async def key_schedule_loop_test(dut, simon_sw):

    i = 0

    while True:

        if simon_sw.m == 4:
            aux0 = (
                simon_sw.ror(
                    simon_sw.n, simon_sw.round_keys[i + (simon_sw.m - 1)], 3)
                ^ simon_sw.round_keys[i + 1]
            )
            aux1 = aux0 ^ simon_sw.ror(simon_sw.n, aux0, 1)
            rk = (
                simon_sw.c
                ^ ((Z_sw[simon_sw.Z_sel] >> (i % 62)) & 1)
                ^ aux1
                ^ simon_sw.round_keys[i]
            )
            simon_sw.round_keys[i + simon_sw.m] = rk
        else:
            aux0 = simon_sw.ror(
                simon_sw.n, simon_sw.round_keys[i + (simon_sw.m - 1)], 3
            )
            aux1 = aux0 ^ simon_sw.ror(simon_sw.n, aux0, 1)
            rk = (
                simon_sw.c
                ^ ((Z_sw[simon_sw.Z_sel] >> (i % 62)) & 1)
                ^ aux1
                ^ simon_sw.round_keys[i]
            )
            simon_sw.round_keys[i + simon_sw.m] = rk

        print("ciclo {}".format(i))

        assert int(dut.current_state.value) == int(
            dut.CALC_AUX_0.value
        ), f"ERROR STATE IN CALC_AUX_0, STATE={dut.current_state.value}"

        await n_cycles_clock(dut, 1)

        assert (
            dut.reg_aux_dout.value == aux0
        ), f"ERROR IN AUX0, expected = {hex(aux0)}, calculated = {hex(dut.reg_aux_dout.value)}"

        assert int(dut.current_state.value) == int(
            dut.CALC_AUX_1.value
        ), f"ERROR STATE IN CALC_AUX_1, STATE={dut.current_state.value}"

        await n_cycles_clock(dut, 1)

        assert (
            dut.reg_aux_dout.value == aux1
        ), f"ERROR IN AUX1, expected = {hex(aux1)}, calculated = {hex(dut.reg_aux_dout.value)}"

        assert int(dut.current_state.value) == int(
            dut.WRITE_RK.value
        ), f"ERROR STATE IN WRITE_RK, STATE={dut.current_state.value}"

        assert (
            dut.reg_rk_din[int(dut.rk_counter_dout.value) +
                           int(dut.M.value)].value
            == simon_sw.round_keys[i + simon_sw.m]
        ), f"ERROR IN WRITE_RK, expected = {hex(simon_sw.round_keys[i + simon_sw.m])}, calculated = {hex(dut.reg_aux_din[dut.rk_counter_dout.value + dut.M.value])}"

        await n_cycles_clock(dut, 1)

        assert int(dut.current_state.value) == int(
            dut.CHECK_COUNTER.value
        ), f"ERROR STATE IN CHECK_COUNTER, STATE={dut.current_state.value}"

        i = i + 1

        if i == (int(dut.T.value) - int(dut.M.value)):
            return

        await n_cycles_clock(dut, 1)


async def end_state_function_test(dut, simon_sw):
    await n_cycles_clock(dut, 1)

    assert int(dut.current_state.value) == int(
        dut.END_STATE.value
    ), f"ERROR STATE IN END, STATE={dut.current_state.value}"

    assert dut.end_signal.value == 1, f"ERROR in end_round signal"

    for i in range(0, dut.T.value):
        assert (
            dut.round_keys[i].value == simon_sw.round_keys[i]
        ), f"ERROR in RK{i}, expected = {hex(simon_sw.round_keys[i])}, calculated = {hex(dut.round_keys[i].value)} "


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

    setup_dut(dut, key, Z_sw[simon_cipher_sw.Z_sel])

    await rst_function_test(dut)
    await preambule_test(dut, simon_cipher_sw, key)
    await key_schedule_loop_test(dut, simon_cipher_sw)

    simon_cipher_sw_2 = simon.SIMON(2 * N, M * N)
    simon_cipher_sw_2.key_schedule(key)

    await end_state_function_test(dut, simon_cipher_sw_2)
