import pandas as pd

def calculate_chain_email_stats(emails):
    # Calculate the proportion of chain emails that cannot be unsubscribed easily
    pass


def create_email_agg_df(df):

    # Read the data from a CSV file
    df = pd.read_csv('./outputs/email_metadata.csv')

    # Convert 'date_sent' to datetime format
    df['date_sent'] = pd.to_datetime(df['date_sent'])

    # Sort the DataFrame by sender_email and date_sent
    df = df.sort_values(['sender_email', 'date_sent'], ascending=[True, False])

    # Calculate the time difference between consecutive emails for the same sender
    df['time_diff'] = df.groupby('sender_email')['date_sent'].diff()

    # Convert time difference to a more readable format (like days)
    df['time_diff_days'] = df['time_diff'].dt.days

    # Create a DataFrame for email count per sender
    count_df = df.groupby('sender_email', as_index=False)['date_sent'].count()
    count_df.rename(columns={'date_sent': 'email_count'}, inplace=True)

    # Drop rows where 'time_diff' is NaT or NaN
    filtered_df = df.dropna(subset=['time_diff'])

    # Group by sender_email and calculate the average time difference in days
    agg_df = filtered_df.groupby('sender_email', as_index=False).agg({
        'time_diff_days': 'mean'  # mean time difference
    })

    # Rename columns for clarity
    agg_df.rename(columns={'time_diff_days': 'average_time_diff_days'}, inplace=True)

    # Merge the aggregated DataFrame with the count DataFrame
    final_df = pd.merge(agg_df, count_df, on='sender_email')
    final_df = final_df.sort_values(by = ['email_count'], ascending=False)

    # Display the final DataFrame
    return final_df


def get_latest_email_id(df, sender_email):
    # First, filter the DataFrame to only include rows where sender_email matches the input
    filtered_df = df[df['sender_email'] == sender_email]
    
    # If no records are found, return a message
    if filtered_df.empty:
        return {'success':False, 'message':"No emails found from this sender."}
    
    # Then, sort the DataFrame by 'date_sent' in descending order
    sorted_df = filtered_df.sort_values('date_sent', ascending=False)
    
    # Get the 'email_id' of the first row, which will be the latest email
    latest_email_id = sorted_df.iloc[0]['message_id']
    
    return {'success':True, 'message':latest_email_id}

