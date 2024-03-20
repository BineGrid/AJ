import requests
import base64

# SugarSync API credentials
API_KEY = 'ODkyNTQwMTY3Nzk4OTA5OTU0Mw'
API_SECRET = 'NTFmZWM4MWY2NTM0NGFmNDhkZWY2YTFhZDliMWUwNjE'

# Base64 encode the API key and secret
credentials = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()

# SugarSync API endpoints
API_BASE_URL = 'https://api.sugarsync.com'
AUTH_ENDPOINT = '/authorization'
FOLDER_ENDPOINT = '/Folders'

def get_access_token():
    # Make a POST request to authenticate and obtain access token
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'password',
        'username': 'info@moonstones110.com',
        'password': '114xwxma',
        'app_id': '/sc/892540/32_1008193986'
    }
    response = requests.post(API_BASE_URL + AUTH_ENDPOINT, headers=headers, data=data)
    response_json = response.json()
    return response_json['access_token']

def list_root_folder(access_token):
    # Make a GET request to list the contents of the root folder
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(API_BASE_URL + FOLDER_ENDPOINT.format(folder_id='root'), headers=headers)
    response_json = response.json()
    return response_json

def main():
    # Get access token
    access_token = get_access_token()

    # List contents of root folder
    root_folder_contents = list_root_folder(access_token)
    print(root_folder_contents)

if __name__ == '__main__':
    main()
