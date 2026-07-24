#!/bin/bash

# Wazuh Active Response - ai-isolate.sh
# Isolates a Linux host from the network using iptables.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
LOG_FILE="/var/ossec/logs/active-responses.log"
IPTABLES_CHAIN="WAZUH_ISOLATE"

# --- Functions ---
log_message() {
    echo "$(date '+%Y/%m/%d %H:%M:%S') ai-isolate.sh: $1" >> "$LOG_FILE"
}

add_isolation_rules() {
    log_message "Adding isolation rules for agent $AGENT_NAME ($AGENT_IP)"
    # Create a new chain for isolation rules if it doesn't exist
    iptables -N $IPTABLES_CHAIN 2>/dev/null

    # Drop all incoming and outgoing traffic
    iptables -A $IPTABLES_CHAIN -j DROP

    # Insert jump rule to the INPUT, FORWARD, and OUTPUT chains
    iptables -I INPUT -j $IPTABLES_CHAIN
    iptables -I FORWARD -j $IPTABLES_CHAIN
    iptables -I OUTPUT -j $IPTABLES_CHAIN

    log_message "Host $AGENT_NAME ($AGENT_IP) isolated."
}

delete_isolation_rules() {
    log_message "Deleting isolation rules for agent $AGENT_NAME ($AGENT_IP)"
    # Delete jump rules from INPUT, FORWARD, and OUTPUT chains
    iptables -D INPUT -j $IPTABLES_CHAIN 2>/dev/null
    iptables -D FORWARD -j $IPTABLES_CHAIN 2>/dev/null
    iptables -D OUTPUT -j $IPTABLES_CHAIN 2>/dev/null

    # Flush and delete the custom chain
    iptables -F $IPTABLES_CHAIN 2>/dev/null
    iptables -X $IPTABLES_CHAIN 2>/dev/null

    log_message "Host $AGENT_NAME ($AGENT_IP) network restored."
}

# --- Main Logic ---
read INPUT_JSON
log_message "Received JSON: $INPUT_JSON"

# Parse JSON input
COMMAND=$(echo "$INPUT_JSON" | jq -r '.command')
AGENT_IP=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.agent.ip')
AGENT_NAME=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.agent.name')
RULE_ID=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.rule.id')

if [ -z "$AGENT_IP" ]; then
    log_message "ERROR: Agent IP not found in JSON input. Cannot proceed with isolation."
    exit 1
fi

case "$COMMAND" in
    add)
        add_isolation_rules
        ;;
    delete)
        delete_isolation_rules
        ;;
    timeout)
        # For stateful active responses, 'timeout' command is also used to revert.
        # In this script, 'delete' handles the revert logic.
        delete_isolation_rules
        ;;
    *)
        log_message "ERROR: Unknown command '$COMMAND' received."
        exit 1
        ;;
esac

exit 0
