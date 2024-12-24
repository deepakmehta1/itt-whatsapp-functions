import requests
import json
import os

# Get the base URL for all APIs from the environment variable
SMART_CHAT_URL = os.getenv('SMART_CHAT_URL', 'http://localhost:8080')

def login_for_whatsapp(mobile, name, secret_token):
    # Define the URL of the API endpoint (base URL + specific endpoint)
    url = os.path.join(SMART_CHAT_URL, '/v2/auth/login-for-whatsapp')  # Full URL for login API
    
    # Define the request body
    payload = {
        "mobile": mobile,
        "name": name,
        "secret_token": secret_token
    }

    try:
        # Make the POST request to the API
        response = requests.post(url, json=payload)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            # Parse the response JSON data
            return response.json()
        else:
            # Handle the case where the API returns a non-200 status code
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API request
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }


def start_chat(access_token):
    # Construct the URL for the start chat API (base URL + specific endpoint)
    url = os.path.join(SMART_CHAT_URL, '/v2/chat/start')  # Full URL for start chat
    
    # Set the headers with the Authorization token
    headers = {
        "Authorization": access_token
    }
    
    try:
        # Make the POST request to the API
        response = requests.post(url, headers=headers)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            # Parse the response JSON data and extract the content
            response_data = response.json()
            content = json.loads(response_data.get('response', '{}')).get('content', '')
            return {
                'statusCode': response.status_code,
                'content': content
            }
        else:
            # Handle the case where the API returns a non-200 status code
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API request
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }

def send_chat(access_token, message):
    # Construct the URL for the send chat API (base URL + specific endpoint)
    url = os.path.join(SMART_CHAT_URL, '/v2/chat/message')  # Full URL for send chat
    
    # Set the headers with the Authorization token
    headers = {
        "Authorization": access_token
    }
    
    # Define the request body
    payload = {
        "message": message
    }
    
    try:
        # Make the POST request to the API
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            # Parse the response JSON data and extract the content
            response_data = response.json()
            content = json.loads(response_data.get('response', '{}')).get('content', '')
            return {
                'statusCode': response.status_code,
                'content': content
            }
        else:
            # Handle the case where the API returns a non-200 status code
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API request
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }
