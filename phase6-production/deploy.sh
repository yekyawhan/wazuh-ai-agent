
#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Wazuh AI Agent Production Deployment..."

# --- 1. Check Prerequisites ---
echo "Checking prerequisites (Docker and Docker Compose)..."
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker before proceeding."
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose is not installed. Please install Docker Compose before proceeding."
    exit 1
fi
echo "Docker and Docker Compose are installed."

# --- 2. Load Environment Variables ---
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)
else
    echo "Warning: $ENV_FILE not found. Please create it based on .env.example and fill in your credentials."
    echo "Attempting to proceed, but some services might fail due to missing environment variables."
fi

# --- 3. Create Necessary Directories and Set Permissions ---
echo "Creating necessary directories and setting permissions..."
mkdir -p qdrant_data ai-agent-data prometheus_config prometheus_data grafana_data

# Create a dummy prometheus.yml if it doesn't exist
if [ ! -f "prometheus_config/prometheus.yml" ]; then
    echo "Creating default prometheus.yml"
    cat <<EOF > prometheus_config/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-agent-monitoring'
    static_configs:
      - targets: ['ai-agent:8000'] # Assuming ai-agent exposes /metrics endpoint

  - job_name: 'feedback-loop-monitoring'
    static_configs:
      - targets: ['feedback-loop:8001'] # Assuming feedback-loop exposes /metrics endpoint

  - job_name: 'health-check-exporter'
    static_configs:
      - targets: ['localhost:8000'] # The health_check.py script will expose metrics here
EOF
fi

# --- 4. Build Docker Images ---
echo "Building Docker images..."
# Assuming ai-agent and rollback-manager have their own Dockerfiles in their respective directories
# For feedback-loop, we created a Dockerfile.feedback in wazuh-phase5
docker build -t wazuh-ai-agent:production ../ai-agent # Adjust path as needed
docker build -t wazuh-rollback-manager:production ../rollback-manager # Adjust path as needed
docker build -f ../wazuh-phase5/Dockerfile.feedback -t wazuh-feedback-loop:production ../wazuh-phase5

# --- 5. Start All Services with Docker Compose ---
echo "Starting all services using docker-compose..."
docker-compose -f docker-compose.production.yml up -d

# --- 6. Run Health Checks (initial) ---
echo "Waiting for services to come up and running initial health checks..."
sleep 30 # Give services some time to start

docker-compose -f docker-compose.production.yml ps

echo "Deployment complete. Check 'docker-compose ps' for service status."
echo "You can access Prometheus on port 9090 and Grafana on port 3000."
echo "The AI Agent API is available on port 8000, and Feedback Loop API on port 8001."
