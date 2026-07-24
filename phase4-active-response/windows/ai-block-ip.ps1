param(
    [string]$json_input
)

# Wazuh Active Response - ai-block-ip.ps1
# Blocks a malicious IP address using Windows Firewall.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
$LOG_FILE = "C:\Program Files (x86)\ossec-agent\active-response\active-responses.log"
$FIREWALL_RULE_PREFIX = "Wazuh_Block_IP_"

# --- Functions ---
function Log-Message {
    param(
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy/MM/dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "$timestamp ai-block-ip.ps1: $message"
}

function Add-BlockRule {
    Log-Message "Blocking IP: $($SrcIP) (Rule ID: $($RuleID))"
    $ruleName = "$($FIREWALL_RULE_PREFIX)$($SrcIP.Replace('.', '-'))"
    
    try {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Action Block -RemoteAddress $SrcIP -Profile Any -ErrorAction Stop
        New-NetFirewallRule -DisplayName "$($ruleName)_Outbound" -Direction Outbound -Action Block -RemoteAddress $SrcIP -Profile Any -ErrorAction Stop
        Log-Message "IP $($SrcIP) blocked using Windows Firewall."
    } catch {
        Log-Message "ERROR: Failed to block IP $($SrcIP). Error: $($_.Exception.Message)"
    }
}

function Remove-BlockRule {
    Log-Message "Unblocking IP: $($SrcIP) (Rule ID: $($RuleID))"
    $ruleName = "$($FIREWALL_RULE_PREFIX)$($SrcIP.Replace('.', '-'))"

    try {
        Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        Remove-NetFirewallRule -DisplayName "$($ruleName)_Outbound" -ErrorAction SilentlyContinue
        Log-Message "IP $($SrcIP) unblocked using Windows Firewall."
    } catch {
        Log-Message "ERROR: Failed to unblock IP $($SrcIP). Error: $($_.Exception.Message)"
    }
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
$SrcIP = $data.parameters.alert.srcip
$RuleID = $data.parameters.alert.rule.id

if ([string]::IsNullOrEmpty($SrcIP)) {
    Log-Message "ERROR: Source IP not found in JSON input. Cannot proceed with blocking."
    exit 1
}

switch ($Command) {
    "add" {
        Add-BlockRule
    }
    "delete" {
        Remove-BlockRule
    }
    "timeout" {
        Remove-BlockRule
    }
    default {
        Log-Message "ERROR: Unknown command 
        exit 1
    }
}

exit 0
