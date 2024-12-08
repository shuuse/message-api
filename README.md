# Message API Service

A simple REST API service for storing and managing messages. This service allows you to create, retrieve, and manage messages with a simple API key authentication system. Perfect for small applications needing to store up to 1000 messages.

## Features

- Create and store messages with sender information
- Each message has a unique UUID
- View unread messages without changing their status
- Mark specific messages as read using their UUID
- Simple API key authentication using environment variables
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

4. Create a `.env` file in the root directory:
```bash
echo "API_KEY=your-secret-key-here" > .env
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
    "message": "Hello world"
}
```
Response includes an automatically generated UUID for the message.

### Get All Messages
```http
GET /messages/
Header: X-API-Key: your-secret-key-here
```

### Get Unread Messages (without marking them as read)
```http
GET /messages/unread
Header: X-API-Key: your-secret-key-here
```

### Mark Specific Message as Read
```http
PUT /messages/{uuid}/read
Header: X-API-Key: your-secret-key-here
```
Replace `{uuid}` with the actual message UUID.

### Cleanup Old Messages
```http
DELETE /messages/cleanup
Header: X-API-Key: your-secret-key-here
```

## Testing

Here's a complete test sequence using curl:

```bash
# Create a new message
curl -X POST http://localhost:8000/messages/ \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"sender": "Test", "message": "Hello World"}'

# Get the UUID from the response, then use it to mark as read
curl -X PUT http://localhost:8000/messages/[UUID]/read \
  -H "X-API-Key: your-secret-key-here"

# View unread messages
curl -X GET http://localhost:8000/messages/unread \
  -H "X-API-Key: your-secret-key-here"
```

Python example:
```python
import requests

headers = {
    'X-API-Key': 'your-secret-key-here',
    'Content-Type': 'application/json'
}

# Create a new message
data = {
    "sender": "ChatGPT",
    "message": "Hello world"
}
response = requests.post('http://localhost:8000/messages/', 
                        json=data, 
                        headers=headers)
message_id = response.json()['id']

# Get unread messages
unread = requests.get('http://localhost:8000/messages/unread',
                     headers=headers)

# Mark specific message as read
requests.put(f'http://localhost:8000/messages/{message_id}/read',
            headers=headers)
```

## Deployment

### Initial Deployment to Render

1. Create a free account on Render.com
2. Create a new Web Service and connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `API_KEY` with your chosen secret key
4. Deploy the service

### Updating the Deployment

The service will automatically redeploy when you push changes to GitHub. To update:

1. Make your changes locally
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Your commit message"
git push
```
3. Render will automatically detect the changes and redeploy

Note: The free tier of Render will spin down your service after 15 minutes of inactivity. The first request after inactivity might take a few seconds to respond while the service spins up again.


## ChatGPT Actions Integration

This API includes a special endpoint for ChatGPT Actions integration. To add this API as a ChatGPT action:

1. Go to ChatGPT's Actions configuration
2. Choose "Import from URL"
3. Enter: `https://message-api-0rws.onrender.com/.well-known/openapi.yaml`
4. Configure the authentication:
   - Authentication Type: API Key
   - Auth Type: Custom
   - Header Name: X-API-Key
   - API Key: Your API key from the .env file or Render environment variables

Once configured, you can test the action by asking ChatGPT to send a test message. The action allows ChatGPT to create new messages through your API with proper authentication.

Example prompt: "Send a test message using the Message API"

## Message Constraints

- Maximum message length: 500 characters
- If a message exceeds this limit, the API will return a 400 error with a descriptive message
- This limit applies to all messages, including those sent through ChatGPT actions

## Error Responses

The API may return the following error responses:

- 400 Bad Request: Message exceeds 500 characters or other validation errors
- 403 Forbidden: Invalid or missing API key
- 404 Not Found: Message ID not found when marking as read

## API Documentation

When running the service, visit `/docs` to see the automatic OpenAPI documentation and test the endpoints interactively.

## Security Notes

- Keep your API key secure and never commit it to the repository
- The `.env` file is included in `.gitignore` to prevent accidental exposure
- Use a strong, random API key in production
- Always use HTTPS when calling the API in production

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is open source and available under the MIT License.