# Ollama Local LLM Setup for Wazuh AI Agent

## Overview

This guide covers how to configure Ollama as the local LLM backend for the Wazuh AI Agent, replacing OpenAI API calls with a self-hosted model. Two options are provided based on your hardware.

## Hardware Specifications

| Resource | Current | Future |
|----------|---------|--------|
| CPU | 80 cores | 80 cores |
| GPU | None | NVIDIA (planned) |
| Use Case | Security alert classification, threat analysis | Same + faster inference |

---

## Option 1: CPU Only (80 Cores)

### Recommended Models (CPU-optimized)

| Model | Size | RAM Required | Speed (80 cores) | Security Task Quality |
|-------|------|-------------|-------------------|----------------------|
| **qwen2.5:7b** | 4.7GB | ~8GB | ~15-20 tok/s | Excellent - best quality/speed ratio |
| **llama3.1:8b** | 4.7GB | ~8GB | ~15-20 tok/s | Very Good |
| **mistral:7b** | 4.1GB | ~6GB | ~18-22 tok/s | Good |
| **phi3:14b** | 7.9GB | ~12GB | ~8-12 tok/s | Excellent - slower but smarter |
| **qwen2.5:14b** | 9.0GB | ~14GB | ~8-10 tok/s | Best quality for CPU |

### Primary Recommendation: `qwen2.5:7b`

**Why:** Best balance of speed and intelligence for security classification tasks. Supports JSON output natively, good at structured reasoning, and runs well on CPU with 80 cores.

### Installation

```bash
# Install model
ollama pull qwen2.5:7b

# Optional: Pull backup model for comparison
ollama pull llama3.1:8b

# Verify
ollama list
```

### Performance Tuning for CPU (80 cores)

```bash
# Set environment variables for Ollama
export OLLAMA_NUM_PARALLEL=4          # Handle 4 concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2     # Keep 2 models in memory
export OLLAMA_KEEP_ALIVE=30m          # Keep model loaded for 30 min

# For systemd service, add to /etc/systemd/system/ollama.service:
# [Service]
# Environment="OLLAMA_NUM_PARALLEL=4"
# Environment="OLLAMA_MAX_LOADED_MODELS=2"
# Environment="OLLAMA_KEEP_ALIVE=30m"
# Environment="OLLAMA_HOST=0.0.0.0:11434"
```

### Create Custom Security Model (Modelfile)

```bash
cat > /home/ollama/Modelfile-security << 'EOF'
FROM qwen2.5:7b

PARAMETER temperature 0.1
PARAMETER num_ctx 4096
PARAMETER num_thread 40
PARAMETER repeat_penalty 1.1

SYSTEM """You are a cybersecurity AI analyst specialized in Wazuh SIEM alert classification. 
Your job is to:
1. Classify security alerts into threat categories
2. Assign severity scores (0-10)
3. Identify MITRE ATT&CK techniques
4. Recommend response actions

Always respond in valid JSON format with these keys:
- threat_type: one of [malware, brute_force, privilege_escalation, data_exfiltration, lateral_movement, reconnaissance, persistence, command_and_control, denial_of_service, insider_threat, other]
- severity_score: float 0-10
- confidence: float 0-1
- mitre_technique: string or null
- summary: concise explanation
- recommended_action: one of [block_ip, isolate_host, kill_process, disable_user, collect_forensics, alert_only]
"""
EOF

# Create the custom model
ollama create wazuh-security -f /home/ollama/Modelfile-security

# Test it
ollama run wazuh-security "Classify this alert: Multiple failed SSH login attempts from IP 192.168.1.100 to root account on server web-01. 15 attempts in 2 minutes."
```

---

## Option 2: GPU (NVIDIA) - Future Upgrade

### Recommended Models (GPU-optimized)

| Model | VRAM Required | Speed | Security Task Quality |
|-------|--------------|-------|----------------------|
| **qwen2.5:32b** | 20GB | ~40-60 tok/s | Outstanding |
| **llama3.1:70b** | 40GB+ | ~20-30 tok/s | Best available |
| **deepseek-v2:16b** | 12GB | ~50-70 tok/s | Excellent |
| **qwen2.5:14b** | 10GB | ~60-80 tok/s | Very Good + Fast |
| **mistral-nemo:12b** | 8GB | ~70-90 tok/s | Good + Very Fast |

### GPU Installation

```bash
# Install NVIDIA Container Toolkit (if using Docker)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Pull larger model for GPU
ollama pull qwen2.5:32b

# Create GPU-optimized security model
cat > /home/ollama/Modelfile-security-gpu << 'EOF'
FROM qwen2.5:32b

PARAMETER temperature 0.1
PARAMETER num_ctx 8192
PARAMETER num_gpu 99
PARAMETER repeat_penalty 1.1

SYSTEM """You are a cybersecurity AI analyst specialized in Wazuh SIEM alert classification. 
Your job is to:
1. Classify security alerts into threat categories
2. Assign severity scores (0-10)
3. Identify MITRE ATT&CK techniques
4. Recommend response actions
5. Provide detailed analysis with context

Always respond in valid JSON format with these keys:
- threat_type: one of [malware, brute_force, privilege_escalation, data_exfiltration, lateral_movement, reconnaissance, persistence, command_and_control, denial_of_service, insider_threat, other]
- severity_score: float 0-10
- confidence: float 0-1
- mitre_technique: string or null
- summary: concise explanation
- recommended_action: one of [block_ip, isolate_host, kill_process, disable_user, collect_forensics, alert_only]
- analysis: detailed reasoning
"""
EOF

ollama create wazuh-security-gpu -f /home/ollama/Modelfile-security-gpu
```

### GPU Environment Variables

