#!/bin/bash

# Wazuh Active Response - ai-block-ip.sh
# Blocks a malicious IP address using iptables/firewalld on Linux.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
LOG_FILE="/var/ossec/logs/active-responses.log"

# --- Functions ---
log_message() {
    echo "$(date 

add_block_rule() {
    log_message "Blocking IP: $SRC_IP (Rule ID: $RULE_ID)"
    # Check if firewalld is running
    if systemctl is-active --quiet firewalld;
    then
        firewall-cmd --permanent --add-rich-rule="rule family=\'ipv4\' source address=\'$SRC_IP\' drop"
        firewall-cmd --reload
        log_message "IP $SRC_IP blocked using firewalld."
    else
        # Use iptables if firewalld is not active
        iptables -I INPUT -s "$SRC_IP" -j DROP
        log_message "IP $SRC_IP blocked using iptables."
    fi
}

delete_block_rule() {
    log_message "Unblocking IP: $SRC_IP (Rule ID: $RULE_ID)"
    # Check if firewalld is running
    if systemctl is-active --quiet firewalld;
    then
        firewall-cmd --permanent --remove-rich-rule="rule family=\'ipv4\' source address=\'$SRC_IP\' drop"
        firewall-cmd --reload
        log_message "IP $SRC_IP unblocked using firewalld."
    else
        # Use iptables if firewalld is not active
        iptables -D INPUT -s "$SRC_IP" -j DROP 2>/dev/null
        log_message "IP $SRC_IP unblocked using iptables."
    fi
}

# --- Main Logic ---
read INPUT_JSON
log_message "Received JSON: $INPUT_JSON"

# Parse JSON input
COMMAND=$(echo "$INPUT_JSON" | jq -r 
SRC_IP=$(echo "$INPUT_JSON" | jq -r 
RULE_ID=$(echo "$INPUT_JSON" | jq -r 

if [ -z "$SRC_IP" ]; then
    log_message "ERROR: Source IP not found in JSON input. Cannot proceed with blocking."
    exit 1
fi

case "$COMMAND" in
    add)
        add_block_rule
        ;;
    delete)
        delete_block_rule
        ;;
    timeout)
        delete_block_rule
        ;;
    *)
        log_message "ERROR: Unknown command 
        exit 1
        ;;
esac

exit 0
