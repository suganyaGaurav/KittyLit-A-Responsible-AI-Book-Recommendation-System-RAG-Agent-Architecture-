"""
agents/routes.py
----------------
Flask blueprint for Agent-related API endpoints.

Author: **Suganya P**
Date: 2025-08-12
"""

from flask import Blueprint, request, jsonify  # Import Flask components for routing and JSON handling
from agents.orchestrator import AgentOrchestrator  # Import the main Agent orchestrator class

# Create a Blueprint named 'agent' with URL prefix '/agent'
agent_blueprint = Blueprint('agent', __name__, url_prefix='/agent')

# Instantiate the AgentOrchestrator once to reuse for all incoming requests
agent_orchestrator = AgentOrchestrator()

import logging
logging.basicConfig(level=logging.DEBUG)

@agent_blueprint.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    logging.debug(f"Request data: {data}")
    results = orchestrator.get_recommendations(data)
    logging.debug(f"Orchestrator results: {results}")
    return jsonify(results)


@agent_blueprint.route('/recommend', methods=['POST'])
def recommend_books():
    """
    POST endpoint to get book recommendations via AgentOrchestrator.

    Expects JSON payload with query parameters such as title, genre, language, year, etc.
    Returns JSON response containing a list of recommended books and chatbot reply.
    Includes error handling and validation.
    """
    try:
        # Parse JSON payload from the POST request body
        data = request.get_json()

        # Validate the input data: must be a non-empty dictionary
        if not data or not isinstance(data, dict):
            # Return 400 Bad Request if JSON is missing or malformed
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        # Call the orchestrator's main method to process the input query
        result = agent_orchestrator.handle_query(data)

        # Prepare the JSON response with recommended books and chatbot reply
        response = {
            "books": result.get("books", []),                 # List of recommended book dictionaries
            "chatbot_reply": result.get("chatbot_reply", "")  # Chatbot's textual response or empty string
        }

        # Return successful JSON response with 200 OK
        return jsonify(response)

    except Exception as e:
        # Log the error for debugging purposes (prints to console)
        print(f"[agent/routes] Error processing recommendation: {e}")

        # Return generic 500 Internal Server Error with JSON error message
        return jsonify({"error": "Internal server error"}), 500
