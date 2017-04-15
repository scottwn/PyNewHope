import params
import precomp
import os

QINV = 12287 # -inverse_mod(p,2^18)
RLOG = 18

def to_bytes(coefficients):
    output = []
    for i in range(0,params.N // 4): # Floor division returns int in python3.6.
        # Compress 4 coefficients so they are less than parameter Q and get them
        # back as a list.
        t = reducer(coefficients, i)
        output.append(t[0] & 0xff)
        output.append((t[0] >> 8 | t[1] << 6) & 0xff)
        output.append(t[1] >> 2 & 0xff)
        output.append((t[1] >> 10 | t[2] << 4) & 0xff)
        output.append(t[2] >> 4 & 0xff)
        output.append((t[2] >> 12 | t[3] << 2) & 0xff)
        output.append(t[3] >> 6 & 0xff)
    return output

def from_bytes(received):
    output = []
    for i in range(0,params.N // 4):
        # TODO: Use bit manipulation to fake uints.
        output.append(received[7 * i + 0] | (received[7 * i + 1] & 0x3f) << 8)
        output.append(
            received[7 * i + 1] >> 6 
            | received[7 * i + 2] << 2 
            | (received[7 * i + 3] & 0x0f) << 10)
        output.append(
            received[7 * i + 3] >> 4
            | received[7 * i + 4] << 4
            | (received[7 * i + 5] & 0x03) << 12)
        output.append(received[7 * i + 5] >> 2 | received[7 * i + 6] << 6)
    return output

def reducer(coefficients, i):
    output = []
    for j in range(0,4):
        output.append(barrett_reduce(coefficients[4 * i + j]))
    for j in range(0,4):
        output[j] = less_than_q(output[j])
    return output

def less_than_q(value):
    m = value - params.Q
    if m < 0:
        return value
    else:
        return m

# Get a random sampling of integers from a normal distribution around parameter
# Q.
def get_noise():
    coeffs = []
    for i in range(0,params.N):
        t = int.from_bytes(os.urandom(4), byteorder='little')
        d = 0
        for j in range(0,8):
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
            W = omega[jTwiddle]
            jTwiddle += 1
            temp = coefficients[j]
            coefficients[j] = temp + coefficients[j + distance]
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
    for i in range(0,params.N):
        t = montgomery_reduce(3186 * b[i])
        coefficients.append(montgomery_reduce(a[i] * t))
    return coefficients

# a and b are the coefficients of these polys as lists.
def add(a, b):
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
