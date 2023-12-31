import boto3
import json
import base64
from datetime import date
import psycopg2

class FetchRewards():
    
    def __init__(self, end_url, queue_name, msg_max, wait_time):
        self.end_url = end_url
        self.queue_name = queue_name
        self.msg_max = msg_max
        self.wait_time = wait_time

    def get_messages(self):
        # Function to receive SQS messages

        sqs_client = boto3.client('sqs','us-east-1',endpoint_url=self.end_url)
        response = sqs_client.receive_message(QueueUrl= self.end_url+'/'+ self.queue_name)
        return response['Messages']

    def encoding_logic(self, data):
        # Function to base64 encode input data

        msg_bytes = data.encode('ascii')
        base64_bytes = base64.b64encode(msg_bytes)
        encoded_msg = base64_bytes.decode('ascii')
        return encoded_msg

    def get_json(self, msg):
        # Function to get the json body 

        result = []
        for json_object in msg:
            body = json.loads(json_object["Body"])
            result.append(body)
        return result

    def encode_data(self, data):
        # Function to encode ip and device_id

        for user in data:
            user['masked_ip'] = self.encoding_logic(user['ip'])
            user['masked_device_id'] = self.encoding_logic(user['device_id'])
        return data

    def load_postgres_new(self, messages):
        # Function to load SQS data into postgres

        for message in messages:
            
            # Converting None type in locale column to either string or the actual value that exists
            message['locale'] = 'None' if message['locale'] == None else message['locale']

            # Get today's date 
            today = date.today().strftime("%Y-%m-%d")
            message['create_date'] = today

            # Removime unmasked ip and device_id
            message.pop('ip')
            message.pop('device_id')

            # Alter query to handle the app_version type error by changing type from integer to varchar
            query1 = '''alter table user_logins alter column app_version type VARCHAR'''

            # Insert query to insert the extracted SQS message data into the postgres database
            query2 = '''insert into user_logins (''' +','.join(list(message.keys()))+''') values '''+ str(tuple(message.values()))

            #Connecting to the database and executing the queries
            conn = psycopg2.connect(database = "postgres", user = "postgres", password = "postgres", host = "localhost", port = "5432")
            cur = conn.cursor()
            cur.execute(query1)
            conn.commit()
            cur.execute(query2)
            conn.commit()
            conn.close()

def main():
    end_url = 'http://localhost:4566/000000000000'
    queue_name = 'login-queue'
    msg_max = 5
    wait_time = 2
    fetch_rewards = FetchRewards(end_url, queue_name, msg_max, wait_time)

    values = fetch_rewards.get_messages()
    messages = fetch_rewards.get_json(values)
    encoded_msg = fetch_rewards.encode_data(messages)
    fetch_rewards.load_postgres_new(encoded_msg)

    return

if __name__ == "__main__":
    main()