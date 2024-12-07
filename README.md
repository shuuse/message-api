# Message API Service

A simple REST API service for storing and managing messages. This service allows you to create, retrieve, and manage messages with a simple API key authentication system. Perfect for small applications needing to store up to 1000 messages.

## Features

- Create and store messages with sender information
- Mark messages as read/unread
- Retrieve and automatically mark unread messages
- Simple API key authentication
- Automatic timestamp addition
- Message limit enforcement (max 1000 messages)
- File-based storage
- Optional cleanup endpoint to manage message volume

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shuuse/message-api.git
cd message-api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

Start the service locally:
```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Create a Message
```http
POST /messages/
Header: X-API-Key: your-secret-key-here
Content-Type: application/json

{
    "sender": "ChatGPT",
    "message": "Hello world",
    "read": false
}
```

### Get All Messages
```http
GET /messages/
Header: X-API-Key: your-secret-key-here
```

### Get and Mark Unread Messages
```http
GET /messages/unread
Header: X-API-Key: your-secret-key-here
```
This endpoint returns all unread messages and marks them as read in a single operation.

### Mark Message as Read
```http
PUT /messages/{index}/read
Header: X-API-Key: your-secret-key-here
```

### Cleanup Old Messages
```http
DELETE /messages/cleanup
Header: X-API-Key: your-secret-key-here
```

## Configuration

The API key is set through an environment variable. Before running the service, set your API key:

```bash
export API_KEY=your-secret-key-here
```

## Deployment

This service can be deployed for free on Render.com:

1. Create a new Web Service on Render
2. Link your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `API_KEY`

## API Documentation

When running the service, visit `/docs` to see the automatic OpenAPI documentation and test the endpoints interactively.

## Example Usage

Python example using requests:
```python
import requests

headers = {
    'X-API-Key': 'your-secret-key-here',
    'Content-Type': 'application/json'
}

# Create a new message
data = {
    "sender": "ChatGPT",
    "message": "Hello world",
    "read": False
}
response = requests.post('http://localhost:8000/messages/', 
                        json=data, 
                        headers=headers)

# Get and mark unread messages
unread = requests.get('http://localhost:8000/messages/unread',
                     headers=headers)
```

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is open source and available under the MIT License.