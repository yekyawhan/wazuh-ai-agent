# Production Architecture

```
Wazuh
 |
AI SOC Agent
 |
+-------------------------+
| TheHive | MISP | Cortex |
+-------------------------+
 |
n8n SOAR
 |
pfSense / Active Response
```

## Modules

- Detection Engineering
- Incident Response
- Playbook Automation
- Purple Team Validation
- Observability
