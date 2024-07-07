#!/bin/bash

set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check mwinit
check_mwinit() {
    log "Checking mwinit..."
    if ! mwinit -l | grep -q .; then
        log "mwinit session is not active. Please run 'mwinit -s' and try again."
        exit 1
    fi
    log "mwinit check passed."
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

# Check and set AWS_PROFILE
check_aws_profile() {
    log "Checking AWS_PROFILE..."
    if [ -z "$AWS_PROFILE" ]; then
        USERNAME=$(whoami)
        PROFILE="${USERNAME}-Admin"
        if grep -q "\[profile ${PROFILE}\]" ~/.aws/config; then
            export AWS_PROFILE="${PROFILE}"
            log "AWS_PROFILE set to ${PROFILE}"
        else
            log "Warning: AWS_PROFILE not set and ${PROFILE} not found in ~/.aws/config"
        fi
    else
        log "AWS_PROFILE is set to $AWS_PROFILE"
    fi
    
    # Export AWS_PROFILE to ensure it's available to subprocesses
    export AWS_PROFILE
    
    # Debug: Print all AWS-related environment variables
    log "AWS-related environment variables:"
    env | grep AWS
}

# Check AWS identity
check_aws_identity() {
    log "Checking AWS identity..."
    
    # Debug: Print current AWS configuration
    log "Current AWS configuration:"
    aws configure list
    
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

main