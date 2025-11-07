#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=development

export OPENAI_API_KEY=<OPENAI_API_KEY>
# Start the Flask server
# flask run
python app.py
