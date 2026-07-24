
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any

from .config import Config
from .models import WazuhAlert, ClassificationResult, DecisionResult, ActionResult
from .classifier import AlertClassifier
from .knowledge_base import KnowledgeBase
from .decision_engine import DecisionEngine
from .action_executor import ActionExecutor

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL, format=
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances of components
classifier: AlertClassifier = None
knowledge_base: KnowledgeBase = None
decision_engine: DecisionEngine = None
action_executor: ActionExecutor = None

# Store some basic stats
agent_stats = {
    "total_alerts_received": 0,
    "alerts_classified": 0,
    "actions_recommended": 0,
    "actions_auto_executed": 0,
    "actions_alert_only": 0,
    "errors": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier, knowledge_base, decision_engine, action_executor
    logger.info("AI Agent starting up...")
    try:
        classifier = AlertClassifier()
        knowledge_base = KnowledgeBase()
        decision_engine = DecisionEngine(knowledge_base)
        action_executor = ActionExecutor()
        logger.info("AI Agent components initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize AI Agent components: {e}")
        raise RuntimeError(f"Failed to initialize AI Agent components: {e}")
    yield
    logger.info("AI Agent shutting down.")

app = FastAPI(title="Wazuh AI Agent", description="AI-powered security response agent for Wazuh SIEM", version="0.1.0", lifespan=lifespan)

async def process_alert_pipeline(alert: WazuhAlert):
    global agent_stats
    agent_stats["total_alerts_received"] += 1
    try:
        logger.info(f"Processing alert: {alert.id}")

        # 1. Classify Alert
        classification = await classifier.classify_alert(alert)
        agent_stats["alerts_classified"] += 1
        logger.info(f"Alert {alert.id} classified: {classification.threat_type} (Severity: {classification.severity_score}, Confidence: {classification.confidence})")

        # 2. Store alert embedding and retrieve context
        await knowledge_base.store_alert_embedding(alert, classification)
        
        # 3. Make Decision
        decision = await decision_engine.make_decision(alert, classification)
        logger.info(f"Decision for alert {alert.id}: {decision.action_type} (Requires Approval: {decision.requires_approval})")

        if decision.action_type == "AUTO":
            agent_stats["actions_auto_executed"] += 1
        elif decision.action_type == "RECOMMEND":
            agent_stats["actions_recommended"] += 1
        else:
            agent_stats["actions_alert_only"] += 1

        # 4. Execute Action
        action_result = await action_executor.execute_action(decision, alert)
        logger.info(f"Action execution for alert {alert.id}: {action_result.success} - {action_result.message}")

    except Exception as e:
        agent_stats["errors"] += 1
        logger.error(f"Error in alert processing pipeline for {alert.id}: {e}", exc_info=True)

@app.post("/analyze", response_model=Dict[str, Any], status_code=202)
async def analyze_alert(alert: WazuhAlert, background_tasks: BackgroundTasks):
    """Receives a Wazuh alert, processes it through the AI pipeline, and initiates a response."""
    logger.debug(f"Received alert for analysis: {alert.id}")
    background_tasks.add_task(process_alert_pipeline, alert)
    return JSONResponse(
        status_code=202,
        content={
            "message": "Alert received and being processed",
            "alert_id": alert.id
        }
    )

@app.get("/status", response_model=Dict[str, str])
async def get_status():
    """Returns the current status of the AI Agent."""
    return {"status": "running", "message": "Wazuh AI Agent is operational."}

@app.get("/stats", response_model=Dict[str, int])
async def get_stats():
    """Returns operational statistics of the AI Agent."""
    return agent_stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.FASTAPI_HOST, port=Config.FASTAPI_PORT)
