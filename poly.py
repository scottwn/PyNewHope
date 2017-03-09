import params
import sha3 # need to implement
import rand # need to implement

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
    buf = rand.n(params.N * 4)
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
