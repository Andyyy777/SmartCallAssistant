#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=development

$env:OPENAI_API_KEY ='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'
# Start the Flask server
flask run
