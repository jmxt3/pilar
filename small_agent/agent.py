from typing import Any, Dict

from google.adk import Agent
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

try:
    from .state import AgentState
    from .tools import AgentTools
except ImportError:
    from state import AgentState
    from tools import AgentTools

from .llm_client import GeminiADKClient
from config.loader import get_config

# Load configuration
# Load configuration
project_config = get_config()
persona = project_config.persona
required_names = ", ".join([f.name for f in project_config.fields if f.required])
field_desc = "\n    ".join([f"- {f.name}: {f.description}" for f in project_config.fields])
escalation_triggers = ", ".join(project_config.escalation.triggers)

# In-memory store for agent state per session
session_states: Dict[str, AgentState] = {}


def _get_tools(tool_context: ToolContext) -> AgentTools:
    """Retrieves or creates the AgentTools instance for the current session."""
    try:
        session_id = tool_context.session.id
    except AttributeError:
        # Fallback or try to inspect what tool_context has if session doesn't have id
        # But assuming session.id exists based on typical ADK structure
        session_id = str(tool_context.session)

    if session_id not in session_states:
        session_states[session_id] = AgentState(conversation_id=session_id)
    return AgentTools(session_states[session_id])


def collect_field(name: str, value: str, tool_context: ToolContext) -> Dict[str, Any]:
  """Collects a specific piece of user information."""
  tools = _get_tools(tool_context)
  return tools.collect_field(name, value)


def escalate_conversation(
    reason: str, summary: str, tool_context: ToolContext
) -> Dict[str, Any]:
  """Escalates the conversation to a human agent."""
  tools = _get_tools(tool_context)
  return tools.escalate_conversation(reason, summary, tool_context)



# LLM Client initialization
llm_client = GeminiADKClient(model_name=project_config.llm.model)

root_agent = llm_client.create_agent(
    name='customer_support_agent',
    instruction=f"""
    You are {persona.name}, {persona.title} at {persona.company_name}.
    Personality: {persona.personality}
    
    Your goal is to collect the following user information:
    {field_desc}
    
    Rules:
    1. Only ask for ONE missing field at a time.
    2. Call the 'collect_field' tool when the user provides a field value.
    3. The 'collect_field' tool will tell you which fields are still missing. Use that info to decide what to ask next.
    4. If the 'collect_field' tool returns 'is_complete': True, Call 'escalate_conversation' immediately.
    5. If the user mentions an escalation trigger (e.g. {escalation_triggers}), call 'escalate_conversation' immediately.
    6. Main Greeting to use at start: "{persona.greeting_template.format(name=persona.name, title=persona.title)}"
    7. Start small talk if the user asks unrelated questions, then pivot back to collection.
    8. Do not make up info.
    """,
    tools=[collect_field, LongRunningFunctionTool(func=escalate_conversation)],
    config=types.GenerateContentConfig(temperature=project_config.llm.temperature),
)
