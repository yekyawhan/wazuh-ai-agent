# SOC Workflow Guide (မြန်မာ)

## Security Incident Flow

```
Alert ဖြစ်ပေါ်ခြင်း
        |
Wazuh Detection
        |
AI Analysis
        |
Threat Intelligence Check
        |
Risk Assessment
        |
TheHive Case
        |
Response Action
        |
Review & Improvement
```

## AI Agent Responsibilities

### SOC Manager Agent

- Alert priority သတ်မှတ်ခြင်း
- Workflow coordination

### Threat Hunter Agent

- IOC analysis
- Threat hunting support

### Incident Response Agent

- Response recommendation
- Playbook execution

### Reporting Agent

- Incident summary
- Security report generation

## Continuous Improvement

Detection rules, playbooks နှင့် AI knowledge base များကို incident feedback အပေါ်မူတည်ပြီး update လုပ်ရန်လိုအပ်သည်။
