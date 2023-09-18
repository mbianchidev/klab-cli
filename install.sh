#!/bin/bash

AWS_DOC_URL="https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html"
EKSCTL_DOC_URL="https://eksctl.io/introduction/#installation"
AZURE_DOC_URL="https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt"
GCP_DOC_URL="https://cloud.google.com/sdk/docs/install"
TF_DOC_URL="https://learn.hashicorp.com/tutorials/terraform/install-cli"

# Function to check if a command is available, kinda clunky but w/e
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install a package using apt-get and updating each time (slow? maybe)
install_with_apt() {
    sudo apt-get update
    sudo apt-get install -y "$1"
}

install_with_brew() {
    brew tap --repair
    brew update
    brew install "$1"
}

install_with_yum() {
    sudo yum update
    sudo yum install -y "$1"
}

install_with_dnf() {
    sudo dnf update
    sudo dnf install -y "$1"
}

install_with_zypper() {
    sudo zypper update
    sudo zypper install -y "$1"
}

install_req() {
    # Also sets the package manager variable
    if check_command "apt-get"; then
        PACKAGE_MANAGER="apt-get"
    elif check_command "brew"; then
        PACKAGE_MANAGER="brew"
    elif check_command "yum"; then
        PACKAGE_MANAGER="yum"
    elif check_command "dnf"; then
        PACKAGE_MANAGER="dnf"
    elif check_command "zypper"; then
        PACKAGE_MANAGER="zypper"
    else
        echo "Error: Unsupported package manager found."
        return 1
    fi

    packages=("$@")

    for package in "${packages[@]}"; do
        if ! check_command "$package"; then
            case $PACKAGE_MANAGER in
                "apt-get")
                    install_with_apt "$package"
                    ;;
                "yum")
                    install_with_yum "$package"
                    ;;
                "dnf")
                    install_with_dnf "$package"
                    ;;
                "zypper")
                    install_with_zypper "$package"
                    ;;
            esac
        fi
    done
}

check_install_brew() { 
    if ! check_command "brew"; then
        echo "Homebrew is not installed. Installing it now."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
}

# Install required packages and updates your packages
install_req "tar" "curl" "unzip"

# Function to prompt for user input, could it be done better? probably
get_architecture() {
    echo "Select your system architecture:"
    echo "0. Exit"
    echo "1. x64"
    echo "2. ARM"
    read -p "Enter the number corresponding to your choice: " choice

    case $choice in
        0)
            ARCHITECTURE="Unknown"
            ARCH="Unknown"
            ;;
        1)
            ARCHITECTURE="x64"
            ARCH="amd64"
            ;;
        2)
            ARCHITECTURE="ARM"
            ARCH="arm64"
            ;;
        *)
            echo "Invalid choice. Please select 1 or 2 (or 0 to exit)."
            get_architecture
            ;;
    esac
}

get_bash_config_file() {
    echo "Select your bash config file:"
    echo "0. Exit"
    echo "1. ~/.bashrc"
    echo "2. ~/.zshrc"
    read -p "Enter the number corresponding to your choice: " choice

    case $choice in
        0)
            BASH_CONFIG=""
            ;;
        1)
            BASH_CONFIG="~/.bashrc"
            ;;
        2)
            BASH_CONFIG="~/.zshrc"
            ;;
        *)
            echo "Invalid choice. Please select 1 or 2 (or 0 to exit)."
            get_bash_config_file
            ;;
    esac
}

# Get current directory and save it
CURRENT_DIR=$(pwd)
# Change to the home directory
cd ~

# Prompt the user for architecture choice
get_architecture

# Prompt the user for bash config choice
get_bash_config_file

get_os_info() {
    if [ -f "/etc/os-release" ]; then
        # Get the OS information from /etc/os-release
        source /etc/os-release
        OS_NAME="$NAME"
        OS_VERSION="$VERSION_ID"
        case "$ID" in
            ubuntu | debian)
                OS_TYPE="Debian/Ubuntu"
                ;;
            centos | rhel)
                OS_TYPE="RHEL/CentOS"
                ;;
            opensuse | opensuse-leap)
                OS_TYPE="Suse"
                ;;
            fedora)
                OS_TYPE="Fedora"
                ;;
            *)
                OS_TYPE="Unknown"
                ;;
        esac
    elif [ -f "/etc/redhat-release" ]; then
        # Check for RHEL/CentOS based on the /etc/redhat-release file
        OS_NAME="Red Hat Enterprise Linux or CentOS"
        OS_VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+\.[0-9]+' | head -1)
        OS_TYPE="RHEL/CentOS"
    elif [ -f "/etc/debian_version" ]; then
        # Check for Debian based on the /etc/debian_version file
        OS_NAME="Debian"
        OS_VERSION=$(cat /etc/debian_version)
        OS_TYPE="Debian/Ubuntu"
    elif [ -f "/etc/SuSE-release" ]; then
        # Check for Suse based on the /etc/SuSE-release file
        OS_NAME="OpenSuse"
        OS_VERSION=$(cat /etc/SuSE-release | grep -oE '[0-9]+\.[0-9]+' | head -1)
        OS_TYPE="Suse"
    else
        # Unable to determine the OS type
        OS_NAME="Unknown"
        OS_VERSION="Unknown"
        OS_TYPE="Unknown"
    fi
}

