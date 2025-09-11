from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/status')
def health_status():
    """Health check endpoint with export metadata"""
    # Get export metadata path from config or environment
    metadata_path = app.config.get('EXPORT_METADATA_PATH', 
                                  os.getenv('EXPORT_METADATA_PATH', 
                                           '/tmp/last_export.json'))
    
    response = {"status": "ok"}
    
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                export_data = json.load(f)
            response["export_metadata"] = export_data
    except Exception:
        # If we can't read metadata, still return basic status
        pass
    
    return jsonify(response)
