import logging
import uuid
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from openai import OpenAI
from typing import List, Dict, Any, Optional

from .config import Config
from .models import WazuhAlert, ClassificationResult, AlertEmbedding, PlaybookEntry

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.OPENAI_EMBEDDING_MODEL
        self.alert_collection_name = Config.QDRANT_COLLECTION_ALERTS
        self.playbook_collection_name = Config.QDRANT_COLLECTION_PLAYBOOKS
        self._initialize_collections()

    def _collection_exists(self, collection_name: str) -> bool:
        """Check if a Qdrant collection already exists."""
        try:
            self.qdrant_client.get_collection(collection_name)
            return True
        except (UnexpectedResponse, Exception):
            return False

    def _initialize_collections(self):
        """Initialize Qdrant collections only if they don't already exist."""
        # Initialize alerts collection
        if not self._collection_exists(self.alert_collection_name):
            try:
                self.qdrant_client.create_collection(
                    collection_name=self.alert_collection_name,
                    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
                )
                logger.info(f"Qdrant collection '{self.alert_collection_name}' created.")
            except Exception as e:
                logger.warning(f"Could not create collection '{self.alert_collection_name}': {e}")
        else:
            logger.info(f"Qdrant collection '{self.alert_collection_name}' already exists.")

        # Initialize playbooks collection
        if not self._collection_exists(self.playbook_collection_name):
            try:
                self.qdrant_client.create_collection(
                    collection_name=self.playbook_collection_name,
                    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
                )
                logger.info(f"Qdrant collection '{self.playbook_collection_name}' created.")
                # Add default playbooks only on first creation
                self._add_default_playbooks()
            except Exception as e:
                logger.warning(f"Could not create collection '{self.playbook_collection_name}': {e}")
        else:
            logger.info(f"Qdrant collection '{self.playbook_collection_name}' already exists.")

    def _generate_uuid(self, seed: str) -> str:
        """Generate a deterministic UUID from a string seed."""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))

    def _add_default_playbooks(self):
        """Add default security playbooks to Qdrant."""
        playbooks = [
            PlaybookEntry(
                playbook_id="pb-malware-001",
                threat_type="malware",
                severity_range=[7.0, 10.0],
                conditions={"os": "windows", "process_name": "malicious.exe"},
                recommended_action="isolate_host",
                action_parameters={"reason": "detected malware"},
                approval_required=False,
                description="Isolate host on high-severity malware detection."
            ),
            PlaybookEntry(
                playbook_id="pb-bruteforce-001",
                threat_type="brute_force",
                severity_range=[5.0, 10.0],
                conditions={"service": "ssh", "failed_attempts": 5},
                recommended_action="block_ip",
                action_parameters={"duration": "1h"},
                approval_required=False,
                description="Block source IP for 1 hour after multiple failed SSH login attempts."
            ),
            PlaybookEntry(
                playbook_id="pb-privesc-001",
                threat_type="privilege_escalation",
                severity_range=[8.0, 10.0],
                conditions={},
                recommended_action="collect_forensics",
                action_parameters={"scope": "full"},
                approval_required=True,
                description="Collect full forensics on privilege escalation, requires admin approval."
            ),
            PlaybookEntry(
                playbook_id="pb-lateral-001",
                threat_type="lateral_movement",
                severity_range=[7.0, 10.0],
                conditions={},
                recommended_action="isolate_host",
                action_parameters={"reason": "lateral movement detected"},
                approval_required=True,
                description="Isolate host on lateral movement detection, requires admin approval."
            ),
            PlaybookEntry(
                playbook_id="pb-exfil-001",
                threat_type="data_exfiltration",
                severity_range=[8.0, 10.0],
                conditions={},
                recommended_action="block_ip",
                action_parameters={"duration": "24h", "reason": "data exfiltration"},
                approval_required=False,
                description="Block destination IP for 24 hours on data exfiltration detection."
            ),
            PlaybookEntry(
                playbook_id="pb-c2-001",
                threat_type="command_and_control",
                severity_range=[8.0, 10.0],
                conditions={},
                recommended_action="isolate_host",
                action_parameters={"reason": "C2 communication detected"},
                approval_required=False,
                description="Isolate host immediately on C2 communication detection."
            ),
        ]
        points = []
        for pb in playbooks:
            embedding = self._get_embedding(pb.description)
            point_id = self._generate_uuid(pb.playbook_id)
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=pb.model_dump()
            ))
        if points:
            self.qdrant_client.upsert(
                collection_name=self.playbook_collection_name,
                points=points,
                wait=True
            )
            logger.info(f"Added {len(points)} default playbooks to '{self.playbook_collection_name}'.")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector from text using OpenAI."""
        text = text.replace("\n", " ").strip()
        response = self.openai_client.embeddings.create(input=[text], model=self.embedding_model)
        return response.data[0].embedding

    async def store_alert_embedding(self, alert: WazuhAlert, classification: ClassificationResult):
        """Store alert with its embedding in Qdrant for future similarity search."""
        try:
            alert_text = f"Rule: {alert.rule_description}. Agent: {alert.agent_name}. Summary: {classification.summary}"
            if alert.full_log:
                alert_text += f" Log: {alert.full_log[:500]}"
            embedding = self._get_embedding(alert_text)

            payload = {
                "alert_id": alert.id,
                "timestamp": alert.timestamp,
                "rule_id": alert.rule_id,
                "rule_level": alert.rule_level,
                "rule_description": alert.rule_description,
                "agent_id": alert.agent_id,
                "agent_name": alert.agent_name,
                "threat_type": classification.threat_type,
                "severity_score": classification.severity_score,
                "confidence": classification.confidence,
                "mitre_technique": classification.mitre_technique,
                "summary": classification.summary,
            }

            point_id = self._generate_uuid(alert.id)
            self.qdrant_client.upsert(
                collection_name=self.alert_collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ],
                wait=True
            )
            logger.info(f"Stored embedding for alert {alert.id}.")
        except Exception as e:
            logger.error(f"Error storing alert embedding for {alert.id}: {e}")

    async def retrieve_similar_alerts(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve similar past alerts using vector similarity search."""
        try:
            query_embedding = self._get_embedding(query_text)
            search_result = self.qdrant_client.search(
                collection_name=self.alert_collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            return [hit.payload for hit in search_result]
        except Exception as e:
            logger.error(f"Error retrieving similar alerts for query '{query_text}': {e}")
            return []

    async def retrieve_playbooks(self, threat_type: str, severity_score: float, limit: int = 3) -> List[PlaybookEntry]:
        """Retrieve matching playbooks based on threat type and severity."""
        try:
            query_embedding = self._get_embedding(f"{threat_type} security incident with severity {severity_score}")

            filter_conditions = models.Filter(
                must=[
                    models.FieldCondition(
                        key="threat_type",
                        match=models.MatchValue(value=threat_type)
                    ),
                    models.FieldCondition(
                        key="severity_range",
                        range=models.Range(lte=severity_score)
                    ),
                ]
            )

            search_result = self.qdrant_client.search(
                collection_name=self.playbook_collection_name,
                query_vector=query_embedding,
                query_filter=filter_conditions,
                limit=limit,
                with_payload=True
            )
            return [PlaybookEntry(**hit.payload) for hit in search_result]
        except Exception as e:
            logger.error(f"Error retrieving playbooks for threat_type '{threat_type}' and severity '{severity_score}': {e}")
            return []

    async def add_playbook(self, playbook: PlaybookEntry):
        """Add a new playbook to the knowledge base."""
        try:
            embedding = self._get_embedding(playbook.description)
            point_id = self._generate_uuid(playbook.playbook_id)
            self.qdrant_client.upsert(
                collection_name=self.playbook_collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=playbook.model_dump()
                    )
                ],
                wait=True
            )
            logger.info(f"Added playbook '{playbook.playbook_id}' to knowledge base.")
        except Exception as e:
            logger.error(f"Error adding playbook '{playbook.playbook_id}': {e}")
