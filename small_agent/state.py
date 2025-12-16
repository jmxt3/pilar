from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class ConversationStatus(str, Enum):
    COLLECTING = "COLLECTING"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"

class AgentState(BaseModel):
    conversation_id: str
    status: ConversationStatus = ConversationStatus.COLLECTING
    collected_fields: Dict[str, str] = Field(default_factory=dict)
    summary: Optional[str] = None
    messages: List[Dict[str, str]] = Field(default_factory=list)

    def is_complete(self, required_fields: List[str]) -> bool:
        """
        Checks if all required fields have been collected.
        """
        if self.status in [ConversationStatus.ESCALATED, ConversationStatus.COMPLETED]:
            return True
            
        # Check if all required fields are in collected_fields and have a non-empty value
        for field in required_fields:
            if field.lower() not in self.collected_fields or not self.collected_fields[field.lower()]:
                return False
        return True
