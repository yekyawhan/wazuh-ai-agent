#!/bin/bash

# Wazuh Active Response - ai-disable-user.sh
# Disables a user account on Linux using usermod -L.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
LOG_FILE="/var/ossec/logs/active-responses.log"

# --- Functions ---
log_message() {
    echo "$(date 

disable_user() {
    log_message "Attempting to disable user: $USERNAME (Rule ID: $RULE_ID)"
    if id "$USERNAME" &>/dev/null; then
        usermod -L "$USERNAME"
        if [ $? -eq 0 ]; then
            log_message "User account 
        else
            log_message "ERROR: Failed to lock user account 
        fi
    else
        log_message "ERROR: User 
    fi
}

enable_user() {
    log_message "Attempting to enable user: $USERNAME (Rule ID: $RULE_ID)"
    if id "$USERNAME" &>/dev/null; then
        usermod -U "$USERNAME"
        if [ $? -eq 0 ]; then
            log_message "User account 
        else
            log_message "ERROR: Failed to unlock user account 
        fi
    else
        log_message "ERROR: User 
    fi
}

# --- Main Logic ---
read INPUT_JSON
log_message "Received JSON: $INPUT_JSON"

# Parse JSON input
COMMAND=$(echo "$INPUT_JSON" | jq -r 
USERNAME=$(echo "$INPUT_JSON" | jq -r 
RULE_ID=$(echo "$INPUT_JSON" | jq -r 

if [ -z "$USERNAME" ]; then
    log_message "ERROR: Username not found in JSON input. Cannot proceed with user account modification."
    exit 1
fi

case "$COMMAND" in
    add)
        disable_user
        ;;
    delete)
        enable_user
        ;;
    timeout)
        enable_user
        ;;
    *)
        log_message "ERROR: Unknown command 
        exit 1
        ;;
esac

exit 0
