import sys
import os
from pathlib import Path

try:
    # for package import
    from .config import Config
    from .log_config import log
    from .gui import Gui
    from .api import Api, ApiException
    from .crypt import Crypt
except ModuleNotFoundError:
    # for direct call of clipster.py
    from config import Config
    from log_config import log
    from gui import Gui
    from api import Api, ApiException
    from crypt import Crypt


def get_cred(mygui):
    """ Get credentials, check them and save to config
    """
    log.debug("Asking for credentials.")
    mygui.ask_for_cred()


def set_clip(mygui, api):
    """ Upload current clip to server and display tray notification
    """
    try:
        clip = api.upload()
    except ApiException as e:
        mygui.tray.show_message(
            f"{Config.APP_NAME} - Set Clip Error",
            f"Error setting Clip:\n{e}",
            data_base64=Config.ICON_B64,
            time=Config.SHOW_MESSAGE_DURATION,
        )
    else:
        mygui.tray.show_message(
            f"{Config.APP_NAME} - Set Clip",
            f"{clip[0:Config.MAX_NOTIFY_LEN]}",
            data_base64=Config.ICON_B64,
            time=Config.SHOW_MESSAGE_DURATION,
        )


def get_clip(mygui, api):
    """ Download clip from server and display tray notification
    """
    try:
        clip = api.download()
    except ApiException as e:
        mygui.tray.show_message(
            f"{Config.APP_NAME} - Get Clip Error",
            f"Error downloading Clip:\n{e}",
            data_base64=Config.ICON_B64,
            time=Config.SHOW_MESSAGE_DURATION,
        )
    else:
        mygui.tray.show_message(
            f"{Config.APP_NAME} - Got Clip",
            f"{clip[0:Config.MAX_NOTIFY_LEN]}",
            data_base64=Config.ICON_B64,
            time=Config.SHOW_MESSAGE_DURATION,
        )


def deal_with_tray_event(mygui, api, event):
    """ React to menu actions in tray
    """
    log.info(event)
    if event == "Get Clip":
        get_clip(mygui, api)
    elif event == "Set Clip":
        set_clip(mygui, api)
    elif event == "Edit Credentials":
        get_cred(mygui)
    elif event == "Exit":
        sys.exit(0)


def wait_for_tray_event(mygui, server, username, hash_login, hash_msg):
    """ Check for config modification while waiting for action in systray
    """
    log.debug("Main Loop\n")
    log.debug(f"{server} - {username} - {hash_login} - {hash_msg}")
    api = Api(server, username, hash_login, hash_msg)

    while True:
        if Config.was_configfile_modified():
            log.info("Configfile was modified.")
            self_restart()
        event = mygui.tray.read()
        deal_with_tray_event(mygui, api, event)


def self_restart():
    """ self restart after configuration change
    """
    log.debug("Restarting program")
    python = sys.executable
    os.execl(python, python, *sys.argv)


def main():
    """ Make sure config is valid and start main loop
    """
    mygui = Gui()
    while not Config.is_configfile_valid():
        log.debug("No valid config file")
        get_cred(mygui)
    wait_for_tray_event(
        mygui, Config.SERVER, Config.USER, Config.PW_HASH_LOGIN, Config.PW_HASH_MSG,
    )


if __name__ == "__main__":
    main()
