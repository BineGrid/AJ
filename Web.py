"""
    This deals with everything web related both for grabbing information 
    and for writting information to the web pages
    
    This will deal with grabbing all the information from the Toast website
    & input information into shiftnote
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import DevScreenControl as DSC
from DevScreenControl import ShiftField as SF, ToastButton
from Shift import Shift

with open('config.json') as f:
  config = json.load(f)

# ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ███╗███████╗                                 
#██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗ ████║██╔════╝                                 
#██║     ███████║██████╔╝██║   ██║██╔████╔██║█████╗                                   
#██║     ██╔══██║██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝                                   
#╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗                                 
# ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝                                 
# ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     ██╗     ███████╗██████╗ 
#██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     ██║     ██╔════╝██╔══██╗
#██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     ██║     █████╗  ██████╔╝
#██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     ██║     ██╔══╝  ██╔══██╗
#╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗███████╗███████╗██║  ██║

class Tabs:
    '''
        All the possible tabs 
    '''
    TOAST = "toast"
    SHIFTNOTE = "shift"
    UNKOWN_TAB = "unkown"
    
driver = None

def init_chrome():
    '''
        You must call this before performing any web activities
    '''
    # Opens Chrome and initializes the driver
    global driver
    driver = webdriver.Chrome()
    
    # This disables pointless error print outs from Selenium
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Add options to disable download protection
    options.add_argument('--safebrowsing-disable-download-protection')

    # Opens Chrome and initializes the driver
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

def bring_to_front():
    '''
        Brings the automated chrome window to the front of the screen
        
        This allows you to find things via images on screen, since it
        gauruntees the chrome window is the first window on screen
    '''
    position = driver.get_window_position()
    driver.minimize_window()
    driver.set_window_position(position['x'], position['y'])
    driver.maximize_window()
    time.sleep(1)
    
def scroll_to_element(by: By, value: str):
    '''
        This will scroll the window to the bottom
    '''
    # Get the element at the bottom of the page
    bottom_element = driver.find_element(by, value)

    # Scroll to the bottom of the page using ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(bottom_element)
    actions.perform()

def check_element_exists(by: By, element: str):
    try:
        driver.find_element(by, element)
    except NoSuchElementException:
        return False
    return True

def get_current_tab():
    '''
        Returns the current Tab that is open
    '''
    if Tabs.TOAST in driver.current_url:
        return Tabs.TOAST
    elif Tabs.SHIFTNOTE in driver.current_url:
        return Tabs.SHIFTNOTE
    else:
        return Tabs.UNKOWN_TAB
    

def get_current_open_tabs():
    '''
        Returns a single string containing all the open known tab names
        Any unkown tabs will just be listed as unkown and still added to the string
    '''
    openTabs = ""
    handles = driver.window_handles
    for handle in handles:
        driver.switch_to.window(handle)
        openTabs += get_current_tab()
    return openTabs

def switch_url(url:str):
    '''
        Switches the Url of the current tab\n
        Dont call this unless you know what you're doing\n
        Use SwitchTabUrl instead its much safer
    '''
    if driver.current_url != url:
        driver.execute_script("window.location.href = '" + url + "';")
        time.sleep(config["DEFAULT_LOADING_WAIT"])

    
def switch_tab_url(tab: Tabs, url: str):
    '''
        This will change the url for a desired tab\n
        
        If the window for the specified tab ins't
        open then the function will open it

        If the Tab and/or Url are already open
        the function will do nothing
    '''
    
    # Check if tab exists, if not create one
    if tab not in get_current_open_tabs():
        print(" - Tab Didn't Exist Creating New Tab! - ")
        if tab == Tabs.TOAST:
            Toast.login()
        elif tab == Tabs.SHIFTNOTE:
            ShiftNote.login()
        else:
            raise Exception("Specified Tab has no case!: " + tab)
    
    if get_current_tab() != tab:
        driver.switch_to.window(tab)
    switch_url(url)


#████████╗ ██████╗  █████╗ ███████╗████████╗
#╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝
#   ██║   ██║   ██║███████║███████╗   ██║   
#   ██║   ██║   ██║██╔══██║╚════██║   ██║   
#   ██║   ╚██████╔╝██║  ██║███████║   ██║   

class Toast:
    '''
        This class contains all web activities pertaining to ToastTab
    '''
    
    def login():
        # Opens Toast Login Page
        if get_current_tab() != Tabs.UNKOWN_TAB:
            # Opens a new window if the current window is supposed to be open
            driver.execute_script(f"window.open('about:blank','{Tabs.TOAST}');")
            driver.switch_to.window(Tabs.TOAST)
        else:
            # Renames the current tab name to the proper name
            driver.execute_script(f"window.name = '{Tabs.TOAST}';")
        driver.get(config["TOAST_LOGIN_URL"])
        
        wait = WebDriverWait(driver, config["DEFAULT_LOADING_WAIT"])
        userWait = WebDriverWait(driver, 60)
        
        # Wait a little longer for page to load
        time.sleep(5)
        # Finds User input
        user = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        user.send_keys(config["TOASTUSER"])
        
        # Click Continue
        driver.find_element(By.NAME, "action").click()
        
        # This checks if there is a captcha (sometimes there just isn't one, idk why)
        # If there is a captcha increase the wait time to account for the user pressing the captcha
        if (check_element_exists(By.ID, "ulp-recaptcha")):
            # TODO Fix the captcha detection thingy
            #AJGui.createPopUpMsg("Please press the im not a robot check box\nThen press continue", "Help!")
            # Finds Password input
            passwd = userWait.until(
                EC.presence_of_element_located((By.NAME, "password")))
        else:
            passwd = wait.until(
                EC.presence_of_element_located((By.NAME, "password")))
            
        passwd.send_keys(config["TOASTPASS"])
        # Click Login
        driver.find_element(By.NAME, "action").click()
        
    def download_sales_summary():
        '''
            Switch to the payment summary url on the toast tab and download all the csv files
        '''
        switch_tab_url(Tabs.TOAST, config["TOASTHOME_URL"])
        switch_tab_url(Tabs.TOAST, config["TOASTSALES_URL"])
        driver.find_element(By.ID, "dropdown-20").click()
        time.sleep(0.1)
        DSC.click_image(ToastButton.CSV_Download)
        time.sleep(config["DEFAULT_DOWNLOAD_WAIT"])
        
    def download_payroll_export():
        '''
            Switch to the payroll url on the toast tab an download the export
        '''
        switch_tab_url(Tabs.TOAST, config["TOASTLABOR_URL"])
        driver.find_element(By.ID, "payroll-export").click()
        time.sleep(config["DEFAULT_DOWNLOAD_WAIT"])
        
    def download_everything(self):
        '''
            Download ALL the files that we may need from toast
        '''
        self.download_sales_summary()
        self.download_payroll_export()


#███████╗██╗  ██╗██╗███████╗████████╗███╗   ██╗ ██████╗ ████████╗███████╗
#██╔════╝██║  ██║██║██╔════╝╚══██╔══╝████╗  ██║██╔═══██╗╚══██╔══╝██╔════╝
#███████╗███████║██║█████╗     ██║   ██╔██╗ ██║██║   ██║   ██║   █████╗  
#╚════██║██╔══██║██║██╔══╝     ██║   ██║╚██╗██║██║   ██║   ██║   ██╔══╝  
#███████║██║  ██║██║██║        ██║   ██║ ╚████║╚██████╔╝   ██║   ███████╗
#╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚══════╝

class ShiftNote:
    '''
        This class contains all web activities pertaining to ShiftNote
    '''
    def login():
        # Opens ShiftNote Login Page
        if get_current_tab() != Tabs.UNKOWN_TAB:
            # Opens a new window if the current window is supposed to be open
            driver.execute_script(f"window.open('about:blank','{Tabs.SHIFTNOTE}');")
            driver.switch_to.window(Tabs.SHIFTNOTE)
        else:
            # Renames the current tab name to the proper name
            driver.execute_script(f"window.name = '{Tabs.SHIFTNOTE}';")
        driver.get(config["SHIFTNOTE_LOGIN_URL"])
        
        wait = WebDriverWait(driver, config["DEFAULT_LOADING_WAIT"])
        # Finds User input
        user = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        user.send_keys(config["SHIFTUSER"])
        # Finds Password input
        passwd = wait.until(EC.presence_of_element_located((By.NAME, "Password")))
        passwd.send_keys(config["SHIFTPASS"])
        # Click Login
        driver.find_element(By.NAME, "Submit").click()
        
    def enter_daily(sales, for_sales, g_count, takeout, angel_share = None):
        if sales is not None:
            DSC.enter_shiftnote_field(SF.Numeric.Sales, sales)
            
        if for_sales is not None:
            DSC.enter_shiftnote_field(SF.Numeric.For_Sales, for_sales)
            
        if sales is not None:
            DSC.enter_shiftnote_field(SF.Numeric.Guest_Count, g_count)
            
        if takeout is not None:
            DSC.enter_shiftnote_field(SF.Numeric.Takeout, takeout)
            
        if angel_share is not None:
            DSC.enter_shiftnote_field(SF.Numeric.Angel_Share, angel_share)
            
        #driver.find_element(By.ID, "submit1").click()
            
    def enter_labor(FOH_P, FOH_A, BOH_P, BOH_A):
        scroll_to_element(By.ID, config["SHIFT_SALES_LABOR_ID"])
        DSC.enter_shiftnote_field(SF.Numeric.BOH_Lab_For, BOH_P)
        DSC.enter_shiftnote_field(SF.Numeric.BOH_Lab_Act, BOH_A)
        DSC.enter_shiftnote_field(SF.Numeric.FOH_Lab_For, FOH_P)
        DSC.enter_shiftnote_field(SF.Numeric.FOH_Lab_Act, FOH_A)
        #driver.find_element(By.ID, "submit1").click()
        
    def enter_sales_labor(text: str):
        scroll_to_element(By.ID, config["SHIFT_MARKETING_ID"])
        DSC.enter_shiftnote_field(SF.Input.Sales_and_Lab, text)
        #driver.find_element(By.ID, "savebtn").click()
        
    def enter_business_flow(text: str):
        scroll_to_element(By.ID, config["SHIFT_BUSINESS_FLOW_ID"])
        DSC.enter_shiftnote_field(SF.Input.Business_Flow, text)
        #driver.find_element(By.ID, "savebtn").click()
        
    def enter_staffing_levels(text: str):
        scroll_to_element(By.ID, config["SHIFT_IMMEDIATE_STAFFING_ID"])
        DSC.enter_shiftnote_field(SF.Input.Staffing_Levels, text)
        scroll_to_element(By.ID, config["SHIFT_IMMEDIATE_STAFFING_ID"])
        #driver.find_element(By.ID, "savebtn").click()
        
    def enter_shift(self, shift: Shift):
        '''
            Takes in a shift object and then uses all its data to input everything into Shiftnote
        '''
        switch_tab_url(Tabs.SHIFTNOTE, config["SHIFTREPORT_URL"])
        bring_to_front()
        self.enter_daily(str(shift.netSales), str(shift.ProjSales), str(shift.guestCount), str(shift.takeoutSales))
        self.enter_labor(str(shift.ProjFOHLabor), str(shift.ActFOHLabor), str(shift.ProjBOHLabor), str(shift.ActBOHLabor))
        self.enter_sales_labor(shift.get_sales_proj_vs_act_perc())


