
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

    # Qdrant settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_ALERTS: str = os.getenv("QDRANT_COLLECTION_ALERTS", "wazuh_alerts")
    QDRANT_COLLECTION_PLAYBOOKS: str = os.getenv("QDRANT_COLLECTION_PLAYBOOKS", "security_playbooks")

    # Wazuh API settings
    WAZUH_API_URL: str = os.getenv("WAZUH_API_URL", "https://localhost:55000")
    WAZUH_API_USER: str = os.getenv("WAZUH_API_USER", "wazuh_api_user")
    WAZUH_API_PASSWORD: str = os.getenv("WAZUH_API_PASSWORD", "wazuh_api_password")

    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: int = int(os.getenv("TELEGRAM_CHAT_ID", 1721493612)) # User's provided chat ID

    # AI Agent thresholds
    AUTO_ACTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("AUTO_ACTION_CONFIDENCE_THRESHOLD", 0.9))
    RECOMMEND_ACTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("RECOMMEND_ACTION_CONFIDENCE_THRESHOLD", 0.6))

    # FastAPI settings
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", 8000))

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
