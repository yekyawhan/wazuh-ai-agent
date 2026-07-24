
import os
import requests
import time
from prometheus_client import start_http_server, Gauge
from datetime import datetime

# Configuration from environment variables
AI_AGENT_URL = os.getenv("AI_AGENT_URL", "http://localhost:8000/health")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6334/healthz")
FEEDBACK_LOOP_URL = os.getenv("FEEDBACK_LOOP_URL", "http://localhost:8001/metrics")
ROLLBACK_MANAGER_URL = os.getenv("ROLLBACK_MANAGER_URL", "http://localhost:8002/health")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Prometheus Metrics
SERVICE_HEALTH = Gauge("service_health", "Health status of a service (1=up, 0=down)", ["service_name"])
SERVICE_RESPONSE_TIME = Gauge("service_response_time_seconds", "Response time of a service in seconds", ["service_name"])

def send_telegram_message(message):
    """Sends a message to a Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID not set. Skipping Telegram notification.")
        return

    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(telegram_api_url, json=payload)
        response.raise_for_status()
        print("Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

def check_service_health(service_name, url):
    """Checks the health of a given service and updates Prometheus metrics."""
    start_time = time.time()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        health_status = 1 # Up
        print(f"[{datetime.now()}] {service_name} is UP.")
    except requests.exceptions.RequestException as e:
        health_status = 0 # Down
        error_message = f"[{datetime.now()}] {service_name} is DOWN! Error: {e}"
        print(error_message)
        send_telegram_message(error_message)
    finally:
        response_time = time.time() - start_time
        SERVICE_HEALTH.labels(service_name).set(health_status)
        SERVICE_RESPONSE_TIME.labels(service_name).set(response_time)
        return health_status

def main():
    # Start up the server to expose the metrics.
    start_http_server(8000) # Prometheus metrics will be available on port 8000
    print("Prometheus metrics server started on port 8000.")

    services = {
        "ai-agent": AI_AGENT_URL,
        "qdrant": QDRANT_URL,
        "feedback-loop": FEEDBACK_LOOP_URL,
        "rollback-manager": ROLLBACK_MANAGER_URL
    }

    while True:
        print("\n--- Performing health checks ---")
        for service_name, url in services.items():
            check_service_health(service_name, url)
        time.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    main()
