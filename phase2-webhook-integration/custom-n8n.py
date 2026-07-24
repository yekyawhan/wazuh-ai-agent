
import json
import requests
import sys
import os
import logging
import time

# Configure logging
logging.basicConfig(filename='/var/ossec/logs/integrations.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

WEBHOOK_URL = "https://n8n.y3kh.dpdns.org/webhook/wazuh-alerts"
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 10

def send_alert_to_n8n(alert_data):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(WEBHOOK_URL, json=alert_data, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            logging.info(f"Successfully forwarded alert to n8n. Status Code: {response.status_code}")
            return True
        except requests.exceptions.Timeout:
            logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES}: Request timed out while sending alert to n8n.")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES}: Connection error while sending alert to n8n: {e}")
        except requests.exceptions.HTTPError as e:
            logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES}: HTTP error while sending alert to n8n: {e}")
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES}: An unexpected error occurred: {e}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY_SECONDS)
    logging.error(f"Failed to send alert to n8n after {MAX_RETRIES} attempts.")
    return False


if __name__ == "__main__":
    # Read alert data from stdin
    alert_json = sys.stdin.readline()

    try:
        alert = json.loads(alert_json)
        logging.info(f"Received alert: {alert.get('rule', {}).get('id')} - {alert.get('rule', {}).get('description')}")
        send_alert_to_n8n(alert)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from stdin: {alert_json}")
    except Exception as e:
        logging.error(f"Error processing alert: {e}")
