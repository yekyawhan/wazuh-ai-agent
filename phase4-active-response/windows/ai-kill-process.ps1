param(
    [string]$json_input
)

# Wazuh Active Response - ai-kill-process.ps1
# Kills a malicious process by name or PID on Windows.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
$LOG_FILE = "C:\Program Files (x86)\ossec-agent\active-response\active-responses.log"

# --- Functions ---
function Log-Message {
    param(
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy/MM/dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "$timestamp ai-kill-process.ps1: $message"
}

function Kill-Process {
    Log-Message "Attempting to kill process: $($ProcessIdentifier) (Rule ID: $($RuleID))"

    if ($ProcessIdentifier -match "^\d+$") {
        # It's a PID
        try {
            Stop-Process -Id ([int]$ProcessIdentifier) -Force -ErrorAction Stop
            Log-Message "Process with PID $($ProcessIdentifier) killed successfully."
        } catch {
            Log-Message "ERROR: Failed to kill process with PID $($ProcessIdentifier). Error: $($_.Exception.Message)"
        }
    } else {
        # It's a process name
        try {
            Get-Process -Name "$ProcessIdentifier" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction Stop
            Log-Message "Processes with name '$ProcessIdentifier' killed successfully."
        } catch {
            Log-Message "ERROR: Failed to kill processes with name '$ProcessIdentifier'. Error: $($_.Exception.Message)"
        }
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
$ProcessIdentifier = $data.parameters.alert.process_name # Assuming process_name or process_id will be passed
$RuleID = $data.parameters.alert.rule.id

if ([string]::IsNullOrEmpty($ProcessIdentifier)) {
    Log-Message "ERROR: Process identifier (name or PID) not found in JSON input. Cannot proceed with killing process."
    exit 1
}

switch ($Command) {
    "add" {
        Kill-Process
    }
    "delete" {
        Log-Message "INFO: Process killing is a destructive action and cannot be directly reverted by a 'delete' command."
    }
    "timeout" {
        Log-Message "INFO: Process killing is a destructive action and cannot be directly reverted by a 'timeout' command."
    }
    default {
        Log-Message "ERROR: Unknown command '$Command' received."
        exit 1
    }
}

exit 0
