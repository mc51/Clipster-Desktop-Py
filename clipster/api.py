import requests
import pyperclip
import json

try:
    # for package import
    from .log_config import log
    from .config import Config
    from .crypt import Crypt
except ModuleNotFoundError:
    # for direct call of clipster.py
    from log_config import log
    from config import Config
    from crypt import Crypt


class ApiException(Exception):
    """ All exceptions occuring when dealing with API
    """

    pass


class RegisterException(Exception):
    """ Could not register user
    """

    pass


class LoginException(Exception):
    """ Could not login user
    """

    pass


class Api:
    """ Deal with API requests and local clipboard
    """

    SERVER = None
    USER = None
    HASH_LOGIN = None
    HASH_MSG = None
    crypto = None

    def __init__(self, server, user, hash_login, hash_msg):
        self.SERVER = server
        self.USER = user
        self.HASH_LOGIN = hash_login
        self.HASH_MSG = hash_msg
        self.crypto = Crypt(
            username=user, password=None, hash_login=hash_login, hash_msg=hash_msg
        )

    def copy(self):
        """
        Return the current clipboard text
        """
        data = pyperclip.paste()
        return data

    def upload(self):
        """
        Send the copied text to SERVER
        """
        clip = self.copy()
        clip_encrypted = self.crypto.encrypt(clip)
        payload = {"text": clip_encrypted, "device": f"{Config.DEVICE_ID}"}
        try:
            res = requests.post(
                self.SERVER + Config.API_COPY_PASTE,
                data=payload,
                auth=(self.USER, self.HASH_LOGIN),
                timeout=Config.CONN_TIMEOUT,
                verify=Config.VERIFY_SSL_CERT,
                headers=Config.HEADERS,
            )
        except requests.exceptions.RequestException as e:
            log.exception("Error in upload request")
            raise ApiException(e)
        else:
            if res.status_code == 201:
                log.info("Success! Copied to Cloud-Clipboard.")
                return clip
            else:
                log.error(f"Error cannot upload clip: {res.text}")
                raise ApiException(res.text[0 : Config.MAX_RESPONSE_LEN])

    def paste(self, data):
        """
        Copies 'data' to local clipboard which enables pasting.
        """
        pyperclip.copy(data)

    def download(self):
        """
        Downloads from SERVER and updates the local clipboard.
        """
        log.info("downloading clip")
        try:
            res = requests.get(
                self.SERVER + Config.API_COPY_PASTE,
                auth=(self.USER, self.HASH_LOGIN),
                timeout=Config.CONN_TIMEOUT,
                verify=Config.VERIFY_SSL_CERT,
                headers=Config.HEADERS,
            )
        except requests.exceptions.RequestException as e:
            log.exception("Error in download request")
            raise ApiException(e)
        else:
            if res.status_code == 200:
                clip = json.loads(res.text)["text"]
                clip = self.crypto.decrypt(clip)
                log.info(f"Got new clip from SERVER:\n{clip}")
                self.paste(clip)
                return clip
            else:
                log.error(f"Cannot download clip: {res.status_code} - {res.text}")
                raise ApiException(res.text[0 : Config.MAX_RESPONSE_LEN])

    @staticmethod
    def register(server, user, pw):
        """
        register user on server using hash generated from pw
        """
        crypto = Crypt(user, pw)
        login_hash = crypto.pw_hash_login
        payload = {"username": user, "password": login_hash}
        try:
            res = requests.post(
                server + Config.API_REGISTER,
                data=payload,
                timeout=Config.CONN_TIMEOUT,
                verify=Config.VERIFY_SSL_CERT,
                headers=Config.HEADERS,
            )
        except requests.exceptions.RequestException as e:
            log.exception("Error in register request")
            raise RegisterException(e)
        if res.status_code == 201:
            log.info(f"Hi {user}! You are all set.")
            return True
        else:
            log.error(f"Cannot register user: {res.status_code} - {res.text}")
            raise RegisterException(res.text[0 : Config.MAX_RESPONSE_LEN])

    @staticmethod
    def login(server, user, pw):
        """
        authenticate user using hash generated from pw
        """
        crypto = Crypt(user, pw)
        login_hash = crypto.pw_hash_login
        try:
            res = requests.get(
                server + Config.API_LOGIN,
                auth=(user, login_hash),
                timeout=Config.CONN_TIMEOUT,
                verify=Config.VERIFY_SSL_CERT,
                headers=Config.HEADERS,
            )
        except requests.exceptions.RequestException as e:
            log.exception("Error in login request")
            raise LoginException(e)
        if res.status_code >= 200 and res.status_code < 400:
            log.info("Login successful")
            return True
        else:
            log.error(f"Login failed: {res.status_code} - {res.text}")
            raise LoginException(res.text[0 : Config.MAX_RESPONSE_LEN])
