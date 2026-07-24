
import os
import json
import time
import random
from datetime import datetime, timedelta

# Placeholder for AI Agent API endpoint
AI_AGENT_API_URL = os.getenv("AI_AGENT_API_URL", "http://localhost:8000/process_alert")

def generate_fake_alert(scenario):
    """Generates a fake Wazuh-like alert based on a given scenario."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    agent_id = f"agent-{random.randint(1, 10)}"
    src_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    dst_ip = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"

    alert_template = {
        "timestamp": timestamp,
        "rule": {"level": 7, "description": "", "id": ""},
        "agent": {"id": agent_id, "name": f"server-{agent_id}"},
        "full_log": "",
        "location": "syslog"
    }

    if scenario == "brute_force":
        alert_template["rule"]["id"] = "5712"
        alert_template["rule"]["description"] = "SSH authentication failed."
        alert_template["full_log"] = f"sshd[{random.randint(1000, 9999)}]: Failed password for invalid user {random.choice(['admin', 'user', 'root'])} from {src_ip} port {random.randint(1024, 65535)} ssh2"
    elif scenario == "malware_detection":
        alert_template["rule"]["id"] = "80701"
        alert_template["rule"]["description"] = "YARA rule match - Possible malware detected."
        alert_template["full_log"] = f"File /tmp/malware.exe detected by YARA rule 'malware_signature_1' on host {agent_id} from {src_ip}"
    elif scenario == "lateral_movement":
        alert_template["rule"]["id"] = "60604"
        alert_template["rule"]["description"] = "Windows process created from suspicious source."
        alert_template["full_log"] = f"Sysmon: EventID 1: Process Create: \n  Image: C:\\Windows\\System32\\cmd.exe\n  ParentImage: C:\\Windows\\System32\\winrm.exe\n  User: DOMAIN\\{random.choice(['user1', 'svc_account'])}"
    elif scenario == "port_scan":
        alert_template["rule"]["id"] = "60101"
        alert_template["rule"]["description"] = "Nmap scan detected."
        alert_template["full_log"] = f"Nmap scan from {src_ip} targeting {dst_ip} on ports 21,22,23,80,443"
    else:
        alert_template["rule"]["id"] = "100000"
        alert_template["rule"]["description"] = "Generic test alert."
        alert_template["full_log"] = f"This is a generic test alert for scenario: {scenario}"

    return alert_template

def send_alert_to_ai_agent(alert):
    """Sends an alert to the AI Agent API and measures response time."""
    import requests # Import requests here to avoid global import if not always needed
    start_time = time.time()
    try:
        response = requests.post(AI_AGENT_API_URL, json=alert, timeout=10)
        response.raise_for_status()
        end_time = time.time()
        return response.json(), (end_time - start_time)
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        print(f"Error sending alert to AI Agent: {e}")
        return {"error": str(e)}, (end_time - start_time)

def run_simulation(num_alerts=100, scenarios=None):
    """Runs a simulation of various attack scenarios."""
    if scenarios is None:
        scenarios = ["brute_force", "malware_detection", "lateral_movement", "port_scan", "generic"]

    results = []
    print(f"Starting simulation with {num_alerts} alerts...")

    for i in range(num_alerts):
        scenario = random.choice(scenarios)
        fake_alert = generate_fake_alert(scenario)
        
        print(f"[{i+1}/{num_alerts}] Simulating {scenario}...")
        ai_response, response_time = send_alert_to_ai_agent(fake_alert)

        results.append({
            "scenario": scenario,
            "alert": fake_alert,
            "ai_response": ai_response,
            "response_time": response_time,
            "success": "error" not in ai_response
        })
        time.sleep(0.1) # Small delay to simulate real-world traffic

    return results

def analyze_results(results):
    """Analyzes simulation results and generates a report."""
    total_alerts = len(results)
    successful_responses = sum(1 for r in results if r["success"])
    failed_responses = total_alerts - successful_responses
    avg_response_time = sum(r["response_time"] for r in results) / total_alerts if total_alerts > 0 else 0

    # Placeholder for accuracy and false positive rate calculation
    # In a real system, this would compare AI decision with expected outcome for each scenario
    # For now, we'll just count successful API calls.
    
    print("\n--- Simulation Report ---")
    print(f"Total Alerts Simulated: {total_alerts}")
    print(f"Successful AI Agent Responses: {successful_responses}")
    print(f"Failed AI Agent Responses: {failed_responses}")
    print(f"Average Response Time: {avg_response_time:.4f} seconds")

    # Example of how you might start to calculate accuracy/FPR
    # This would require defining 'ground truth' for each scenario and comparing
    # the 'ai_response' to it.
    # For instance, if 'brute_force' scenario should result in 'block_ip' action.
    
    print("\nDetailed Results (first 5):")
    for i, r in enumerate(results[:5]):
        print(f"  Scenario: {r['scenario']}")
        print(f"  AI Response: {r['ai_response']}")
        print(f"  Response Time: {r['response_time']:.4f}s")
        print(f"  Success: {r['success']}")
        print("  ---")

    with open("simulation_report.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Full simulation results saved to simulation_report.json")

if __name__ == "__main__":
    num_alerts_to_simulate = int(os.getenv("NUM_ALERTS_TO_SIMULATE", "50"))
    simulation_results = run_simulation(num_alerts=num_alerts_to_simulate)
    analyze_results(simulation_results)
