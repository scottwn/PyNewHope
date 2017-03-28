import params
import precomp
import sha3 # need to implement
import os

QINV = 12287 # -inverse_mod(p,2^18)
RLOG = 18

def get_noise():
    buf = []
    coeffs = []
    for i in range(0,params.N * 4):
        buf.append(os.urandom(1))
    for i in range(0,params.N):
        t = buf[i]
        d = 0
        for j in range(0,8):
            # j is a signed integer???
            d += (t >> j) & 0x01010101
        a = ((d >> 8) & 0xff) + (d & 0xff)
        b = (d >> 24) + ((d >> 16) & 0xff)
        coeffs.append(a + params.Q - b)
    return coeffs

def ntt(coefficients, omega):
    for i in range(0,10,2):
        distance = 1 << i
        coefficients = ntt_helper(distance, coefficients, omega)
        distance <<= 1
        coefficients = ntt_helper(distance, coefficients, omega)
    return coefficients

def ntt_helper(distance, coefficients, omega):
    for start in range(0,distance):
        jTwiddle = 0
        for j in range(start,params.N - 1,2 * distance):
            W = omega[jTwiddle++]
            temp = coefficients[j]
            coefficients[j] = temp + coefficients[j + distance]
            coefficients[j + distance] = montgomery_reduce(
                W * (temp + 3 * params.Q - coefficients[j + distance]))
    return coefficients

def poly_ntt(coefficients):
    coefficients = mul_coefficients(coefficients, precomp.psis_bitrev_montgomery)
    coefficients = ntt(coefficients, precomp.omegas_montgomery)
    return coefficients

def pointwise(a, b): # a and b are the coefficients of these polys as lists
    coefficients = []
    for i in range(0,params.N):
        t = montgomery_reduce(3186 * b[i])
        coefficients.append(montgomery_reduce(a[i] * t))
    return coefficients

def add(a, b): # a and b are the coefficients of these polys as lists
    coefficients = []
    for i in range(0,params.N):
        coefficients.append(barrett_reduce(a[i] + b[i]))
    return coefficients

def mul_coefficients(coefficients, factors):
    for i in range(0,params.N):
        coefficients[i] = montgomery_reduce(coefficients[i] * factors[i])
    return coefficients

def montgomery_reduce(a):
    u = a * QINV
    u &= (1 << RLOG) - 1
    u *= params.Q
    a += u
    return a >> 18

def barrett_reduce(a):
    u = (a * 5) >> 16
    u *= params.Q
    a -= u
    return a
