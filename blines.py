from hashlib import sha3_512
from string import ascii_letters, digits

DEEP_PARTS = ascii_letters + digits + "_-"


known_blins = {}


def blihash(secret):
    sha = sha3_512(secret.encode()).digest()
    byte_string = ''.join([format(s, '08b') for s in sha])
    hashed = []
    for i in range(0, len(byte_string), 6):
        chunk = byte_string[i:(i + 6)].zfill(6)
        index = int(chunk, 2)
        hashed.append(DEEP_PARTS[index])
    return ''.join(hashed)


def named_blin(name):
    nbl = blihash(name)
    blin = nbl[::4] + "BLIN" + nbl[1::15]
    known_blins[blin] = name
    return blin


# I knew you were evil.
# You win a mail inbox named "hacker@blin.host".
# Send message to @nkiselv.

named_blin('copyright')
named_blin('drop')
named_blin('etagblin')
named_blin('jwt')
named_blin('paraminjection')
named_blin('pathfinder')
named_blin('powermanager')
named_blin('pyhack')
named_blin('rmrf')
named_blin('sitemap')
named_blin('subdomain')
named_blin('sudo')
named_blin('uname')
named_blin('userlogin')
named_blin('visudo')
named_blin('xblin')
