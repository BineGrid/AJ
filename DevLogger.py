import json
import logging

with open('/mnt/wslg/distro/home/dcann/mojo/AJ/config.json') as f:
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

# This is the actually just a regular python logger with a custom handler
# Since I needed to add a custom handler to it I wanted to put it in one place
# and then have all my code reference it here
logger = logging.getLogger(__name__)
logger.addHandler(GUITextHandler())
    
