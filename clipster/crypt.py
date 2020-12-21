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

    HASH_ITERS_LOGIN = 20000
    HASH_ITERS_MSG = 10000
    HASH_LENGTH = 32
    fernet = None
    pw_hash_login = None
    pw_hash_msg = None

    def __init__(self, username, password, hash_login=None, hash_msg=None):
        """ Create / Set hashes to be used for login and crypto by hashing the
            user's password. Initialize Fernet with crypto hash

        Args:
            username (str): Login cleartext username
            password (str): Login cleartext password
            hash_login (str): PW Hash for authentication
            hash_msg (str): PW Hash for crypto
        """
        self.pw_hash_login = hash_login
        self.pw_hash_msg = hash_msg
        if password:
            salt = f"clipster_{username}_{password}".encode()
            password = password.encode()
            self.pw_hash_login = self.get_hash(password, salt, self.HASH_ITERS_LOGIN)
            self.pw_hash_msg = self.get_hash(password, salt, self.HASH_ITERS_MSG)
        self.fernet = Fernet(self.pw_hash_msg)

    def get_hash(self, password, salt, iterations):
        """ Create PBKDF2 Hash of password

        Args:
            password (str): Password to be hashed
            salt (str): Salt used in hashing
            iterations (int): Hash Iterations

        Returns:
            str: Base64 urlsafe hash
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.HASH_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        hashh = kdf.derive(password)
        hashh = base64.urlsafe_b64encode(hashh)
        return hashh.decode()

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
