
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support
# Assuming a simple text-based classification for demonstration
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Placeholder for Qdrant client and embedding model
class MockQdrantClient:
    def __init__(self):
        print("Initializing Mock Qdrant Client...")
        self.collection = []

    def upsert_vectors(self, vectors, payloads):
        for vec, pay in zip(vectors, payloads):
            self.collection.append({"vector": vec.tolist(), "payload": pay})
        print(f"Upserted {len(vectors)} vectors to Mock Qdrant.")

class MockEmbeddingModel:
    def __init__(self):
        print("Initializing Mock Embedding Model...")

    def encode(self, texts):
        # In a real scenario, this would use a pre-trained embedding model (e.g., Sentence-BERT, OpenAI embeddings)
        # For now, a simple hash or TF-IDF like representation
        vectorizer = TfidfVectorizer(max_features=100)
        return vectorizer.fit_transform(texts).toarray()

def load_labeled_data(input_file):
    """Loads labeled alerts from a JSONL file."""
    labeled_alerts = []
    try:
        with open(input_file, 'r') as f:
            for line in f:
                labeled_alerts.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: Labeled data file {input_file} not found.")
    return labeled_alerts

def fine_tune_classification_model(X_train, y_train, X_test, y_test):
    """Fine-tunes a classification model and evaluates it."""
    print("Fine-tuning classification model...")

    # For demonstration, using a simple Logistic Regression with TF-IDF features
    # In a real scenario, this would involve a more sophisticated model (e.g., BERT-based classifier)
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)

    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)

    print("\n--- Model Evaluation ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")

    return model, vectorizer # Return model and vectorizer for later use

def populate_qdrant_knowledge_base(qdrant_client, embedding_model, historical_alerts):
    """Generates embeddings and populates the Qdrant knowledge base."""
    print("Populating Qdrant knowledge base with historical alerts...")

    texts_to_embed = []
    payloads = []

    for alert in historical_alerts:
        # Extract relevant text for embedding. Adjust as needed.
        text = alert.get("original_alert", {}).get("full_log", "")
        if not text:
            text = alert.get("original_alert", {}).get("rule", {}).get("description", "")
        
        if text:
            texts_to_embed.append(text)
            payloads.append({
                "alert_id": alert.get("original_alert", {}).get("id"),
                "threat_type": alert.get("threat_type"),
                "severity": alert.get("severity"),
                "correct_response": alert.get("correct_response"),
                "timestamp": alert.get("original_alert", {}).get("timestamp")
            })

    if texts_to_embed:
        embeddings = embedding_model.encode(texts_to_embed)
        qdrant_client.upsert_vectors(embeddings, payloads)
    else:
        print("No text found in historical alerts to embed.")

def main():
    labeled_data_file = os.getenv("LABELED_DATA_FILE", "labeled_alerts.jsonl")
    
    labeled_alerts = load_labeled_data(labeled_data_file)
    if not labeled_alerts:
        print("No labeled alerts found for training. Exiting.")
        return

    # Prepare data for classification model training
    # Using 'full_log' or 'description' as features, and 'threat_type' as target
    X = [alert.get("original_alert", {}).get("full_log", alert.get("original_alert", {}).get("rule", {}).get("description", "")) for alert in labeled_alerts]
    y = [alert["threat_type"] for alert in labeled_alerts]

    # Filter out empty features
    filtered_data = [(x, y_val) for x, y_val in zip(X, y) if x.strip()]
    if not filtered_data:
        print("No valid data points after filtering empty features. Exiting.")
        return
    X_filtered, y_filtered = zip(*filtered_data)

    X_train, X_test, y_train, y_test = train_test_split(list(X_filtered), list(y_filtered), test_size=0.2, random_state=42)

    # Fine-tune classification model
    classification_model, vectorizer = fine_tune_classification_model(X_train, y_train, X_test, y_test)

    # Initialize Qdrant client and embedding model
    qdrant_client = MockQdrantClient()
    embedding_model = MockEmbeddingModel()

    # Populate Qdrant knowledge base
    populate_qdrant_knowledge_base(qdrant_client, embedding_model, labeled_alerts)

    print("Training pipeline completed.")

if __name__ == '__main__':
    main()
