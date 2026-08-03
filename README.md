# Wazuh AI Agent — Production AI SOC Platform

AI-powered SOC automation platform integrating Wazuh, TheHive, MISP, Cortex, n8n and pfSense.

## Components

- Wazuh SIEM
- AI SOC Agents
- Threat Intelligence
- SOAR Automation
- Detection Engineering
- Incident Response
- Security Knowledge Base

## Production Stack

Docker Swarm deployment with existing SOC services:

- n8n workflow automation
- TheHive case management
- MISP threat intelligence
- Cortex analyzers
- pfSense response integration

## Repository

```
agents/
integrations/
detections/
knowledge/
response/
observability/
deploy/
docs/
```

## Security

Production secrets must be injected through deployment environment or Docker Swarm secrets.

Version: 1.0.0
