import hashlib
import os
import binascii
import hmac


def sha_random(size=160):
    return binascii.b2a_hex(os.urandom(size))[:size]


def derive(ikm, size, salt=None, info=None, hash=None):
    """Derive the input keyring material IKM to another key of the specified
    size, using additional info if provided"""
    hkdf = HKDF(salt=salt, hash=hash)
    return hkdf.derive(ikm, size, info)


class HKDF(object):
    """Implementation of the HMAC Key Derivation Function (HKDF) described
    on https://tools.ietf.org/html/rfc5869.
    """
    def __init__(self, salt='', hash=None):
        """
        :param salt: optional salt value (a non-secret random value).
                     If not provided, it is set to a string of Hashlen zeros.

        """
        self.hash = hash or hashlib.sha1
        self.hashlen = self.hash().digest_size

        self.salt = salt or chr(0) * (self.hashlen)
        self.okm = None

    def derive(self, ikm, size, info=None):
        prk = self.extract(ikm)
        return self.expand(prk, size, info)

    def extract(self, ikm):
        """
        Extract a pseudo random key (PRK) from the salt and the input keyring
        material (IKM)

        :param IKM: input keyring material

        Returns a pseudorandom key and its lenght
        """
        res = hmac.new(key=self.salt, msg=ikm, digestmod=self.hash)
        return res.digest()

    def expand(self, prk, size, info=None):
        """Expand the given pseudo random key (PRK) to give the output keyring
        material.

        :param prk: the pseudo rando mkey
        :param size: the size of the output keyring material
        :param info: optional context and application specific information
                     (empty per default)

        Returns the output keyring material (OKM)
        """
        if info is None:
            info = ""

        T, temp = "", ""

        i = 0x01
        while len(T) < size:
            msg = temp + info + chr(i)
            h = hmac.new(prk, msg, self.hash)
            temp = h.digest()
            i += 1
            T += temp

        self.okm = T[0:size]

        return self.okm


if __name__ == '__main__':
    salt = sha_random()
    hkdf = HKDF(salt=salt)
    key = 'somekey'

    print 'salt: %s' % salt
    print 'key: %s' % key
    print 'hkdfk: %s' % hkdf.derive(key, 128)