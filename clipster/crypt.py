import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    # for package import
    from .log_config import log
    from .config import Config
except ModuleNotFoundError:
    # for direct call of clipster.py
    from log_config import log
    from config import Config


class EncryptException(Exception):
    """ All exceptions occuring when dealing with Crypt
    """

    pass


class DecryptException(Exception):
    """ All exceptions occuring when dealing with Crypt
    """

    pass


class Crypt:
    """ Symmetric encryption / decryption of clipboard data using Fernet
    """

    hash_iterations = 100000
    hash_length = 32
    fernet = None

    def __init__(self, username, password):
        """ create an encryption key by hashing the user's password and a salt
            use that to initialize Fernet

        Args:
            username (str): Login username
            password (str): Login password
        """
        salt = f"clipster_{password}_{username}".encode()
        password = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=self.hash_length,
            salt=salt,
            iterations=self.hash_iterations,
        )
        key = kdf.derive(password)
        key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(key)

    def encrypt(self, data):
        data = data.encode()
        encrypted = self.fernet.encrypt(data)
        return encrypted

    def decrypt(self, data):
        data = data.encode()
        clear = self.fernet.decrypt(data)
        clear = clear.decode()
        return clear
