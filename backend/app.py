import os
import uuid
import logging
from flask import Flask, Response, jsonify, make_response, request, session, g
from flask_cors import CORS
from flask_session import Session
from utils.chat import ChatBot
from dotenv import load_dotenv

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS")

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
Session(app)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": CORS_ORIGINS}})

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", CORS_ORIGINS)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", CORS_ORIGINS)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# initialize chatbot class once
chatbot = ChatBot()

@app.route('/api/get_session_id', methods=['GET', 'OPTIONS'])
def get_session_id():
    """Get a session ID for the user

    Returns:
        Response: JSON response containing the session ID
    """
    
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True  # Make the session permanent
    
    logger.info(f"Sending session_id: {session['session_id']}")

    return _corsify_actual_response(make_response(jsonify({"session_id": session['session_id']})))

@app.route('/api/get_message_history', methods=['POST', 'OPTIONS'])
def get_message_history():
    """Get the message history for the user

    Returns:
        Response: JSON response containing the message history
    """
    
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"error": "Missing 'session_id' parameter"}), 400
    
    try:
        logger.info(f"Fetching message history for session_id: {session_id}")
        messages = chatbot.get_message_history(session_id)
        if not messages:
            return _corsify_actual_response(make_response(jsonify({"messages": [], "info": "No messages found"}))), 200
        
        return _corsify_actual_response(make_response(jsonify({"messages": messages}))), 200
    except ValueError as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": f"Invalid session_id: {session_id}"}), 500
    
    
@app.route('/api/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    """Send a message to the chatbot
    
    Returns:
        Response: JSON response containing the chatbot's response
        
    """
    
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    prompt = data.get('message')
    session_id = data.get('session_id')
    
    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400

    if not session_id:
        return jsonify({"error": "Missing 'session_id' parameter"}), 400

    if 'session_id' not in session or session['session_id'] != session_id:
        return jsonify({"error": f"Invalid session_id: {session_id}"}), 400

    try:
        logger.info(f"Current Session: {session}")
        response = chatbot.run_with_history(prompt, session_id)
        response_message = response if isinstance(response, str) else str(response)

        return _corsify_actual_response(make_response(jsonify({"message": response_message})))
    except ValueError as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": f"An error has occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)