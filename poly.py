import params
import precomp
import sha3 # need to implement
import os

QINV = 12287 # -inverse_mod(p,2^18)
RLOG = 18

def uniform(a, seed):
    pos = 0
    ctr = 0
    val = 0
    nblocks = 16
    state = sha3.absorb(seed, params.NEWHOPE_SEEDBYTES)
    buf = sha3.squeezeblocks(nblocks, state)
    # TODO: write these keccak functions; they need to return lists
    while ctr < params.N:
        val = (buf[pos] | buf[pos + 1] << 8) & 0x3fff
        if val < params.Q:
            coeffs[ctr++] = val
            # polynomial coefficients for passing to polynomial object in
            # keygen function
        pos += 2
        if pos > sha3.RATE * nblocks - 2:
            nblocks = 1
            buf = sha3.squeezeblocks(nblocks, state)
            pos = 0
    return coeffs

def get_noise():
    buf = []
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
        coeffs[i] = a + params.Q - b
    return coeffs

def ntt(coefficients, omega):
    for i in range(0,10,2):
        distance = 1 << i
        for start in range(0,distance):
            jTwiddle = 0
            for j in range(start,params.N - 1,2 * distance):
                W = omega[jTwiddle++]
                temp = coefficients[j]
                coefficients[j] = temp + coefficients[j + distance]
                coefficients[j + distance] = montgomery_reduce(
                    W * (temp + 3 * params.Q - coefficients[j + distance]))
        distance <<= 1
        for start in range(0,distance):
            jTwiddle = 0
            for j in range(start,params.N - 1,2 * distance):
                W = omega[jTwiddle++]
                temp = coefficients[j]
                coefficients[j] = barrett_reduce(temp + coefficients[j + distance])
                coefficients[j + distance] = montgomery_reduce(
                    W * (temp + 3 * params.Q - coefficients[j + distance]))
#TODO: get rid of repeated code
    return coefficients

def poly_ntt(coefficients):
    coefficients = mul_coefficients(coefficients, precomp.psis_bitrev_montgomery)
    coefficients = ntt(coefficients, precomp.omegas_montgomery)

def pointwise(a, b): # a and b are the coefficients of these polys as lists
    for i in range(0,params.N):
        t = montgomery_reduce(3186 * b[i])
        coefficients[i] = montgomery_reduce(a[i] * t)
    return coefficients

def add(a, b): # a and b are the coefficients of these polys as lists
    for i in range(0,params.N):
        coefficients[i] = barrett_reduce(a[i] + b[i])
    return coefficients

def to_bytes(coefficients):
    output = []
    for i in range(0,params.N / 4):
        t = []
        for j in range(0,4):
            t.append(barrett_reduce(coefficients[4 * i + j]))
        for j in range(0,4):
            t[j] = check_coeff(t[j])
        output.append(t[0] & 0xff)
        output.append((t[0] >> 8) | (t[1] << 6))
        output.append(t[1] >> 2)
        output.append((t[1] >> 10) | (t[2] << 4))
        output.append(t[2] >> 4)
        output.append((t[2] >> 12) | (t[3] << 2))
        output.append(t[3] >> 6)
    return output

def check_coeff(t):
    m = t - params.Q #uint16_t
    c = m #int16_t
    c >>= 15
    return m ^ ((t ^ m) & c)

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
