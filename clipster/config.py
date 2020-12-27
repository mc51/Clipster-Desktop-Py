import platform
import configparser
import PySimpleGUIQt as sg
from pathlib import Path

try:
    # for package import
    from .log_config import log
    from .crypt import Crypt
except ModuleNotFoundError:
    # for direct call of clipster.py
    from log_config import log
    from crypt import Crypt


class Config:

    APP_NAME = "Clipster"
    DEFAULT_SERVER_URI = "https://clipster.cc"
    SHOW_MESSAGE_DURATION = 2000
    CONN_TIMEOUT = 6
    MATCH_NONWHITESPACE = r"\S.*"
    MATCH_SERVER = (
        r"^(https):\/\/[^\s\/$.?#].[^\s]*|http://localhost:|http://127.0.0.1:"
    )
    DEVICE_ID = f"desktop_{platform.node()}"
    PATH_CONFIG_DIR = Path.home() / ".config/clipster/"
    PATH_CONFIG_FILE = PATH_CONFIG_DIR / "config"
    CONFIGFILE_MTIME = None
    MAX_NOTIFY_LEN = 60
    MAX_RESPONSE_LEN = 400
    MAX_CLIP_PREVIEW_LEN = 200

    HEADERS = {"Accept": "application/json"}
    API_COPY_PASTE = "/copy-paste/"
    API_REGISTER = "/register/"
    API_LOGIN = "/verify-user/"
    SERVER = None
    USER = None
    PW = None
    PW_HASH_LOGIN = None
    PW_HASH_MSG = None
    VERIFY_SSL_CERT = True

    def __init__(self):
        pass

    @classmethod
    def was_configfile_modified(cls):
        """ Check if configfile has been changed since last modificatiom
        """
        log.debug("Checking if configfile has been modified")
        if cls.CONFIGFILE_MTIME:
            mtime = Path(cls.PATH_CONFIG_FILE).stat().st_mtime
            if mtime > cls.CONFIGFILE_MTIME:
                return True
            else:
                return False
        cls.CONFIGFILE_MTIME = Path(cls.PATH_CONFIG_FILE).stat().st_mtime
        return False

    @classmethod
    def is_configfile_valid(cls):
        """ Check if we have a valid config, read it and save values
        """
        log.debug("Validating config")
        conf = configparser.ConfigParser()
        if cls.PATH_CONFIG_FILE.exists():
            conf.read(cls.PATH_CONFIG_FILE)
            try:
                cls.SERVER = conf.get("settings", "server")
                cls.USER = conf.get("settings", "username")
                cls.PW_HASH_LOGIN = conf.get("settings", "hash_login")
                cls.PW_HASH_MSG = conf.get("settings", "hash_msg")
                cls.VERIFY_SSL_CERT = conf.getboolean("settings", "verify_ssl_cert")
            except (configparser.NoSectionError, KeyError):
                return False
            if cls.SERVER and cls.USER and cls.PW_HASH_LOGIN and cls.PW_HASH_MSG:
                log.debug("Config ok")
                return True
        return False

    @classmethod
    def write_config(cls, server, username, password):
        """ Write config file and save modification time
        """
        log.debug(
            f"Writing config file: {server} {username} {password} {cls.VERIFY_SSL_CERT}"
        )
        crypto = Crypt(username, password)
        cls.PATH_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.PATH_CONFIG_FILE.touch(exist_ok=True)
        config = configparser.ConfigParser()
        config["settings"] = {
            "server": server,
            "username": username,
            "hash_login": crypto.pw_hash_login,
            "hash_msg": crypto.pw_hash_msg,
            "verify_ssl_cert": cls.VERIFY_SSL_CERT,
        }
        with open(cls.PATH_CONFIG_FILE, "w") as configfile:
            config.write(configfile)
        if not cls.CONFIGFILE_MTIME:
            cls.CONFIGFILE_MTIME = Path(cls.PATH_CONFIG_FILE).stat().st_mtime
        return True

    # PNG Icon 128x128 encoded with base64
    ICON_B64 = b"""iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
                WXMAAC4jAAAuIwF4pT92AAAAB3RJTUUH5AofFCUzT8cWAQAACRlJREFUeF7tnFtIFF8cx3+7rrne
                0jVXWZF0FQk1Y8XLahcI0x66EWQR9WI+SFbEBhFEGBRCEL1ZEEQ9RIGhRj0kBl2wmxe8RJqmheuW
                Ieuaa+3NVdff/yFanDMW5u4/Zz2/D3wfmjlzzpzffMzZM+PKEBGB4BY5u4HgCxKAc0gAziEBOIcE
                4BwSgHNIAM4hATiHBOAcEoBzSADOIQE4hwTgHBKAc0gAziEBOIcE4BwSgHNIAM4hATiHBOAcEoBz
                SADOIQE4hwTgHBKAc0gAziEBOIcE4BwSgHNIAM4hATiHBOAcEoBzSADOIQE4hwTgHBKAc0gAziEB
                OIcE4BwSgHNIAM4hATiHBOAcBbshUHC5XGC1WsFms0FfXx+Mjo7C8PAwOJ1OSEhIgKSkJEhPT4e4
                uDhQq9UQEhLCdvFHXC4XWCwWMJvNMDAwAEajESwWC0RFRUFiYiJoNBpIT0+HiIgIiImJ+ev+JQMG
                GF1dXXj8+HHMzc3FuLg4BIA/JiYmBvPz8/Hy5cs4MzPDdifCbrfj+fPnMScnB1evXi3qj41Go8GC
                ggI8ffo09vX1sd1JnoAQwOPxYH9/P+bk5IguwN8kMjISnz9/znbvpaGhAUNCQkTH/U2KiopweHgY
                PR4P270kkbwA3d3duHv3blGhfUl5ebngAjmdTty7d6+onS85ePAgDg0NzZuJNJG0AFeuXEGZTCYq
                rj+Sn5/vHWft2rWi/f6ITCbD27dvz5uR9JCkABMTE3jkyBFRQf2dXbt2YWFhoWi7v2MwGNDlcrHT
                lASSE+D79++YmZkpKmKgJz8/H51OJzvdZUdSApjNZkxJSREVb6WkoKAAJycn2WkvK5IRYGRkZEVf
                /F/JysrCb9++sdNfNiQhwNTUFGZkZIiKtVJTXFy8qDWJf8GyC2C3233+fB+IKSkpkcRawbIK4PF4
                8PDhw6Li8JJTp07h3NwcW5Z/yrIKcO7cOVFReEtNTQ1bln/KggLU19fjhQsX8NGjR+wuv1FTUyMq
                Bo+RyWRYV1fHlsdv1NXV4cWLF7GxsZHdhYjzBHA4HFhdXY1yuVxwggaDYX57v9DR0YGhoaGiYvCa
                NWvW4ODgIFsmn9m/f79gnIiICLx69argBtQrAHsXrlAosKSkBAEAe3t7vQf4ytDQEF38BaJWq9Fm
                s7HlWjKPHz9GgJ83m+xYW7du9bYDRMRjx44JGpSWlnob3Lt3D8+cOeP9ty+Mj49jWlqa6IQoP5Od
                nY12u50t25IoLS3FtrY2REScmZnBbdu2Cca6dOkSIiKCxWLBpKQk7w69Xj+/H0RErKqqYjctidzc
                XNGkKcLs2rWLLduSYH9oZ2dnBQ+91q9fjzabDaG/v19wAl1dXYIDEfGPz9AXw9TUFOr1etFkKQtn
                586dPn88XOia1dbWeseIiIhAo9GI8OzZM8Hg/mZ6ehq3b98umqQUkpycjAkJCaLtUsihQ4fYUvqM
                yWQSjPH+/XuEuro6wUar1coet2TMZjMmJiaKJieVfP36FTs6OkTbpZJ169ahw+Fgy7pkOjs7Bf33
                9PQgtLS0CDb+ujnwlYaGhkW9s7cciYqKEvyqa2pq8vlVsP8rWq0Wm5qa5lV26ZSXlwv67u/vRxgc
                HESFQuHdqFQq0Ww2s8cumpGRESwsLMSgoCDRZKSShV7eZH8VSinBwcFYUlLi06Pk3t5ewTVRqVT4
                +fNnhPHxcdRqtYIBExIS8MmTJzgxMcH2syBjY2P4+vVrya/rZ2VlocViYU/fi9FoFHwikmIqKiqw
                ra1t0Y+ULRYLPnz4EFUqlaCfDRs2oM1mQxki4r59++D+/fvAkpqaCjqdDrZs2QI6nQ5iY2Nh1apV
                YLPZwGQyQXd3N7x48QJMJhOYTCZARLYLyWAwGKC6uhrCw8PZXQImJyehsrISamtr2V2SQaFQQFJS
                EqSkpMCmTZsgJycHEhMTITw8HNxuN4yNjUFnZyc0NzdDb28vmEwmtgs4ceIE1NTUACAivnz5UmTa
                SolarcYHDx4IfioWw82bNzE6OlrU30rJx48fEXHeUjC7brwScvLkSfzy5Yv3ov4tg4ODWFZWJuo3
                0HP27FnvHL0C2Gw2jI+PFzUOxCQnJ+OHDx+8k/SV1tZWVKvVonECMZmZmYKXUwUrP01NTaIDAimF
                hYV4586d+VPyK9evX8fs7GzRuIESpVKJ7e3tgjmJlv4C8X4gOTkZm5ub0e12s9PxOy6XCxsbGzE2
                NlZ0HlJOcHDwgo+cRQIg/lxHZj8aSi0xMTG4Y8eO377o8C+ora3F4uLiRf0R6XImMzMTu7u72dNH
                xN8IgPjz0W1lZaWos+VORkYG3rp1C0dGRnx+YOIPZmdn0WQy4bVr1/63PzHzJVVVVX9cQPqtAL9o
                bm5GnU63bEulKpUK09LS0GAw4MDAAHt6kuPt27dYUVGBWq0Wo6KiRPP5FwkNDcWCggLs6elhT0+E
                DHFxqzcdHR1QV1cHN27cAKvVyu72G9HR0aDX62Hjxo2g1+tBq9VCamoqBAUFsU0lzfT0NHz69AmM
                RiO0tLTAmzdvoLW1FVwuF9vUb2g0Gjh69Cjs2bMHdDodu3tBFi3AfNrb2+Hu3btQX18PP378gNnZ
                WfB4PDA3NweICHNzc4L2crkcZDIZyGQyCAoKArlcDgqFAuRyOeTl5UFeXh5s3rwZioqKQKlUCo5d
                adhsNnj69Cm8evUK2tvb4d27d+DxeLz183g8gD//Z/5tHefXMDY2Fg4cOABlZWWQnp4uaL8YliTA
                fBwOB5hMJjCbzTAxMQFTU1MwMTEBbrcbAADCwsIgMjISwsLCQKlUQnx8PKhUKtBoNBAWFsb0xid2
                ux1GR0fBarWC2WwGt9sNDocD7HY7OJ1OkMvlEBIS4v0qGrVaDXFxcaDVan3+ahqfBSACG/qWMM4h
                ATiHBOAcEoBzSADOIQE4hwTgHBKAc0gAziEBOIcE4BwSgHNIAM4hATiHBOAcEoBzSADOIQE4hwTg
                HBKAc0gAziEBOIcE4BwSgHNIAM4hATiHBOAcEoBzSADOIQE4hwTgHBKAc0gAziEBOIcE4BwSgHNI
                AM4hATiHBOAcEoBzSADOIQE4hwTgHBKAc0gAzvkPY4FfWv2+aGoAAAAASUVORK5CYII=
                """
