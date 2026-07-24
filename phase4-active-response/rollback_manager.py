import json
import os
import datetime
import uuid
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# --- Configuration ---
LOG_FILE = "/var/ossec/logs/active-responses.log" # Wazuh AR log file
ROLLBACK_LOG_FILE = "/home/ubuntu/wazuh-phase4/rollback_actions.json"
ACTIVE_RESPONSE_SCRIPTS_PATH = "/home/ubuntu/wazuh-phase4/active-response/"

# --- Data Models ---
class ActionLogEntry(BaseModel):
    id: str
    timestamp: datetime.datetime
    action_type: str
    target: str
    status: str = "active"
    rollback_command: Optional[str] = None
    rollback_payload: Optional[dict] = None
    timeout_seconds: Optional[int] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    rule_id: Optional[str] = None

class LogActionRequest(BaseModel):
    action_type: str
    target: str
    rollback_command: Optional[str] = None
    rollback_payload: Optional[dict] = None
    timeout_seconds: Optional[int] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    rule_id: Optional[str] = None

# --- Helper Functions ---
def log_message(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")} rollback_manager.py: {message}\n")

def load_actions() -> List[ActionLogEntry]:
    if not os.path.exists(ROLLBACK_LOG_FILE):
        return []
    with open(ROLLBACK_LOG_FILE, "r") as f:
        data = json.load(f)
    return [ActionLogEntry(**entry) for entry in data]

def save_actions(actions: List[ActionLogEntry]):
    with open(ROLLBACK_LOG_FILE, "w") as f:
        json.dump([action.dict(by_alias=True) for action in actions], f, indent=2, default=str)

def execute_rollback_script(command: str, payload: dict):
    script_path = os.path.join(ACTIVE_RESPONSE_SCRIPTS_PATH, command)
    if not os.path.exists(script_path):
        log_message(f"ERROR: Rollback script not found: {script_path}")
        return False

    # Prepare the JSON payload for the script with command "delete"
    # Wazuh AR scripts expect a JSON with a "command" field
    payload_for_script = {"command": "delete", "parameters": {"alert": payload}}
    json_payload_str = json.dumps(payload_for_script)

    try:
        # Execute the script, passing JSON via stdin
        process = subprocess.run(
            ["bash", script_path], # Assuming bash for .sh scripts, adjust for .ps1
            input=json_payload_str.encode("utf-8"),
            capture_output=True,
            check=True
        )
        log_message(f"Rollback script {command} executed successfully. Stdout: {process.stdout.decode().strip()}, Stderr: {process.stderr.decode().strip()}")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"ERROR: Rollback script {command} failed. Stdin: {json_payload_str}, Stdout: {e.stdout.decode().strip()}, Stderr: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        log_message(f"ERROR: Failed to execute rollback script {command}. Error: {e}")
        return False

# --- API Endpoints ---
@app.post("/log_action", response_model=ActionLogEntry)
async def log_active_response_action(request: LogActionRequest):
    actions = load_actions()
    new_action = ActionLogEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now(),
        action_type=request.action_type,
        target=request.target,
        rollback_command=request.rollback_command,
        rollback_payload=request.rollback_payload,
        timeout_seconds=request.timeout_seconds,
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        rule_id=request.rule_id
    )
    actions.append(new_action)
    save_actions(actions)
    log_message(f"Logged new action: {new_action.id} - {new_action.action_type} on {new_action.target}")
    return new_action

@app.post("/rollback/{action_id}")
async def manual_rollback(action_id: str):
    actions = load_actions()
    action_found = False
    for action in actions:
        if action.id == action_id:
            action_found = True
            if action.status == "rolled_back":
                log_message(f"Action {action_id} already rolled back.")
                raise HTTPException(status_code=400, detail="Action already rolled back.")
            
            if not action.rollback_command or not action.rollback_payload:
                log_message(f"Action {action_id} has no defined rollback command or payload.")
                raise HTTPException(status_code=400, detail="No rollback command or payload defined for this action.")

            log_message(f"Attempting manual rollback for action {action_id}...")
            if execute_rollback_script(action.rollback_command, action.rollback_payload):
                action.status = "rolled_back"
                save_actions(actions)
                log_message(f"Manual rollback for action {action_id} successful.")
                return {"message": f"Rollback for action {action_id} successful.", "action": action}
            else:
                log_message(f"Manual rollback for action {action_id} failed.")
                raise HTTPException(status_code=500, detail="Rollback script execution failed.")
    
    if not action_found:
        raise HTTPException(status_code=404, detail="Action not found.")

@app.get("/actions", response_model=List[ActionLogEntry])
async def get_all_actions():
    return load_actions()

@app.get("/pending_rollbacks", response_model=List[ActionLogEntry])
async def get_pending_rollbacks():
    actions = load_actions()
    pending = []
    now = datetime.datetime.now()
    for action in actions:
        if action.status == "active" and action.timeout_seconds:
            # Calculate if timeout has passed. Assuming timestamp is UTC or consistent.
            time_elapsed = (now - action.timestamp).total_seconds()
            if time_elapsed >= action.timeout_seconds:
                pending.append(action)
    return pending

@app.post("/perform_auto_rollbacks")
async def perform_auto_rollbacks():
    actions = load_actions()
    rolled_back_count = 0
    now = datetime.datetime.now()
    updated_actions = []

    for action in actions:
        if action.status == "active" and action.timeout_seconds:
            time_elapsed = (now - action.timestamp).total_seconds()
            if time_elapsed >= action.timeout_seconds:
                if action.rollback_command and action.rollback_payload:
                    log_message(f"Attempting auto-rollback for action {action.id} (timeout reached)...")
                    if execute_rollback_script(action.rollback_command, action.rollback_payload):
                        action.status = "rolled_back"
                        rolled_back_count += 1
                        log_message(f"Auto-rollback for action {action.id} successful.")
                    else:
                        log_message(f"Auto-rollback for action {action.id} failed.")
                else:
                    log_message(f"Action {action.id} has no defined rollback command or payload for auto-rollback.")
        updated_actions.append(action)
    
    save_actions(updated_actions)
    return {"message": f"Attempted auto-rollbacks. {rolled_back_count} actions rolled back.", "rolled_back_count": rolled_back_count}

# To run this with uvicorn:
# uvicorn rollback_manager:app --host 0.0.0.0 --port 8000
