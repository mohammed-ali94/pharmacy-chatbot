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
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    try:
        # First get the CID
        search_url = f"{base_url}/compound/name/{drug_name}/cids/JSON"
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                cid = data['IdentifierList']['CID'][0]
                # Now get the compound info
                info_url = f"{base_url}/compound/cid/{cid}/description/JSON"
                info_response = requests.get(info_url)
                if info_response.status_code == 200:
                    info_data = info_response.json()
                    if 'InformationList' in info_data and 'Information' in info_data['InformationList']:
                        info = info_data['InformationList']['Information'][0]
                        return {
                            "name": drug_name.upper(),
                            "cid": cid,
                            "description": info.get('Description', 'No description available'),
                            "title": info.get('Title', 'No title available')
                        }
        return {"message": "No drug information found in PubChem."}
    except Exception as e:
        return {"message": f"Error fetching PubChem data: {str(e)}"}

# Function to fetch data from OpenFDA API
def get_drug_info_openfda(drug_name):
    """Fetch drug information from the OpenFDA Drugs API."""
    api_key = "your-api-key"  # Optional: Add your API key here for higher rate limits
    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}&limit=1"
    try:
        response = requests.get(url)
        logger.debug(f"OpenFDA response: {response.text}")  # Log the response for debugging
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    "brand_name": result.get('openfda', {}).get('brand_name', ['Not available'])[0],
                    "generic_name": result.get('openfda', {}).get('generic_name', ['Not available'])[0],
                    "indications": result.get('indications_and_usage', ['Not available'])[0],
                    "warnings": result.get('warnings', ['Not available'])[0],
                    "dosage": result.get('dosage_and_administration', ['Not available'])[0],
                    "manufacturer": result.get('openfda', {}).get('manufacturer_name', ['Not available'])[0]
                }
        return {"message": "No drug information found in OpenFDA."}
    except Exception as e:
        return {"message": f"Error fetching OpenFDA data: {str(e)}"}

# Function to fetch data from RxNav API
def get_rxnav_info(drug_name):
    """Fetch drug information from RxNav API."""
    try:
        url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={drug_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'drugGroup' in data and 'conceptGroup' in data['drugGroup']:
                drug_info = data['drugGroup']['conceptGroup']
                return {
                    "status": "success",
                    "drug_classes": [group.get('conceptProperties', []) for group in drug_info if 'conceptProperties' in group],
                    "source": "RxNav"
                }
        return {"status": "partial", "message": "Limited RxNav information available"}
    except Exception as e:
        return {"message": f"Error fetching RxNav data: {str(e)}"}

# Function to fetch data from DailyMed API
def get_dailymed_info(drug_name):
    """Fetch drug information from DailyMed API."""
    try:
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                return {
                    "status": "success",
                    "labels": data['data'],
                    "source": "DailyMed"
                }
        return {"status": "partial", "message": "Limited DailyMed information available"}
    except Exception as e:
        return {"message": f"Error fetching DailyMed data: {str(e)}"}

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
        # Get drug info from all sources
        pubchem_data = get_drug_info_pubchem(drug_name)
        openfda_data = get_drug_info_openfda(drug_name)
        rxnav_data = get_rxnav_info(drug_name)
        dailymed_data = get_dailymed_info(drug_name)
        
        # Combine the results from both APIs
        # Check if we have OpenFDA data
        if "message" not in openfda_data:
            return jsonify({
                "status": "success",
                "primary_source": "FDA",
                "openfda_data": openfda_data,
                "additional_sources": {
                    "pubchem_data": pubchem_data,
                    "rxnav_data": rxnav_data,
                    "dailymed_data": dailymed_data
                }
            })
        else:
            return jsonify({
                "status": "partial",
                "message": "Limited FDA data available. The following data might be incomplete or missing:",
                "openfda_data": openfda_data,
                "alternative_sources": {
                    "pubchem_data": pubchem_data,
                    "rxnav_data": rxnav_data,
                    "dailymed_data": dailymed_data
                }
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

