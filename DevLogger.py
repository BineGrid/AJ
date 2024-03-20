import json
import logging

with open('config.json') as f:
  config = json.load(f)
  
# Create a custom handler that updates the text element in the GUI window
class GUITextHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        message = self.format(record)
        print(message)
    
# Define the logger
logging.basicConfig(level=config["debug_level"])
    # TODO have it save log files if in debug mode
    #filename=log_file,
    #filemode='w'

logger = logging.getLogger(__name__)
logger.addHandler(GUITextHandler())
    
