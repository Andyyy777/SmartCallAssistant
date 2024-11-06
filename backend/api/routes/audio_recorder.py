from api.audio_recorder import AudioRecorder
from api.ai_assistant import AIAssistant
from flask import Blueprint, jsonify, request
from flask_cors import CORS

audio_recorder = Blueprint('audio', __name__, url_prefix='/audio')
CORS(audio_recorder, origins=["http://localhost:3000"])
recorder = AudioRecorder()
# ai_assistant = AIAssistant()


@audio_recorder.route('/start', methods=['POST'])
def start():
    recorder.start_recording()
    return jsonify({"status": "Recording started"})

@audio_recorder.route('/pause', methods=['POST'])
def pause():
    recorder.pause_recording()
    return jsonify({"status": "Recording paused"})

@audio_recorder.route('/resume', methods=['POST'])
def resume():
    recorder.resume_recording()
    return jsonify({"status": "Recording resumed"})

@audio_recorder.route('/stop', methods=['POST'])
def stop():
    path = recorder.stop_recording()
    if "Error" in path:
        return jsonify({"status": path}), 400
    return jsonify({"status": "Recording stopped", "path":path})

# @audio_recorder.route('/save', methods=['POST'])
# def save():
#     filename = request.json.get('filename', 'output.mp3')
#     success = recorder.save_recording(DATA_DIR+filename)
#     if success:
#         return jsonify({"status": "Recording saved", "file": filename})
#     else:
#         return jsonify({"status": "No recording to save"}), 400