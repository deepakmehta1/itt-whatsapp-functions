import requests
import json
import os

# Get the base URL for all APIs from the environment variable
SMART_CHAT_URL = os.getenv('SMART_CHAT_URL', 'http://localhost:8080')

def login_for_whatsapp(mobile, name, secret_token):
    # Define the URL of the API endpoint (base URL + specific endpoint)
    url = SMART_CHAT_URL + '/v2/auth/login-for-whatsapp'
    
    # Define the request body
    payload = {
        "mobile": mobile,
        "name": name,
        "secret_token": secret_token
    }

    print(f"Calling login_for_whatsapp with mobile: {mobile}, name: {name}")

    try:
        # Make the POST request to the API
        print(f"Making POST request to {url} with payload: {json.dumps(payload)}")
        response = requests.post(url, json=payload)
        
        # Check if the response status code is 200
        if response.status_code == 200:
            print("Login successful. Access token received.")
            return {
                'statusCode': 200,
                'accessToken': response.json().get("accessToken")
            }
        else:
            print(f"Login failed with status code {response.status_code}. Response: {response.text}")
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }


def start_chat(access_token):
    # Construct the URL for the start chat API (base URL + specific endpoint)
    url = SMART_CHAT_URL + '/v2/chat/start'
    
    # Set the headers with the Authorization token
    headers = {
        "Authorization": access_token
    }

    print(f"Calling start_chat with access_token: {access_token}")

    try:
        # Make the POST request to the API
        print(f"Making POST request to {url} with headers: {json.dumps(headers)}")
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            # Parse the response JSON data and extract the content
            response_data = response.json()
            content = json.loads(response_data.get('response', '{}')).get('content', '')
            print(f"Start chat successful. Content: {content}")
            return {
                'statusCode': 200,
                'content': content
            }
        else:
            print(f"Start chat failed with status code {response.status_code}. Response: {response.text}")
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }

def send_chat(access_token, message):
    # Construct the URL for the send chat API (base URL + specific endpoint)
    url = SMART_CHAT_URL + '/v2/chat/message'
    
    # Set the headers with the Authorization token
    headers = {
        "Authorization": access_token
    }
    
    # Define the request body
    payload = {
        "message": message
    }

    print(f"Calling send_chat with access_token: {access_token}, message: {message}")

    try:
        # Make the POST request to the API
        print(f"Making POST request to {url} with payload: {json.dumps(payload)}")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            content = json.loads(response_data.get('response', '{}')).get('content', '')
            print(f"Send chat successful. Content: {content}")
            return {
                'statusCode': 200,
                'content': content
            }
        else:
            print(f"Send chat failed with status code {response.status_code}. Response: {response.text}")
            return {
                'statusCode': response.status_code,
                'message': 'API call failed',
                'details': response.text
            }
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return {
            'statusCode': 500,
            'message': 'An error occurred during the API request',
            'error': str(e)
        }
