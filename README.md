# SmartCallAssistant

## Backend server (Flask)
1. `cd backend`
2. (Optional, first run) create and activate a virtualenv: `python3 -m venv .venv && source .venv/bin/activate` (use `.\venv\Scripts\activate` on Windows).
3. Install the dependencies (Flask, Flask-CORS, OpenAI SDK, numpy, scipy, sounddevice, etc.) via your preferred `requirements.txt` or `pip install flask flask-cors openai numpy scipy sounddevice`.
4. Provide the required environment variables (at least `OPENAI_API_KEY`) in your shell or a `.env` file so the AI assistant can reach OpenAI. Currently it is in backend/start.sh
5. Start the API server:
   - `bash start.sh` or `sh start.sh` to reuse the helper script that sets Flask env vars and runs `python app.py`; or
   - `python app.py` (defaults to `http://localhost:5001`).

## Frontend server (React)
1. In a second terminal, `cd frontend`.
2. Install dependencies (first run): `npm install`.
3. Launch the React development server with `npm start` and open `http://localhost:3000`.

Always start the backend first so the frontend can successfully call the Flask routes.
