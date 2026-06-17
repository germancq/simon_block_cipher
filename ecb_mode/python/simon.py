#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : simon.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 17.06.2026
# Last Modified Date: 17.06.2026
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import math

# Z = [
#    0b11111010001001010110000111001101111101000100101011000011100110,
#    0b10001110111110010011000010110101000111011111001001100001011010,
#    0b10101111011100000011010010011000101000010001111110010110110011,
#    0b11011011101011000110010111100000010010001010011100110100001111,
#    0b11010001111001101011011000100000010111000011001010010011101111,
# ]

Z = [
    0b01100111000011010100100010111110110011100001101010010001011111,
    0b01011010000110010011111011100010101101000011001001111101110001,
    0b11001101101001111110001000010100011001001011000000111011110101,
    0b11110000101100111001010001001000000111101001100011010111011011,
    0b11110111001001010011000011101000000100011011010110011110001011,
]

T = {
    16: {4: 32},
    24: {3: 36, 4: 36},
    32: {3: 42, 4: 44},
    48: {2: 52, 3: 54},
    64: {2: 68, 3: 69, 4: 72},
}

Z_sel = {
    16: {4: 0},
    24: {3: 0, 4: 1},
    32: {3: 2, 4: 3},
    48: {2: 2, 3: 3},
    64: {2: 2, 3: 3, 4: 4},
}


class SIMON:

    # N:len of plaintext
    # M: len of key
    def __init__(self, N, M):
        self.n = int(N / 2)
        self.m = int(M / self.n)
        self.key_len = M
        self.c = (2**self.n) - 4
        self.round_keys = []
        self.T = T[self.n][self.m]
        self.Z_sel = Z_sel[self.n][self.m]

    def rol(self, size, x, i):
        if i == 0:
            return x
        else:
            out = ((x << 1) + (x >> (size - 1))) % (2**size)
            return self.rol(size, out, i - 1)

    def ror(self, size, x, i):
        if i == 0:
            return x
        else:
            lsb = x & 0x1
            out = (x >> 1) + (lsb << (size - 1))
            return self.ror(size, out, i - 1)

    def f_circular(self, x):
        print("f_circular")
        aux = self.rol(self.n, x, 8) & self.rol(self.n, x, 1)
        res = aux ^ self.rol(self.n, x, 2)
        print(hex(res))
        return res

    def round_function(self, x, y, k):
        x_new = self.f_circular(x) ^ k ^ y
        y_new = x
        return x_new, y_new

    def key_schedule(self, key):
        for i in range(0, self.T):
            self.round_keys.insert(i, 0)

        for i in range(0, self.m):
            rk = (key >> ((self.n) * i)) & ((2 ** (self.n)) - 1)
            self.round_keys[i] = rk

        for i in range(0, self.T - self.m):
            if self.m == 4:
                aux = (
                    self.ror(self.n, self.round_keys[i + (self.m - 1)], 3)
                    ^ self.round_keys[i + 1]
                )
                aux = aux ^ self.ror(self.n, aux, 1)
                rk = (
                    self.c
                    ^ ((Z[self.Z_sel] >> (i % 62)) & 1)
                    ^ aux
                    ^ self.round_keys[i]
                )
                self.round_keys[i + self.m] = rk
            else:
                aux = self.ror(self.n, self.round_keys[i + (self.m - 1)], 3)
                aux = aux ^ self.ror(self.n, aux, 1)
                rk = (
                    self.c
                    ^ ((Z[self.Z_sel] >> (i % 62)) & 1)
                    ^ aux
                    ^ self.round_keys[i]
                )
                self.round_keys[i + self.m] = rk

    def encrypt(self, plaintext):
        y = plaintext & ((2**self.n) - 1)
        x = (plaintext >> self.n) & ((2**self.n) - 1)

        for i in range(0, self.T):
            print(i)
            print(hex(x))
            print(hex(y))
            x, y = self.round_function(x, y, self.round_keys[i])

        return (x << (self.n)) + y


if __name__ == "__main__":
    print("SIMON")
    simon = SIMON(128, 256)
    print(hex(simon.c))
    simon.key_schedule(
        0x1F1E1D1C1B1A191817161514131211100F0E0D0C0B0A09080706050403020100
    )
    for rk in simon.round_keys:
        print(hex(rk))
    result = simon.encrypt(0x74206E69206D6F6F6D69732061207369)
    print(hex(result))
