"""
Assignment 22: Understand Language (NLU) with LUIS
====================================================
Create a language understanding model to extract intent and entities
from user requests to set a timer.

This Azure Functions app receives text input and returns parsed timer
duration using Microsoft LUIS (Language Understanding Intelligent Service).

Author: [Your Name]
Date: 2024
"""

import azure.functions as func
import json
import os
import logging
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials


# ============================================================================
# CONFIGURATION
# ============================================================================

# Load LUIS credentials from local.settings.json
LUIS_KEY = os.environ.get('LUIS_KEY')
LUIS_ENDPOINT_URL = os.environ.get('LUIS_ENDPOINT_URL')
LUIS_APP_ID = os.environ.get('LUIS_APP_ID')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_timer_duration(prediction_response):
    """
    Extract timer duration in seconds from LUIS prediction response.
    
    Args:
        prediction_response: LUIS prediction result
        
    Returns:
        int: Total seconds for timer, or None if intent not recognized
    """
    
    # Check if top intent is "set timer"
    if prediction_response.prediction.top_intent != 'set timer':
        logging.warning(f"Unrecognized intent: {prediction_response.prediction.top_intent}")
        return None
    
    # Extract entities
    entities = prediction_response.prediction.entities
    
    # Get number and time_unit arrays
    numbers = entities.get('number', [])
    time_units = entities.get('time unit', [])
    
    if not numbers or not time_units:
        logging.warning("Missing number or time_unit entities")
        return None
    
    # Calculate total seconds
    total_seconds = 0
    
    # Match each number with its time unit (order matters)
    for i in range(len(numbers)):
        number = numbers[i]
        
        # Extract time unit (may be nested in array)
        if i < len(time_units):
            time_unit_data = time_units[i]
            # Handle nested array format from LUIS
            if isinstance(time_unit_data, list):
                time_unit = time_unit_data[0] if time_unit_data else 'minute'
            else:
                time_unit = time_unit_data
        else:
            time_unit = 'minute'  # default
        
        # Convert to seconds
        if time_unit.lower() == 'minute':
            total_seconds += number * 60
        elif time_unit.lower() == 'second':
            total_seconds += number
    
    return total_seconds


# ============================================================================
# MAIN AZURE FUNCTION
# ============================================================================

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function that understands timer requests using LUIS.
    
    Expected input:
        POST body: {"text": "set a timer for 5 minutes and 30 seconds"}
    
    Expected output:
        {"seconds": 330}
    
    Args:
        req: HTTP request containing user text
        
    Returns:
        HTTP response with timer duration or error
    """
    
    logging.info("text-to-timer function triggered")
    
    # Validate LUIS credentials
    if not LUIS_KEY or not LUIS_ENDPOINT_URL or not LUIS_APP_ID:
        logging.error("Missing LUIS credentials in environment")
        return func.HttpResponse(
            json.dumps({"error": "Missing LUIS configuration"}),
            status_code=500
        )
    
    try:
        # Get JSON body from request
        req_body = req.get_json()
        text = req_body.get('text', '')
        
        if not text:
            logging.error("No text provided in request")
            return func.HttpResponse(
                json.dumps({"error": "Missing 'text' field"}),
                status_code=400
            )
        
        logging.info(f"Processing: {text}")
        
        # Create LUIS client
        credentials = CognitiveServicesCredentials(LUIS_KEY)
        client = LUISRuntimeClient(
            endpoint=LUIS_ENDPOINT_URL,
            credentials=credentials
        )
        
        # Create prediction request
        prediction_request = {'query': text}
        
        # Get prediction from LUIS (using Staging slot)
        prediction_response = client.prediction.get_slot_prediction(
            app_id=LUIS_APP_ID,
            slot_name='Staging',
            prediction_request=prediction_request
        )
        
        # Extract timer duration
        total_seconds = extract_timer_duration(prediction_response)
        
        if total_seconds is None:
            logging.warning(f"Could not extract timer from: {text}")
            return func.HttpResponse(
                status_code=404  # Intent not recognized
            )
        
        # Log success
        logging.info(f"Timer set for {total_seconds} seconds")
        
        # Return success with timer duration
        return func.HttpResponse(
            json.dumps({
                "seconds": total_seconds,
                "intent": prediction_response.prediction.top_intent,
                "confidence": max(
                    [score for score in prediction_response.prediction.intents.values()],
                    key=lambda x: x.score
                ).score
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except KeyError as e:
        logging.error(f"Missing key in JSON: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Invalid JSON format: {str(e)}"}),
            status_code=400
        )
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500
        )
