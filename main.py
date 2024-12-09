# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field, validator
from typing import List
import json
from datetime import datetime
import asyncio
import aiohttp
import logging
from typing import Optional
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
ping_task: Optional[asyncio.Task] = None


if not API_KEY:
    raise ValueError("API_KEY environment variable must be set")

async def ping_server():
    """Keeps the server alive by pinging it every 5 minutes"""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get("https://message-api-0rws.onrender.com/messages/") as response:
                    logging.info(f"Ping status: {response.status}")
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logging.error(f"Ping failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

@app.on_event("startup")
async def start_ping():
    global ping_task
    ping_task = asyncio.create_task(ping_server())

@app.on_event("shutdown")
async def stop_ping():
    if ping_task:
        ping_task.cancel()

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
    
    @validator('message')
    def validate_message_length(cls, v):
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'Message must be {MAX_MESSAGE_LENGTH} characters or less')
        return v

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


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <html>
        <head>
            <title>Message API Privacy Policy</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 40px auto; 
                    padding: 0 20px; 
                    line-height: 1.6; 
                }
            </style>
        </head>
        <body>
            <h1>Privacy Policy for Message API</h1>
            <p>Last updated: December 8, 2024</p>
            
            <h2>Information We Collect</h2>
            <p>Our API service collects and stores the following information:</p>
            <ul>
                <li>Message content (limited to 500 characters)</li>
                <li>Sender name</li>
                <li>Timestamp of message creation</li>
                <li>Message read status</li>
            </ul>
            
            <h2>How We Use Information</h2>
            <p>The collected information is used solely for:</p>
            <ul>
                <li>Storing and retrieving messages as requested through the API</li>
                <li>Managing message read/unread status</li>
            </ul>
            
            <h2>Data Retention</h2>
            <p>Messages are stored until:</p>
            <ul>
                <li>They are automatically removed when the 1000 message limit is reached</li>
                <li>The service is reset or redeployed</li>
            </ul>
            
            <h2>Security</h2>
            <p>Access to the API is protected by API key authentication. All requests must include a valid API key.</p>
            
            <h2>Contact</h2>
            <p>For any privacy-related questions, please create an issue in the GitHub repository.</p>
        </body>
    </html>
    """

@app.get("/.well-known/openapi.yaml")
async def get_openapi_yaml():
    """
    Provides a simplified OpenAPI schema specifically for ChatGPT actions.
    """
    openapi_schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Message API",
            "description": f"API for sending messages (max {MAX_MESSAGE_LENGTH} characters)",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://message-api-0rws.onrender.com"
            }
        ],
        "paths": {
            "/messages/": {
                "post": {
                    "summary": "Create a new message",
                    "operationId": "createMessage",
                    "security": [
                        {
                            "ApiKeyAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["sender", "message"],
                                    "properties": {
                                        "sender": {
                                            "type": "string",
                                            "description": "Name of the message sender"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": f"Content of the message (max {MAX_MESSAGE_LENGTH} characters)",
                                            "maxLength": MAX_MESSAGE_LENGTH
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Message created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "string",
                                                "format": "uuid"
                                            },
                                            "sender": {
                                                "type": "string"
                                            },
                                            "message": {
                                                "type": "string"
                                            },
                                            "read": {
                                                "type": "boolean"
                                            },
                                            "timestamp": {
                                                "type": "string",
                                                "format": "date-time"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Message too long or validation error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "detail": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {},
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
    return JSONResponse(content=openapi_schema)


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