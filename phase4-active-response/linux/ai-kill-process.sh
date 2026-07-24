#!/bin/bash

# Wazuh Active Response - ai-kill-process.sh
# Kills a malicious process by name or PID on Linux.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
LOG_FILE="/var/ossec/logs/active-responses.log"

# --- Functions ---
log_message() {
    echo "$(date 

kill_process() {
    log_message "Attempting to kill process: $PROCESS_IDENTIFIER (Rule ID: $RULE_ID)"
    if [[ "$PROCESS_IDENTIFIER" =~ ^[0-9]+$ ]]; then
        # It's a PID
        if kill -9 "$PROCESS_IDENTIFIER"; then
            log_message "Process with PID $PROCESS_IDENTIFIER killed successfully."
        else
            log_message "ERROR: Failed to kill process with PID $PROCESS_IDENTIFIER."
        fi
    else
        # It's a process name
        if pkill -9 -f "$PROCESS_IDENTIFIER"; then
            log_message "Processes with name containing \"$PROCESS_IDENTIFIER\" killed successfully."
        else
            log_message "ERROR: Failed to kill processes with name containing \"$PROCESS_IDENTIFIER\"."
        fi
    fi
}

# --- Main Logic ---
read INPUT_JSON
log_message "Received JSON: $INPUT_JSON"

# Parse JSON input
COMMAND=$(echo "$INPUT_JSON" | jq -r 
PROCESS_IDENTIFIER=$(echo "$INPUT_JSON" | jq -r 
RULE_ID=$(echo "$INPUT_JSON" | jq -r 

if [ -z "$PROCESS_IDENTIFIER" ]; then
    log_message "ERROR: Process identifier (name or PID) not found in JSON input. Cannot proceed with killing process."
    exit 1
fi

case "$COMMAND" in
    add)
        kill_process
        ;;
    delete)
        # Killing a process is generally not reversible in a simple 'delete' action.
        # Log a message indicating this.
        log_message "INFO: Process killing is a destructive action and cannot be directly reverted by a 'delete' command."
        ;;
    timeout)
        log_message "INFO: Process killing is a destructive action and cannot be directly reverted by a 'timeout' command."
        ;;
    *)
        log_message "ERROR: Unknown command 
        exit 1
        ;;
esac

exit 0
