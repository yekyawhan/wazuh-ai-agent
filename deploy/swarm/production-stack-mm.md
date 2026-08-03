# Docker Swarm Production Stack Guide (မြန်မာ)

## ရည်ရွယ်ချက်

ဒီ Deployment Guide သည် Wazuh AI Agent ကို လက်ရှိ Docker Swarm SOC Environment တွင် ထည့်သွင်းအသုံးပြုရန် ရည်ရွယ်ထားသည်။

လက်ရှိ Architecture:

```
pfSense Firewall
        |
        |
Docker Swarm Cluster
        |
+----------------------+
| Wazuh                |
| AI SOC Agent         |
| n8n SOAR             |
| TheHive              |
| MISP                 |
| Cortex               |
+----------------------+
```

## Deployment Principles

- Persistent storage အသုံးပြုရန်
- External network အသုံးပြုရန်
- Secrets များကို runtime တွင် inject လုပ်ရန်
- Health check များ ထည့်သွင်းရန်
- Backup နှင့် monitoring ပြုလုပ်ရန်

## Service Integration Flow

```
Wazuh Alert
    |
AI Analysis
    |
MISP/Cortex Enrichment
    |
TheHive Case
    |
n8n Automation
    |
pfSense Response
```

## Production Checklist

- [ ] Docker Swarm health check
- [ ] Storage validation
- [ ] API connectivity test
- [ ] Secret validation
- [ ] Monitoring verification
