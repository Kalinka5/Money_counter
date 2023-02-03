from typing import List
from logger import Logger
from more_itertools import chunked


def get_column(spreadsheets, spreadsheet_id: str, sheet_name: str, column_name: str, min_index: int, max_index=""):
    """
    Getting a column from a table, returns a list with the values of the column
    :param spreadsheets: spreadsheets of sheets api service
    :param spreadsheet_id: table id
    :param sheet_name: sheet name
    :param column_name: column name
    :param min_index: minimal index to read
    :param max_index: maximum index to read
    :return: list
    """
    result = []
    sheet_range = sheet_name + f"!{column_name}{min_index}:{column_name}{max_index}"
    data = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute().get('values', [])

    for row in data:
        try:
            result.append(row[0])
        except IndexError:
            result.append('')
    return result


def get_part_of_table(spreadsheets, spreadsheet_id: str, sheet_name: str, column_start: str,
                      column_end: str, min_index: int, max_index: int):
    """
    Getting a part of the table, returns a list with the values of the column
    :param spreadsheets: spreadsheets of sheets api service
    :param spreadsheet_id: table id
    :param sheet_name: sheet name
    :param column_start: initial column
    :param column_end: final column
    :param min_index: minimal index to read
    :param max_index: maximum index to read
    :return: list
    """
    result = []

    sheet_range = sheet_name + f"!{column_start}{min_index}:{column_end}{max_index}"
    data = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute().get('values', [])

    for row in data:
        for value in row:
            result.append(value)

    return result


def get_last_index(spreadsheets, spreadsheet_id: str, sheet_name: str, column_names: List[str], min_index: int):
    """
    Function to get first empty cells in the columns
    :param spreadsheets:
    :param spreadsheet_id: table id
    :param sheet_name: sheet name
    :param column_names: list of column's names
    :param min_index: minimal index to read
    :return: list
    """
    result = []

    for column in column_names:
        column_data = get_column(spreadsheets, spreadsheet_id, sheet_name, column, min_index)
        max_index = len(column_data) + min_index
        result.append(max_index)

    return result


def get_columns_update(data: List[str], sheet_name: str, column: str, row_index_start: int, row_index_end: int):
    """
    Returns a dictionary for updating multiple table columns
    :param data: list of data
    :param sheet_name: sheet name
    :param column: column name
    :param row_index_start: initial index
    :param row_index_end: final index
    :return: dict
    """
    return {
        "range": f"{sheet_name}!{column}{row_index_start}:{column}{row_index_end}",
        "majorDimension": "COLUMNS",
        "values": [data]
    }


def get_rows_update(data: List[str], sheet_name: str, column_start: str, column_end: str, row_index: int):
    """
    Returns a dictionary for updating multiple table rows
    :param data: list of data
    :param sheet_name: sheet name
    :param column_start: initial column
    :param column_end: final column
    :param row_index: row index
    :return: dict
    """
    return {
        "range": f"{sheet_name}!{column_start}{row_index}:{column_end}{row_index}",
        "majorDimension": "ROWS",
        "values": [data]
    }


def spreadsheet_chunks_update(spreadsheets, data: list, spreadsheet_id: str, logger: Logger, cells_per_update=400):
    """
    Writes data to the table, sends chunks across 400 elements by default to avoid connection loss due to a timeout.
    :param spreadsheets: spreadsheets of sheets api service
    :param data: data to update the table
    :param spreadsheet_id: sheet id
    :param logger: Logger to write logs
    :param cells_per_update: amount of data
    :return:
    """
    for chunk in chunked(data, cells_per_update):
        if logger:
            logger.info(f"Start updating the table.")
        spreadsheets.values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                    "valueInputOption": "USER_ENTERED",
                    "data": chunk,
                }
            ).execute()
        if logger:
            logger.info("The update was successful.\n")
