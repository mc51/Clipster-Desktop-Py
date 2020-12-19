import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import InvalidToken

try:
    # for package import
    from .log_config import log
except ModuleNotFoundError:
    # for direct call of clipster.py
    from log_config import log


class EncryptException(Exception):
    """ All exceptions occuring when dealing with Crypt
    """


class DecryptException(Exception):
    """ All exceptions occuring when dealing with Crypt
    """


class Crypt:
    """ Symmetric encryption / decryption of clipboard data using Fernet
    """

    HASH_ITERATIONS = 10000
    HASH_LENGTH = 32
    fernet = None
    pw_hashed = None

    def __init__(self, username, password):
        """ create an encryption key by hashing the user's password and a salt
            use that to initialize Fernet

        Args:
            username (str): Login username
            password (str): Login password
        """
        salt = f"clipster_{username}_{password}".encode()
        password = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.HASH_LENGTH,
            salt=salt,
            iterations=self.HASH_ITERATIONS,
        )
        key = kdf.derive(password)
        key = base64.urlsafe_b64encode(key)
        self.pw_hashed = key.decode()
        self.fernet = Fernet(key)

    def encrypt(self, data):
        """ Returns encrypted text
        """
        data = data.encode()
        encrypted = self.fernet.encrypt(data)
        return encrypted

    def decrypt(self, data):
        """ Return encrypted text
        """
        data = data.encode()
        try:
            clear = self.fernet.decrypt(data)
        except InvalidToken as e:
            log.exception(f"ERROR Decrypt: {e}")
            clear = "Error: Could not decrypt received clip".encode()
        clear = clear.decode()
        return clear
