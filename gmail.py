import base64
from bs4 import BeautifulSoup
from traceback import format_exc
import re
from logger import Logger
import os
import sys
from googleapiclient.errors import HttpError


def get_mails_list(service, query: str, grab_per_query=500):
    """
    Get all mail's id by key word (query)
    :param service: gmail api service
    :param query: key word to search mails
    :param grab_per_query: amount of mail's id
    :return: list
    """
    page = None
    mails = []
    while True:
        response = service.users().messages().list(userId='me', includeSpamTrash=False, q=query, pageToken=page,
                                                   maxResults=grab_per_query).execute()
        page = response.get('nextPageToken', None)
        messages = response.get('messages', None)
        if messages:
            mails += messages
        if not page:
            break
    return mails


def parsing_letters(service, messages: list, logger: Logger):
    """
    Function to parsing mails to get money values and app's names
    :param service: gmail api service
    :param messages: all mail list
    :param logger: Logger to write logs
    :return: list
    """
    result = []
    # iterate through all the messages
    for msg in messages:
        subject = ""
        message = ""
        body_html = ""
        money = ""

        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']
            parts = payload.get('parts')

            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']

            if subject == "Квитанция от Apple":
                for part in parts:
                    body = part.get("body")
                    data = body.get("data")
                    mime_type = part.get("mimeType")

                    if mime_type == 'text/html':
                        body_html = base64.urlsafe_b64decode(data)

                soup = BeautifulSoup(body_html, "lxml")

                for string in soup.stripped_strings:
                    message += f"{string}\n"

                money = re.search(r"(\d+,\d+)\xa0USD\n", message)
                app = re.search(r"(iCloud\+)|(Apple\xa0Music)", message)
                app = app[0].replace("\xa0", " ")

                # Printing the subject, sender's email and message
                logger.info(f"App: {app}")
                logger.info(f"Money: {money[0]}")
                result.append([app, money[1]])

        except TypeError:
            logger.info(f"Additional App")
            logger.info(f"Money: {money[0]}")
            result.append(["Additional app", money[1]])

        except Exception:
            logger.error(format_exc())

    return result


def delete_emails(service, messages_for_trash, log):
    try:
        if messages_for_trash:
            ids = []
            for info_msg in messages_for_trash:
                ids.append(info_msg['id'])
            service.users().messages().batchModify(
                userId='me',
                body={
                    "ids": [ids],
                    'addLabelIds': ['TRASH']
                }).execute()
        log.info(f"Deleting {len(messages_for_trash)} mails")
    except HttpError as e:
        exc_type, _, exc_tb = sys.exc_info()
        log.error(f'Unexpected error {exc_type} at {os.path.split(__file__)[1]} at line {exc_tb.tb_next.tb_lineno}.\n'
                  f'Info: {e}', isError=True)
