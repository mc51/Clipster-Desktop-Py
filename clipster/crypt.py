from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

try:
    # for package import
    from .log_config import log
    from .config import Config
except ModuleNotFoundError:
    # for direct call of clipster.py
    from log_config import log
    from config import Config


class Crypt:
    """encrypt and decrypt clips
    """

    iterations = 200000
    password = None
    fernet = None
    key = None

    def __init__(self, password):
        self.password = password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=password,
            iterations=self.iterations,
        )
        key = kdf.derive(password)
        print("KEY:", key)
        self.key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(self.key)

    def encrypt(self, data):
        token = self.fernet.encrypt(data)
        return token

    def decrypt(self, data):
        clear = self.fernet.decrypt(data)
        return clear
