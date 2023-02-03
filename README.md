# Money_counter
![Pypi](https://img.shields.io/pypi/v/google?color=orange&style=plastic)
![Python](https://img.shields.io/pypi/pyversions/google_auth_oauthlib?color=gree&style=plastic)
![Watchers](https://img.shields.io/github/watchers/Kalinka5/Money_counter?style=social)
![Stars](https://img.shields.io/github/stars/Kalinka5/Money_counter?style=social)

PROGRAM IS USED TO **COUNT YOUR SUBSCRIPTIONS SPENDING** BY USING **GOOGLE** AND **SPREADSHEETS API**S.

## *Usage*
First of all, to use this program, you should create [new project](https://console.cloud.google.com/projectcreate?previousPage=%2Fwelcome%3Fproject%3Dmoneycounter-376608%26authuser%3D1&organizationId=0&authuser=1) in Google Cloud. After creation the project, go to the APIs & Services in navigation menu. Choose Library section. Then, in the search field input Gmail API click on this app and click on button "Enable". With Google Sheets API do the same things.

Secondly, create new sheet in the [Google Sheets](https://www.google.com/sheets/about/). Further, add column names for comfort.

Last but not least, you should install some packages:
+ [more-itertools](https://pypi.org/project/more-itertools/)
+ [lxml](https://pypi.org/project/lxml/)
+ [google-api-python-client](https://pypi.org/project/google-api-python-client/)
+ [google-auth-oauthlib](https://pypi.org/project/google-auth-oauthlib/)
+ [google](https://pypi.org/project/google/)
___

## *Example*
To begin with, open config file with all values:
```python
# Open Config file with all configuration
with open(os.path.join('configs', 'config.json')) as file:
    config = json.load(file)
```

Then, we should create services of our Google and Spreadsheets APIs. Before that create variables with values for creation services. Where CLIENT_SECRET_FILE is credentials of program in our project in the Google Cloud. And SCOPES is list of string values to interact with APIs.
```python
# Values to create services
creds = None
CLIENT_SECRET_FILE = os.path.join('configs', 'client_secret.json')  # get file path
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://mail.google.com/']
```

After that, create services by using function create_service():
```python
# Create gmail and sheet services
sheet_service = create_service(CLIENT_SECRET_FILE, "sheets", "v4", SCOPES, config["gmail"], logger)
gmail_service = create_service(CLIENT_SECRET_FILE, "gmail", "v1", SCOPES, config["gmail"], logger)
```






___
