import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_swagger_ui import get_swaggerui_blueprint
import logging

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
def index():
    return send_file('templates/index.html')

# Function to fetch data from PubChem API
def get_drug_info_pubchem(drug_name):
    """Fetch drug information from the PubChem Compound API."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and len(data['result']) > 0:
                drug_info = data['result'][0]
                return {
                    "name": drug_info.get("name", "No name available"),
                    "cid": drug_info.get("cid", "No CID available")
                }
            else:
                return {"message": "No drug information found in PubChem."}
        else:
            return {"message": "Failed to fetch data from PubChem."}
    except requests.exceptions.RequestException as e:
        return {"message": f"Request error: {str(e)}"}

# Function to fetch data from OpenFDA API
def get_drug_info_openfda(drug_name):
    """Fetch drug information from the OpenFDA Drugs API."""
    url = f"https://api.fda.gov/drug/label.json?search=brand_name:{drug_name}&limit=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                drug_info = data['results'][0]
                return {
                    "name": drug_info.get("brand_name", "No brand name available"),
                    "generic_name": drug_info.get("generic_name", "No generic name available"),
                    "substance_name": drug_info.get("substance_name", "No substance name available"),
                    "approval_date": drug_info.get("approval_date", "No approval date available"),
                    "product_id": drug_info.get("product_id", "No product ID available")
                }
            else:
                return {"message": "No drug information found in OpenFDA."}
        else:
            return {"message": "Failed to fetch data from OpenFDA."}
    except requests.exceptions.RequestException as e:
        return {"message": f"Request error: {str(e)}"}

# API route to get drug information
@app.route('/api/v1/drug', methods=['GET'])
def drug_info():
    """API endpoint to get drug information from multiple sources."""
    drug_name = request.args.get('name', '').strip()
    
    if not drug_name:
        return jsonify({
            "status": "error",
            "message": "Drug name is required"
        }), 400
    
    try:
        # Get drug info from both PubChem and OpenFDA
        pubchem_data = get_drug_info_pubchem(drug_name)
        openfda_data = get_drug_info_openfda(drug_name)
        
        # Combine the results from both APIs
        return jsonify({
            "status": "success",
            "pubchem_data": pubchem_data,
            "openfda_data": openfda_data
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
                    "summary": "Get drug information from multiple sources",
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
                                    "pubchem_data": {"type": "object"},
                                    "openfda_data": {"type": "object"}
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

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
