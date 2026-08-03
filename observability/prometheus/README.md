# Prometheus Monitoring

Metrics collection for AI SOC Platform.

Tracked metrics:

- Agent availability
- API response time
- Incident processing count
- Service health
- Error rate

Example flow:

```
Service
 |
Metrics Exporter
 |
Prometheus
 |
Grafana Dashboard
```
