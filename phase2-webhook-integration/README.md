# Wazuh AI Agent - Phase 2: Wazuh → n8n Webhook Integration

This project provides the necessary files to integrate Wazuh SIEM with n8n for automated alert processing, enrichment, and storage in Qdrant vector database. This setup forms Phase 2 of the larger Wazuh AI Agent project.

## Project Structure

- `ossec_integration_config.xml`: Wazuh `ossec.conf` integration snippet.
- `custom-n8n.py`: Python script for Wazuh to forward alerts to n8n webhook.
- `n8n_wazuh_webhook_workflow.json`: Importable n8n workflow for alert processing.
- `alert_enrichment.py`: Python script for enriching alerts with GeoIP, VirusTotal, WHOIS, and Threat Intelligence.
- `qdrant_setup.py`: Python script to set up Qdrant collection and indexes for Wazuh alerts.
- `README.md`: This documentation.

## 1. Wazuh Integration Configuration

To integrate Wazuh with the `custom-n8n.py` script and forward alerts to n8n, you need to modify your Wazuh manager's `ossec.conf` file.

### 1.1. `ossec_integration_config.xml`

Add the following XML snippet to your `/var/ossec/etc/ossec.conf` file, typically within the `<ossec_config>` section. This configures Wazuh to forward alerts with a level of 7 or higher in JSON format to the `custom-n8n.py` script.

```xml
<integration>
  <name>custom-n8n</name>
  <hook_url>https://n8n.y3kh.dpdns.org/webhook/wazuh-alerts</hook_url>
  <level>7</level>
  <alert_format>json</alert_format>
</integration>
```

**Note:** The `hook_url` specified here is for the `custom-n8n.py` script to use, not directly for Wazuh. Wazuh will call the `custom-n8n.py` script, which then sends the alert to the n8n webhook.

### 1.2. `custom-n8n.py`

This Python script acts as the intermediary between Wazuh and your n8n webhook. It receives alerts from Wazuh via `stdin`, parses them, and forwards them to the specified n8n webhook URL.

**Deployment Steps:**

1.  **Copy the script:** Place `custom-n8n.py` into the Wazuh integrations directory on your Wazuh manager:
    ```bash
    sudo cp /home/ubuntu/wazuh-phase2/custom-n8n.py /var/ossec/integrations/
    ```
2.  **Make it executable:**
    ```bash
    sudo chmod +x /var/ossec/integrations/custom-n8n.py
    ```
3.  **Install dependencies:** Ensure the `requests` library is installed in the Python environment used by Wazuh. If Wazuh uses its own Python environment, you might need to install it there. Otherwise, a system-wide install should suffice:
    ```bash
    sudo pip3 install requests
    ```
4.  **Restart Wazuh Manager:** After modifying `ossec.conf` and deploying the script, restart the Wazuh manager to apply changes:
    ```bash
    sudo systemctl restart wazuh-manager
    ```

## 2. n8n Workflow Configuration

The `n8n_wazuh_webhook_workflow.json` file contains an importable n8n workflow that processes Wazuh alerts.

### 2.1. Importing the Workflow

1.  **Access n8n:** Navigate to your n8n instance (e.g., `https://n8n.y3kh.dpdns.org`).
2.  **Import:** In the n8n interface, click on 
"File" > "Import from File" or "Import from URL" and select the `n8n_wazuh_webhook_workflow.json` file.
3.  **Activate:** After importing, activate the workflow by toggling the 
toggle in the top right corner.

### 2.2. Workflow Overview

The n8n workflow performs the following actions:

-   **Wazuh Webhook:** Receives JSON alerts from the `custom-n8n.py` script at `https://n8n.y3kh.dpdns.org/webhook/wazuh-alerts`.
-   **Parse Alert & Determine Severity:** Parses key fields from the Wazuh alert (e.g., `rule.id`, `rule.level`, `agent.name`, `data.srcip`) and assigns a severity (low, medium, high, critical) based on the `rule.level`.
    -   `rule.level >= 10`: Critical
    -   `rule.level >= 7`: High
    -   `rule.level >= 5`: Medium
    -   `rule.level >= 3`: Low
-   **Route by Severity:** Branches the workflow based on the determined severity. High and Critical alerts are routed for immediate notification.
-   **Telegram Notification:** For high and critical alerts, sends a detailed notification to the specified Telegram Chat ID (`1721493612`). **You will need to configure your Telegram credentials in n8n.**
-   **VirusTotal Enrichment (Placeholder):** This node is a placeholder. In a production environment, you would integrate the `alert_enrichment.py` script or use n8n's HTTP Request node to call the VirusTotal API directly. **Remember to replace `YOUR_VIRUSTOTAL_API_KEY` in `alert_enrichment.py` with your actual key.**
-   **Store in Qdrant (Placeholder) & Log for AI:** This node is a placeholder for storing the alert data in Qdrant and logging all alerts for AI training purposes. In a production setup, you would use n8n's HTTP Request node to interact with the Qdrant API or execute the `qdrant_setup.py` script.

