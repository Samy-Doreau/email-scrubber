from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup
import base64

import os.path

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailAPI:
    def __init__(self):
        self.creds = None
        self.service = self.get_api_credentials()
        

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

            # Create a dictionary with the extracted info
            sender_info = {"sender_name": sender_name, "sender_email": sender_email}
            
        except :
            # Handle the case where the string format is incorrect
            
            sender_name = ""
            sender_email = input_str
        
        return sender_info

    def get_body_from_email_id(self, email_id):
        service = build("gmail", "v1", credentials=self.creds)
        txt = service.users().messages().get(userId="me", id=email_id).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt["payload"]
            headers = payload["headers"]

            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d["name"] == "Subject":
                    subject = d["value"]
                if d["name"] == "From":
                    sender = d["value"]

            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get("parts")[0]
            data = parts["body"]["data"]
            data = data.replace("-", "+").replace("_", "/")
            # decoded_data = base64.b64decode(data)

            # Now, the data obtained is in lxml. So, we will parse
            # it with BeautifulSoup library
            # soup = BeautifulSoup(decoded_data, "lxml")
            # body = soup.body()

            # Printing the subject, sender's email and message
            # print("Subject: ", subject)
            # print("From: ", sender)
            # print("Message: ", body)
            # print("\n")
        except:
            pass

    def get_emails(self):
        email_list = []
        service = build("gmail", "v1", credentials=self.creds)
        result = service.users().messages().list(maxResults=200, userId="me").execute()
        messages = result.get("messages")
        for msg in messages:
            email_dict = {}
            email_dict["message_id"] = msg["id"]
            # Get the message from its id
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()

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
                        email_dict["date_sent"] = d["value"]
                email_list.append(email_dict)

            except:
                pass

        return email_list
