import json
from api_client import login_for_whatsapp, start_chat, send_chat

def lambda_handler(event, context):
    # Extract method and validate presence of the method key
    method = event.get("method", "")
    if not method:
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
            secret_token = event.get("secret_token")

            if not mobile or not name or not secret_token:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required fields for login: mobile, name, or secret_token.'
                    })
                }

            # Call login_for_whatsapp with the provided parameters
            response_data = method_function(mobile, name, secret_token)

        elif method == "start_chat":
            access_token = event.get("access_token")
            if not access_token:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required field: access_token for start_chat.'
                    })
                }

            # Call start_chat with the provided access token
            response_data = method_function(access_token)

        elif method == "send_chat":
            access_token = event.get("access_token")
            message = event.get("message")
            if not access_token or not message:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Missing required fields: access_token or message for send_chat.'
                    })
                }

            # Call send_chat with the provided access token and message
            response_data = method_function(access_token, message)

        else:
            # If method is not valid, return a 400 error
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f"Unsupported method: {method}."
                })
            }

    except Exception as e:
        # Catch any unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An error occurred while processing the request: {str(e)}"
            })
        }

    # Check the response data from the called function and format it accordingly
    if response_data.get('statusCode') == 200:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'API call successful',
                'data': response_data.get('content') or response_data.get('accessToken')
            })
        }
    else:
        return {
            'statusCode': response_data.get('statusCode', 500),
            'body': json.dumps({
                'success': False,
                'message': response_data.get('message', 'API call failed'),
                'details': response_data.get('details', ''),
                'error': response_data.get('error', '')
            })
        }
