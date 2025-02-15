import os
import uuid
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from dotenv import load_dotenv
from session import SessionData, verifier, backend, cookie
from utils.chat import ChatBot, MessageHistoryDB

# Load environment variables
load_dotenv(".env")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting application...")

app = FastAPI()

# Load configuration from environment or a config file
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
logger.info(f"CORS origins: {cors_origins}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot_instance = ChatBot()

@app.get("/api/create_session")
async def create_session(response: JSONResponse):
    logger.info("Creating new session...")
    session_id = uuid.uuid4()
    session_data = SessionData(session_id=str(session_id))
    
    await backend.create(session_id, session_data)
    cookie.attach_to_response(response, session_id)
    logger.info(f"Sending session_id: {session_id}")
    
    return {"session_id": str(session_id)}

from fastapi.responses import JSONResponse

@app.post("/api/handle_old_session", dependencies=[Depends(cookie)])
async def handle_old_session(request: Request, session_data: SessionData = Depends(verifier)):
    data = await request.json()
    logger.info(f"Received request: {data}")
    session_id = data.get('session_id')
    
    if not session_id:
        logger.error("Missing 'session_id' parameter")
        raise HTTPException(status_code=400, detail="Missing 'session_id' parameter")
    
    # Optionally retrieve existing session or create new
    session_data = SessionData(session_id=session_id)
    await backend.create(session_id, session_data)
    
    # Create a JSONResponse and attach the cookie to it
    response = JSONResponse({"messages": []})
    cookie.attach_to_response(response, session_id)
    
    try:
        logger.info(f"Fetching message history for session_id: {session_id}")
        db = MessageHistoryDB(session_id)
        messages = db.retrieve_messages()
        if not messages:
            logger.info("No messages found")
            response = JSONResponse({"messages": [], "info": "No messages found"})
        else:
            response = JSONResponse({"messages": messages})
        
        cookie.attach_to_response(response, session_id)
        return response
    
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid session_id: {session_id}")


@app.post("/api/send_message", dependencies=[Depends(cookie)])
async def send_message(request: Request, session_data: SessionData = Depends(verifier)):
    data = await request.json()
    prompt = data.get('message')
    
    # get session_id from cookie
    session_id = session_data.session_id
    
    if not prompt or not session_id:
        logger.error("Missing required parameters")
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    if session_data.session_id != session_id:
        logger.error(f"Invalid session_id: {session_id}")
        raise HTTPException(status_code=400, detail=f"Invalid session_id: {session_id}")
    
    try:
        logger.info(f"Current Session: {session_data.session_id}")
        response = chatbot_instance.run(prompt, session_id)
        response_message = response if isinstance(response, str) else str(response)
        return {"message": response_message}
    
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error has occurred: {e}")

if __name__ == "__main__":
    logger.info("Running application...")
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, log_level="info")