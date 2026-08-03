# AI SOC Platform Architecture (မြန်မာ)

## Overview

Wazuh AI Agent သည် Security Operations Center (SOC) အတွက် AI Automation Layer အဖြစ် တည်ဆောက်ထားသော Platform ဖြစ်သည်။

## Architecture Flow

```
Endpoint / Network Event
          |
          v
      Wazuh SIEM
          |
          v
     AI SOC Agent
          |
+-----------------------+
| MISP | Cortex | Hive  |
| n8n  | pfSense        |
+-----------------------+
          |
          v
 Automated Response
```

## Component Roles

### Wazuh

Security event collection နှင့် detection engine ဖြစ်သည်။

### AI SOC Agent

Alert analysis, decision support နှင့် automation coordination ပြုလုပ်သည်။

### MISP

Threat Intelligence နှင့် IOC enrichment အတွက် အသုံးပြုသည်။

### TheHive

Incident case management နှင့် investigation tracking အတွက် အသုံးပြုသည်။

### Cortex

Security observable analysis automation အတွက် အသုံးပြုသည်။

### n8n

SOAR workflow automation engine ဖြစ်သည်။

### pfSense

Network response နှင့် firewall automation အတွက် အသုံးပြုသည်။
