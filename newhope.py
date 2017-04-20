import poly
import params
import os
import hashlib

def get_noise():
    coefficients = poly.get_noise()
    coefficeints = poly.poly_ntt(coefficients)
    return coefficients

def sharedb(received):
    pka = poly.from_bytes(received)
    seed = received[-params.NEWHOPE_SEEDBYTES:]
    a_coeffs = gen_a(seed)
    s_coeffs = get_noise()
    e_coeffs = get_noise()
    b_coeffs = poly.pointwise(a_coeffs,s_coeffs)
    b_coeffs = poly.add(b_coeffs,e_coeffs)
    v_coeffs = poly.pointwise(pka,s_coeffs)
    v_coeffs = poly.invntt(v_coeffs)
    e_prime = poly.get_noise()
    v_coeffs = poly.add(v_coeffs, e_prime)

def keygen(verbose = False):
    seed = os.urandom(params.NEWHOPE_SEEDBYTES)
    a_coeffs = gen_a(seed)
    print_coeffs(a_coeffs, 'a', verbose)
    s_coeffs = get_noise()
    print_coeffs(s_coeffs, 's_ntt', verbose)
    e_coeffs = get_noise()
    r_coeffs = poly.pointwise(s_coeffs, a_coeffs)
    p_coeffs = poly.add(e_coeffs, r_coeffs)
    print_coeffs(p_coeffs, 'p', verbose)
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
                shake_output[j * 2:j * 2 + 2], byteorder = 'little')
            j += 1
            if j * 2 >= len(shake_output):
                print('Error: Not enough data from SHAKE-128')
                exit(1)
        output.append(coefficient)
    return output

def print_coeffs(coefficients, name, verbose):
    if verbose:
        print(name + '_coeffs:')
        for i in range(0,len(coefficients)):
            print(str(i) + ': ' + str(coefficients[i]))
