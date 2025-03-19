from flask import Flask, request, jsonify
from flask_cors import CORS
from models.ml_model import MLModel
from models.ai_model import AIModel
from utils.log_parser import parse_logs
import sqlite3
import os
import signal
import sys

app = Flask(__name__)
CORS(app)
ml_model = MLModel()
ai_model = AIModel()

if not os.path.exists('data'):
    os.makedirs('data')
with sqlite3.connect('data/training.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS training (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, message_pattern TEXT, tags TEXT, status TEXT)')

@app.route('/upload', methods=['POST'])
def upload_logs():
    try:
        file = request.files['file']
        print(f"Received file: {file.filename}")
        logs = parse_logs(file)
        print(f"Parsed logs: {logs}")
        processed_logs = [ml_model.process_log(log) for log in logs]
        print(f"Processed logs: {processed_logs}")
        try:
            summary = ai_model.summarize(processed_logs)
            print(f"Summary: {summary}")
            return jsonify({'logs': processed_logs, 'summary': summary['summary']})
        except Exception as e:
            print(f"Summarization error: {str(e)}")
            return jsonify({'logs': processed_logs, 'summary': f'Error summarizing: {str(e)}'})
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'logs': [], 'summary': f'Error: {str(e)}'}), 500
    
    
@app.route('/analyze', methods=['POST'])
def analyze_log():
    try:
        data = request.json
        logs = data.get('logs', [data.get('log')])
        summary = ai_model.summarize(logs)
        return jsonify({'summary': summary['summary']})
    except Exception as e:
        return jsonify({'summary': f'Error: {str(e)}'}), 500

@app.route('/train', methods=['POST'])
def train_model():
    try:
        data = request.json
        log, tags, status = data['log'], data['tags'], data['status']
        updated_log = ml_model.train(log, tags, status)
        with sqlite3.connect('data/training.db') as conn:
            conn.execute('INSERT INTO training (level, message_pattern, tags, status) VALUES (?, ?, ?, ?)',
                         (log['level'], log['message'], ','.join(tags), status))
        return jsonify({'updatedLog': updated_log})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def shutdown_server(signalnum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown_server)
    signal.signal(signal.SIGTERM, shutdown_server)
    app.run(host='0.0.0.0', port=5001, debug=True)