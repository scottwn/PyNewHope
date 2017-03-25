import poly
import params
import os
import hashlib

def encode_a(coefficients, seed):
    send = poly.to_bytes(coefficients)
    for i in range(0,params.NEWHOPE_SEEDBYTES):
        send.append(seed[i])
    return send

def keygen(sk):
    # 2200 bytes from SHAKE-128 function is enough data to get 1024 coefficients
    # smaller than 5q, from Alkim, Ducas, Pöppelmann, Schwabe section 7:
    shake_output = hashlib.shake_128().digest(2200)
    a_coeffs = []
    for i in range(0,params.N):
        j = 0
        coefficient = 5 * params.Q
        # Reject coefficients that are greater than or equal to 5q:
        while coefficient >= 5 * params.Q:
            coefficient = int.from_bytes(
                shake_output[j * 2:j * 2 + 2], byteorder = 'little')
            j++
        a_coeffs.append(coefficient)
    sk_coeffs = poly.get_noise()
    sk_coeffs = poly.poly_ntt(sk.coeffs)
    e_coeffs = poly.get_noise()
    e_coeffs = poly.poly_ntt(e.coeffs)
    r_coeffs = poly.pointwise(sk.coeffs, a.coeffs)
    pk_coeffs = poly.add(e.coeffs, r.coeffs)
    return encode_a(pk.coeffs, seed)
