import os
from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint
import logging
from drug_info import get_drug_info
from pyngrok import ngrok

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Swagger configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Drug Information API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    """Render the home page with API testing interface"""
    return render_template('index.html')

@app.route('/api/v1/drug', methods=['GET'])
def drug_info():
    """API endpoint to get drug information"""
    drug_name = request.args.get('name', '').strip()
    
    if not drug_name:
        return jsonify({
            "status": "error",
            "message": "Drug name is required"
        }), 400
    
    try:
        drug_data = get_drug_info(drug_name)
        return jsonify({
            "status": "success",
            "data": drug_data
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve drug information"
        }), 500

# Create Swagger specification
@app.route('/static/swagger.json')
def swagger_spec():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Drug Information API",
            "version": "1.0"
        },
        "paths": {
            "/api/v1/drug": {
                "get": {
                    "summary": "Get drug information",
                    "parameters": [
                        {
                            "name": "name",
                            "in": "query",
                            "required": True,
                            "type": "string",
                            "description": "Name of the drug"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "data": {"type": "object"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request"
                        },
                        "500": {
                            "description": "Server error"
                        }
                    }
                }
            }
        }
    })

def setup_ngrok():
    """Setup ngrok tunnel"""
    try:
        public_url = ngrok.connect(5000).public_url
        logger.info(f"Ngrok tunnel established at: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"Failed to establish ngrok tunnel: {str(e)}")
        return None
