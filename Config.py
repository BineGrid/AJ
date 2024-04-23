import json
import DevLogger as DL

__config: dict = None

def get_config() -> dict:
    return __config

def write(config: dict):
    '''
        Writes out the current config var in this file to the config.json file
    '''
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)      
    except Exception as e:
        DL.logger.critical("ERROR: Failed to write config!")
        DL.logger.exception(e)

def read():
    '''
        Reads the config.json file again and updates the values to the config var in this file
    '''
    global __config
    try:
        with open('config.json') as f:
            __config = json.load(f)      
    except Exception as e:
        DL.logger.critical("ERROR: Failed to read config!")
        DL.logger.exception(e)

if __config is None:
    read()