## 3. Alert Enrichment

The `alert_enrichment.py` script provides functions to enrich Wazuh alerts with additional context from various sources.

### 3.1. `alert_enrichment.py`

This script includes:

-   **GeoIP Lookup:** Uses MaxMind GeoLite2 database to determine geographical information for IP addresses.
    -   **Action Required:** You need to download the `GeoLite2-City.mmdb` database from MaxMind (requires free registration) and place it in `/home/ubuntu/wazuh-phase2/` (or a path accessible by the script).
        -   Download link: [MaxMind GeoLite2 Signup](https://www.maxmind.com/en/geolite2/signup)
-   **VirusTotal Hash/IP Check:** Queries VirusTotal for reputation and analysis statistics of IP addresses and file hashes.
    -   **Action Required:** Replace `YOUR_VIRUSTOTAL_API_KEY` in the script with your actual VirusTotal API key.
-   **WHOIS Lookup:** Retrieves WHOIS information for IP addresses or domains.
-   **Threat Intelligence Correlation:** A placeholder for integrating with external Threat Intelligence platforms or internal blacklists.

**Integration with n8n:**

To use this script within n8n, you can either:

1.  **Execute Command Node:** Use an 
n8n "Execute Command" node to run `alert_enrichment.py` with the alert JSON as input.
2.  **HTTP Request Node:** If you expose `alert_enrichment.py` as a microservice (e.g., using Flask/FastAPI), you can use an n8n "HTTP Request" node to send the alert data and receive the enriched data.

## 4. Qdrant Setup

The `qdrant_setup.py` script is designed to initialize your Qdrant vector database for storing Wazuh alerts.

### 4.1. `qdrant_setup.py`

This script performs the following:

-   **Connects to Qdrant:** Establishes a connection to your Qdrant instance (default: `localhost:6333`).
-   **Creates/Recreates Collection:** Creates a collection named `wazuh_alerts` with a specified vector size (default: 768, adjust based on your embedding model) and cosine distance.
-   **Creates Payload Indexes:** Adds indexes for common alert fields (`rule.id`, `rule.level`, `agent.name`, `data.srcip`) to enable efficient filtering and searching.
-   **Functions for Storage and Query:** Includes `store_alert` and `query_alerts` functions for interacting with the collection.

**Deployment Steps:**

1.  **Ensure Qdrant is Running:** Make sure your Qdrant instance is accessible at the configured host and port.
2.  **Run the script:** Execute the script to set up the collection and indexes:
    ```bash
    python3 /home/ubuntu/wazuh-phase2/qdrant_setup.py
    ```

**Integration with n8n:**

Similar to the enrichment script, you can integrate Qdrant operations into n8n using:

1.  **Execute Command Node:** Run `qdrant_setup.py` (or specific functions within it) via an n8n "Execute Command" node.
2.  **HTTP Request Node:** If you expose Qdrant's API or a custom microservice for Qdrant interaction, use an n8n "HTTP Request" node.

## 5. Troubleshooting Guide

-   **Wazuh Alerts not reaching n8n:**
    -   Check Wazuh manager logs (`/var/ossec/logs/ossec.log`) for errors related to the `custom-n8n` integration.
    -   Verify `custom-n8n.py` has execute permissions (`chmod +x`).
    -   Ensure `requests` library is installed in Wazuh's Python environment.
    -   Check `custom-n8n.py` logs (`/var/ossec/logs/integrations.log`) for any errors during alert forwarding.
    -   Confirm the n8n webhook URL is correct and accessible from the Wazuh manager.
-   **n8n Workflow Issues:**
    -   Check n8n execution logs for errors in the "Wazuh Webhook" or subsequent nodes.
    -   Ensure the n8n workflow is activated.
    -   Verify that the Telegram credentials are correctly configured in n8n.
-   **Enrichment Script Errors:**
    -   Check the logs generated by `alert_enrichment.py` for specific error messages.
    -   Ensure the `GeoLite2-City.mmdb` file is in the correct location.
    -   Verify the VirusTotal API key is correctly set.
-   **Qdrant Connection Problems:**
    -   Ensure the Qdrant service is running and accessible from where `qdrant_setup.py` is executed.
    -   Check Qdrant logs for any issues.
    -   Verify the `QDRANT_HOST` and `QDRANT_PORT` in `qdrant_setup.py` are correct.

## References

-   [Wazuh Integrations Documentation](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/integration.html)
-   [n8n Documentation](https://docs.n8n.io/)
-   [Qdrant Documentation](https://qdrant.tech/documentation/)
-   [MaxMind GeoLite2](https://www.maxmind.com/en/geolite2/signup)
-   [VirusTotal API](https://developers.virustotal.com/v3.0/reference)
