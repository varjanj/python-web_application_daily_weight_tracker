import os
import pandas as pd
from datetime import datetime
from config import Config

def save_weight_entry(weight: float):
    """
    Saves a new weight entry with the current timestamp into the CSV file.
    """
    # 1. Get current date and time formatted as YYYY-MM-DD HH:MM:SS
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Create a clean dictionary where keys are columns and values are lists
    new_data = {"Date": [current_time], "Weight": [weight]}

    # 3. Convert the dictionary into a Pandas DataFrame
    df = pd.DataFrame(new_data)

    # 4. Check if the file already exists to decide if we need headers
    file_exists = os.path.exists(Config.DATA_FILE_NAME)

    # 5. Append data to CSV (index=False ensures we don't save row numbers)
    df.to_csv(
        Config.DATA_FILE_NAME,
        mode="a",
        header=not file_exists,
        index=False,
        sep=";",
    )

def load_weight_data() -> pd.DataFrame:
    """
    Loads the weight data from the CSV file and returns a Pandas DataFrame.
    If the file does not exist, returns an empty DataFrame with expected columns.
    """
    # 1. Check if the file exists
    if not os.path.exists(Config.DATA_FILE_NAME):
        return pd.DataFrame(columns=["Date", "Weight"])

    # 2. Load the CSV file
    df = pd.read_csv(Config.DATA_FILE_NAME, sep=";")

    # 3. Clean the 'Date' column to show ONLY dates, without time
    # First, convert text to Pandas datetime object, then extract just the date
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    return df