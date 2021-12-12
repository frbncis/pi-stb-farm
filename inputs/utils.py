def configure_logging(logging):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def add_mqtt_arguments(arg_group):
    arg_group.add_argument('--mqtt-host', help='MQTT Host', required=True)
    arg_group.add_argument('--mqtt-user', help='MQTT User', required=True)
    arg_group.add_argument('--mqtt-password', help='MQTT Password', required=True)
    
