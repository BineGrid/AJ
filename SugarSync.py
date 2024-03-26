import json
from xml.dom.minidom import Element
import requests
import xml.etree.ElementTree as ET


# Load configuration from JSON file
with open('config.json') as f:
    config = json.load(f)

API_SAMPLE_USER_AGENT = "/Folders"
APP_AUTH_REFRESH_TOKEN_API_URL = "https://api.sugarsync.com/app-authorization"

def get_refresh_token(username, password, application, access_key, private_access_key):
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

# Usage example:
username = config["SugarSync_Username"]
password = config["SugarSync_Password"]
application = config["SugarSync_AP_ID"]
access_key = config["SugarSync_API_Key"]
private_access_key = config["SugarSync_API_Secret"]

def get_access_token(acc_key, priv_key, ref_token):
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

def make_api_request(acc_token, endpoint, method='GET', data=None):
    # Construct the request URL
    url = f"https://api.sugarsync.com/{endpoint}"
    
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
        else:
            return response.text  # Return the response text as is
    else:
        # Handle error response (e.g., raise exception, log error)
        response.raise_for_status()
    
# Gets our refresh token and access token using a user and password
refresh_token = get_refresh_token(username, password, application, access_key, private_access_key)
access_token = get_access_token(access_key, private_access_key, refresh_token)
        
def get_moonstones_folder_url() -> str:
    root_url = config["SugarSync_Root_URL"]
    
    make_api_request(access_token, "user")

get_moonstones_folder_url()

