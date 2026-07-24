param(
    [string]$json_input
)

# Wazuh Active Response - ai-collect-forensics.ps1
# Collects forensic evidence (processes, connections, files, memory dump info) on Windows.
# This script is designed to be called by Wazuh Active Response.

# --- Configuration ---
$LOG_FILE = "C:\Program Files (x86)\ossec-agent\active-response\active-responses.log"
$FORENSICS_BASE_DIR = "C:\Program Files (x86)\ossec-agent\active-response\forensics"

# --- Functions ---
function Log-Message {
    param(
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy/MM/dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "$timestamp ai-collect-forensics.ps1: $message"
}

function Collect-Evidence {
    Log-Message "Collecting forensic evidence for agent $($AgentName) ($($AgentIP)) (Rule ID: $($RuleID))"

    $currentDateTime = Get-Date -Format "yyyyMMddHHmmss"
    $LOCAL_FORENSICS_DIR = Join-Path $FORENSICS_BASE_DIR "$($AgentName)-$($AgentIP)-$($RuleID)-$currentDateTime"

    try {
        New-Item -ItemType Directory -Path $LOCAL_FORENSICS_DIR -ErrorAction Stop | Out-Null
        Log-Message "Saving forensics to: $LOCAL_FORENSICS_DIR"

        # Collect running processes
        Get-Process | Select-Object Name, Id, Path, StartTime, CPU, WorkingSet | Export-Csv -Path (Join-Path $LOCAL_FORENSICS_DIR "processes.csv") -NoTypeInformation -ErrorAction SilentlyContinue
        Log-Message "Collected running processes."

        # Collect network connections
        Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | Export-Csv -Path (Join-Path $LOCAL_FORENSICS_DIR "network_connections.csv") -NoTypeInformation -ErrorAction SilentlyContinue
        Get-NetUDPEndpoint | Select-Object LocalAddress, LocalPort, OwningProcess | Export-Csv -Path (Join-Path $LOCAL_FORENSICS_DIR "udp_connections.csv") -NoTypeInformation -ErrorAction SilentlyContinue
        Log-Message "Collected network connections."

        # Collect system information
        Get-ComputerInfo | Out-File -FilePath (Join-Path $LOCAL_FORENSICS_DIR "system_info.txt") -ErrorAction SilentlyContinue
        Log-Message "Collected system information."

        # Collect memory usage information (not a full memory dump, but general info)
        Get-Counter 
        Log-Message "Collected memory information."

        # Example: Collect specific log files (adjust as needed)
        # Copy-Item -Path "C:\Windows\System32\winevt\Logs\System.evtx" -Destination (Join-Path $LOCAL_FORENSICS_DIR "System.evtx") -ErrorAction SilentlyContinue
        # Copy-Item -Path "C:\Windows\System32\winevt\Logs\Security.evtx" -Destination (Join-Path $LOCAL_FORENSICS_DIR "Security.evtx") -ErrorAction SilentlyContinue

        Log-Message "Forensic evidence collection complete."
    } catch {
        Log-Message "ERROR: Failed during forensic collection. Error: $($_.Exception.Message)"
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
$AgentIP = $data.parameters.alert.agent.ip
$AgentName = $data.parameters.alert.agent.name
$RuleID = $data.parameters.alert.rule.id

if ([string]::IsNullOrEmpty($AgentIP)) {
    Log-Message "ERROR: Agent IP not found in JSON input. Cannot proceed with forensics collection."
    exit 1
}

switch ($Command) {
    "add" {
        Collect-Evidence
    }
    "delete" {
        Log-Message "INFO: Forensic collection is a one-time action and does not have a direct \'delete\' command."
    }
    "timeout" {
        Log-Message "INFO: Forensic collection is a one-time action and does not have a direct \'timeout\' command."
    }
    default {
        Log-Message "ERROR: Unknown command 
        exit 1
    }
}

exit 0
