import os
from flask import Flask, render_template, request, jsonify, session
import BACKEND

app = Flask(__name__)
app.secret_key = "medical_chatbot_secret_key" # Required for sessions

@app.route('/')
def index():
    session.clear() # Starts a fresh conversation on page refresh
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_text = request.form.get('message', '').strip()
    
    # Initialize history in session if it doesn't exist
    if 'history' not in session:
        session['history'] = []

    # Handle File Upload Info
    file = request.files.get('file')
    if file and file.filename != '':
        user_text += f"\n[User attached file: {file.filename}]"

    if not user_text:
        return jsonify({"response": "I didn't hear anything."})

    # Add the NEW user message to the existing history
    current_history = session['history']
    current_history.append({"role": "user", "content": user_text})

    try:
        # Send the WHOLE history to BACKEND.py
        bot_response = BACKEND.ask_medical_gemini(current_history)
        
        # Add the bot's answer to the history too
        current_history.append({"role": "assistant", "content": bot_response})
        
        # Save updated history back to session
        session['history'] = current_history
        
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
