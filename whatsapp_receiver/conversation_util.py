import boto3
import json
from datetime import datetime

# Initialize the AWS clients for Lambda and DynamoDB
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

def invoke_lambda(function_name, payload):
    """
    Invokes a Lambda function with a specified payload and returns the response.
    This function is used to invoke different Lambda methods like `login_for_whatsapp`, `start_chat`, and `send_chat`.

    Parameters:
    - function_name: The name of the Lambda function to invoke
    - payload: The data to send to the Lambda function

    Returns:
    - The response payload returned by the invoked Lambda function, or an error message.
    """
    try:
        print(f"Invoking Lambda function: {function_name} with payload: {json.dumps(payload)}")
        
        # Invoke the Lambda function synchronously (wait for the response)
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous invocation
            Payload=json.dumps(payload)  # Convert the payload to JSON
        )
        
        # Read and decode the response payload
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        print('Lambda response payload:', response_payload)  # Log the response for debugging
        return response_payload

    except Exception as e:
        # If an error occurs during Lambda invocation, return a failure message
        print(f"Error invoking Lambda function '{function_name}': {str(e)}")
        return {
            'success': False,
            'message': f"Error invoking lambda: {str(e)}"
        }


def get_conversation(mobile, date):
    """
    Checks if a conversation exists for the given mobile number and date in the DynamoDB table.
    Returns the conversation details if it exists, otherwise None.

    Parameters:
    - mobile: The mobile number associated with the conversation
    - date: The date of the conversation

    Returns:
    - The conversation item if found, otherwise None
    """
    print(f"Checking for conversation with mobile: {mobile} on date: {date}")
    
    try:
        # Access the 'conversation' table in DynamoDB
        table = dynamodb.Table('conversation')
        response = table.get_item(
            Key={'mobile': mobile, 'cr_date': date}  # Partition and sort key
        )
        
        if 'Item' in response:
            print(f"Conversation found: {response['Item']}")
            return response['Item']  # Return the conversation item if found
        else:
            print("No conversation found for this mobile and date.")
            return None
        
    except Exception as e:
        # Print any error messages from DynamoDB
        print(f"Error fetching conversation: {str(e)}")
        return None


def create_conversation(mobile, name, access_token):
    """
    Creates a new conversation entry in the DynamoDB table with the given details.

    Parameters:
    - mobile: The mobile number to associate with the conversation
    - name: The name of the user
    - access_token: The access token generated during login for WhatsApp

    Returns:
    - True if the conversation is successfully created, otherwise False.
    """
    # Generate the current date in YYYY-MM-DD format for the 'cr_date' field
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Prepare the item to be inserted into the DynamoDB table
    item = {
        'mobile': mobile,
        'cr_date': current_date,  # Date as sort key
        'name': name,
        'access_token': access_token
    }

    print(f"Creating new conversation entry with mobile: {mobile}, name: {name}, access_token: {access_token}")

    try:
        # Access the 'conversation' table in DynamoDB
        table = dynamodb.Table('conversation')
        # Insert the item into the table
        table.put_item(Item=item)
        print("Conversation entry created successfully.")
        return True
    except Exception as e:
        # Log any error that occurs during the insertion
        print(f"Error creating conversation entry: {str(e)}")
        return False


def find_conversation_and_communicate(mobile, name, input_text):
    """
    Main function to find or create a conversation and communicate with the user.
    If a conversation exists, it uses the existing `access_token` to send a message. 
    If not, it logs the user in, creates a conversation, and starts a new chat.

    Parameters:
    - mobile: The mobile number of the user
    - name: The name of the user
    - input_text: The message to send in case the conversation already exists

    Returns:
    - The response from the `send_chat` or `start_chat` Lambda function
    """
    # Generate the current date dynamically
    current_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Checking conversation for mobile: {mobile}, date: {current_date}")

    # Step 1: Check if the conversation exists in the DynamoDB table
    conversation = get_conversation(mobile, current_date)

    if conversation:
        # If a conversation exists, retrieve the access_token
        access_token = conversation.get('access_token')
        
        # Step 2: Invoke the `send_chat` method in the "musafir-interface" Lambda
        payload = {
            'method': 'send_chat',  # Specify the method to invoke
            'access_token': access_token,
            'message': input_text  # The message to send
        }
        print(f"Sending chat with access_token: {access_token}, message: {input_text}")
        # Call the Lambda function and return the response
        response = invoke_lambda('musafir-interface', payload)
        response_data = json.loads(response.get('body'))
        return {
                    'success': True,
                    'content': response_data.get('data', {}).get('content')
                }
    else:
        # If no conversation exists, log in and start a new chat
        print(f"No conversation found, proceeding with login and new chat.")
        
        # Step 3: Invoke the `login_for_whatsapp` method in the "musafir-interface" Lambda
        login_payload = {
            'method': 'login_for_whatsapp',  # Specify the method to invoke
            'mobile': mobile,
            'name': name
        }
        # Call the Lambda function and get the login response
        print(f"Logging in with mobile: {mobile}, name: {name}")
        login_response = invoke_lambda('musafir-interface', login_payload)
        print('login_response:', login_response)  # Log the login response for debugging

        if login_response.get('success', True):  # Check if login was successful
            response_data = json.loads(login_response.get('body'))
            access_token = response_data.get('data').get('accessToken')

            # Step 4: Create a new conversation entry in DynamoDB
            print(f"Creating conversation entry for mobile: {mobile}, name: {name}, access_token: {access_token}")
            create_response = create_conversation(mobile, name, access_token)
            if create_response:
                # Step 5: Invoke the `start_chat` method in the "musafir-interface" Lambda
                start_chat_payload = {
                    'method': 'start_chat',  # Specify the method to invoke
                    'access_token': access_token
                }
                print(f"Starting chat with access_token: {access_token}")
                # Call the Lambda function to start the chat and return the response
                start_chat_response = invoke_lambda('musafir-interface', start_chat_payload)
                response_data = json.loads(start_chat_response.get('body'))
                return {
                    'success': True,
                    'content': response_data.get('data', {}).get('content')
                }
            else:
                # Return error response if conversation entry creation fails
                print("Error: Failed to create conversation entry.")
                return {
                    'success': False,
                    'message': 'Error creating conversation entry.'
                }
        else:
            # Return error response if login fails
            print("Error: Failed to login for WhatsApp.")
            return {
                'success': False,
                'message': 'Error logging in for WhatsApp.'
            }
