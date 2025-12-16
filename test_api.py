
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Create Conversation
    print("Creating conversation...")
    resp = requests.post(f"{BASE_URL}/conversations/")
    if resp.status_code != 200:
        print(f"Failed to create conversation: {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    conversation_id = data["conversation_id"]
    print(f"Conversation ID: {conversation_id}")
    
    # 2. Get Initial State
    print("\nGetting initial state...")
    resp = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
    if resp.status_code != 200:
        print(f"Failed to get state: {resp.text}")
        sys.exit(1)
    print(f"State: {resp.json()}")

    # 3. Send Message
    print("\nSending message: 'Hello, my name is John Doe'")
    resp = requests.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages/",
        json={"text": "Hello, my name is John Doe"}
    )
    if resp.status_code != 200:
        print(f"Failed to send message: {resp.text}")
        sys.exit(1)
    
    messages = resp.json()
    print("Bot Responses:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['text']}")

    # 4. Get History
    print("\nGetting chat history...")
    resp = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages/")
    if resp.status_code != 200:
        print(f"Failed to get history: {resp.text}")
        sys.exit(1)
    history = resp.json()
    print(f"History count: {len(history['messages'])}")
    for msg in history['messages']:
        print(f"  {msg['role']}: {msg['text']}")

    # 5. Check Collected Fields
    print("\nChecking state for collected fields...")
    resp = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
    state = resp.json()
    print(f"Collected Fields: {state['collected_fields']}")

if __name__ == "__main__":
    test_flow()
