import json
from xml.dom.minidom import Element
import requests
import xml.etree.ElementTree as ET
import re
from datetime import date, datetime
import DevLogger as DL
import os

# Load configuration from JSON file
with open('config.json') as f:
    config = json.load(f)
    
    
#   █████╗ ██╗   ██╗████████╗██╗  ██╗███████╗███╗   ██╗████████╗██╗ ██████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
#  ██╔══██╗██║   ██║╚══██╔══╝██║  ██║██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
#  ███████║██║   ██║   ██║   ███████║█████╗  ██╔██╗ ██║   ██║   ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║
#  ██╔══██║██║   ██║   ██║   ██╔══██║██╔══╝  ██║╚██╗██║   ██║   ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
#  ██║  ██║╚██████╔╝   ██║   ██║  ██║███████╗██║ ╚████║   ██║   ██║╚██████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
                                                     
API_SAMPLE_USER_AGENT = "/Folders"
APP_AUTH_REFRESH_TOKEN_API_URL = "https://api.sugarsync.com/app-authorization"

def __get_refresh_token(username, password, application, access_key, private_access_key):
    # Construct the XML request payload
    request_payload = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <appAuthorization>
        <username>{username}</username>
        <password>{password}</password>
        <application>{application}</application>
        <accessKeyId>{access_key}</accessKeyId>
        <privateAccessKey>{private_access_key}</privateAccessKey>
    </appAuthorization>"""

    # Make a HTTP POST request to the app authorization API
    headers = {
        "User-Agent": API_SAMPLE_USER_AGENT,
        "Content-Type": "application/xml"
    }
    response = requests.post(APP_AUTH_REFRESH_TOKEN_API_URL, headers=headers, data=request_payload)

    # Check if the request was successful (status code 201)
    if response.status_code == 201:
        # Extract the refresh token from the "Location" response header
        refresh_token = response.headers.get("Location")
        return refresh_token
    else:
        # Handle unsuccessful response (e.g., log error, raise exception)
        response.raise_for_status()

# Setting in all the config values
username = config["SugarSync_Username"]
password = config["SugarSync_Password"]
application = config["SugarSync_AP_ID"]
access_key = config["SugarSync_API_Key"]
private_access_key = config["SugarSync_API_Secret"]

def __get_access_token(acc_key, priv_key, ref_token):
    # Fill the XML request template
    request_xml = f"""
    <tokenAuthRequest>
        <accessKeyId>{acc_key}</accessKeyId>
        <privateAccessKey>{priv_key}</privateAccessKey>
        <refreshToken>{ref_token}</refreshToken>
    </tokenAuthRequest>
    """

    # Make a HTTP POST request to SugarSync authorization API
    headers = {
        'User-Agent': 'SugarSync API Sample/1.0',
        'Content-Type': 'application/xml',
    }
    
    response = requests.post('https://api.sugarsync.com/authorization', headers=headers, data=request_xml)
    access_token = None
    
    # Check the response
    if response.status_code == 201:
        # Access token can be retrieved from the "Location" response header
        access_token = response.headers['Location']
        print("Access token:", access_token)
    else:
        print("Failed to obtain access token. HTTP Status Code:", response.status_code)
        
    return access_token

# --=== These are the authentication tokens ===--
__refresh_token = __get_refresh_token(username, password, application, access_key, private_access_key)
__access_token = __get_access_token(access_key, private_access_key, __refresh_token)
# These are really important ^^^


#  ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗                           
#  ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗                          
#  ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝                          
#  ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗                          
#  ██║  ██║███████╗███████╗██║     ███████╗██║  ██║                          
#  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝                          
#  ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
#  ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
#  █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
#  ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
#  ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
#  ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

def make_api_request(acc_token, url, method='GET', data=None):
    '''
        Perform any basic http api request
        
        method defaults the 'GET'
    '''
    # Construct the request headers with the access token
    headers = {
        'Authorization': f'Bearer {acc_token}',
        'Content-Type': 'application/json'
    }
    
    # Make the API request
    response = requests.request(method, url, headers=headers, json=data)
    print("Response:", response)
    
    # Check the response status code
    if response.status_code == 200:
        # Check the content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()  # Return the JSON response data
        elif 'application/xml' in content_type:
            return response.text  # Return the response text as is
        else:
            return response # return the whole response
    else:
        # Handle error response (e.g., raise exception, log error)
        response.raise_for_status()

def get_element_name(element: Element) -> str:
    '''
        Returns the contents of the displayName tag within the element
    '''
    return element.find('displayName').text

def list_all_folder_elements(folder_url: str) -> list[Element]:
    '''
        Returns a list of all the elements within a folders contents url
    '''
    folder_xml_tree = ET.fromstring(make_api_request(__access_token, folder_url))
    return [folder for folder in folder_xml_tree.findall(".//collection[@type='folder']")]

def list_all_file_elements(folder_url: str) -> list[Element]:
    '''
        Returns a list of all the elements within a folders contents url
    '''
    file_xml_tree = ET.fromstring(make_api_request(__access_token, folder_url))
    return [file for file in file_xml_tree.findall(".//file")]

def find_folder_in_url(folder_url: str, folder_display_name: str) -> Element:
    '''
        This functions finds all the collection elements with the 'type=folder' tag
        
        You must pass in a folders contents url and it cant be the user folder or the shared folder
        it must be within the dir
    '''
    contents_folder = ET.fromstring(make_api_request(__access_token, folder_url))
    
    for collection in contents_folder.findall(".//collection[@type='folder']"):
        if get_element_name(collection) == folder_display_name:
            return collection
    
def get_moonstones_folder_url() -> str:
    '''
        This returns the contents url to the '/Moonstones SugarSync 2011' within sugarsync
        
        All the other helper functions don't work unless you within this specfic url
    '''

    # Grabs the root user xml tree
    root = ET.fromstring(make_api_request(__access_token, config["SugarSync_Root_URL"]))
    shared_folders_url = root.find('receivedShares').text
    
    shared_root = ET.fromstring(make_api_request(__access_token, shared_folders_url))
    
    for received_share in shared_root.findall('receivedShare'):
        display_name = received_share.find('displayName').text
        if display_name == "Moonstones SugarSync 2011":
            return received_share.find('sharedFolder').text 
    
def find_folder_url_xpath(x_path: str) -> str:
    '''
        Takes in a folder path starting withing the "/Moonstones SugarSync" 2011 folder
        
        Then returns the folder url of the last folder in the path 
    '''
    ordered_folder_list = x_path.split("/")
    
    moonstones_folder = ET.fromstring(make_api_request(__access_token, get_moonstones_folder_url()))
    curr_folder_url = moonstones_folder.find('contents').text
    
    for next_folder in ordered_folder_list:
        curr_folder_url = find_folder_in_url(curr_folder_url, next_folder).find('contents').text
        print(f"Curr Folder: {next_folder}, URL: {curr_folder_url}")
    
    return curr_folder_url

def extract_folder_date(string: str):
    '''
        Takes in a folder name and extracts the 4 digit year
        and/or the 2 digit month
        
        Returns (Month, Year) as a tuple
        Month = None if no month is found in the folder name
    '''
    
    # Define regular expression patterns for matching month and year
    month_year_pattern = r'\b(\d{1,2}\.\d{4})\b'  # Matches month and year in format MM.YYYY
    year_pattern = r'\b(\d{4})\b'  # Matches only year in format YYYY
    
    # Search for month and year pattern
    match = re.search(month_year_pattern, string)
    if match:
        split_text = match.group(1).split(".")
        return (int(split_text[0]), int(split_text[1]))
    
    # If month and year pattern not found, search for year pattern
    match = re.search(year_pattern, string)
    if match:
        return (None, int(match.group(1)))
    
    # If neither month and year nor year pattern found, return None
    return None

def extract_file_date_range(string: str) -> tuple[date, date]:
    '''
        Takes in a file name and extracts both the dates
        and returns them as a tuple of dates
        
        Returns (Date1, Date2) as a tuple
    '''
    
    # Define regular expression patterns for matching month and year
    date_pattern = r'(\d{2}\.\d{2}\.\d{4})\-(\d{2}\.\d{2}\.\d{4})'  # Matches month and year in format MM.DD.YYYY

    match = re.search(date_pattern, string)
    
    if match:
        # Extract and parse the two dates
        date1 = datetime.strptime(match.group(1), '%m.%d.%Y').date()
        date2 = datetime.strptime(match.group(2), '%m.%d.%Y').date()
        return (date1, date2)
    
    # If no date range found return none
    return None
           
def find_dated_folder_element(date: date, folder_url: str) -> Element:
    '''
        Takes in a date and then finds the folder within the folder_url 
        whos name best matches that date
        
        Folders in our sugarsync follow the dating conevtion of either just being dated
        as a single year or being dated as a single month within a specific year
    '''
    
    # Find all the elements in sub dir
    element_list = list_all_folder_elements(folder_url)
    
    # Find the element that has a matching name to todays date
    for element in element_list:
        extract_date = extract_folder_date(element.find("displayName").text)
        
        if extract_date[0] is not None:
            if extract_date == (date.month, date.year):
                return element
        elif extract_date[1] == date.year:
            return element
        
def find_dated_file_element(date: date, folder_url: str) -> Element:
    # Find all the elements in sub dir
    element_list = list_all_file_elements(folder_url)
    
    # Find the element that has a matching name to todays date
    for element in element_list:
        # Extract the date from the file name
        extracted_dates = extract_file_date_range(element.find("displayName").text)
        if extracted_dates is not None:
            # Should return two dates
            date1 = extracted_dates[0]
            date2 = extracted_dates[1]
            
            if (date1 <= date) and (date <= date2):
                return element
        
     # If we find nothing return none
    return None
         
        
#  ██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ 
#  ██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗
#  ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║
#  ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║
#  ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝


def download_file(url: str, dir: str, filename: str):
    '''
        Downloads a file from the given URL and saves it to the specified destination.

        :param url: The URL of the file to be downloaded.
        :param dir: The file path where the downloaded file will be saved.
        :param filename: The name of the file, please include its extension as well
    '''
    response = make_api_request(__access_token, url)
    if response.status_code == 200:
        with open(os.path.join(dir, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        DL.logger.debug(f"File downloaded successfully to {dir}")
    else:
        DL.logger.error(f"Failed to download file from {url}. HTTP Status Code: {response.status_code}")


def download_dated_SL_file(date: date, dir: str) -> str:
    '''
        Locates the proper S&L folder depending on the date inputed
        
        Returns the downloaded filename 
    '''
    # Open the first dated folder
    sl_folder_contents = find_dated_folder_element(date, find_folder_url_xpath("ADMIN/Sales and Labor")).find('contents').text

    # Open the second dated folder
    sl_folder_contents_2 = find_dated_folder_element(date, sl_folder_contents)

    # Find the dated file within the second dated folder
    sl_element = find_dated_file_element(date, sl_folder_contents_2.find('contents').text)
    
    file_name = sl_element.find("displayName").text
    filedata_url = sl_element.find("fileData").text
    
    download_file(filedata_url, dir, file_name)
    return file_name