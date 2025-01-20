import json
from flask import Flask, Response, jsonify, make_response, request, stream_with_context
from utils.chat import ChatBot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
chatbot = ChatBot()

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400

    try:
        response = chatbot.invoke(prompt)
        return _corsify_actual_response(make_response(jsonify({"response": response})))
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