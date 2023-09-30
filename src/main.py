from gmail_api import GmailAPI
from email_parser import EmailParser
from unsubscribe_service import UnsubscribeService
from analytics import calculate_chain_email_stats


def main():
    # Initialize Gmail API
    gmail_api = GmailAPI()
    email_list = gmail_api.get_emails()
    print(email_list)
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
