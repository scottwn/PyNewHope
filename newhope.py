import poly
import params
import rand

def keygen(send, sk, rand):
    seed = rand.n(params.NEWHOPE_SEEDBYES) # function returns n random 8-bit unsigned integers
    a.coeffs = poly.uniform(seed)
    sk.coeffs = poly.getnoise()
