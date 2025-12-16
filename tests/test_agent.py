
import pytest
from unittest.mock import MagicMock, patch
from small_agent.state import AgentState, ConversationStatus
from small_agent.tools import AgentTools
from config.models import BaseConfig, FieldConfig

@pytest.fixture
def mock_config():
    config = BaseConfig()
    config.fields = [
        FieldConfig(name="name", description="User name", required=True),
        FieldConfig(name="email", description="User email", required=True),
        FieldConfig(name="phone", description="User phone", required=False),
    ]
    return config

@pytest.fixture
def agent_state():
    return AgentState(conversation_id="test_session")

def test_collect_field_incomplete(agent_state, mock_config):
    tools = AgentTools(agent_state)
    
    with patch("config.loader.get_config", return_value=mock_config):
        # Collect first field
        result = tools.collect_field("name", "John")
        
        assert result["status"] == "collected"
        assert result["field"] == "name"
        assert result["value"] == "John"
        assert result["is_complete"] is False
        assert "email" in result["missing_fields"]
        assert "name" not in result["missing_fields"]
        assert agent_state.collected_fields["name"] == "John"

def test_collect_field_complete(agent_state, mock_config):
    tools = AgentTools(agent_state)
    
    with patch("config.loader.get_config", return_value=mock_config):
        # Collect all required fields
        tools.collect_field("name", "John")
        result = tools.collect_field("email", "john@example.com")
        
        assert result["is_complete"] is True
        assert len(result["missing_fields"]) == 0
        assert agent_state.collected_fields["email"] == "john@example.com"

def test_escalate_conversation(agent_state):
    tools = AgentTools(agent_state)
    mock_context = MagicMock()
    
    result = tools.escalate_conversation(
        reason="User request",
        summary="User wants a human",
        tool_context=mock_context
    )
    
    assert result["status"] == "escalated"
    assert result["ticketId"].startswith("support-ticket-")
    assert agent_state.status == ConversationStatus.ESCALATED
    assert "User wants a human" in agent_state.summary
