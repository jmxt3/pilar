
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from small_agent.api import app, session_states
from google.genai import types

client = TestClient(app)

@pytest.fixture
def mock_runner_run_async():
    with patch("small_agent.api.runner.run_async") as mock_run:
        yield mock_run

def test_create_conversation():
    response = client.post("/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] in session_states

def test_get_conversation_state_not_found():
    response = client.get("/conversations/non-existent-id")
    assert response.status_code == 404

def test_send_message_flow(mock_runner_run_async):
    # 1. Create conversation
    create_resp = client.post("/conversations/")
    conv_id = create_resp.json()["conversation_id"]
    
    # 2. Mock Runner response
    # It yields events. A ModelTurn event has content.
    async def event_generator(*args, **kwargs):
        # Create a mock event with text content
        mock_event = MagicMock()
        mock_event.content.parts = [types.Part(text="Hello human")]
        yield mock_event
        
    mock_runner_run_async.side_effect = event_generator
    
    # 3. Send message
    msg_resp = client.post(
        f"/conversations/{conv_id}/messages/",
        json={"text": "Hi bot"}
    )
    
    assert msg_resp.status_code == 200
    messages = msg_resp.json()
    assert len(messages) == 1
    assert messages[0]["role"] == "model"
    assert messages[0]["text"] == "Hello human"
    
    # 4. Check internal state history
    state = session_states[conv_id]
    # Should have user message and model message
    assert len(state.messages) == 2
    assert state.messages[0]["role"] == "user"
    assert state.messages[0]["text"] == "Hi bot"
    assert state.messages[1]["role"] == "model"
    assert state.messages[1]["text"] == "Hello human"

def test_get_chat_history():
    # Setup state manually
    conv_id = "history-test"
    from small_agent.state import AgentState
    session_states[conv_id] = AgentState(conversation_id=conv_id)
    session_states[conv_id].messages = [
        {"role": "user", "text": "A"},
        {"role": "model", "text": "B"}
    ]
    
    response = client.get(f"/conversations/{conv_id}/messages/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 2
    assert data["messages"][0]["text"] == "A"
