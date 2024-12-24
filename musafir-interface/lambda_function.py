import boto3
import json
from api_client import login_for_whatsapp, start_chat, send_chat

# Initialize the SSM client
ssm_client = boto3.client('ssm')

def get_whats_app_secret_token():
    """
    Fetches the WhatsApp secret token from AWS SSM Parameter Store.
    
    Returns:
    - The WhatsApp secret token if found, or a default token if not found or an error occurs.
    """
    try:
        # Fetch the WhatsApp secret token from SSM Parameter Store
        response = ssm_client.get_parameter(
            Name='WASecretToken',  # Parameter name in SSM
            WithDecryption=True  # Decrypt the value if it's encrypted
        )
        secret_token = response['Parameter']['Value']
        print("Successfully fetched WhatsApp secret token from SSM.")
        return secret_token
    except Exception as e:
        # If an error occurs, log the error and return a default token
        print(f"Error fetching WhatsApp secret token from SSM: {str(e)}")
        return 'No-Login-Required-For-Whatsapp-Chats'  # Default token


def lambda_handler(event, context):
    # Fetch the WhatsApp secret token dynamically from SSM Parameter Store
    whats_app_secret_token = get_whats_app_secret_token()
    
    # Print incoming event for debugging purposes
    print(f"Received event: {json.dumps(event)}")
    
    # Extract method and validate presence of the method key
    method = event.get("method", "")
    if not method:
        print("Error: Missing 'method' field.")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Missing required field: method.'
            })
        }

    # Define a dictionary that maps method names to functions
    method_map = {
        "login_for_whatsapp": login_for_whatsapp,
        "start_chat": start_chat,
        "send_chat": send_chat
    }

    # Check if the method is valid
    method_function = method_map.get(method)
    if not method_function:
        print(f"Error: Invalid method '{method}'. Valid methods are: {', '.join(method_map.keys())}.")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"Invalid method: {method}. Valid methods are: {', '.join(method_map.keys())}."
            })
        }

    # Extract the required parameters for the selected method
    try:
        if method == "login_for_whatsapp":
            mobile = event.get("mobile")
            name = event.get("name")

            print(f"Calling login_for_whatsapp with mobile: {mobile}, name: {name}")

            if not mobile or not name:
                print("Error: Missing required fields for login: mobile, name.")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required fields for login: mobile, name.'
                    })
                }

            # Call login_for_whatsapp with the provided parameters
            response_data = method_function(mobile, name, whats_app_secret_token)
            print("Response from login_for_whatsapp:", response_data)

        elif method == "start_chat":
            access_token = event.get("access_token")
            if not access_token:
                print("Error: Missing required field: access_token for start_chat.")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required field: access_token for start_chat.'
                    })
                }

            # Call start_chat with the provided access token
            print(f"Calling start_chat with access_token: {access_token}")
            response_data = method_function(access_token)
            print("Response from start_chat:", response_data)

        elif method == "send_chat":
            access_token = event.get("access_token")
            message = event.get("message")
            if not access_token or not message:
                print("Error: Missing required fields: access_token or message for send_chat.")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required fields: access_token or message for send_chat.'
                    })
                }

            # Call send_chat with the provided access token and message
            print(f"Calling send_chat with access_token: {access_token}, message: {message}")
            response_data = method_function(access_token, message)
            print("Response from send_chat:", response_data)

        else:
            print(f"Error: Unsupported method: {method}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f"Unsupported method: {method}."
                })
            }

    except Exception as e:
        # Catch any unexpected errors and log them
        print(f"Error: An unexpected error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An error occurred while processing the request: {str(e)}"
            })
        }

    # Check the response data from the called function and format it accordingly
    if response_data.get('statusCode') == 200:
        print("API call successful. Returning success response.")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'API call successful',
                'data': response_data
            })
        }
    else:
        print(f"API call failed with statusCode: {response_data.get('statusCode')}.")
        return {
            'statusCode': response_data.get('statusCode', 500),
            'body': json.dumps({
                'success': False,
                'message': response_data.get('message', 'API call failed'),
                'details': response_data.get('details', ''),
                'error': response_data.get('error', '')
            })
        }
