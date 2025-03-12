from app import app, setup_ngrok
import logging

if __name__ == "__main__":
    # Setup ngrok tunnel
    public_url = setup_ngrok()
    if public_url:
        logging.info(f"API is accessible at: {public_url}")
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
