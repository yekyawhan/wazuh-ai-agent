# Production Deployment Guide (မြန်မာ)

## Overview

ဒီ Project ကို Docker Swarm Production Environment အတွက် ရည်ရွယ်ထားသည်။ လက်ရှိ SOC Infrastructure တွင် run နေသော Wazuh, TheHive, MISP, Cortex, n8n စနစ်များနှင့် API Integration ဖြင့် ချိတ်ဆက်အသုံးပြုနိုင်သည်။

## Deployment Architecture

```
Docker Swarm Cluster
        |
        +-- AI SOC Agent
        +-- n8n SOAR
        +-- Wazuh
        +-- TheHive
        +-- MISP
        +-- Cortex
```

## Requirements

- Docker Swarm Cluster
- Persistent Storage
- Internal Network Connectivity
- API Credentials
- Secret Management

## Deployment Steps

1. Prepare Docker Swarm nodes
2. Configure external networks
3. Configure persistent volumes
4. Inject runtime secrets
5. Deploy services
6. Verify health checks

## Security Note

Production API keys, passwords နှင့် tokens များကို Git repository ထဲတွင် မထည့်ရပါ။ Docker Swarm Secrets သို့မဟုတ် Secret Manager အသုံးပြုရန် အကြံပြုသည်။
