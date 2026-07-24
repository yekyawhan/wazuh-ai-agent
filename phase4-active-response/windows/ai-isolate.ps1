param(
    [string]$json_input
)

# Wazuh Active Response - ai-isolate.ps1
# Isolates a Windows host from the network using Windows Firewall.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
$LOG_FILE = "C:\Program Files (x86)\ossec-agent\active-response\active-responses.log"
$FIREWALL_RULE_NAME = "Wazuh_Isolation_Rule"

# --- Functions ---
function Log-Message {
    param(
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy/MM/dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "$timestamp ai-isolate.ps1: $message"
}

function Add-IsolationRules {
    Log-Message "Adding isolation rules for agent $($AgentName) ($($AgentIP))"

    # Block all outbound traffic
    New-NetFirewallRule -DisplayName "$FIREWALL_RULE_NAME Outbound" -Direction Outbound -Action Block -Profile Any -ErrorAction SilentlyContinue
    # Block all inbound traffic
    New-NetFirewallRule -DisplayName "$FIREWALL_RULE_NAME Inbound" -Direction Inbound -Action Block -Profile Any -ErrorAction SilentlyContinue

    Log-Message "Host $($AgentName) ($($AgentIP)) isolated."
}

function Remove-IsolationRules {
    Log-Message "Removing isolation rules for agent $($AgentName) ($($AgentIP))"

    Remove-NetFirewallRule -DisplayName "$FIREWALL_RULE_NAME Outbound" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "$FIREWALL_RULE_NAME Inbound" -ErrorAction SilentlyContinue

    Log-Message "Host $($AgentName) ($($AgentIP)) network restored."
}

# --- Main Logic ---
Log-Message "Received JSON: $json_input"

try {
    $data = ConvertFrom-Json $json_input
} catch {
    Log-Message "ERROR: Decoding JSON has failed, invalid input format. Error: $($_.Exception.Message)"
    exit 1
}

$Command = $data.command
$AgentIP = $data.parameters.alert.agent.ip
$AgentName = $data.parameters.alert.agent.name
$RuleID = $data.parameters.alert.rule.id

if ([string]::IsNullOrEmpty($AgentIP)) {
    Log-Message "ERROR: Agent IP not found in JSON input. Cannot proceed with isolation."
    exit 1
}

switch ($Command) {
    "add" {
        Add-IsolationRules
    }
    "delete" {
        Remove-IsolationRules
    }
    "timeout" {
        Remove-IsolationRules
    }
    default {
        Log-Message "ERROR: Unknown command '$Command' received."
        exit 1
    }
}

exit 0
