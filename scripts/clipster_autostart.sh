#!/bin/sh
# MC51 - Install script for Clipster Desktop Client
# Install autostart for pip installed pip package

set -e

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

is_darwin() {
    case "$(uname -s)" in
    *darwin* ) true ;;
    *Darwin* ) true ;;
    * ) false;;
    esac
}

confirm() {
    # call with a prompt string or use a default
    read -r -p "${1:-Do you want to continue? [y/N]} " response
    echo ""
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}


echo
echo "*** Clipster - Script for autostart installation ***"
echo

if is_darwin; then
    echo
    echo "ERROR: This script only support Linux. It seems you are on MacOS"
    echo
fi

userid="$(id -u 2>/dev/null || true)"
sh_c="sh -c"
if [ "$userid" -ne 0 ]; then
    if command_exists sudo; then
        sh_c="sudo -E sh -c"
    elif command_exists su; then
        sh_c="su -c"
    else
        echo
        echo "ERROR: installer needs the ability to run commands as root"
        echo "Unable to find either "sudo" or "su" to make this happen."
        echo
        exit 1
    fi
fi

if command_exists clipster; then
    PATH_CLIPSTER=$(which clipster)
    echo
    echo "OK: Found \"clipster\" command here: $PATH_CLIPSTER"
else
    echo
    echo "ERROR: Could not find clipster command. Make sure your clipster-desktop installation is complete"
    echo "ERROR: Also, make sure to use the same virtualenv you installed clipster in, to call this script"
    echo
    exit 1
fi

# Write service file
# Get path to executable

echo
echo "INFO: Creating /etc/systemd/system/clipster.service to autostart clipster with systemd"
echo "INFO: We need to create this as root. The sudo command will be used for that"
echo "INFO: You'll need to provide your password"
echo

# Write Systemd config file for auto loading script
echo "
[Unit]
Description=Clipster Desktop - A Multi Platform Cloud Clipboard
After=network.target

[Service]
WorkingDirectory=/tmp
ExecStart=$PATH_CLIPSTER
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=always
RestartSec=1
User=$USER

[Install]
WantedBy=multi-user.target" | $sh_c "tee /etc/systemd/system/clipster.service"

echo
echo "INFO: running \"systemctl daemon-reload\" to reload systemd daemon config."
$sh_c "systemctl daemon-reload"
echo
echo "INFO: running \"systemctl enable clipster\" to enable autostart of clipster as daemon."
$sh_c "systemctl enable clipster"
echo
echo "INFO: running \"systemctl start clipster\" to start clipster daemon."
$sh_c "systemctl stop clipster"
$sh_c "systemctl start clipster"
echo
echo "INFO: running \"systemctl status clipster\" to check if clipster is running."

if $sh_c "systemctl status clipster"; then
    echo
    echo "OK: Installation completed. Clipster is running and will autostart from now on."
    echo
    exit 0
else
    echo
    echo "ERROR: Installation failed. Clipster daemon is not running."
    echo
    exit 1
fi
