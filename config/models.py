from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class AgentPersona(BaseModel):
    name: str = "Kora"
    title: str = "Assistant"
    personality: str = "Warm, concise, helpful coordinator"
    company_name: str = "BrandName"
    greeting_template: str = "Hola, soy {name}, tu {title}. Te ayudo a registrar tus datos."

class FieldConfig(BaseModel):
    name: str
    description: str
    required: bool = True
    validation_regex: Optional[str] = None

class EscalationConfig(BaseModel):
    enabled: bool = True
    triggers: List[str] = Field(default_factory=list)

class LLMConfig(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    temperature: float = 0.1

class BaseConfig(BaseModel):
    persona: AgentPersona = Field(default_factory=AgentPersona)
    fields: List[FieldConfig] = Field(default_factory=list)
    escalation: EscalationConfig = Field(default_factory=EscalationConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
