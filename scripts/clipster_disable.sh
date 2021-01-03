#!/bin/sh
# MC51 - Uninstall script for Clipster Desktop Client
# Remove clipster service from systemd

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

echo
echo "*** Clipster - Disabling autostart via systemd ***"
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


# Disable
echo
echo "INFO: Removing /etc/systemd/system/clipster.service to disable clipster autostart via systemd"
echo "INFO: We need root rights to do this. The sudo command will be used for that"
echo "INFO: You'll need to provide your password"
echo

echo "INFO: running \"systemctl stop clipster\" to stop clipster daemon"
$sh_c "systemctl stop clipster"
echo
echo "INFO: running \"systemctl disable clipster\" to disable autostart of clipster as daemon"
$sh_c "systemctl disable clipster"
echo
echo "INFO: running \"systemctl daemon-reload\" to reload systemd daemon config"
$sh_c "systemctl daemon-reload"
echo
echo "OK: Disabled clipster autostart via systemd"
echo "INFO: To enable again, run the \"clipster_enable.sh\" command"
echo
exit 0
