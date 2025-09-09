from src.error_service.handler import handle_error
from flask import jsonify

# Flask error handling middleware example
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        error_info = handle_error(e, context={'endpoint': str(getattr(e, 'endpoint', None))})
        return jsonify({'error': error_info['message'], 'type': error_info['type']}), 500
