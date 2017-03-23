import poly
import params
import os

def encode_a(coefficients, seed):
    send = poly.to_bytes(coefficients)
    for i in range(0,params.NEWHOPE_SEEDBYTES):
        send.append(seed[i])
    return send

def keygen(sk):
    seed = []
    for i in range(0,params.NEWHOPE_SEEDBYTES):
        seed.append(os.urandom(1))
    a.coeffs = poly.uniform(seed)
    sk.coeffs = poly.get_noise()
    sk.coeffs = poly.poly_ntt(sk.coeffs)
    e.coeffs = poly.get_noise()
    e.coeffs = poly.poly_ntt(e.coeffs)
    r.coeffs = poly.pointwise(sk.coeffs, a.coeffs)
    pk.coeffs = poly.add(e.coeffs, r.coeffs)
    return encode_a(pk.coeffs, seed)
