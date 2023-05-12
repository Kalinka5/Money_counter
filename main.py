from gmail import get_mails_list, parsing_letters, delete_emails
from spreadsheet import get_columns_update, get_rows_update, spreadsheet_chunks_update, \
    get_last_index, get_part_of_table
from typing import List
from logger import Logger
import traceback
import os
import json
import pickle
from traceback import format_exc
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def create_service(client_secret_file: str, api_name: str, api_version: str, scopes: List[str], email: str,
                   loger: Logger):
    """
    Function to create Sheets API или Gmail API
    :param client_secret_file: credentials from Google Cloud
    :param api_name: "gmail" or "sheets"
    :param api_version: "v1" or "v4"
    :param scopes: OAuth consent scopes
    :param email: gmail address, in which the API will be used
    :param loger: Logger to write logs
    :return: service
    """
    port = 8000  # Connect port
    cred = None

    try:
        # Create path to token
        pickle_file = os.path.join('tokens', f'token_{email.replace(".", "_")}.pickle')
        loger.info(f"Loading token '{pickle_file}'.")
        if not os.path.exists("tokens"):  # Create folder, if you don't have
            os.makedirs("tokens")

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as file:
                cred = pickle.load(file)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
                while True:
                    # If the port is already used, go to the next port
                    try:
                        cred = flow.run_local_server(port=port)
                        break
                    except OSError:
                        port += 1

            with open(pickle_file, 'wb') as file:
                pickle.dump(cred, file)

        service = build(api_name, api_version, credentials=cred)
        return service

    except Exception:
        loger.error(format_exc())


if __name__ == '__main__':
    logger = Logger(unique_file_name_prefics="fundsMailParser", logs_expiring_time=5, program_name="FundsMailParser")

    try:
        # Open Config file with all configuration
        with open(os.path.join('configs', 'config.json')) as configs:
            config = json.load(configs)

        # Values to create services
        creds = None
        CLIENT_SECRET_FILE = os.path.join('configs', 'client_secret.json')  # get file path
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://mail.google.com/']

        # Create gmail and sheet services
        gmail = os.environ.get("Gmail_money", "")
        sheet_service = create_service(CLIENT_SECRET_FILE, "sheets", "v4", SCOPES, gmail, logger)
        gmail_service = create_service(CLIENT_SECRET_FILE, "gmail", "v1", SCOPES, gmail, logger)

        # All values to interact with program
        table_id = os.environ.get("spreadsheetID", "")
        sheet_name = config["sheetName"]
        column_music = config["columnAppleMusic"]
        column_cloud = config["column_iCloud"]
        column_others = config["other_column"]
        dollar_column = config["dollar_column"]
        uah_column = config["UAH_column"]
        min_index = config["minIndex"]
        spreadsheet = sheet_service.spreadsheets()

        # Get all id mails with key-word q.
        mails = get_mails_list(gmail_service, config["q"])

        # Get list of app's name and values of money
        parsed_gmails = parsing_letters(gmail_service, mails, logger)

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

        # get last indexes of each column
        columns = [column_music, column_cloud, column_others]
        last_index = get_last_index(spreadsheet, table_id, sheet_name, columns, min_index)

        # Preparing values to update the columns Apple Music, iCloud, Additional app.
        table_data = [
            get_columns_update(data_apple_music, sheet_name, column_music, last_index[0], len(data_apple_music) + 1),
            get_columns_update(data_icloud, sheet_name, column_cloud, last_index[1], len(data_apple_music) + 1),
            get_columns_update(data_others, sheet_name, column_others, last_index[2], len(data_apple_music) + 1)]
        # Update columns Apple Music, iCloud, Additional app
        spreadsheet_chunks_update(spreadsheet, table_data, table_id, logger)

        # Get list of all money values from table
        list_money = get_part_of_table(spreadsheet, table_id, sheet_name, column_music, column_others, min_index, 18)

        # Count sum of all values
        summa = 0
        for i in list_money:
            summa += float(i.replace(",", "."))

        # Create dollar and UAH variables
        summa_d = f"{summa:.2f}"
        summa_h = f"{summa*40:.2f}"

        # Preparing values to update the columns Sum($) and Sum(₴).
        table_sum_data = [
            get_rows_update([summa_d, summa_h], sheet_name, dollar_column, uah_column, min_index)
        ]
        # Update columns Sum($) and Sum(₴)
        spreadsheet_chunks_update(spreadsheet, table_sum_data, table_id, logger)

        # Delete mails from email address
        delete_emails(gmail_service, mails, logger)

    except Exception:
        logger.error(traceback.format_exc())
