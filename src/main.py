from gmail_api import GmailAPI
from email_parser import EmailParser
from unsubscribe_service import UnsubscribeService
from analytics import calculate_chain_email_stats, calculate_time_between_emails
import pandas as pd

def convert_results_to_df(email_list):
    # Flatten nested dictionary
    flattened_email_list = []
    for email in email_list:
        flattened_email = email.copy()  # Make a shallow copy
        sender_info = flattened_email.pop(
            "sender"
        )  # Remove and return the 'sender' dict
        flattened_email.update(sender_info)  # Merge the nested dictionary into the copy
        flattened_email_list.append(flattened_email)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(flattened_email_list)

    return df


def write_to_csv_with_pandas(df, csv_file):
    df.to_csv(csv_file, index=False)

    return df


def main():
    # Initialize Gmail API
    gmail_api = GmailAPI()
    email_list = gmail_api.get_emails()
    results_df = convert_results_to_df(email_list=email_list)


    write_to_csv_with_pandas(
        df=results_df, csv_file="outputs/email_metadata.csv"
    )
    
    # messages = gmail_api.get_mailing_list_emails()

    # # Parse Emails
    # email_parser = EmailParser(messages)
    # emails = email_parser.parse_emails()

    # # Unsubscribe
    # unsub_service = UnsubscribeService(emails)
    # unsub_service.attempt_unsubscribe()

    # # Analytics
    # calculate_chain_email_stats(emails)


if __name__ == "__main__":
    main()
