import pandas as pd

def calculate_chain_email_stats(emails):
    # Calculate the proportion of chain emails that cannot be unsubscribed easily
    pass


def calculate_time_between_emails(df):

    # Convert date_sent to datetime
    df['date_sent'] = pd.to_datetime(df['date_sent'], errors='coerce')

    # Sort by sender_email and date_sent
    df = df.sort_values(['sender_email', 'date_sent'])

    # Calculate the time difference between consecutive emails for the same sender
    df['time_diff'] = df.groupby('sender_email')['date_sent'].diff()

    # Optional: Convert time difference to a more readable format (like days)
    df['time_diff_days'] = df['time_diff'].dt.days

    return df
