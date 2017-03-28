import poly
import params
import os
import hashlib

def keygen():
    seed = os.urandom(params.NEWHOPE_SEEDBYTES)
    hashing_algorithm = hashlib.shake_128()
    hashing_algorithm.update(seed)
    # 2200 bytes from SHAKE-128 function is enough data to get 1024 coefficients
    # smaller than 5q, from Alkim, Ducas, Pöppelmann, Schwabe section 7:
    shake_output = hashing_algorithm.digest(2200)
    a_coeffs = []
    for i in range(0,params.N):
        j = 0
        coefficient = 5 * params.Q
        # Reject coefficients that are greater than or equal to 5q:
        while coefficient >= 5 * params.Q:
            coefficient = int.from_bytes(
                shake_output[j * 2:j * 2 + 2], byteorder = 'little')
            j++
            if j * 2 >= len(shake_output):
                print('Error: Not enough data from SHAKE-128')
                exit(1)
        a_coeffs.append(coefficient)
    s_coeffs = poly.get_noise()
    s_coeffs = poly.poly_ntt(s_coeffs)
    e_coeffs = poly.get_noise()
    e_coeffs = poly.poly_ntt(e.coeffs)
    r_coeffs = poly.pointwise(s_coeffs, a_coeffs)
    p_coeffs = poly.add(e_coeffs, r_coeffs)
    return bytes(p_coeffs) + seed
