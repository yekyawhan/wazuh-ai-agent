
import json
import os
from collections import Counter

# Placeholder for AI Classifier - In a real scenario, this would be an API call or model inference
class AIClassifier:
    def __init__(self):
        # Initialize your AI model here
        pass

    def classify(self, alert_data):
        """Simulates AI classification of an alert."""
        # This is a mock classification. Replace with actual model inference.
        rule_id = alert_data.get("rule", {}).get("id")
        description = alert_data.get("rule", {}).get("description", "").lower()
        full_data = json.dumps(alert_data).lower()

        threat_type = "unknown"
        severity = "low"
        correct_response = "investigate"

        if "authentication failure" in description or "failed login" in full_data:
            threat_type = "brute_force"
            severity = "high"
            correct_response = "block_ip"
        elif "malware" in description or "virus" in full_data:
            threat_type = "malware"
            severity = "critical"
            correct_response = "isolate_host"
        elif "port scan" in description or "reconnaissance" in full_data:
            threat_type = "reconnaissance"
            severity = "medium"
            correct_response = "monitor_traffic"
        elif "ssh" in description and "login" in description:
            threat_type = "ssh_login"
            severity = "medium"
            correct_response = "review_logs"
        elif "sysmon" in description and "process creation" in description:
            threat_type = "process_creation"
            severity = "low"
            correct_response = "log_event"

        return {
            "threat_type": threat_type,
            "severity": severity,
            "correct_response": correct_response
        }

def load_alerts(input_file):
    """Loads alerts from a JSONL file."""
    alerts = []
    try:
        with open(input_file, 'r') as f:
            for line in f:
                alerts.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found.")
    return alerts

def save_labeled_data(output_file, labeled_data):
    """Saves labeled alerts to a JSONL file."""
    with open(output_file, 'w') as f:
        for item in labeled_data:
            f.write(json.dumps(item) + '\n')
    print(f"Labeled data saved to {output_file}")

def main():
    input_file = os.getenv("INPUT_FILE", "wazuh_alerts.jsonl")
    output_file = os.getenv("OUTPUT_FILE", "labeled_alerts.jsonl")

    alerts = load_alerts(input_file)
    if not alerts:
        print("No alerts to label. Exiting.")
        return

    classifier = AIClassifier()
    labeled_data = []
    threat_type_counts = Counter()
    severity_counts = Counter()
    response_counts = Counter()

    print(f"Starting labeling of {len(alerts)} alerts...")
    for i, alert in enumerate(alerts):
        # Simulate manual override (e.g., if a UI was present)
        # For this script, we'll just use AI classification
        classification = classifier.classify(alert)

        labeled_alert = {
            "original_alert": alert,
            "threat_type": classification["threat_type"],
            "severity": classification["severity"],
            "correct_response": classification["correct_response"],
            "labeled_by": "AI_classifier" # Could be "manual" if overridden
        }
        labeled_data.append(labeled_alert)

        threat_type_counts[classification["threat_type"]] += 1
        severity_counts[classification["severity"]] += 1
        response_counts[classification["correct_response"]] += 1

        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1} alerts...")

    save_labeled_data(output_file, labeled_data)

    print("\n--- Labeling Statistics ---")
    print("Threat Type Distribution:")
    for threat, count in threat_type_counts.most_common():
        print(f"  {threat}: {count}")

    print("\nSeverity Distribution:")
    for sev, count in severity_counts.most_common():
        print(f"  {sev}: {count}")

    print("\nCorrect Response Distribution:")
    for resp, count in response_counts.most_common():
        print(f"  {resp}: {count}")

if __name__ == '__main__':
    main()
