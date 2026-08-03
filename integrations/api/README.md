# Security API Integration Layer

API connectors for:

- Wazuh
- MISP
- Cortex
- TheHive
- n8n

Design:

```
Security Event
      |
API Connector
      |
AI Analysis
      |
Response Workflow
```

Production credentials must be injected at runtime.
