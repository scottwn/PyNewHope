import params
import sha3 #need to implement

def poly_uniform(a, seed):
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
            a.coeffs[ctr++] = val
            #a is a polynomial, need to write this class
        pos += 2
        if pos > sha3.RATE * nblocks - 2:
            nblocks = 1
            buf = sha3.squeezeblocks(nblocks, state)
            pos = 0
