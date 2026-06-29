#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon_cte_test.py
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
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):
    N = int(dut.N.value)
    M = int(dut.M.value)

    print(N)
    print(M)

    await Timer(10, units="ns")

    for i in range(0, 5):
        assert (
            int(dut.Z[i].value) == simon.Z[i]
        ), f"ERROR with Z{i}, with N = {N} and M={M}, expected_value = {simon.Z[i]} and calculated = {dut.Z[i].value}"

    assert (
        int(dut.Z_sel.value) == simon.Z_sel[N][M]
    ), f"ERROR with Z_sel, with N = {N} and M = {M}, expected_value = {simon.Z_sel[N][M]} and calculated = {dut.Z_sel.value}"

    assert (
        int(dut.T.value) == simon.T[N][M]
    ), f"ERROR with T, with N = {N} and M = {M}, expected_value = {simon.T[N][M]} and calculated = {dut.T.value}"
