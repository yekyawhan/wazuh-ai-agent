from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from uuid import uuid4


class WazuhRule(BaseModel):
    id: str
    level: int
    description: str
    mitre: Optional[Dict[str, Any]] = None
    groups: Optional[List[str]] = None


class WazuhAgent(BaseModel):
    id: str
    name: str
    ip: Optional[str] = None


class WazuhDecoder(BaseModel):
    name: Optional[str] = None


class WazuhAlert(BaseModel):
    """
    Accepts Wazuh alert JSON in its native nested format:
    {
      "id": "...",
      "timestamp": "...",
      "rule": {"id": "...", "level": 5, "description": "..."},
      "agent": {"id": "...", "name": "..."},
      "decoder": {"name": "..."},
      "full_log": "...",
      "data": {...},
      "location": "..."
    }
    """
    id: str
    timestamp: str
    rule: WazuhRule
    agent: WazuhAgent
    decoder: Optional[WazuhDecoder] = None
    full_log: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    location: Optional[str] = None

    # Convenience properties for backward compatibility
    @property
    def rule_id(self) -> str:
        return self.rule.id

    @property
    def rule_level(self) -> int:
        return self.rule.level

    @property
    def rule_description(self) -> str:
        return self.rule.description

    @property
    def agent_id(self) -> str:
        return self.agent.id

    @property
    def agent_name(self) -> str:
        return self.agent.name

    @property
    def decoder_name(self) -> Optional[str]:
        return self.decoder.name if self.decoder else None


class ClassificationResult(BaseModel):
    threat_type: str
    severity_score: float
    confidence: float
    mitre_technique: Optional[str] = None
    summary: str


class DecisionResult(BaseModel):
    action_type: str
    target: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    requires_approval: bool
    reason: str


class ActionResult(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class AlertEmbedding(BaseModel):
    alert_id: str
    embedding: List[float]
    metadata: Dict[str, Any]


class PlaybookEntry(BaseModel):
    playbook_id: str
    threat_type: str
    severity_range: List[float]
    conditions: Dict[str, Any]
    recommended_action: str
    action_parameters: Dict[str, Any]
    approval_required: bool
    description: str
