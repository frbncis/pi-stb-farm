import argparseUtils
import argparse
import paho.mqtt.client as mqtt
import time
from evdev import ecodes

MQTT_TOPIC = 'stbfarm/remotes/#'

parser = argparse.ArgumentParser(description='Script that subscribes to remote key events published through MQTT')

parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

argparseUtils.add_mqtt_arguments(required)
required.add_argument('--mqtt-client-name', help='Name for the MQTT client', required=True)

args = parser.parse_args()

def on_message(client, userdata, message):
    if '/key/' in message.topic:
        key = int(message.topic.split('/')[-1])
        print(f'KEY\t{key}\t({ecodes.KEY[key]})\t\tvalue={str(message.payload.decode("utf-8"))}')
    elif '/state/' in message.topic:
        state = message.topic.split('/')[-1]
        print(f'STATE\t{state}\t\t\tvalue={str(message.payload.decode("utf-8"))}')


client = mqtt.Client(args.mqtt_client_name)
client.on_message = on_message
client.username_pw_set(args.mqtt_user, args.mqtt_password)
client.connect(args.mqtt_host, keepalive=10)

print('subscribing...')
client.loop_start()
client.subscribe(MQTT_TOPIC)
print('starting loop')

while True:
    pass
