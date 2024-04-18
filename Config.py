import json
import DevLogger as DL

config = None

def write():
    '''
        Writes out the current config var in this file to the config.json file
    '''
    try:
        global config
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
    except Exception as e:
        DL.logger.critical("ERROR: Failed to write config!")
        DL.logger.exception(e)
        
    # Read the new config with the latest values
    read()

def read():
    '''
        Reads the config.json file again and updates the values to the config var in this file
    '''
    try:
        global config
        with open('config.json') as f:
            config = json.load(f)      
    except Exception as e:
        DL.logger.critical("ERROR: Failed to read config!")
        DL.logger.exception(e)

# Read the config everytime someone imports this file
read()