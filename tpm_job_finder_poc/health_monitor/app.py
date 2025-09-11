from flask import Flask, jsonify
import os
import json

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/status')
def status():
    metadata_path = app.config.get('EXPORT_METADATA_PATH', None)
    export_metadata = {}
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                export_metadata = json.load(f)
        except Exception:
            export_metadata = {}
    return jsonify({'status': 'ok', 'export_metadata': export_metadata})
