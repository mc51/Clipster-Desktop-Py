import PySimpleGUIQt as sg
import re

try:
    # for package import
    from .config import Config
    from .log_config import log
    from .crypt import Crypt
    from .api import Api
    from .api import RegisterException, LoginException
except ModuleNotFoundError:
    # for direct call of clipster.py
    from config import Config
    from log_config import log
    from crypt import Crypt
    from api import Api
    from api import RegisterException, LoginException


class Gui:
    # Define Systray menu
    menu_def = [
        "BLANK",
        [
            "&Get last Clip",
            "Get &all Clips",
            "&Share Clip",
            "---",
            "&Edit Credentials",
            "---",
            "E&xit",
        ],
    ]

    # Define own color theme
    sg.LOOK_AND_FEEL_TABLE["Clipster"] = {
        "BACKGROUND": "1234567890",
        "TEXT": "1234567890",
        "INPUT": "1234567890",
        "TEXT_INPUT": "1234567890",
        "SCROLL": "1234567890",
        "BUTTON": ("white", "black"),
        "PROGRESS": ("#01826B", "#D0D0D0"),
        "BORDER": 1,
        "SLIDER_DEPTH": 1,
        "PROGRESS_DEPTH": 0,
    }

    tray = None
    def_server = Config.DEFAULT_SERVER_URI
    def_user = ""
    def_pw = ""

    def __init__(self):
        sg.theme("Clipster")
        self.tray = sg.SystemTray(menu=self.menu_def, data_base64=Config.ICON_B64)

    def create_cred_layout(self):
        """ Layouts in simplepyguy cannot be reused
            need to create new one when (re)-opening windows
            if valid, use configured credentials as default values
        """

        if Config.SERVER and Config.USER and Config.PW:
            self.def_server = Config.SERVER
            self.def_user = Config.USER
            self.def_pw = Config.PW

        layout = [
            [
                sg.Text("Server address: ", size=(30, 1)),
                sg.InputText(default_text=self.def_server, key="server", size=(25, 1)),
            ],
            [
                sg.Text("Disable SSL certificate check: ", size=(30, 1)),
                sg.Checkbox(
                    "(only check if using your own server)",
                    default=not Config.VERIFY_SSL_CERT,
                    key="ignore_cert",
                ),
            ],
            [
                sg.Text("Username: ", size=(30, 1)),
                sg.InputText(default_text=self.def_user, key="user", size=(25, 1)),
            ],
            [
                sg.Text("Password: ", size=(30, 1)),
                sg.InputText(default_text=self.def_pw, key="pw", size=(25, 1)),
            ],
            [sg.Text("")],
            [
                sg.Button("Login", size=(18, 1)),
                sg.Button("Register", size=(18, 1)),
                sg.Cancel(size=(18, 1)),
            ],
        ]
        return layout

    def show_clip_list_window(self, clips):
        """ Show all received clips in a Windows with a Listview and allow
            user select and copy an entry
        """
        # TODO: Show Only preview of Clip to reduce length
        layout = [
            [
                sg.Listbox(
                    values=clips,
                    size=(60, 6),
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key="sel_clip",
                )
            ],
            [sg.Button("Copy to clipboard", size=(20, 1)), sg.Cancel(size=(20, 1))],
        ]
        window = sg.Window(
            title=f"{Config.APP_NAME} - Your Clips",
            layout=layout,
            size=(600, 300),
            icon=Config.ICON_B64,
        )
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            log.debug("List Clips selection canceled")
            pass
        elif event == "Copy to clipboard":
            Api.paste(values.get("sel_clip")[0])
        window.close()

    def is_valid_server_address(self, server):
        """ Does server address match the format?
        """
        if not re.match(Config.MATCH_SERVER, server):
            return False
        return True

    def ask_for_cred(self):
        """ Create Windows asking for credentials
        """
        window = sg.Window(
            title=f"{Config.APP_NAME} - Enter credentials for registration / login",
            layout=self.create_cred_layout(),
            size=(500, 150),
            icon=Config.ICON_B64,
        )
        while not self.check_cred(window):
            pass
        log.debug("Ask for creds loop exited")
        window.close()
        return True

    def check_cred(self, window):
        """ Given credentials input check if we can perform action of
            login or registration on server

        Args:
            window (PySimpleGUIQt.Window): GUI-Window asking for creds

        Returns:
            bool: True if credentials are valid, else False
        """
        event, values = window.read()
        log.debug(f"{event} - {values}\n\n")
        if event in (sg.WIN_CLOSED, "Cancel"):
            log.debug("Credentials entry canceled")
            return True
        else:
            self.set_config_ignore_ssl_cert(values.get("ignore_cert"))
            if self.is_cred_input_valid(values):
                server, user, pw = self.is_cred_input_valid(values)
                if event == "Login":
                    if self.check_cred_login_and_save(server, user, pw):
                        sg.popup(
                            f"Credentials saved to config file: {Config.PATH_CONFIG_FILE}",
                            title=f"{Config.APP_NAME}",
                        )
                        return True
                elif event == "Register":
                    if self.check_cred_register_and_save(server, user, pw):
                        sg.popup(
                            f"Credentials saved to config file: {Config.PATH_CONFIG_FILE}",
                            title=f"{Config.APP_NAME}",
                        )
                    return True
        return False

    def set_config_ignore_ssl_cert(self, ignore_cert):
        """ Set config option to ignore ssl certificate validty in requests

        Args:
            ignore_cert (bool): Ignore SSL certificate
        """
        Config.VERIFY_SSL_CERT = not ignore_cert

    def is_cred_input_valid(self, values):
        """ Are credentials complete and server address valid?
        """
        server = values.get("server")
        if server == "":
            server = Config.DEFAULT_SERVER_URI
        user = values.get("user")
        pw = values.get("pw")
        if user == "" or pw == "":
            sg.popup(
                f"Please enter an username and password", title=f"{Config.APP_NAME}",
            )
            return False
        if not self.is_valid_server_address(server):
            sg.popup(
                f"Invalid server address: {server}\nUse format https://domain.tld:port",
                title=f"{Config.APP_NAME}",
            )
            return False
        if len(pw) < Config.MIN_PW_LENGTH:
            sg.popup(
                f"Your password must have at least 8 characters ",
                title=f"{Config.APP_NAME}",
            )
            return False
        log.debug(f"{server} - {user} - {pw}")
        return server, user, pw

    def check_cred_login_and_save(self, server, user, pw):
        """ Can we login using credentials? If so, save to configfile
        """
        try:
            Api.login(server, user, pw)
        except LoginException as e:
            log.error(f"Could not log in.\nPW: {pw}\nError: {e}")
            answer = sg.popup_yes_no(
                f"Login failed\n\nServer: {server}\nUser: {user}\nPassword: {pw}\n\n"
                f"Message: {e}\n\n"
                "Still save your credentials to the config file?",
                title=f"{Config.APP_NAME}",
            )
            if answer == "Yes":
                log.debug("Still saving creds")
                Config.write_config(server, user, pw)
                return True
            else:
                log.debug("Retry to login")
                return False
        else:
            log.debug("Logged in. Writing config")
            Config.write_config(server, user, pw)
            return True

    def check_cred_register_and_save(self, server, user, pw):
        """ Can we register using credentials? If so, save to configfile
        """
        try:
            Api.register(server, user, pw)
        except RegisterException as e:
            log.error(f"Could not register.\nPW: {pw}\nError: {e}")
            answer = sg.popup_yes_no(
                f"Registration failed\n\nServer: {server}\nUser: {user}\nPassword: {pw}\n\n"
                f"Message: {e}\n\n"
                "Still save your credentials to the config file?",
                title=f"{Config.APP_NAME}",
            )
            if answer == "Yes":
                log.debug("Still saving creds")
                Config.write_config(server, user, pw)
                return True
            else:
                log.debug("Retry to register")
                return False
        else:
            log.debug("Registration OK. Writing config")
            Config.write_config(server, user, pw)
            return True
