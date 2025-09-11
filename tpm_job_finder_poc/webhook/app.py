from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/deploy', methods=['POST'])
def deploy_webhook():
	data = request.get_json(force=True)
	version = data.get('version')
	action = data.get('action')
	source = data.get('source')
	if not version or not action:
		return jsonify({"error": "Missing version or action"}), 400
	if action == 'roll-forward':
		result = f"Rolled forward to {version}"
	elif action == 'rollback':
		result = f"Rolled back to {version}"
	else:
		return jsonify({"error": "Unknown action"}), 400
	return jsonify({"status": "success", "result": result})
