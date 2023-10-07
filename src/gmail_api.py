from __future__ import print_function
from typing import List, Dict

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import pytz


from bs4 import BeautifulSoup
import base64

import os.path

SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://mail.google.com/"]


class GmailAPI:
    def __init__(self, nb_emails):
        self.nb_emails = nb_emails
        self.creds = None
        self.get_api_credentials()
        self.service = build("gmail", "v1", credentials=self.creds)

    def execute_with_status(func, *args, **kwargs):
        print("Executing function...", end="", flush=True)
        result = func(*args, **kwargs)
        print("Done")
        return result

    def get_api_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if not os.path.exists("credentials"):
            os.makedirs("credentials")

        # Check if the token.json file exists
        if os.path.exists("credentials/token.json"):
            try:
                self.creds = Credentials.from_authorized_user_file(
                    "credentials/token.json", SCOPES
                )
            except Exception as e:
                print(f"An error occurred while loading token.json: {e}")

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("credentials/token.json", "w") as token:
                token.write(self.creds.to_json())
        pass

    def list_email_tags(self):
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=self.creds)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    def extract_sender_info(self, input_str):
        try:
            # Find the positions of the opening '<' and closing '>'
            open_angle = input_str.index("<")
            close_angle = input_str.index(">")

            # Extract the name and email using string slicing
            sender_name = input_str[:open_angle].strip()
            sender_email = input_str[open_angle + 1 : close_angle].strip()

        except:
            # Handle the case where the string format is incorrect

            sender_name = ""
            sender_email = input_str

        # Create a dictionary with the extracted info
        sender_info = {"sender_name": sender_name, "sender_email": sender_email}
        return sender_info

    def get_body_from_email_id(self, email_id):
        service = build("gmail", "v1", credentials=self.creds)
        txt = service.users().messages().get(userId="me", id=email_id).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt["payload"]

            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get("parts")[0]
            data = parts["body"]["data"]
            data = data.replace("-", "+").replace("_", "/")
            decoded_data = base64.b64decode(data)
            return decoded_data

        except:
            pass

    def get_emails(self, sender_email=None):
        log_message = (
            f"Fetching messages from {sender_email} .. "
            if sender_email
            else "Fetching messages  .. "
        )
        print(log_message, end="", flush=True)
        email_list = []

        query = f"from:{sender_email}" if sender_email else None
        print(query)
        result = (
            self.service.users()
            .messages()
            .list(maxResults=self.nb_emails, userId="me", q=query)
            .execute()
        )
        messages = result.get("messages")
        print(f"Done, {len(messages)} messages fetched from gmail. ")
        print("Parsing messages .. ", end="", flush=True)

        total_messages = len(messages)
        index = 1

        for msg in messages:
            if index == total_messages:
                print(f"\rProcessing email {index+1}/{total_messages}")
            else:
                print(
                    f"\rProcessing email {index+1}/{total_messages}", end="", flush=True
                )

            index += 1
            email_dict = {}
            email_dict["message_id"] = msg["id"]

            # Get the message from its id
            txt = (
                self.service.users().messages().get(userId="me", id=msg["id"]).execute()
            )

            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt["payload"]
                headers = payload["headers"]

                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d["name"] == "Subject":
                        email_dict["subject"] = d["value"]
                    if d["name"] == "From":
                        email_dict["sender"] = self.extract_sender_info(d["value"])
                    if d["name"] == "Date":
                        date_dt = parsedate_to_datetime(d["value"])
                        date_utc = date_dt.astimezone(pytz.UTC)
                        email_dict["date_sent"] = date_utc.isoformat()

                email_list.append(email_dict)

            except Exception as e:
                print(f"An error occurred: {e}")
                pass
        print("Done")
        return email_list

    def delete_emails(self, message_ids: List[str]):
        for id in message_ids:
            self.service.users().messages().delete(userId="me", id=id).execute()
            print(f"Deleted message {id}.")
