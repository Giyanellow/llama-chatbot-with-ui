from calendar import c
from flask import Flask, Response, jsonify, make_response, request, stream_with_context, session, g
from flask_cors import CORS
from utils.chat import ChatBot
from dotenv import load_dotenv
import json
import uuid
import logging
import os

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS_ORIGINS= os.getenv("CORS_ORIGINS")

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

@app.before_request
def execute_before_request():
    global session_id
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    g.session_id = session['session_id']
    
@app.route('/api/get_message_history', methods=['GET', 'OPTIONS'])
def get_message_history():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'session_id' not in session:
        return jsonify({"error": "Session ID not found"}), 400

    try:
        logger.info(f"Fetching message history for session_id: {g.session_id}")
        messages = chatbot.get_message_history(g.session_id)
        if not messages:
            return _corsify_actual_response(make_response(jsonify({"messages": [], "info": "No messages found"}))), 200
        
        return _corsify_actual_response(make_response(jsonify({"messages": messages}))), 200
    except ValueError as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'session_id' not in session:
        return jsonify({"error": "Session ID not found"}), 400
    else:
        session_id = session['session_id']

    data = request.get_json()
    prompt = data.get('message')
    
    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400

    try:
        logger.info(f"Current Session: {session}")
        response = chatbot.run_with_history(prompt, session_id)

        return _corsify_actual_response(make_response(jsonify({"message": response})))
    except ValueError as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream_message', methods=['POST', 'OPTIONS'])
def stream_message():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400

    # This code block will generate a JSON response for each chunk of the response
    def generate_json(prompt):
        with app.app_context():
            full_content = ""
            for chunk in chatbot.stream_invoke(prompt):
                full_content += chunk
                json_data = {
                    "content": chunk,
                    "done": False
                }
                json_str = json.dumps(json_data)
                json_bytes = json_str.encode('utf-8')
                yield json_bytes
                yield b'\n'

            # flag to indicate that the response is complete
            json_data = {
                "full_content": full_content,
                "done": True
            }
            json_str = json.dumps(json_data)
            json_bytes = json_str.encode('utf-8')
            yield json_bytes

    return Response(stream_with_context(generate_json(prompt)), mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)