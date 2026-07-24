#!/bin/bash

# Wazuh Active Response - ai-collect-forensics.sh
# Collects forensic evidence (processes, connections, files, memory dump info) on Linux.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
LOG_FILE="/var/ossec/logs/active-responses.log"
FORENSICS_DIR="/var/ossec/active-response/forensics"

# --- Functions ---
log_message() {
    echo "$(date 

collect_evidence() {
    log_message "Collecting forensic evidence for agent $AGENT_NAME ($AGENT_IP) (Rule ID: $RULE_ID)"

    mkdir -p "$FORENSICS_DIR/$AGENT_NAME-$AGENT_IP-$RULE_ID-$(date +%Y%m%d%H%M%S)"
    LOCAL_FORENSICS_DIR="$FORENSICS_DIR/$AGENT_NAME-$AGENT_IP-$RULE_ID-$(date +%Y%m%d%H%M%S)"

    log_message "Saving forensics to: $LOCAL_FORENSICS_DIR"

    # Collect running processes
    ps aux > "$LOCAL_FORENSICS_DIR/processes.txt" 2>&1
    log_message "Collected running processes."

    # Collect network connections
    netstat -tulnp > "$LOCAL_FORENSICS_DIR/network_connections.txt" 2>&1
    log_message "Collected network connections."

    # Collect open files (lsof might require root privileges)
    lsof > "$LOCAL_FORENSICS_DIR/open_files.txt" 2>&1
    log_message "Collected open files."

    # Collect system information
    uname -a > "$LOCAL_FORENSICS_DIR/system_info.txt" 2>&1
    log_message "Collected system information."

    # Collect memory usage information (not a full memory dump)
    cat /proc/meminfo > "$LOCAL_FORENSICS_DIR/memory_info.txt" 2>&1
    log_message "Collected memory information."

    # Example: Collect specific log files (adjust as needed)
    # cp /var/log/auth.log "$LOCAL_FORENSICS_DIR/auth.log" 2>&1
    # cp /var/log/syslog "$LOCAL_FORENSICS_DIR/syslog" 2>&1

    log_message "Forensic evidence collection complete."
}

# --- Main Logic ---
read INPUT_JSON
log_message "Received JSON: $INPUT_JSON"

# Parse JSON input
COMMAND=$(echo "$INPUT_JSON" | jq -r 
AGENT_IP=$(echo "$INPUT_JSON" | jq -r 
AGENT_NAME=$(echo "$INPUT_JSON" | jq -r 
RULE_ID=$(echo "$INPUT_JSON" | jq -r 

if [ -z "$AGENT_IP" ]; then
    log_message "ERROR: Agent IP not found in JSON input. Cannot proceed with forensics collection."
    exit 1
fi

case "$COMMAND" in
    add)
        collect_evidence
        ;;
    delete)
        log_message "INFO: Forensic collection is a one-time action and does not have a direct \'delete\' command."
        ;;
    timeout)
        log_message "INFO: Forensic collection is a one-time action and does not have a direct \'timeout\' command."
        ;;
    *)
        log_message "ERROR: Unknown command 
        exit 1
        ;;
esac

exit 0
