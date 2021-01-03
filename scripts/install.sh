#!/bin/sh
# MC51 - Install script for Clipster Desktop Client
# Borrowed stuff from the https://get.docker.com shell script
set -e
PYTHON_EXEC=python3

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

get_distribution() {
    lsb_dist=""
    # Every system that we officially support has /etc/os-release
    if [ -r /etc/os-release ]; then
        lsb_dist="$(. /etc/os-release && echo "$ID")"
    fi
    # Returning an empty string here should be alright since the
    # case statements don't act unless you provide an actual value
    echo "$lsb_dist"
}

is_darwin() {
    case "$(uname -s)" in
    *darwin* ) true ;;
    *Darwin* ) true ;;
    * ) false;;
    esac
}

check_forked() {
    # Check for lsb_release command existence, it usually exists in forked distros
    if command_exists lsb_release; then
        # Check if the `-u` option is supported
        set +e
        lsb_release -a -u > /dev/null 2>&1
        lsb_release_exit_code=$?
        set -e
        # Check if the command has exited successfully, it means we're in a forked distro
        if [ "$lsb_release_exit_code" = "0" ]; then
            # Print info about current distro
            echo "You're using '$lsb_dist' version '$dist_version'."
            # Get the upstream release info
            lsb_dist=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'id' | cut -d ':' -f 2 | tr -d '[:space:]')
            dist_version=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'codename' | cut -d ':' -f 2 | tr -d '[:space:]')
            # Print info about upstream distro
            echo "Upstream release is '$lsb_dist' version '$dist_version'."
        else
            if [ -r /etc/debian_version ] && [ "$lsb_dist" != "ubuntu" ] && [ "$lsb_dist" != "raspbian" ]; then
                if [ "$lsb_dist" = "osmc" ]; then
                    # OSMC runs Raspbian
                    lsb_dist=raspbian
                else
                    # We're Debian and don't even know it!
                    lsb_dist=debian
                fi
                dist_version="$(sed 's/\/.*//' /etc/debian_version | sed 's/\..*//')"
                case "$dist_version" in
                    10)
                        dist_version="buster"
                    ;;
                    9)
                        dist_version="stretch"
                    ;;
                    8|'Kali Linux 2')
                        dist_version="jessie"
                    ;;
                esac
            fi
        fi
    fi
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

install_reqs() {
    echo "INFO: To install requirements we will need root. Please enter your sudo / root password."

    # perform some very rudimentary platform detection
    lsb_dist=$( get_distribution )
    lsb_dist="$(echo "$lsb_dist" | tr "[:upper:]" "[:lower:]")"

    case "$lsb_dist" in

        ubuntu)
            if command_exists lsb_release; then
                dist_version="$(lsb_release --codename | cut -f2)"
            fi
            if [ -z "$dist_version" ] && [ -r /etc/lsb-release ]; then
                dist_version="$(. /etc/lsb-release && echo "$DISTRIB_CODENAME")"
            fi
        ;;

        debian|raspbian)
            dist_version="$(sed 's/\/.*//' /etc/debian_version | sed 's/\..*//')"
            case "$dist_version" in
                10)
                    dist_version="buster"
                ;;
                9)
                    dist_version="stretch"
                ;;
                8)
                    dist_version="jessie"
                ;;
            esac
        ;;

        centos|rhel)
            if [ -z "$dist_version" ] && [ -r /etc/os-release ]; then
                dist_version="$(. /etc/os-release && echo "$VERSION_ID")"
            fi
        ;;

        *)
            if command_exists lsb_release; then
                dist_version="$(lsb_release --release | cut -f2)"
            fi
            if [ -z "$dist_version" ] && [ -r /etc/os-release ]; then
                dist_version="$(. /etc/os-release && echo "$VERSION_ID")"
            fi
        ;;

    esac

    # Check if this is a forked Linux distro
    check_forked
    packages="xsel"
    # Run setup for each distro accordingly
    case "$lsb_dist" in

        ubuntu|debian|raspbian)
            $sh_c "apt-get update"
            $sh_c "apt-get install $packages"
        ;;
        centos|fedora|rhel)
            if [ "$lsb_dist" = "fedora" ]; then
                pkg_manager="dnf"
            else
                pkg_manager="yum"
            fi
            $sh_c "$pkg_manager install $packages"
        ;;
        *)
            if [ -z "$lsb_dist" ]; then
                if is_darwin; then
                    echo
                    echo "ERROR: Unsupported operating system 'macOS'"
                    echo
                    exit 1
                fi
            fi
            echo
            echo "ERROR: Unsupported distribution '$lsb_dist'"
            echo
            exit 1
            ;;
    esac
    # exit 0
}

userid="$(id -u 2>/dev/null || true)"
sh_c="sh -c"
if [ "$userid" -ne 0 ]; then
    if command_exists sudo; then
        sh_c="sudo -E sh -c"
    elif command_exists su; then
        sh_c="su -c"
    else
        echo
        echo "ERROR: installer needs the ability to run commands as root to install requirements."
        echo "Unable to find either "sudo" or "su" to make this happen."
        exit 1
    fi
fi

echo
echo "OK: Running as user $USER"
echo

if command_exists clipster; then
    echo "WARNING: The command \"clipster\" already exists. Make sure to remove / deactivate previous installations."
    echo
    confirm
else
    echo "OK: No previous clipster installation found."
fi


if command_exists $PYTHON_EXEC; then
    ver=$(${PYTHON_EXEC} -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
    while [ "$ver" -lt "36" ]; do
        echo
        echo "ERROR: This package requires python 3.6 or greater. Your python3 executable is only $ver "
        echo
        read -r -p "Enter path or name to a different python version [e.g. /usr/bin/python3.7]:  " PYTHON_EXEC
        ver=$(${PYTHON_EXEC} -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
    done
        echo
        echo "OK: Using Python $ver"
    if ${PYTHON_EXEC} -m pip -V; then
        echo
        echo "OK: Found pip. Ready to install clipster-desktop python package and requirements"
        set +e
        ${PYTHON_EXEC} -m pip install --user .
        if [ $? -ne 0 ]; then
            # pip install --user will fail in virtualenvs, catch error and try again without it
            echo
            echo "ERROR: When using a virtualenv, we can't use pip install --user. Trying again without it..."
            set -e
            ${PYTHON_EXEC} -m pip install .
        fi
    else
        echo
        echo "ERROR: Could not find pip, which is required. Learn how to install it here: https://pip.pypa.io/en/stable/installing/"
        exit 1
    fi
else
    echo
    echo "ERROR: Coult not find $PYTHON_EXEC exectuable. Make sure python is available "
    echo
fi

if command_exists xsel || command_exists xclip || is_darwin; then
    echo
    echo "OK: Found \"xsel\" or \"xclip\" command."
else
    echo
    echo "INFO: We need the \"xsel\" or \"xclip\" packages but they were not found. Trying to install \"xsel\" first."
    install_reqs
fi

# Write service file
# Get path to executable
PATH_CLIPSTER=$(which clipster)
echo
echo "OK: Found \"clipster\" command in $PATH_CLIPSTER."
echo
echo "INFO: Creating /etc/systemd/system/clipster.service file autostart."

# Write Systemd config file for auto loading script
echo "
[Unit]
Description=Clipster - A Multi Platform Cloud Clipboard
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
    echo "OK: Installation completed. Clipster is running."
    echo
    exit 0
else
    echo
    echo "ERROR: Installation failed. Clipster daemon is not running."
    echo
    exit 1
fi
