from flask import Flask, render_template, request, jsonify
from sheets_service import SheetsService
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key')

# Initialize sheets service
sheets_service = SheetsService()

@app.route('/')
def index():
    """Main page for mood tracking"""
    return render_template('index.html')

@app.route('/api/mood', methods=['POST'])
def submit_mood():
    """Submit a mood entry"""
    data = request.json
    mood_value = data.get('mood')
    notes = data.get('notes', '')
    timestamp = datetime.now().isoformat()
    
    try:
        # Add entry to Google Sheets
        success = sheets_service.add_entry(timestamp, mood_value, notes)
        if success:
            return jsonify({'status': 'success', 'message': 'Mood logged successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to log mood'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/moods', methods=['GET'])
def get_moods():
    """Get recent mood entries"""
    try:
        entries = sheets_service.get_recent_entries(limit=30)
        return jsonify({'status': 'success', 'data': entries})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
