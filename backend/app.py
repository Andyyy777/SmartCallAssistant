from api.routes.audio_recorder import audio_recorder
from flask_cors import CORS
from api.routes.ai_assistant import ai_assistant
from flask import Flask, render_template

app = Flask(__name__)
CORS(app, origins="http://localhost:3000", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"], supports_credentials=True)
app.register_blueprint(audio_recorder)
app.register_blueprint(ai_assistant)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)

