from Crypto.Hash import SHA256

def gen_public_key(identity, pkg_public_key):
    """
    Returns the public key of an individual using the PKG Public Key
    If there are multiple PKGs, the pkg_public_key must be the
    same that the individual used to generate its own Private Key.
    """
    h = SHA256.new()
    h.update(identity.encode('utf-8'))
    h.update(pkg_public_key.encode('utf-8'))
    return h.hexdigest()

def encrypt(public_key, message):
    """
    Encrypts the especified message with a Random Session Key (RSK).
    The RSK is then encrypted with the individual's public key and 
    added to the encrypted text.
    """
    pass

def encrypt(identity, pkg_public_key, message):
    """
    Equivalent to encrypt(public_key, message) but will generate the
    individual's public key before calling encrypt.
    """
    public_key = make_public_key(identity, pkg_public_key)
    return encrypt(public_key, message)

def decrypt(secret_key, message):
    """
    Decrypts the message using the individual's Secret Key
    """
    pass