```bash
# /etc/systemd/system/ollama.service
Environment="OLLAMA_NUM_PARALLEL=8"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_KEEP_ALIVE=60m"
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="CUDA_VISIBLE_DEVICES=0"
```

---

## n8n Integration

### Method 1: HTTP Request Node (Recommended)

In your n8n workflow, add an **HTTP Request** node after receiving the Wazuh alert:

**Configuration:**
| Setting | Value |
|---------|-------|
| Method | POST |
| URL | `http://<ollama-server-ip>:11434/api/chat` |
| Body Type | JSON |
| Authentication | None (internal network) |

**Request Body:**
```json
{
  "model": "wazuh-security",
  "messages": [
    {
      "role": "user",
      "content": "Classify this Wazuh alert:\n\nRule ID: {{ $json.rule.id }}\nRule Level: {{ $json.rule.level }}\nDescription: {{ $json.rule.description }}\nAgent: {{ $json.agent.name }}\nFull Log: {{ $json.full_log }}\n\nRespond in JSON format."
    }
  ],
  "stream": false,
  "format": "json"
}
```

**Parse Response:**
Add a **Code** node after the HTTP Request:
```javascript
const response = JSON.parse($input.first().json.message.content);
return [{
  json: {
    ...response,
    original_alert: $input.first().json
  }
}];
```

### Method 2: OpenAI-Compatible API (for AI Agent code)

Ollama exposes an OpenAI-compatible API at `/v1/chat/completions`. Update the AI Agent's config:

```bash
# In .env file for phase3-ai-agent-core:
OPENAI_API_KEY=ollama                           # Any string works
OPENAI_API_BASE=http://<ollama-ip>:11434/v1     # Ollama OpenAI endpoint
OPENAI_MODEL=wazuh-security                     # Your custom model name
OPENAI_EMBEDDING_MODEL=nomic-embed-text         # Local embedding model
```

### Method 3: n8n AI Agent Node (Built-in)

n8n has a built-in **Ollama** node:
1. Go to n8n → Settings → Credentials → Add Credential
2. Select "Ollama API"
3. Base URL: `http://<ollama-ip>:11434`
4. Use the **AI Agent** or **Chat Model** node with Ollama credential

---

## AI Agent Code Update for Ollama

Update `phase3-ai-agent-core/ai_agent/config.py`:

```python
# Add Ollama-specific settings
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "wazuh-security")

# LLM Backend selection
LLM_BACKEND: str = os.getenv("LLM_BACKEND", "ollama")  # "ollama" or "openai"
```

Update `phase3-ai-agent-core/ai_agent/classifier.py`:

```python
from openai import OpenAI

class AlertClassifier:
    def __init__(self):
        if Config.LLM_BACKEND == "ollama":
            self.client = OpenAI(
                base_url=f"{Config.OLLAMA_HOST}/v1",
                api_key="ollama"  # Ollama doesn't need real key
            )
            self.model = Config.OLLAMA_MODEL
        else:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
```

---

## Local Embedding Model (for Qdrant)

Instead of OpenAI embeddings, use a local model:

```bash
# Pull embedding model
ollama pull nomic-embed-text

# Test
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "SSH brute force attack from 192.168.1.100"
}'
```

Update `knowledge_base.py` for local embeddings:

```python
def _get_embedding(self, text: str) -> List[float]:
    if Config.LLM_BACKEND == "ollama":
        import httpx
        response = httpx.post(
            f"{Config.OLLAMA_HOST}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        return response.json()["embedding"]
    else:
        response = self.openai_client.embeddings.create(input=[text], model=self.embedding_model)
        return response.data[0].embedding
```

> **Note:** `nomic-embed-text` produces 768-dimensional vectors. Update Qdrant collection vector size from 1536 to 768 if switching from OpenAI embeddings.

---

## Quick Start Commands

```bash
# 1. Pull models
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 2. Create custom security model
ollama create wazuh-security -f Modelfile-security

# 3. Test classification
curl http://localhost:11434/api/chat -d '{
  "model": "wazuh-security",
  "messages": [{"role": "user", "content": "Classify: Multiple failed SSH logins from 10.0.0.5"}],
  "stream": false,
  "format": "json"
}'

# 4. Test embedding
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Brute force SSH attack"
}'

# 5. Update AI Agent .env
echo 'LLM_BACKEND=ollama' >> phase3-ai-agent-core/.env
echo 'OLLAMA_HOST=http://localhost:11434' >> phase3-ai-agent-core/.env
echo 'OLLAMA_MODEL=wazuh-security' >> phase3-ai-agent-core/.env
```

---

## Performance Expectations

### CPU (80 cores) with qwen2.5:7b

| Metric | Expected |
|--------|----------|
| Tokens/sec | 15-20 |
| Alert classification time | 3-5 seconds |
| Concurrent requests | 4 |
| RAM usage | ~8GB |
| CPU usage under load | 40-50 cores |

### GPU (future) with qwen2.5:32b

| Metric | Expected |
|--------|----------|
| Tokens/sec | 40-60 |
| Alert classification time | 1-2 seconds |
| Concurrent requests | 8 |
| VRAM usage | ~20GB |
| CPU usage | Minimal |

---

## Switching Between CPU and GPU

When you add a GPU later:

```bash
# 1. Pull larger model
ollama pull qwen2.5:32b

# 2. Create GPU model
ollama create wazuh-security-gpu -f Modelfile-security-gpu

# 3. Update .env
sed -i 's/OLLAMA_MODEL=wazuh-security/OLLAMA_MODEL=wazuh-security-gpu/' phase3-ai-agent-core/.env

# 4. Restart AI Agent
docker-compose restart ai-agent
```

No other code changes needed - just swap the model name.
