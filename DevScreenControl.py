import json
import os
import time
import pyautogui
import DevLogger as DL

class ShiftField:
    '''
        All the Shiftnote input fields enumerated with there image name for convenience
    '''
    class Numeric:
        Sales = "Sales.png"
        For_Sales = "ForecastedSales.png"
        Guest_Count = "GuestCount.png"
        Angel_Share = "AngelShare.png"
        Takeout = "Takeout.png"
        BOH_Lab_For = "BOHLaborForecast.png"
        BOH_Lab_Act = "BOHLaborActual.png"
        FOH_Lab_For = "FOHLaborForecast.png"
        FOH_Lab_Act = "FOHLaborActual.png"
        
    class Input:
        Sales_and_Lab = "SalesLabor.png"
        Specials = "Specials.png"
        Training = "Training.png"
        Tardiness_Call_Outs = "TardinessCallOuts.png"
        Staffing_Levels = "StaffingLevels.png"
        Business_Flow = "BusinessFlow.png"
        Item_86d = "86d.png"
        
class ToastButton:
    CSV_Download = "DownloadCSVFiles.png"

with open('config.json') as f:
  config = json.load(f)
  
# Function to scroll down until a specific color is found
def find_image_move_until_color_found(image, color, x_move=0, y_move=0):
    '''
        This will find the center coords of an image on screen, then move either up or down
        from that point until it finds the desired (R, G, B) color, then click that point
        
        RGB is passed in as a tuple of vals between 0-255
        
        You must set a x_move and a y_move val to specify how many pixels you want to move per tick
        This function will autoterminate if you dont pass in any movemment
    '''
    if x_move == 0 and y_move == 0:
        DL.logger.error("No Movement passed in for find_image_move... in DIC")
        return
    
    image_path = os.path.join(config["images_path"], image)
    try:
        x, y = pyautogui.locateCenterOnScreen(image_path, confidence=config["image_click_confidence"])
            
    except Exception as e:
        DL.logger.error(f"Image: {image} with a confidene of {config["image_click_confidence"]}, was not found on the screen!")
        DL.logger.exception(e)
        
    DL.logger.debug(f"Image: {image}, Found at ({int(x)},{int(y)})")
    
    # Scroll until the desired color is found
    while True:
        pyautogui.moveTo(x, y)
        # Check the color of the pixel at the current location
        pixel_color = pyautogui.pixel(int(x), int(y))
        if pixel_color == color:
            pyautogui.click(x, y)
            break
        # inverted y for negative going down
        y -= y_move
        x += x_move

def click_image(image, x_offset=0, y_offset=0):
    image_path = os.path.join(config["images_path"], image)
    try:
        x, y = pyautogui.locateCenterOnScreen(image_path, confidence=config["image_click_confidence"])
        # I inverted the y because I like negative numbers bringing us towards the bottom of the screen 
        pyautogui.click(x + x_offset, y - y_offset)
    except Exception as e:
        DL.logger.error(f"Image: {image} with a confidene of {config["image_click_confidence"]}, was not found on the screen!")
        DL.logger.exception(e)
    
def enter_shiftnote_field(field: ShiftField, input: str):
    x = 0 
    y = 0
    if(field in vars(ShiftField.Input).values()):
        y = -20
    elif(field in vars(ShiftField.Numeric).values()):
        x = 50
    else:
        DL.logger.error(f"ERROR: Field {field} is not supported")
        
    find_image_move_until_color_found(field, (255, 255, 255), x, y)
    time.sleep(0.2)
    pyautogui.write(input) 
    
#enter_business_flow("test")