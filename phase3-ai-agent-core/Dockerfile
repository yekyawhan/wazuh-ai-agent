
# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Qdrant client (if any, e.g., for grpcio)
# For now, assuming slim-bookworm has most needed, add more if issues arise.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables for configuration
ENV OPENAI_API_KEY="YOUR_OPENAI_API_KEY" \
    QDRANT_HOST="qdrant" \
    QDRANT_PORT=6333 \
    WAZUH_API_URL="https://wazuh-api:55000" \
    WAZUH_API_USER="wazuh_api_user" \
    WAZUH_API_PASSWORD="wazuh_api_password" \
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN" \
    TELEGRAM_CHAT_ID=1721493612 \
    FASTAPI_HOST="0.0.0.0" \
    FASTAPI_PORT=8000 \
    LOG_LEVEL="INFO"

# Run the FastAPI application
CMD ["uvicorn", "ai_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
