
import json
import geoip2.database
import whois
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Configuration --- #
GEOLITE2_DB_PATH = "/home/ubuntu/wazuh-phase2/GeoLite2-City.mmdb"
VIRUSTOTAL_API_KEY = "YOUR_VIRUSTOTAL_API_KEY"  # Replace with your actual VirusTotal API key

# --- GeoIP Lookup --- #
def download_geolite2_db(db_path):
    if not os.path.exists(db_path):
        logging.info(f"GeoLite2 database not found at {db_path}. Attempting to download a sample.")
        # In a real scenario, you would download this from MaxMind after registration.
        # For demonstration, we'll use a placeholder or instruct user to download.
        logging.warning("Please download GeoLite2-City.mmdb from MaxMind and place it in /home/ubuntu/wazuh-phase2/")
        logging.warning("You can get a free license key and download the database from: https://www.maxmind.com/en/geolite2/signup")
        return False
    return True

def get_geoip_info(ip_address):
    if not download_geolite2_db(GEOLITE2_DB_PATH):
        return {"error": "GeoLite2 database not available"}
    try:
        with geoip2.database.Reader(GEOLITE2_DB_PATH) as reader:
            response = reader.city(ip_address)
            return {
                "country": response.country.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude
            }
    except geoip2.errors.AddressNotFoundError:
        return {"error": "IP address not found in GeoLite2 database"}
    except Exception as e:
        return {"error": f"GeoIP lookup failed: {e}"}

# --- VirusTotal Check --- #
def virustotal_lookup(indicator, indicator_type="ip"):
    if not VIRUSTOTAL_API_KEY or VIRUSTOTAL_API_KEY == "YOUR_VIRUSTOTAL_API_KEY":
        return {"error": "VirusTotal API key not configured"}

    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    url = ""
    if indicator_type == "ip":
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{indicator}"
    elif indicator_type == "hash":
        url = f"https://www.virustotal.com/api/v3/files/{indicator}"
    else:
        return {"error": "Unsupported indicator type for VirusTotal"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Extract relevant information, e.g., last_analysis_stats, reputation
        if indicator_type == "ip":
            return {
                "reputation": data.get("data", {}).get("attributes", {}).get("reputation"),
                "last_analysis_stats": data.get("data", {}).get("attributes", {}).get("last_analysis_stats")
            }
        elif indicator_type == "hash":
            return {
                "reputation": data.get("data", {}).get("attributes", {}).get("reputation"),
                "last_analysis_stats": data.get("data", {}).get("attributes", {}).get("last_analysis_stats")
            }
    except requests.exceptions.RequestException as e:
        return {"error": f"VirusTotal lookup failed: {e}"}
    except Exception as e:
        return {"error": f"Error parsing VirusTotal response: {e}"}
    return {}

# --- WHOIS Lookup --- #
def get_whois_info(ip_or_domain):
    try:
        w = whois.whois(ip_or_domain)
        return {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "updated_date": str(w.updated_date),
            "emails": w.emails,
            "name_servers": w.name_servers
        }
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {e}"}

# --- Threat Intelligence Correlation (Placeholder) --- #
def threat_intelligence_correlation(indicator):
    # This is a placeholder for actual TI correlation.
    # In a real scenario, you would query a TI platform (e.g., MISP, AlienVault OTX)
    # or a local threat feed.
    known_bad_ips = ["1.2.3.4", "5.6.7.8"]
    known_bad_hashes = ["a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"]

    if indicator in known_bad_ips:
        return {"threat_feed": "Internal Bad IP List", "description": "Known malicious IP address"}
    if indicator in known_bad_hashes:
        return {"threat_feed": "Internal Bad Hash List", "description": "Known malicious file hash"}

    return {"threat_feed": "None", "description": "No direct correlation found in internal feeds"}


def enrich_alert(alert_data):
    enriched_data = alert_data.copy()

    # Extract relevant indicators from alert_data
    src_ip = alert_data.get("data", {}).get("srcip")
    file_hash = alert_data.get("data", {}).get("file", {}).get("hash", {}).get("sha256") or \
                alert_data.get("data", {}).get("file", {}).get("hash", {}).get("md5")
    domain = alert_data.get("data", {}).get("dst_domain") # Example for domain

    if src_ip:
        logging.info(f"Enriching IP: {src_ip}")
        enriched_data["enrichment"] = enriched_data.get("enrichment", {})
        enriched_data["enrichment"]["geoip"] = get_geoip_info(src_ip)
        enriched_data["enrichment"]["virustotal_ip"] = virustotal_lookup(src_ip, "ip")
        enriched_data["enrichment"]["whois_ip"] = get_whois_info(src_ip)
        enriched_data["enrichment"]["ti_correlation_ip"] = threat_intelligence_correlation(src_ip)

    if file_hash:
        logging.info(f"Enriching File Hash: {file_hash}")
        enriched_data["enrichment"] = enriched_data.get("enrichment", {})
        enriched_data["enrichment"]["virustotal_hash"] = virustotal_lookup(file_hash, "hash")
        enriched_data["enrichment"]["ti_correlation_hash"] = threat_intelligence_correlation(file_hash)

    if domain:
        logging.info(f"Enriching Domain: {domain}")
        enriched_data["enrichment"] = enriched_data.get("enrichment", {})
        enriched_data["enrichment"]["whois_domain"] = get_whois_info(domain)
        enriched_data["enrichment"]["ti_correlation_domain"] = threat_intelligence_correlation(domain)

    return enriched_data


if __name__ == "__main__":
    # This script is expected to be called by n8n or another system with alert_data as stdin
    # For testing, you can provide a sample JSON via stdin:
    # echo '{"rule": {"id": "100001", "level": 7, "description": "Test Alert"}, "agent": {"name": "test-agent"}, "data": {"srcip": "8.8.8.8", "file": {"hash": {"sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}}}}' | python3 alert_enrichment.py
    
    input_data = sys.stdin.read()
    try:
        alert = json.loads(input_data)
        enriched_alert = enrich_alert(alert)
        print(json.dumps(enriched_alert, indent=2))
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from stdin.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error during alert enrichment: {e}")
        sys.exit(1)
