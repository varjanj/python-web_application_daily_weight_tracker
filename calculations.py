import pandas as pd
from config import Config


def calculate_weekly_average(df: pd.DataFrame) -> float:
    """
    Calculates the rolling average from the last N days (defined in Config).
    Returns 0.0 if the DataFrame is empty.
    """
    # 1. Edge case: If the dataframe is empty, average is 0
    if df.empty:
        return 0.0

    # 2. Get the last N records (e.g., 7) from the bottom of the table
    # This automatically handles cases where there are fewer than 7 rows!
    last_entries = df.tail(Config.AVERAGE_DAYS_WINDOW)

    # 3. Calculate the sum of the 'Weight' column for these records
    total_weight = last_entries["Weight"].sum()

    # 4. Get the dynamic count of actual records (your variable X)
    actual_count = len(last_entries)

    # 5. Calculate the average
    average_weight = total_weight / actual_count

    # Round the result to 2 decimal places for clean display
    return round(average_weight, 2)

def calculate_block_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups the data into fixed blocks of N days (e.g., 7 days) based on row index.
    Calculates the average for each closed or currently open block.
    Returns a new DataFrame with Week numbers and their respective averages.
    """
    # If there is no data, return an empty DataFrame with expected columns
    if df.empty:
        return pd.DataFrame(columns=["Week", "Block Average"])

    # 1. Create a copy of DataFrame to avoid modifying the original data
    df_copy = df.copy()

    # 2. Reset index to ensure it goes from 0, 1, 2... sequentially
    df_copy = df_copy.reset_index(drop=True)

    # 3. Math trick: Determine the Week number for each row using integer division
    # Index 0-6 becomes Week 1, index 7-13 becomes Week 2, etc.
    df_copy["Week_Number"] = (df_copy.index // Config.AVERAGE_DAYS_WINDOW) + 1

    # 4. Group by the Week_Number and calculate the mean (average) of 'Weight'
    grouped = df_copy.groupby("Week_Number")["Weight"].mean().reset_index()

    # 5. Rename columns to look professional for the user
    grouped.columns = ["Week", "Block Average"]

    # Round the averages to 2 decimal places
    grouped["Block Average"] = grouped["Block Average"].round(2)

    return grouped