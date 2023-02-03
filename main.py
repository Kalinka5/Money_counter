from gmail import get_mails_list, parsing_letters
from spreadsheet import get_columns_update_query, get_rows_update_query, spreadsheet_chunks_update, get_column, get_last_index
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
        with open(os.path.join('configs', 'config.json')) as file:
            config = json.load(file)

        creds = None
        CLIENT_SECRET_FILE = os.path.join('configs', 'client_secret.json')  # get file path
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://mail.google.com/']

        sheet_service = create_service(CLIENT_SECRET_FILE, "sheets", "v4", SCOPES, config["gmail"], logger)
        gmail_service = create_service(CLIENT_SECRET_FILE, "gmail", "v1", SCOPES, config["gmail"], logger)

        table_id = config["spreadsheetID"]
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

        result = parsing_letters(gmail_service, mails, logger)

        data_apple_music = []
        data_icloud = []
        other_data = []

        for data in result:
            if data[0] == 'Apple Music':
                data_apple_music.append(data[1])
            elif data[0] == 'iCloud+':
                data_icloud.append(data[1])
            elif data[0] == 'Additional app':
                other_data.append(data[1])

        last_index_music = get_last_index(spreadsheet, table_id, sheet_name, column_music, min_index)
        last_index_cloud = get_last_index(spreadsheet, table_id, sheet_name, column_cloud, min_index)
        last_index_other = get_last_index(spreadsheet, table_id, sheet_name, column_others, min_index)

        table_data = [
            get_columns_update_query(data_apple_music, sheet_name, column_music, last_index_music, len(data_apple_music)+1),
            get_columns_update_query(data_icloud, sheet_name, column_cloud, last_index_cloud, len(data_apple_music)+1),
            get_columns_update_query(other_data, sheet_name, column_others, last_index_other, len(data_apple_music)+1)]
        spreadsheet_chunks_update(spreadsheet, table_data, table_id, logger)

        money_Apple_music = get_column(spreadsheet, table_id, sheet_name, column_music, min_index)
        money_iCloud = get_column(spreadsheet, table_id, sheet_name, column_cloud, min_index)
        other_money = get_column(spreadsheet, table_id, sheet_name, column_others, min_index)
        list_sum = money_Apple_music + money_iCloud + other_money

        summa = 0
        for i in list_sum:
            summa += float(i.replace(",", "."))

        summa_d = f"{summa:.2f}"
        summa_h = f"{summa*40:.2f}"

        table_sum_data = [
            get_rows_update_query([summa_d, summa_h], sheet_name, dollar_column, uah_column, min_index)
        ]
        spreadsheet_chunks_update(spreadsheet, table_sum_data, table_id, logger)

    except Exception:
        logger.error(traceback.format_exc())
