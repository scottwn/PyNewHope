import poly
import params
import rand

def encode_a(coefficients, seed):
    send = poly.to_bytes(coefficients)
    for i in range(0,params.NEWHOPE_SEEDBYTES):
        send.append(seed[i])
    return send

def keygen(sk, rand):
    seed = rand.n(params.NEWHOPE_SEEDBYES) # function returns n random 8-bit unsigned integers
    a.coeffs = poly.uniform(seed)
    sk.coeffs = poly.get_noise()
    sk.coeffs = poly.poly_ntt(sk.coeffs)
    e.coeffs = poly.get_noise()
    e.coeffs = poly.poly_ntt(e.coeffs)
    r.coeffs = poly.pointwise(sk.coeffs, a.coeffs)
    pk.coeffs = poly.add(e.coeffs, r.coeffs)
    return encode_a(pk.coeffs, seed)
