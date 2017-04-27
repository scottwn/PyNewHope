import params
import precomp
import os

QINV = 12287 # -inverse_mod(p,2^18)
RLOG = 18

def LDDecode(xi0, xi1, xi2, xi3):
    t = g(xi0)
    t += g(xi1)
    t += g(xi2)
    t += g(xi3)
    t -= 8 * params.Q
    t >>= 31
    return t & 1

def nh_abs(x):
    mask = x >> 31
    return (x ^ mask) - mask

def f(x):
    b = x * 2730
    t = b >> 25
    b = x - t * 12289
    b = 12288 - b
    b >>= 31
    t -= b
    r = t & 1
    xit = t >> 1
    v0 = xit + r
    t -= 1
    r = t & 1
    v1 = (t >> 1) + r
    return (v0, v1, nh_abs(x - v0 * 2 * params.Q))

def g(x):
    b = x * 2730
    t = b >> 27
    b = x - t * 49156
    b = 49155 - b
    b >>= 31
    t -= b
    c = t & 1
    t = (t >> 1) + c
    t *= 8 * params.Q
    return nh_abs(t - x)

def helprec(coefficients):
    rand = []
    output = []
    for i in range(0, 1024):
        output.append(0)
    v0 = [0, 0, 0, 0]
    v1 = [0, 0, 0, 0]
    v_tmp = [0, 0, 0, 0]
    for i in range(0, 32):
        rand.append(int.from_bytes(os.urandom(4), byteorder='little'))
    for i in range(0, 256):
        rbit = rand[i >> 3] >> (i & 7) & 1
        (v0[0], v1[0], k) = f(8 * coefficients[0 + i] + 4 * rbit)
        (v0[1], v1[1], x) = f(8 * coefficients[256 + i] + 4 * rbit)
        k += x
        (v0[2], v1[2], x) = f(8 * coefficients[512 + i] + 4 * rbit)
        k += x
        (v0[3], v1[3], x) = f(8 * coefficients[768 + i] + 4 * rbit)
        k += x
        k = 2 * params.Q - 1 - k >> 31
        v_tmp[0] = ((~k) & v0[0]) ^ (k & v1[0])
        v_tmp[1] = ((~k) & v0[1]) ^ (k & v1[1])
        v_tmp[2] = ((~k) & v0[2]) ^ (k & v1[2])
        v_tmp[3] = ((~k) & v0[3]) ^ (k & v1[3])
        output[0 + i] = (v_tmp[0] - v_tmp[3]) & 3
        output[256 + i] = (v_tmp[1] - v_tmp[3]) & 3
        output[512 + i] = (v_tmp[2] - v_tmp[3]) & 3
        output[768 + i] = (-k + 2 * v_tmp[3]) & 3
    return output

def rec(v_coeffs, c_coeffs):
    key = []
    tmp = [0, 0, 0, 0]
    for i in range(0, 32):
        key.append(0)
    for i in range(0, 256):
        tmp[0] = (
            16 * params.Q
            + 8 * v_coeffs[0 + i]
            - params.Q * (2 * c_coeffs[0 + i] + c_coeffs[768 + i]))
        tmp[1] = (
            16 * params.Q
            + 8 * v_coeffs[256 + i]
            - params.Q * (2 * c_coeffs[256 + i] + c_coeffs[768 + i]))
        tmp[2] = (
            16 * params.Q
            + 8 * v_coeffs[512 + i]
            - params.Q * (2 * c_coeffs[512 + i] + c_coeffs[768 + i]))
        tmp[3] = (
            16 * params.Q
            + 8 * v_coeffs[768 + i]
            - params.Q * (c_coeffs[768 + i]))
        key[i >> 3] |= LDDecode(tmp[0], tmp[1], tmp[2], tmp[3]) << (i & 7)
    return key

def bitrev_vector(coefficients):
    for i in range(0, params.N):
        r = precomp.bitrev_table[i]
        if i < r:
            tmp = coefficients[i]
            coefficients[i] = coefficients[r]
            coefficients[r] = tmp
    return coefficients

def invntt(coefficients):
    coefficients = bitrev_vector(coefficients)
    coefficients = ntt(coefficients, precomp.omegas_inv_montgomery)
    coefficients = mul_coefficients(coefficients, precomp.psis_inv_montgomery)
    return coefficients

# Get a random sampling of integers from a normal distribution around parameter
# Q.
def get_noise():
    coeffs = []
    for i in range(0, params.N):
        t = int.from_bytes(os.urandom(4), byteorder='little')
        d = 0
        for j in range(0, 8):
            d += (t >> j) & 0x01010101
        a = ((d >> 8) & 0xff) + (d & 0xff)
        b = (d >> 24) + ((d >> 16) & 0xff)
        coeffs.append(a + params.Q - b)
    return coeffs

def ntt(coefficients, omega):
    for i in range(0, 10, 2):
        distance = 1 << i
        for start in range(0, distance):
            jTwiddle = 0
            for j in range(start, params.N - 1, 2 * distance):
                W = omega[jTwiddle]
                jTwiddle += 1
                temp = coefficients[j]
                coefficients[j] = temp + coefficients[j + distance]
                coefficients[j + distance] = montgomery_reduce(
                    W * (temp + 3 * params.Q - coefficients[j + distance]))
        distance <<= 1
        for start in range(0, distance):
            jTwiddle = 0
            for j in range(start, params.N - 1, 2 * distance):
                W = omega[jTwiddle]
                jTwiddle += 1
                temp = coefficients[j]
                coefficients[j] = barrett_reduce(temp + coefficients[j + distance])
                coefficients[j + distance] = montgomery_reduce(
                    W * (temp + 3 * params.Q - coefficients[j + distance]))
    return coefficients

def poly_ntt(coefficients):
    coefficients = mul_coefficients(coefficients, precomp.psis_bitrev_montgomery)
    coefficients = ntt(coefficients, precomp.omegas_montgomery)
    return coefficients

# a and b are the coefficients of these polys as lists.
def pointwise(a, b):
    coefficients = []
    for i in range(0, params.N):
        t = montgomery_reduce(3186 * b[i])
        coefficients.append(montgomery_reduce(a[i] * t))
    return coefficients

# a and b are the coefficients of these polys as lists.
def add(a, b):
    coefficients = []
    for i in range(0, params.N):
        coefficients.append(barrett_reduce(a[i] + b[i]))
    return coefficients

def mul_coefficients(coefficients, factors):
    for i in range(0, params.N):
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
