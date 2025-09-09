"""
Health/Status Endpoint
Exposes liveness and last export metadata for hosting/load balancer health checks.
Lightweight, fast, and suitable for Render/Railway.
"""
from flask import Flask, jsonify
from pathlib import Path
import json

app = Flask(__name__)

DEFAULT_EXPORT_METADATA_PATH = "secure_storage/metadata/last_export.json"

@app.route("/health", methods=["GET"])
def health():
    # Liveness check
    return jsonify({"status": "ok"})

@app.route("/status", methods=["GET"])
def status():
    # Liveness + last export metadata
    metadata = {}
    meta_path_str = app.config.get("EXPORT_METADATA_PATH", DEFAULT_EXPORT_METADATA_PATH)
    meta_path = Path(meta_path_str)
    if meta_path.exists():
        try:
            with meta_path.open() as f:
                metadata = json.load(f)
        except Exception:
            metadata = {"error": "Could not read export metadata"}
    return jsonify({"status": "ok", "export_metadata": metadata})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
