
import logging
from typing import List, Dict, Any

from .config import Config
from .models import WazuhAlert, ClassificationResult, DecisionResult, PlaybookEntry
from .knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    async def make_decision(self, alert: WazuhAlert, classification: ClassificationResult) -> DecisionResult:
        action_type = "ALERT_ONLY"
        requires_approval = True
        target = None
        parameters = {}
        reason = "Default: Log and notify due to low confidence or no specific playbook match."

        # Retrieve similar past incidents for context
        similar_alerts = await self.kb.retrieve_similar_alerts(classification.summary)
        if similar_alerts:
            reason += f"\nSimilar past incidents found: {[a['alert_id'] for a in similar_alerts]}"

        # Retrieve relevant playbooks
        relevant_playbooks = await self.kb.retrieve_playbooks(classification.threat_type, classification.severity_score)
        
        # Prioritize playbooks based on confidence and severity
        if relevant_playbooks:
            # For simplicity, let's pick the first matching playbook. 
            # In a real scenario, more sophisticated logic would be needed to choose the best playbook.
            best_playbook = relevant_playbooks[0]
            logger.info(f"Found relevant playbook: {best_playbook.playbook_id}")

            # Check if playbook conditions match the alert (simplified for now)
            # A more robust implementation would parse alert.data and match against playbook.conditions
            conditions_met = True # Assume conditions are met for now

            if conditions_met:
                action_type = best_playbook.recommended_action
                parameters = best_playbook.action_parameters
                requires_approval = best_playbook.approval_required
                reason = f"Action determined by playbook \'{best_playbook.playbook_id}\': {best_playbook.description}"

                # Determine target based on action type and alert data
                if action_type == "block_ip" and alert.data and "srcip" in alert.data:
                    target = alert.data["srcip"]
                elif action_type == "isolate_host" and alert.agent_name:
                    target = alert.agent_name
                elif action_type == "kill_process" and alert.data and "process.name" in alert.data:
                    target = alert.data["process.name"]
                elif action_type == "disable_user" and alert.data and "user.name" in alert.data:
                    target = alert.data["user.name"]
                
                # Override approval based on confidence thresholds if playbook allows auto
                if not requires_approval:
                    if classification.confidence >= Config.AUTO_ACTION_CONFIDENCE_THRESHOLD:
                        action_type = action_type # Keep auto action
                        requires_approval = False
                        reason += "\nConfidence high enough for automatic execution."
                    elif classification.confidence >= Config.RECOMMEND_ACTION_CONFIDENCE_THRESHOLD:
                        action_type = "RECOMMEND"
                        requires_approval = True
                        reason += "\nConfidence sufficient for recommendation, requires approval."
                    else:
                        action_type = "ALERT_ONLY"
                        requires_approval = True
                        reason += "\nConfidence too low for automatic action, reverting to alert only."
            else:
                reason += "\nNo specific playbook conditions met for an automated action."

        # Fallback to confidence-based decision if no playbook or conditions not met
        if action_type == "ALERT_ONLY" and classification.confidence >= Config.AUTO_ACTION_CONFIDENCE_THRESHOLD:
            action_type = "RECOMMEND" # Default to recommend if high confidence but no specific auto action
            requires_approval = True
            reason = f"High confidence ({classification.confidence:.2f}) in classification, recommending action."
        elif action_type == "ALERT_ONLY" and classification.confidence >= Config.RECOMMEND_ACTION_CONFIDENCE_THRESHOLD:
            action_type = "RECOMMEND"
            requires_approval = True
            reason = f"Medium confidence ({classification.confidence:.2f}) in classification, recommending action."

        return DecisionResult(
            action_type=action_type,
            target=target,
            parameters=parameters,
            requires_approval=requires_approval,
            reason=reason
        )
