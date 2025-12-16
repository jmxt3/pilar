import asyncio
import sys
import os
from typing import List
from dotenv import load_dotenv

# Ensure the current directory is in sys.path to handle imports correctly
sys.path.append(os.getcwd())
load_dotenv(os.path.join("small_agent", ".env"), override=True)

import small_agent.agent as agent
from config.loader import get_config
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

async def run_scenario(name: str, user_inputs: List[str]):
    print(f"\n{'-'*20} Scenario: {name} {'-'*20}")
    
    session_service = InMemorySessionService()
    # Create a unique session ID for this scenario
    session_id = f"session_{name.replace(' ', '_').lower()}"
    session = await session_service.create_session(
        app_name="eval_script", user_id="test_user", session_id=session_id
    )
    
    runner = Runner(
        agent=agent.root_agent,
        app_name="eval_script",
        session_service=session_service,
    )

    escalated = False

    model_responses = []

    for user_input in user_inputs:
        print(f"\nUser: {user_input}")
        
        async for event in runner.run_async(
            session_id=session.id, 
            user_id="test_user", 
            new_message=types.Content(role="user", parts=[types.Part(text=user_input)])
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text = part.text.strip()
                        # Print only the text part of the response
                        print(f"Agent: {text}")
                        model_responses.append(text)
                    
                    if part.function_call:
                        print(f"[Tool Call]: {part.function_call.name}")
                        if part.function_call.name == "escalate_conversation":
                            escalated = True
                            
    # Quality Checks
    print("\n--- Evaluation Results ---")
    
    # Check 1: Escalation
    if escalated:
        print("[PASS] Escalation triggered.")
    else:
        # Note: Depending on the scenario, this might be a fail or pass. 
        # But for our test cases, we expect escalation at the end.
        print("[FAIL] Escalation did NOT trigger.")

    # Check 2: Fields (Read directly from agent state)
    if session.id in agent.session_states:
        state = agent.session_states[session.id]
        print(f"State Status: {state.status}")
        print(f"Collected Fields: {state.collected_fields}")
        
        config = get_config()
        required = [f.name for f in config.fields if f.required]
        missing = [f for f in required if f not in state.collected_fields]
        
        if not missing:
             print("[PASS] All required fields collected.")
        else:
             print(f"[INFO] Missing fields: {missing}")
    else:
        print("[WARN] No state found for session.")

    # Check 3: Language/Tone (Basic Keyword Check)
    # We check the logs for common persona words
    # This is a heuristic.
    persona_keywords = ["Hola", "soy", "gracias", "gusto"]
    found_keywords = [kw for kw in persona_keywords if any(kw.lower() in resp.lower() for resp in model_responses)]
    
    if found_keywords:
        print(f"[PASS] Persona keywords found: {set(found_keywords)} (Indicates correct language/tone)")
    else:
        print("[WARN] No persona keywords found. Check language settings.")

async def main():
    # Scenario 1: Happy Path - User provides all info
    await run_scenario("Happy Path", [
        "Hola",
        "Juan Perez",
        "555-1234",
        "juan@example.com"
    ])

    # Scenario 2: Escalation Trigger - User says 'urgent' or 'refund request'
    await run_scenario("Escalation Trigger", [
        "Hola", 
        "Tengo un refund request urgente"
    ])

if __name__ == "__main__":
    asyncio.run(main())
