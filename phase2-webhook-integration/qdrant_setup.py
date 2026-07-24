
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "wazuh_alerts"
VECTOR_SIZE = 768  # This should match the embedding model you plan to use

def initialize_qdrant_client():
    try:
        client = qdrant_client.QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        logging.info(f"Successfully connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Qdrant: {e}")
        return None

def create_collection(client):
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        logging.info(f"Collection \'{COLLECTION_NAME}\' recreated successfully.")
        # Add payload indexing for common fields
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="rule.id",
            field_schema="keyword"
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="rule.level",
            field_schema="integer"
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="agent.name",
            field_schema="keyword"
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="data.srcip",
            field_schema="keyword"
        )
        logging.info("Payload indexes created for common alert fields.")
        return True
    except Exception as e:
        logging.error(f"Failed to create collection \'{COLLECTION_NAME}\': {e}")
        return False

def store_alert(client, alert_data, vector_embedding):
    try:
        # Qdrant expects a list of points
        points = [
            PointStruct(
                id=alert_data.get("id", None) or alert_data.get("timestamp"), # Use a unique ID, timestamp as fallback
                vector=vector_embedding,
                payload=alert_data,
            )
        ]
        operation_info = client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points
        )
        logging.info(f"Alert stored in Qdrant. Operation info: {operation_info}")
        return True
    except Exception as e:
        logging.error(f"Failed to store alert in Qdrant: {e}")
        return False

def query_alerts(client, query_vector, limit=5):
    try:
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        logging.info(f"Query returned {len(search_result)} results.")
        return search_result
    except Exception as e:
        logging.error(f"Failed to query alerts from Qdrant: {e}")
        return []


if __name__ == "__main__":
    client = initialize_qdrant_client()
    if client:
        if create_collection(client):
            logging.info("Qdrant setup complete. Collection and indexes are ready.")
            # Example usage (requires an actual alert JSON and a vector embedding)
            # For demonstration, we'll just show the setup part.
            # To store an alert, you would call store_alert(client, your_alert_json, your_embedding_vector)
            # To query, you would call query_alerts(client, your_query_embedding_vector)
    else:
        logging.error("Qdrant client not initialized. Please ensure Qdrant is running.")
