from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext
from .state import AgentState, ConversationStatus

class AgentTools:
    def __init__(self, state: AgentState):
        self.state = state

    def collect_field(self, name: str, value: str) -> Dict[str, Any]:
        """
        Collects a specific piece of user information.

        Args:
            name: The name of the field to collect (e.g., 'name', 'email', 'phone').
            value: The value provided by the user.
        """
        from config.loader import get_config
        config = get_config()
        required_fields = [f.name for f in config.fields if f.required]

        # Normalize field name to lower case
        field_key = name.lower()
        self.state.collected_fields[field_key] = value
        
        is_complete = self.state.is_complete(required_fields)
        missing_fields = [f for f in required_fields if f not in self.state.collected_fields]

        return {
            'status': 'collected',
            'field': field_key,
            'value': value,
            'is_complete': is_complete,
            'missing_fields': missing_fields
        }

    def escalate_conversation(
        self, reason: str, summary: str, tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Escalates the conversation to a human agent.

        Args:
            reason: The reason for escalation.
            summary: A summary of the conversation so far.
            tool_context: The context for the tool execution.
        """
        self.state.status = ConversationStatus.ESCALATED
        self.state.summary = f"Escalated due to: {reason}. Summary: {summary}"
        
        # In a real app, this might create a ticket in an external system
        ticket_id = f"support-ticket-{self.state.conversation_id}"
        
        return {
            'status': 'escalated',
            'reason': reason,
            'summary': summary,
            'ticketId': ticket_id,
        }