# Call the function to get the OS information
get_os_info

PLATFORM=$(uname -s)_$ARCH

echo "Detected OS type: $OS_TYPE"
echo "OS Name: $OS_NAME"
echo "OS Version: $OS_VERSION"
echo "Architecture: $ARCHITECTURE"
echo "Platform: $PLATFORM"
echo "Package manager: $PACKAGE_MANAGER"

# Check and install Python
if ! check_command "python3"; then
    case $ARCHITECTURE in
        "x64")
            install_with_apt "python3"
            ;;
        "ARM")
            # Replace with the appropriate package manager command for ARM architecture
            echo "Python for ARM is not currently supported in this script. Please install it manually."
            ;;
    esac
fi

# Check and install AWS CLI and eksctl
if ! check_command "aws"; then
    case $ARCHITECTURE in
        "x64")
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            ;;
        "ARM")
            curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
            ;;
    esac
    unzip awscliv2.zip
    sudo ./aws/install
    echo "AWS CLI (should be) installed. If something goes wrong, please install it manually referring to the doc: $AWS_DOC_URL"
    curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
    tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz
    . <(eksctl completion bash)
    echo "EKS CLI (should be) installed. If something goes wrong, please install it manually referring to the doc: $EKSCTL_DOC_URL"
    source $BASH_CONFIG
fi

# Check and install Azure CLI
if ! check_command "az"; then
    case $OS_TYPE in 
        "Debian/Ubuntu")
            sudo apt-get update
            sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg
            sudo mkdir -p /etc/apt/keyrings
            curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
            sudo chmod go+r /etc/apt/keyrings/microsoft.gpg
            AZ_REPO=$(lsb_release -cs)
            echo "deb [arch=`dpkg --print-architecture` signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
            sudo apt-get update
            sudo apt-get install azure-cli
            ;;
        "RHEL/CentOS")
            sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
            case "$OS_VERSION" in
                7)
                    echo "Running RHEL/CentOS version 7"
                    echo -e "[azure-cli]
                    name=Azure CLI
                    baseurl=https://packages.microsoft.com/yumrepos/azure-cli
                    enabled=1
                    gpgcheck=1
                    gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo
                    ;;
                8)
                    echo "Running RHEL/CentOS version 8"
                    sudo dnf install -y https://packages.microsoft.com/config/rhel/8/packages-microsoft-prod.rpm
                    ;;
                9)
                    echo "Running RHEL/CentOS version 9"
                    sudo dnf install -y https://packages.microsoft.com/config/rhel/9.0/packages-microsoft-prod.rpm
                    ;;
                *)
                    echo "Running an older/newer unsupported version of RHEL/CentOS (not 7,8 or 9): $OS_VERSION"
                    ;;
            esac
            sudo dnf install azure-cli
            ;;
        "Suse")
            sudo zypper install -y azure-cli
            ;;
        *)
            echo "OS type not supported: $OS_TYPE. Falling back to installing Azure CLI using curl."
            curl -L https://aka.ms/InstallAzureCli | bash
            ;;
    esac
    echo "Azure CLI (should be) installed. If something went wrong, please install it manually referring to the doc: $AZURE_DOC_URL"
    source $BASH_CONFIG
fi

add_gpg_key_google_cloud() {
    
    execute_commands() {
        local commands=("$@")
        local success=false
        for cmd in "${commands[@]}"; do
            if eval "$cmd"; then
                success=true
                break
            fi
        done
        return $success
    }

    commands=(
        'echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list'
        'echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list'
    )

    execute_commands "${commands[@]}"

    commands=(
        "curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -"
        "curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -"
        "curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo tee /usr/share/keyrings/cloud.google.gpg"
    )

    execute_commands "${commands[@]}"

    # Check if any command was successful
    if $success; then
        echo "GPG key added successfully."
    else
        echo "Error: Failed to add GPG key to the keyring."
    fi
}

