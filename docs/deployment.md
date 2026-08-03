# Production Deployment Guide

## Docker Swarm

The platform is designed for Docker Swarm deployment.

Integrated services:

- Wazuh
- n8n
- TheHive
- MISP
- Cortex
- pfSense

## Deployment Flow

```
Git Repository
      |
Docker Swarm
      |
SOC Services
      |
AI Automation Layer
```

## Credential Handling

Use runtime secrets or protected deployment configuration.

Do not commit production credentials.
