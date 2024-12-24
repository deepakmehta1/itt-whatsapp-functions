import requests
import json
import boto3
import os
from conversation_util import find_conversation_and_communicate

client = boto3.client('sqs')

def push_event(msg):

    ingest_queue_url = 'https://sqs.ap-south-1.amazonaws.com/994442116312/whatsapp_events'
    msg = json.dumps(msg)
    response = client.send_message(QueueUrl=ingest_queue_url, MessageBody=msg)
    print('Pushed to SQS, Response -- ', response)
    
def get_variable(var):
    return os.environ[var]

def get_template(t_type):
    return {'name': t_type, 'language': {'code': 'en'}}

BUTTONS = {
            'Call a human?': {'text': 'Ok. sure. I will ask my team to contact you, Thank you!'},
            'Explore trips?':{'template': 'trip_state_buttons'},
            'Himachal Trips':{'template': 'himachal_trips'},
            'Uttarakhand Trips': {},
            'Kasol Kheerganga': {'document': '637030961426757', 'filename': 'Kasol Kheerganga.pdf'},
            'Manali Solang Kasol': {'document': '500205981511357', 'filename': 'Manali Solang Kasol.pdf'} 
         }

def send_msg(msg):
    try:
        mobile = msg['mobile']
        payload = { 
            "messaging_product": "whatsapp",
            "to": mobile
            }
    
        if 'message_id' in msg:
            payload["context"] = {
                            "message_id": msg['message_id']
                        }
        if 'template' in msg:
            payload['type'] = 'template'
            payload['template'] =  get_template(msg['template'])
            
        if 'text' in msg:
            payload['type'] = 'text'
            payload['text'] = {
                                "preview_url": False,
                                "body": msg['text']
                            }
        if 'document' in msg:
            payload['type'] = 'document'
            payload['document'] = {
                                 "id": msg['document'],
                                 "filename": msg['filename']    
                                } 
        v = get_variable('version')
        phone_number_id = get_variable('phone_number_id')
        token = get_variable('token')
        url = 'https://graph.facebook.com/{}/{}/messages'.format(v,phone_number_id)
        
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer {}'.format(token)
         }
        print('payload --', payload)
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        print('response of the API --', response.text)
        if payload['type'] == 'document':
            response = json.loads(response.text)
            message_id = response['messages'][0]['id']
            msg = {'mobile': mobile, 'message_id': message_id, 'template': 'interested_trip1'}
            send_msg(msg)
    except Exception as e:
        print('Exception occurred -- ', str(e))
        return {'statusCode': 200, 'body': 'ok'}

def contacts(contact_list):
    names = []
    for cl in contact_list:
        name = cl['profile']['name']
        names.append(name)
        print('name -- ', name)
        print('wa_id --', cl['wa_id'])
    return names


def readable(event):
    if event['type'] == 'text':
        msg = '{} : User sent text - {}'.format(event['date_time'], event['content'])
    elif event['type'] == 'button':
        msg = '{} : User pressed button - {}'.format(event['date_time'], event['content'])
    return msg

def query_result(data):
    try:
        query = data['query']
        query = query.replace('filter(', '')
        query = query[:-1]
        filters = list(map(str,query.split(',')))
        for f in filters:
            obj,value = map(str,f.split(':'))
            if obj=='mobile':
                mobile = value
            elif obj == 'date':
                date = value
        conv = get_conversation(mobile, date)
        if conv:
            msg = []
            for c in conv['interactions']:
                msg.append(readable(c))
            msg_data = {'mobile': mobile, 'messages': msg} 
        else:
            msg_data = {'mobile': mobile, 'messages': ['No data found, try with different inputs']}
        if data['source'] == 'whatsapp':
            msg_data = {'mobile': data['to_mobile'], 'message_id': data['msg_id'], 'type': 'text', 'text': str(msg)}
            send_msg(msg_data)
        headers = { "Access-Control-Allow-Origin" : "*"}
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps(msg_data)}
    except Exception as e:
        print('Exception occurred -- ', str(e))
        return {'statusCode': 500, 'headers': headers, 'body': str(e)}
        
def cors_headers():
    headers = {
        "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Request-Method": "GET,OPTIONS,POST"
    }
    return {'statusCode': 200,'headers': headers, 'body': 'ok'}
    
def lambda_handler(event, context):
    print(event)
    if 'httpMethod' in event and event['httpMethod'] == 'OPTIONS':
        return cors_headers()
    if "queryStringParameters" in event and event["queryStringParameters"] and 'q' in event["queryStringParameters"]:
        data = {'query': event["queryStringParameters"]['q'], 'source': 'web'}
        return query_result(data)
    if 'body' in event:
        event = json.loads(event['body'])
        print('event body -- ', event)
        # return {'statusCode': 200, 'body': 'ok'} 
    else:
        return {'statusCode': 200, 'body': 'ok'}
    first_entry = event['entry'][0]
    first_change = first_entry['changes'][0]
    
    # main object of the event
    main_obj = first_change['value']
    if 'contacts' in main_obj:
        names = contacts(main_obj['contacts'])
        c_name = names[0]
    if 'messages' in main_obj:
        for message in main_obj['messages']:
            print('message -- ', message)
            mobile = message['from']
            msg_id = message['id']
            timestamp = message['timestamp']
            event_type = message['type']
            if  event_type == 'text':
                content = message['text']['body']
                if content.startswith('get='):
                    data = {'query': content.replace('get=',''), 'source': 'whatsapp', 'to_mobile': mobile, 'msg_id': msg_id}
                    return query_result(data)
                # msg_data = {'mobile': mobile, 'template': 't_greeting'}
                # send_msg(msg_data)
                chat_response = find_conversation_and_communicate(mobile[2:], c_name, content)
                if chat_response["success"]:
                    text = chat_response.get('content')
                else:
                    text = 'Services are currently down, please try again after sometime.'
                msg_data = {'mobile': mobile, 'text': text}
                send_msg(msg_data)
            elif event_type == 'button':
                button = message['button']
                content = button['text']
                msg_data = {'mobile': mobile}
                msg_data.update(BUTTONS[content])
                send_msg(msg_data)
            else:
                return {'statusCode': 200, 'body': 'ok'}
            # sqs_payload = {'mobile': mobile, 'c_name': c_name, 'm_id': msg_id, 'timestamp': timestamp, 'type': event_type, 'content': content}
            # push_event(sqs_payload)
        
    return {'statusCode': 200, 'body': 'ok'}
