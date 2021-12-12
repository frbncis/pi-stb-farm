
def add_mqtt_arguments(arg_group):
    arg_group.add_argument('--mqtt-host', help='MQTT Host', required=True)
    arg_group.add_argument('--mqtt-user', help='MQTT User', required=True)
    arg_group.add_argument('--mqtt-password', help='MQTT Password', required=True)
    
