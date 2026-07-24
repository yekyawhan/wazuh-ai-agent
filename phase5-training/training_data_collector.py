
import os
import json
import requests
from datetime import datetime, timedelta

# Configuration from environment variables
WAZUH_MANAGER_IP = os.getenv('WAZUH_MANAGER_IP', '172.17.0.1')
WAZUH_API_PORT = os.getenv('WAZUH_API_PORT', '55000')
WAZUH_API_USER = os.getenv('WAZUH_API_USER', 'wazuh-api-user')
WAZUH_API_PASSWORD = os.getenv('WAZUH_API_PASSWORD', 'wazuh-api-password')

OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'wazuh_alerts.jsonl')
DAYS_TO_EXPORT = int(os.getenv('DAYS_TO_EXPORT', '30'))
MIN_ALERTS_TARGET = int(os.getenv('MIN_ALERTS_TARGET', '10000'))

# Wazuh API URL
WAZUH_API_BASE_URL = f'https://{WAZUH_MANAGER_IP}:{WAZUH_API_PORT}'

def get_wazuh_token():
    """Authenticates with Wazuh API and returns an access token."""
    auth_url = f'{WAZUH_API_BASE_URL}/security/user/authenticate'
    try:
        response = requests.post(auth_url, auth=(WAZUH_API_USER, WAZUH_API_PASSWORD), verify=False)
        response.raise_for_status()
        return response.json().get('data', {}).get('token')
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating with Wazuh API: {e}")
        return None

def export_alerts(token, output_file, days_to_export, min_alerts_target):
    """Exports historical Wazuh alerts to a JSONL file."""
    headers = {'Authorization': f'Bearer {token}'}
    alerts_count = 0

    with open(output_file, 'w') as f:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_to_export)

        # Wazuh API expects dates in 'YYYY-MM-DDTHH:MM:SS' format
        start_time_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

        # Initial query parameters
        limit = 500  # Max alerts per request
        offset = 0

        print(f"Exporting alerts from {start_time_str} to {end_time_str}...")

        while True:
            query_params = {
                'limit': limit,
                'offset': offset,
                'from': start_time_str,
                'to': end_time_str,
                'sort': '-timestamp' # Sort by timestamp descending
            }
            alerts_url = f'{WAZUH_API_BASE_URL}/alerts/archives'
            try:
                response = requests.get(alerts_url, headers=headers, params=query_params, verify=False)
                response.raise_for_status()
                data = response.json().get('data', {})
                alerts = data.get('affected_items', [])
                total_items = data.get('total_affected_items', 0)

                if not alerts:
                    break

                for alert in alerts:
                    f.write(json.dumps(alert) + '\n')
                    alerts_count += 1

                print(f"Exported {alerts_count} of {total_items} alerts...")

                if alerts_count >= total_items or alerts_count >= min_alerts_target:
                    break

                offset += limit

            except requests.exceptions.RequestException as e:
                print(f"Error fetching alerts from Wazuh API: {e}")
                break

    print(f"Finished exporting. Total alerts exported: {alerts_count}")
    if alerts_count < min_alerts_target:
        print(f"Warning: Target of {min_alerts_target} alerts not met. Exported {alerts_count}.")

if __name__ == '__main__':
    token = get_wazuh_token()
    if token:
        export_alerts(token, OUTPUT_FILE, DAYS_TO_EXPORT, MIN_ALERTS_TARGET)
    else:
        print("Failed to get Wazuh API token. Exiting.")

