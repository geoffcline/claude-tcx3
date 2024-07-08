#!/bin/bash

# set -x

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check SSH connection to git.amazon.com
check_mwinit() {
    log "Checking SSH connection to git.amazon.com..."
    SSH_OUTPUT=$(ssh git.amazon.com -v 2>&1)
    if echo "$SSH_OUTPUT" | grep -q "Authenticated to git.amazon.com" || echo "$SSH_OUTPUT" | grep -q "Welcome to GitFarm"; then
        log "SSH connection to git.amazon.com successful."
    else
        log "SSH connection to git.amazon.com failed. Please ensure your credentials are set up correctly."
        log "You may need to run 'mwinit -s' to set up your session."
        log "SSH output for debugging:"
        echo "$SSH_OUTPUT"
        exit 1
    fi
}

# Check and install isengardcli
check_isengardcli() {
    log "Checking isengardcli..."
    if ! command_exists isengardcli; then
        log "isengardcli not found. Installing..."
        if ! command_exists toolbox; then
            log "Error: toolbox command not found. Please install toolbox and try again."
            exit 1
        fi
        toolbox install isengard-cli
    fi
    log "isengardcli check passed."
}

# Function to create AWS profile using isengardcli
create_aws_profile() {
    local username="$1"
    local profile="$2"
    log "Creating AWS profile '${profile}' for ${username}..."
    isengardcli add-profile --region us-west-1 --role Admin "${username}@amazon.com"
    if [ $? -eq 0 ]; then
        log "AWS profile '${profile}' created successfully."
        return 0
    else
        log "Failed to create AWS profile '${profile}'."
        return 1
    fi
}

# Check and set AWS_PROFILE
check_aws_profile() {
    log "Checking AWS_PROFILE..."
    if [ -z "$AWS_PROFILE" ]; then
        USERNAME=$(whoami)
        PROFILE="${USERNAME}-Admin"
        if grep -q "\[profile ${PROFILE}\]" ~/.aws/config; then
            export AWS_PROFILE="${PROFILE}"
            log "AWS_PROFILE set to '${PROFILE}'."
        else
            log "Warning: AWS_PROFILE not set and '${PROFILE}' not found in ~/.aws/config"
            read -p "Do you want to create a new AWS profile? (y/n): " CREATE_PROFILE
            if [[ $CREATE_PROFILE =~ ^[Yy]$ ]]; then
                if create_aws_profile "$USERNAME" "$PROFILE"; then
                    export AWS_PROFILE="${PROFILE}"
                    log "AWS_PROFILE set to '${PROFILE}'."
                else
                    log "Failed to create and set AWS_PROFILE. Please create it manually."
                    exit 1
                fi
            else
                log "AWS profile creation skipped. Please set up your AWS profile manually."
                exit 1
            fi
        fi
    else
        log "AWS_PROFILE is set to '$AWS_PROFILE'"
    fi
    log "Using AWS profile: '${AWS_PROFILE}'"
}

# Check AWS identity
check_aws_identity() {
    log "Checking AWS identity..."

    # Attempt to get caller identity
    CALLER_IDENTITY=$(aws sts get-caller-identity 2>&1)
    if [ $? -ne 0 ]; then
        log "Error: Failed to get AWS caller identity. Error message:"
        log "$CALLER_IDENTITY"
        exit 1
    fi

    log "AWS Caller Identity:"
    echo "$CALLER_IDENTITY"

    if ! echo "$CALLER_IDENTITY" | grep -q "Isengard"; then
        log "Error: 'Isengard' not found in the ARN."
        exit 1
    fi
    log "AWS identity check passed."
}

# Setup virtual environment
setup_venv() {
    log "Setting up virtual environment..."
    VENV_DIR="venv"
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log "Virtual environment created."
    fi
    source "$VENV_DIR/bin/activate"
    log "Virtual environment activated."
}

# Install requirements
install_requirements() {
    log "Installing requirements..."
    if [ ! -f "requirements.txt" ]; then
        log "Error: requirements.txt not found."
        exit 1
    fi
    pip install -r requirements.txt
    log "Requirements installed."
}

# Main execution
main() {
    log "Starting setup and verification..."
    check_mwinit
    check_isengardcli
    check_aws_profile
    check_aws_identity
    setup_venv
    install_requirements

    log "Setup and verification completed successfully."
}

# Run main function
main