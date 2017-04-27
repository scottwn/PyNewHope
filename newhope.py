import poly
import params
import os
import hashlib

#global variables:
a_key = []
b_key = []
s_hat = []

def get_noise():
    coefficients = poly.get_noise()
    coefficeints = poly.poly_ntt(coefficients)
    return coefficients

def shareda(received):
    global a_key, s_hat
    c_coeffs = []
    b_coeffs = poly.from_bytes(received)
    for i in range(0, params.N // 4):
        c_coeffs.append(received[params.POLY_BYTES + i] & 0x03)
        c_coeffs.append(received[params.POLY_BYTES + i] >> 2 & 0x03)
        c_coeffs.append(received[params.POLY_BYTES + i] >> 4 * 0x03)
        c_coeffs.append(received[params.POLY_BYTES + i] >> 6)
    v_coeffs = poly.pointwise(s_hat, b_coeffs)
    v_coeffs = poly.invntt(v_coeffs)
    a_key = poly.rec(v_coeffs, c_coeffs)
    return

def sharedb(received):
    global b_key
    pka = poly.from_bytes(received)
    print_coeffs(pka, 'bob b', True)
    seed = received[-params.NEWHOPE_SEEDBYTES:]
    print('bob seed')
    print(str(seed))
    a_coeffs = gen_a(seed)
    s_coeffs = get_noise()
    e_coeffs = get_noise()
    b_coeffs = poly.pointwise(a_coeffs, s_coeffs)
    b_coeffs = poly.add(b_coeffs, e_coeffs)
    v_coeffs = poly.pointwise(pka, s_coeffs)
    v_coeffs = poly.invntt(v_coeffs)
    e_prime = poly.get_noise()
    v_coeffs = poly.add(v_coeffs, e_prime)
    c_coeffs = poly.helprec(v_coeffs)
    output = poly.to_bytes(b_coeffs)
    for i in range(0, params.N // 4):
        output.append(
            c_coeffs[4 * i]
            | c_coeffs[4 * i + 1] << 2
            | c_coeffs[4 * i + 2] << 4
            | c_coeffs[4 * i + 3] << 6)
    b_key = poly.rec(v_coeffs, c_coeffs)
    return bytes(output)

def keygen(verbose = False):
    global s_hat
    seed = os.urandom(params.NEWHOPE_SEEDBYTES)
    print('alice seed')
    print(str(seed))
    a_coeffs = gen_a(seed)
    s_coeffs = get_noise()
    s_hat = s_coeffs
    e_coeffs = get_noise()
    r_coeffs = poly.pointwise(s_coeffs, a_coeffs)
    p_coeffs = poly.add(e_coeffs, r_coeffs)
    print_coeffs(p_coeffs, 'alice b', verbose)
    return bytes(poly.to_bytes(p_coeffs)) + seed

def gen_a(seed):
    hashing_algorithm = hashlib.shake_128()
    hashing_algorithm.update(seed)
    # 2200 bytes from SHAKE-128 function is enough data to get 1024 coefficients
    # smaller than 5q, from Alkim, Ducas, Pöppelmann, Schwabe section 7:
    shake_output = hashing_algorithm.digest(2200)
    output = []
    j = 0
    for i in range(0,params.N):
        coefficient = 5 * params.Q
        # Reject coefficients that are greater than or equal to 5q:
        while coefficient >= 5 * params.Q:
            coefficient = int.from_bytes(
                shake_output[j * 2 : j * 2 + 2], byteorder = 'little')
            # print('j=' + str(j))
            j += 1
            if j * 2 >= len(shake_output):
                print('Error: Not enough data from SHAKE-128')
                exit(1)
        output.append(coefficient)
        # print('chose ' + str(coefficient))
    return output

def print_coeffs(coefficients, name, verbose):
    if verbose:
        with open(name + '.txt', 'w') as f:
            for i in range(0,len(coefficients)):
                f.write(str(i) + ': ' + str(coefficients[i]) + '\n')
