#!/bin/bash
# This script is a placeholder. The unblock functionality is handled by the 'delete' command in ai-block-ip.sh.
# Wazuh will call ai-block-ip.sh with the 'delete' command for unblocking.

LOG_FILE="/var/ossec/logs/active-responses.log"
log_message() {
    echo "$(date 
}

log_message "ai-unblock-ip.sh called. This script is a placeholder. Unblocking is handled by ai-block-ip.sh with the 'delete' command."

exit 0
