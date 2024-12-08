# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List
import json
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Simple file-based storage
MESSAGES_FILE = "messages.json"
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY environment variable must be set")

# Security
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Data model
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message: str
    read: bool = False
    timestamp: str = None

# Initialize storage
def load_messages() -> List[Message]:
    try:
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
            return [Message(**msg) for msg in messages]
    except FileNotFoundError:
        return []

def save_messages(messages: List[Message]):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump([msg.dict() for msg in messages], f)

# API endpoints
@app.post("/messages/", response_model=Message)
async def create_message(message: Message, api_key: str = Depends(verify_api_key)):
    messages = load_messages()
    
    if len(messages) >= 1000:
        raise HTTPException(status_code=400, detail="Maximum message limit reached")
    
    message.timestamp = datetime.now().isoformat()
    messages.append(message)
    save_messages(messages)
    return message

@app.get("/messages/", response_model=List[Message])
async def get_messages(api_key: str = Depends(verify_api_key)):
    return load_messages()

@app.get("/messages/unread", response_model=List[Message])
async def get_unread_messages(api_key: str = Depends(verify_api_key)):
    messages = load_messages()
    return [msg for msg in messages if not msg.read]

@app.put("/messages/{message_id}/read")
async def mark_as_read(message_id: str, api_key: str = Depends(verify_api_key)):
    messages = load_messages()
    for message in messages:
        if message.id == message_id:
            message.read = True
            save_messages(messages)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Message not found")

@app.delete("/messages/cleanup")
async def cleanup_messages(api_key: str = Depends(verify_api_key)):
    messages = load_messages()
    messages = messages[-900:]  # Keep last 900 messages
    save_messages(messages)
    return {"status": "success", "remaining_messages": len(messages)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)