# Check and install Google Cloud SDK (gcloud CLI and kubectl)
if ! check_command "gcloud"; then
    case $OS_TYPE in 
        "Debian/Ubuntu")
            sudo apt-get update
            sudo apt-get install apt-transport-https ca-certificates gnupg curl sudo
            echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
            # Call the function to add the GPG key for Google Cloud
            add_gpg_key_google_cloud
            install_with_apt "google-cloud-cli"
            ;;
        "RHEL/CentOS")
            el_version=""
            case "$OS_VERSION" in
                7)
                    echo "Running RHEL/CentOS version 7"
                    el_version="el7"
                    ;;
                8)
                    echo "Running RHEL/CentOS version 8"
                    el_version="el8"
                    ;;
                9)
                    echo "Running RHEL/CentOS version 9"
                    el_version="el9"
                    ;;
            esac
            sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo 
<< EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-"$el_version"-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
            sudo dnf install google-cloud-cli
            ;;
        "Fedora")
            sudo dnf install libxcrypt-compat.x86_64
            sudo dnf install google-cloud-cli
            ;;
        *) #every other case
        case $ARCHITECTURE in
            "x64")
                curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-444.0.0-linux-x86_64.tar.gz -o "google-cloud-sdk.tar.gz"
                ;;
            "ARM")
                curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-444.0.0-linux-arm.tar.gz -o "google-cloud-sdk.tar.gz"
                ;;
        esac
        tar -xf google-cloud-sdk.tar.gz
        ./google-cloud-sdk/install.sh --quiet
        rm -f google-cloud-sdk.tar.gz
        ;;
    esac
    echo "Google Cloud SDK (should be) installed. If something went wrong, please install it manually referring to the doc: $GCP_DOC_URL"
    source $BASH_CONFIG
    gcloud init --skip-diagnostics --no-launch-browser 
    # login via browser is not possible to automate unless using a complex system of mirrors and levers
fi

# Install terraform
## TODO remove terraform in favor of open-tf as soon as available
if ! check_command "terraform"; then
    case $OS_TYPE in 
        "Debian/Ubuntu")
            sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
            wget -O- https://apt.releases.hashicorp.com/gpg | \
            gpg --dearmor | \
            sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
            gpg --no-default-keyring \
            --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
            --fingerprint
            echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
            https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
            sudo tee /etc/apt/sources.list.d/hashicorp.list
            sudo apt update && sudo apt-get install terraform
            ;;
        "RHEL/CentOS")
            el_version=""
            case "$OS_VERSION" in
                7)
                    echo "Running RHEL/CentOS version 7"
                    el_version="el7"
                    ;;
                8)
                    echo "Running RHEL/CentOS version 8"
                    el_version="el8"
                    ;;
                9)
                    echo "Running RHEL/CentOS version 9"
                    el_version="el9"
                    ;;
            esac
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
            sudo yum -y install terraform
            ;;
        "Fedora")
            sudo dnf install -y dnf-plugins-core
            sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
            sudo dnf -y install terraform
            ;;
        *) #every other case
        check_install_brew
        brew tap hashicorp/tap
        brew install hashicorp/tap/terraform
        ;;
    esac
    terraform -install-autocomplete
    echo "Terraform (should be) installed. If something went wrong, please install it manually referring to the doc: $TF_DOC_URL"
    source $BASH_CONFIG
fi

# Check and install k9s
if ! check_command "k9s"; then
    check_install_brew
    brew tap derailed/k9s
    brew install derailed/k9s/k9s
fi

# Check and install cnquery by mondoo
if ! check_command "cnquery"; then
    bash -c "$(curl -sSL https://install.mondoo.com/sh)"
fi

pip install klab-cli

# Change back to the original directory
cd $CURRENT_DIR

echo "All required tools are installed. Thanks for choosing klab-cli!"

echo "  _______     _______     _______"
echo " /      /\\   /      /\\   /      /\\"
echo "/______/  \\ /______/  \\ /______/  \\"
echo "\\      \\  / \\      \\  / \\      \\  /"
echo " \\______\\/   \\______\\/   \\______\\/"
echo "           "   
echo " __  ___  __           ___      .______             ______  __       __ "
echo "|  |/  / |  |         /   \     |   _  \           /      ||  |     |  |"
echo "|  '  /  |  |        /  ^  \    |  |_)  |  ______ |  ,----'|  |     |  |"
echo "|    <   |  |       /  /_\  \   |   _  <  |______||  |     |  |     |  |"
echo "|  .  \  |  '----. /  _____  \  |  |_)  |         |  '----.|  '----.|  |"
echo "|__|\__\ |_______|/__/     \__\ |______/           \______||_______||__|"
echo "  _______     _______     _______"
echo " /      /\\   /      /\\   /      /\\"
echo "/______/  \\ /______/  \\ /______/  \\"
echo "\\      \\  / \\      \\  / \\      \\  /"
echo " \\______\\/   \\______\\/   \\______\\/"
echo "           "                                                                                          