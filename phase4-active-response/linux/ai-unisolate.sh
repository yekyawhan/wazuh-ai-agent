#!/bin/bash
# This script is a placeholder. The un-isolation functionality is handled by the 'delete' command in ai-isolate.sh.
# Wazuh will call ai-isolate.sh with the 'delete' command for un-isolation.

LOG_FILE="/var/ossec/logs/active-responses.log"
log_message() {
    echo "$(date 
}

log_message "ai-unisolate.sh called. This script is a placeholder. Un-isolation is handled by ai-isolate.sh with the 'delete' command."

exit 0
