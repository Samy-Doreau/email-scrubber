from gmail_api import GmailAPI
from email_parser import EmailParser
from unsubscribe_service import UnsubscribeService
from analytics import create_email_agg_df, get_latest_email_id
import pandas as pd
import re
import curses


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


def list_selection(screen, items):
    selected = [False] * len(items)
    pos = 0  # current position

    while True:
        # Display the list
        screen.clear()
        for idx, item in enumerate(items):
            if pos == idx:
                line = "> {} [{}]".format(item, "X" if selected[idx] else " ")
            else:
                line = "  {} [{}]".format(item, "X" if selected[idx] else " ")
            screen.addstr(idx, 0, line)

        # Get the key pressed
        key = screen.getch()

        # Navigate or select
        if key == curses.KEY_UP and pos > 0:
            pos -= 1
        elif key == curses.KEY_DOWN and pos < len(items) - 1:
            pos += 1
        elif key == 32:  # SPACE key
            selected[pos] = not selected[pos]
        elif key == 10:  # ENTER key
            break

    # Return selected items
    return [item for idx, item in enumerate(items) if selected[idx]]


def extract_unsubscribe_url(input_string):
    # Decode bytes to string if necessary
    if isinstance(input_string, bytes):
        input_string = input_string.decode("utf-8")

    # Find all URLs that start with "https://" and end with "\r\n"
    urls = re.findall(r"https://[^\r\n]+", input_string)
    urls += re.findall(r"\[(https://[^\]]+)\]", input_string)

    # List of trigger words/phrases that might precede an unsubscribe link
    trigger_words = [
        "Unsubscribe",
        "please click here to unsubscribe. ",
        "to opt out",
        "to remove yourself",
    ]

    # Look for the URL immediately following any of the trigger words
    # Look for the URL immediately following any of the trigger words
    for trigger in trigger_words:
        for url in urls:
            if (
                trigger
                in input_string[
                    input_string.find(url) - len(trigger) - 10 : input_string.find(url)
                ]
            ):
                return url.strip("[]")

    # If no unsubscribe link is found, return None
    print(f"Could not find a link to unsubscribe within email body : \n {input_string}")
    return None


def main():
    sync_from_gmail_api_chx = ""
    # Initialize Gmail API
    gmail_api = GmailAPI()

    while sync_from_gmail_api_chx.lower() not in ["y", "n"]:
        sync_from_gmail_api_chx = (
            input("Sync emails from gmail api (y/n) (n) ? \n > ") or "n"
        )
    if sync_from_gmail_api_chx == "y":
        print("Fetching emails from Gmail API .. ", end="", flush=True)
        email_list = gmail_api.get_emails()
        results_df = convert_results_to_df(email_list=email_list)
        print("Done.")

        print("Saving results to file.. ", end="", flush=True)
        write_to_csv_with_pandas(df=results_df, csv_file="outputs/email_metadata.csv")

        print("Done.")

    # Read the data from a CSV file
    df = pd.read_csv("./outputs/email_metadata.csv")
    agg_df = create_email_agg_df(df)

    write_to_csv_with_pandas(df=agg_df, csv_file="outputs/agg_mail_data.csv")

    # target_sender_email_chx = (
    #     input("Enter email to unsub from : (news@email-blacks.co.uk) \n > ")
    #     or "news@email-blacks.co.uk"
    # )

    filtered_df = agg_df[agg_df["email_count"] >= 3]

    frequent_senders = filtered_df.iloc[:, 0].tolist()
    selected_senders = curses.wrapper(list_selection, frequent_senders)
    for sender in selected_senders:
        print(f"Processing sender {sender} .. ", end="", flush=True)
        sender_results = {}

        latest_email_id = get_latest_email_id(df=df, sender_email=sender)
        valid_email = latest_email_id["success"]
        if not valid_email:
            print(f"No email received from {sender}.\n")
        else:
            target_email_id = latest_email_id["message"]

            print(
                f"Fetching email body for message id : {target_email_id} .. ",
                end="",
                flush=True,
            )
            target_email_body = gmail_api.get_body_from_email_id(
                email_id=target_email_id
            )
            results_url = extract_unsubscribe_url(target_email_body)
            if results_url == None:
                sender_results["unsub_url_present"] = False
            else:
                sender_results["unsub_url_present"] = True
                unsubber = UnsubscribeService(results_url)
                unbsub_results = unsubber.attempt_unsubscribe()
                sender_results = {**sender_results, **unbsub_results}
                delete_email_choice = ""

                while delete_email_choice.lower() not in ["y", "n"]:
                    delete_email_choice = input("Delete emails ? (y/n) > ")

                if delete_email_choice == "y":
                    delete_target_emails = gmail_api.get_emails(
                        sender_email="news@email-blacks.co.uk"
                    )
                    delete_target_email_ids = [
                        msg["message_id"] for msg in delete_target_emails
                    ]
                    # gmail_api.delete_emails(delete_target_email_ids)
        print("Done.")


if __name__ == "__main__":
    main()
