
# Phase 5: Training & Fine-tuning for Wazuh AI Agent

This phase focuses on building the necessary components for training, fine-tuning, and evaluating the AI Agent for Wazuh. It includes tools for collecting historical alert data, labeling it, training/fine-tuning the classification model, populating the Qdrant knowledge base, establishing a feedback loop for continuous improvement, and simulating attacks for testing.

## Components:

### 1. Training Data Collector (`training_data_collector.py`)

A Python script designed to export historical alerts from the Wazuh API. This data is crucial for training and fine-tuning the AI classification model.

**Key Features:**
- Connects to the Wazuh Manager API to retrieve alerts.
- Filters alerts by date range, rule level, and agent.
- Exports alerts in JSONL format, suitable for machine learning training.
- Configurable target for minimum number of alerts to export (default: 10,000+).

**Usage:**
Set environment variables for Wazuh API credentials and desired export parameters, then run the script.

```bash
export WAZUH_MANAGER_IP="your_wazuh_manager_ip"
export WAZUH_API_PORT="55000"
export WAZUH_API_USER="your_api_user"
export WAZUH_API_PASSWORD="your_api_password"
export OUTPUT_FILE="wazuh_alerts.jsonl"
export DAYS_TO_EXPORT="90" # Export alerts from the last 90 days
export MIN_ALERTS_TARGET="10000"
python3 training_data_collector.py
```

### 2. Data Labeler (`data_labeler.py`)

This script automates the initial labeling of Wazuh alerts using a placeholder AI classifier. It also provides a framework for manual override and generates statistics on the labeled dataset.

**Key Features:**
- Auto-labels alerts with `threat_type`, `severity`, and `correct_response` using a simulated AI classifier.
- Designed to integrate with a manual labeling interface (though not implemented in this script).
- Exports the labeled dataset to a JSONL file.
- Provides statistics on the distribution of labels (threat type, severity, response).

**Usage:**
Requires an input JSONL file of raw alerts (e.g., from `training_data_collector.py`).

```bash
export INPUT_FILE="wazuh_alerts.jsonl"
export OUTPUT_FILE="labeled_alerts.jsonl"
python3 data_labeler.py
```

### 3. Training Pipeline (`training_pipeline.py`)

Orchestrates the fine-tuning of the AI classification model and the population of the Qdrant knowledge base with embeddings of historical alerts.

**Key Features:**
- Fine-tunes a classification model (e.g., Logistic Regression with TF-IDF for demonstration) using the labeled data.
- Evaluates model performance using precision, recall, and F1-score.
- Generates embeddings for all historical alerts using a mock embedding model.
- Populates a mock Qdrant vector database with these embeddings and relevant metadata.

**Usage:**
Requires a labeled alerts JSONL file.

```bash
export LABELED_DATA_FILE="labeled_alerts.jsonl"
python3 training_pipeline.py
```

### 4. Feedback Loop (`feedback_loop.py`)

A FastAPI application that provides an endpoint for receiving analyst feedback on AI Agent decisions. This feedback is crucial for continuous learning and periodic retraining.

**Key Features:**
- FastAPI endpoint (`/feedback`) to accept structured feedback.
- Stores feedback in a mock Qdrant client (in a real scenario, this would be a persistent Qdrant instance).
- Designed to trigger periodic retraining based on accumulated feedback.
- Includes a placeholder for performance metrics tracking (`/metrics`).

**Usage:**
Run the FastAPI application. It will listen on the specified port.

```bash
export FEEDBACK_PORT="8001"
uvicorn feedback_loop:app --host 0.0.0.0 --port $FEEDBACK_PORT
```

### 5. Test Simulator (`test_simulator.py`)

Simulates various attack scenarios by generating fake Wazuh alerts and sending them to the AI Agent for testing. It measures response times and provides a basic report.

**Key Features:**
- Generates fake alerts for scenarios like brute force, malware detection, lateral movement, and port scans.
- Sends these simulated alerts to the AI Agent's processing endpoint.
- Measures the response time of the AI Agent.
- Generates a basic simulation report, including total alerts, successful responses, and average response time.

**Usage:**
Set the AI Agent API URL and the number of alerts to simulate, then run the script.

```bash
export AI_AGENT_API_URL="http://localhost:8000/process_alert" # Replace with your AI Agent URL
export NUM_ALERTS_TO_SIMULATE="100"
python3 test_simulator.py
```

## Next Steps:

- Integrate actual Wazuh API calls and Qdrant client implementations.
- Develop a robust AI classification model and embedding model.
- Implement a UI for manual labeling and feedback submission.
- Set up automated periodic retraining based on feedback.
- Enhance the test simulator with ground truth for accurate performance metrics (accuracy, false positives/negatives).
