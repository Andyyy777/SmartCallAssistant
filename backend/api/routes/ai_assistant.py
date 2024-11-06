from api.ai_assistant import AIAssistant
from flask import Blueprint, jsonify, request
from flask_cors import CORS

ai_assistant = Blueprint('ai', __name__, url_prefix='/ai')
CORS(ai_assistant, origins=["http://localhost:3000"])
ai = AIAssistant()

@ai_assistant.route('/process', methods=['POST', 'OPTIONS'])
def process():
    try:
        if request.method == 'OPTIONS':
            return '', 200 

        req = request.get_json()
        path = req.get('path')  
    except Exception as e:
        print("e:", e)
    
    if not path:
        return jsonify({"status": "Error", "message": "Path is missing"}), 400

    summary = ai.process(path)
    return jsonify({"status": "Ready", "data": summary})


@ai_assistant.route('/test', methods=['POST'])
def test():
    print("test")