# Small Agent - Configurable Intake Agent

A minimal, configurable RESTful Web API using FastAPI and Google Agent Development Kit (ADK) for a customer support intake agent. The agent collects user information based on a configuration and escalates to a human when necessary.

## Prerequisites

- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** package manager installed.
- **Google Cloud Project** with Vertex AI API enabled.
- **Google Cloud Credentials** configured locally (e.g., via `gcloud auth application-default login`).

## Installation

1.  Clone the repository.
2.  Install dependencies using `uv`:

    ```bash
    uv sync
    ```

## Configuration

1.  Create a `.env` file in the root directory (or in `config/` if preferred, but root is standard for `uv run`).
2.  Add your Google Cloud Project details:

    ```env
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

   *Note: Ensure you have authenticated using `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`.*

## Running the Agent

You can run the agent interactively using the Google ADK CLI or the provided python script.

### Option 1: Using Google ADK CLI (Recommended for Development)

To run the agent with a local debug UI (Inspector):

```bash
uv run adk run small_agent.agent:root_agent --ui
```

To run the agent in the terminal:

```bash
uv run adk run small_agent.agent:root_agent
```

### Option 2: Using the Main Script

We also provide a standalone script to run the agent in the terminal:

```bash
uv run python small_agent/main.py
```

## using and Testing the API

The project includes a FastAPI-based REST API to interact with the agent programmatically.

### 1. Start the API Server

```bash
uv run uvicorn small_agent.api:app --reload --host 127.0.0.1 --port 8000
```

### 2. API Endpoints

-   **Create Conversation**: `POST /conversations/`
-   **Send Message**: `POST /conversations/{conversation_id}/messages/`
-   **Get History**: `GET /conversations/{conversation_id}/messages/`
-   **Get State**: `GET /conversations/{conversation_id}`

### 3. Testing the API

We have provided a test script `test_api.py` that simulates a full conversation flow (creation, sending messages, checking history and state).

```bash
uv run python test_api.py
```

*Ensure the API server is running in a separate terminal before running the test script.*

## Running Evaluations

To run the evaluation set (defined in `basic_eval.py`) which tests the agent against "Happy Path" and "Escalation Trigger" scenarios:

```bash
uv run python basic_eval.py
```

This script will output the conversation logs and pass/fail results for escalation and field collection.
