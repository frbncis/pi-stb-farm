#!/usr/bin/python3
from bluetoothctl import Bluetoothctl
import argparseUtils
import argparse
import evdev
import logging
import time
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt

#DEVICE_PHYSICAL_ADDRESS = 'dc:a6:32:4f:be:b7'
#DEVICE_BLUEOOTH_ADDRESS = '80:F1:F1:0F:46:50'

parser = argparse.ArgumentParser(description='Script that emits keypresses from a Bluetooth remote to MQTT. Manages the remote connection state by disconnecting from the remote after it has been idle for an amount of time. The script assumes that the Bluetooth remote has already been paired.')
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

argparseUtils.add_mqtt_arguments(required)
#required.add_argument('--mqtt-host', help='MQTT Host', required=True)
#required.add_argument('--mqtt-user', help='MQTT User', required=True)
#required.add_argument('--mqtt-password', help='MQTT Password', required=True)

optional.add_argument('--device-timeout', type=int, default=500, help='Specifies the idle timeout for the remote. When this timeout is exceeded, the Bluetooth connection will be disconnected')
parser.add_argument('physical_address', help='The device physical address, as picked up by evdev. To find out the address for your device, run "python3 -m evdev.evtest"')
parser.add_argument('bluetooth_address', help='The device Bluetooth address. This is the one reported by bluetoothctl')

args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

bluetoothctl = Bluetoothctl()
lastInputTimestamp = None
maximumIdleTime = timedelta(seconds=args.device_timeout)

mqtt_topic = f'stbfarm/remotes/{args.bluetooth_address}'

logging.info(f'Will publish key events to topic {mqtt_topic}')

client = mqtt.Client(args.physical_address)
client.username_pw_set(args.mqtt_user, args.mqtt_password)
client.connect(args.mqtt_host, keepalive=10)
client.loop_start()

while True:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    remote = None
    for device in devices:
        if args.physical_address == device.phys: 
            logging.info(f'Connected to remote: {device.path}, {device.name}, {device.phys}')
            remote = device
            lastInputTimestamp = datetime.now()
            client.publish(f'{mqtt_topic}/state/connected', payload=1, retain=True)
            break
    
    if remote is None:
        logging.debug("Could not find remote, sleeping...")
        time.sleep(2)
    else:
        try:
            while True:
                inputEvent = remote.read_one()
    
                if inputEvent != None:
                    lastInputTimestamp = datetime.now()
                    if inputEvent.type == evdev.ecodes.EV_KEY:
                        logging.info(evdev.categorize(inputEvent))
                        client.publish(f'{mqtt_topic}/key/{inputEvent.code}', payload=inputEvent.value, retain=True)
                else:
                    idleTime = datetime.now() - lastInputTimestamp

                    # idelTime is a datetime.timedelta in microseconds
                    if idleTime > maximumIdleTime:
                        logging.info(f'idleTime {idleTime} exceeds maximumIdleTime {maximumIdleTime}, preparing to disconnect')
                        bluetoothctl.disconnect(args.bluetooth_address)
                        logging.info('Disconnected!!!')
                        client.publish(f'{mqtt_topic}/state/connected', 0)
                        break

        except Exception as e:
            logging.info('Disconnected from remote')
            client.publish(f'{mqtt_topic}/state/connected', 0)
            logging.info(e)
