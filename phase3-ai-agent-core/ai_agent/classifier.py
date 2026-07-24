
import logging
import json
from openai import OpenAI
from typing import Dict, Any

from .config import Config
from .models import WazuhAlert, ClassificationResult

logger = logging.getLogger(__name__)

class AlertClassifier:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.threat_categories = [
            "malware", "brute_force", "privilege_escalation", "data_exfiltration",
            "lateral_movement", "reconnaissance", "persistence", "command_and_control",
            "denial_of_service", "insider_threat", "other"
        ]

    async def classify_alert(self, alert: WazuhAlert) -> ClassificationResult:
        prompt = self._build_classification_prompt(alert)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security analyst AI. Classify the Wazuh alert into a threat type, assign a severity score (0-10), confidence (0-1), identify MITRE ATT&CK technique if applicable, and provide a concise summary. Output in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.0
            )
            
            classification_output = json.loads(response.choices[0].message.content)
            
            # Validate and parse the output
            threat_type = classification_output.get("threat_type", "other").lower()
            if threat_type not in self.threat_categories:
                threat_type = "other"

            return ClassificationResult(
                threat_type=threat_type,
                severity_score=float(classification_output.get("severity_score", 0.0)),
                confidence=float(classification_output.get("confidence", 0.0)),
                mitre_technique=classification_output.get("mitre_technique"),
                summary=classification_output.get("summary", "No summary provided.")
            )
        except Exception as e:
            logger.error(f"Error classifying alert {alert.id}: {e}")
            return ClassificationResult(
                threat_type="error",
                severity_score=0.0,
                confidence=0.0,
                mitre_technique=None,
                summary=f"Classification failed due to an error: {e}"
            )

    def _build_classification_prompt(self, alert: WazuhAlert) -> str:
        alert_dict = alert.model_dump_json(indent=2)
        return f"""Classify the following Wazuh alert:

{alert_dict}

Threat Categories: {', '.join(self.threat_categories)}

Provide the output in JSON format with the following keys:
- threat_type (string, one of the threat categories)
- severity_score (float, 0-10)
- confidence (float, 0-1)
- mitre_technique (string, e.g., T1003 for Credential Dumping, or null if not applicable)
- summary (string, concise explanation of the threat)
"""
