
import asyncio
import os
import uuid
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

from .agent import root_agent, session_states
from .state import AgentState, ConversationStatus

# Models
class CreateConversationResponse(BaseModel):
    conversation_id: str

class MessageRequest(BaseModel):
    text: str

class MessageResponse(BaseModel):
    role: str
    text: str

class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, str]]

class ConservationStateResponse(BaseModel):
    conversation_id: str
    status: ConversationStatus
    collected_fields: Dict[str, str]
    summary: Optional[str] = None
    messages: List[Dict[str, str]]

# Global Services
session_service = InMemorySessionService()
APP_NAME = "intake_agent_api"
# We can use a fixed user_id for now or make it dynamic, 
# but the task implies anonymous/single user per conversation context.
DEFAULT_USER_ID = "user" 

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic if needed
    yield
    # Shutdown logic if needed

app = FastAPI(title="Intake Agent API", lifespan=lifespan)

@app.post("/conversations/", response_model=CreateConversationResponse)
async def create_conversation():
    conversation_id = str(uuid.uuid4())
    
    # Create ADK session
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=DEFAULT_USER_ID,
        session_id=conversation_id
    )
    
    # Initialize AgentState
    # This ensures state exists before any messages
    session_states[conversation_id] = AgentState(conversation_id=conversation_id)
    
    return CreateConversationResponse(conversation_id=conversation_id)

@app.post("/conversations/{conversation_id}/messages/", response_model=List[MessageResponse])
async def send_message(conversation_id: str, message: MessageRequest):
    if conversation_id not in session_states:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update local state history
    state = session_states[conversation_id]
    state.messages.append({"role": "user", "text": message.text})
    
    # Prepare content for ADK
    content = types.Content(role="user", parts=[types.Part(text=message.text)])
    
    # Run agent
    responses: List[MessageResponse] = []
    
    try:
        events_async = runner.run_async(
            session_id=conversation_id,
            user_id=DEFAULT_USER_ID,
            new_message=content
        )
        
        async for event in events_async:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text_response = part.text.strip()
                        if text_response:
                            responses.append(MessageResponse(role="model", text=text_response))
                            state.messages.append({"role": "model", "text": text_response})
            
            # Note: We are currently expecting text responses. 
            # If the agent calls tools, those are handled by the runner and the agent loop.
            # Ideally, the agent eventually outputs text back to the user.
            
    except Exception as e:
        # In case of error (e.g. session not found in service, though we created it), handle gracefully
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    return responses

@app.get("/conversations/{conversation_id}/messages/", response_model=ChatHistoryResponse)
async def get_chat_history(conversation_id: str):
    if conversation_id not in session_states:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    state = session_states[conversation_id]
    return ChatHistoryResponse(messages=state.messages)

@app.get("/conversations/{conversation_id}", response_model=ConservationStateResponse)
async def get_conversation_state(conversation_id: str):
    if conversation_id not in session_states:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    state = session_states[conversation_id]
    return ConservationStateResponse(
        conversation_id=state.conversation_id,
        status=state.status,
        collected_fields=state.collected_fields,
        summary=state.summary,
        messages=state.messages
    )
