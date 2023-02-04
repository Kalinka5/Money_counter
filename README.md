# Money_counter
![Pypi](https://img.shields.io/pypi/v/google?color=orange&style=plastic)
![Python](https://img.shields.io/pypi/pyversions/google_auth_oauthlib?color=gree&style=plastic)
![Watchers](https://img.shields.io/github/watchers/Kalinka5/Money_counter?style=social)
![Stars](https://img.shields.io/github/stars/Kalinka5/Money_counter?style=social)

PROGRAM IS USED TO **COUNT YOUR SUBSCRIPTIONS SPENDING** BY USING **GOOGLE** AND **SPREADSHEETS API**S.

![Gif](https://user-images.githubusercontent.com/106172806/216621787-bd1a4a66-377f-467c-a371-9d2d00fd30b3.gif)

![Money](https://user-images.githubusercontent.com/106172806/216789011-9b0dc0f5-700c-4c66-a1a3-4393c1f24cd0.gif)

## *Usage*
First of all, to use this program, you should create [new project](https://console.cloud.google.com/projectcreate?previousPage=%2Fwelcome%3Fproject%3Dmoneycounter-376608%26authuser%3D1&organizationId=0&authuser=1) in Google Cloud. After creation the project, go to the APIs & Services in navigation menu. Choose Library section. Then, in the search field input Gmail API click on this app and click on button "Enable". With Google Sheets API do the same things.

Secondly, create new sheet in the [Google Sheets](https://www.google.com/sheets/about/). Further, add column names for comfort:

![empty_table](https://user-images.githubusercontent.com/106172806/216630610-f76a5e5d-854c-441a-b7a2-b1249701e887.jpg)

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

Then store all values in variables:
```python
# All values to interact with program
table_id = config["spreadsheetID"]
sheet_name = config["sheetName"]
column_music = config["columnAppleMusic"]
column_cloud = config["column_iCloud"]
column_others = config["other_column"]
dollar_column = config["dollar_column"]
uah_column = config["UAH_column"]
min_index = config["minIndex"]
spreadsheet = sheet_service.spreadsheets()
```

Further, get all mail's ids we want (we passing the key-word to the function get_mails_list()):
```python
# Get all id mails with key-word q.
mails = get_mails_list(gmail_service, config["q"])
```

As soon as we get all mail's ids, let's parse each letter to get all values to our table:
```python
# Get list of app's name and values of money
parsed_gmails = parsing_letters(gmail_service, mails, logger)
```
Moreover, with key-word "subject: Apple" we get unneeded letters, like this:

![unused_letters](https://user-images.githubusercontent.com/106172806/216625105-102cf723-a1d7-40b1-9281-d923cc7347fe.jpg)

To avoid these mails, we check subject in parsing_letters() function:
```python
if subject == "Квитанция от Apple":
    ...code
```

As we get all data, let's update our sheet. To make this, we should separate values in 3 groups(Apple Music, iCloud+ and Additional app):
```python
# separate values in each variables
data_apple_music = []
data_icloud = []
data_others = []
for data in parsed_gmails:
    if data[0] == 'Apple Music':
        data_apple_music.append(data[1])
    elif data[0] == 'iCloud+':
        data_icloud.append(data[1])
    elif data[0] == 'Additional app':
        data_others.append(data[1])
```

One more important thing is getting last index in a column to update the column from this index:
```python
# get last indexes of each column
columns = [column_music, column_cloud, column_others]
last_index = get_last_index(spreadsheet, table_id, sheet_name, columns, min_index)
```

Before updating, we should prepare values for each column.
```python
# Preparing values to update the columns Apple Music, iCloud, Additional app.
table_data = [
    get_columns_update(data_apple_music, sheet_name, column_music, last_index[0], len(data_apple_music) + 1),
    get_columns_update(data_icloud, sheet_name, column_cloud, last_index[1], len(data_apple_music) + 1),
    get_columns_update(data_others, sheet_name, column_others, last_index[2], len(data_apple_music) + 1)]
```

After that, let's update the empty table:
```python
# Update columns Apple Music, iCloud, Additional app
spreadsheet_chunks_update(spreadsheet, table_data, table_id, logger)
```
And the final peace of code count sum of all colum's values:
```python
# Get list of all money values from table
list_money = get_part_of_table(spreadsheet, table_id, sheet_name, column_music, column_others, min_index, 18)

# Count sum of all values
summa = 0
for i in list_money:
    summa += float(i.replace(",", "."))

# Create dollar and UAH variables
summa_d = f"{summa:.2f}"
summa_h = f"{summa*40:.2f}"
```

At the end, prepare values in the columns Sum($) and Sum(₴) and update the table again:
```python
# Preparing values to update the columns Sum($) and Sum(₴).
table_sum_data = [
    get_rows_update([summa_d, summa_h], sheet_name, dollar_column, uah_column, min_index)]

# Update columns Sum($) and Sum(₴)
spreadsheet_chunks_update(spreadsheet, table_sum_data, table_id, logger)
```

As a result, we will get the filled table:

![update_table](https://user-images.githubusercontent.com/106172806/216629752-01a516ad-d76c-40d9-8096-91c0c16dfa5d.jpg)

And delete these letters from our email address:
```python
# Delete mails from email address
delete_emails(gmail_service, mails, logger)
```
___
