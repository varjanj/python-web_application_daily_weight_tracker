import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- SUPABASE CLIENT INITIALIZATION ---
# Streamlit automatically fetches these credentials from .streamlit/secrets.toml
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)


def save_weight_entry(weight: float) -> bool:
    """
    Saves a new weight entry with the current timestamp into the Supabase cloud database.
    """
    try:
        # 1. Get current date and time formatted as YYYY-MM-DD HH:MM:SS
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Create a payload matching database snake_case columns
        data_to_insert = {"date": current_time, "weight": float(weight)}

        # 3. Insert the record into Supabase weight_entries table
        supabase.table("weight_entries").insert(data_to_insert).execute()
        return True

    except Exception as e:
        st.error(f"Error saving data to Supabase: {e}")
        return False


def load_weight_data() -> pd.DataFrame:
    """
    Loads the weight data from the Supabase cloud database and returns a Pandas DataFrame.
    Guarantees correct chronological ordering and uppercase column mapping.
    """
    try:
        # 1. Fetch data from Supabase ordered chronologically by date
        response = (
            supabase.table("weight_entries")
            .select("date, weight")
            .order("date", desc=False)
            .execute()
        )

        # 2. If the database table is empty, return an empty DataFrame with expected columns
        if not response.data:
            return pd.DataFrame(columns=["Date", "Weight"])

        # 3. Convert the fetched JSON data into a Pandas DataFrame
        df = pd.DataFrame(response.data)

        # 4. Rename columns from lowercase database format to expected uppercase format
        df = df.rename(columns={"date": "Date", "weight": "Weight"})

        # 5. Parse mixed datetime formats and sort chronologically
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
        df = df.dropna(subset=["Date", "Weight"])
        df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)

        # 6. Format to clean YYYY-MM-DD date object
        df["Date"] = df["Date"].dt.date
        df["Weight"] = df["Weight"].astype(float)

        return df

    except Exception as e:
        st.error(f"Error loading data from Supabase: {e}")
        return pd.DataFrame(columns=["Date", "Weight"])
    
def delete_last_entry() -> dict | None:
    """
    Deletes the most recent weight entry and returns its data (date and weight).
    Returns None if the database is empty.
    """
    try:
        # Fetch the ID, date, and weight of the last entry
        last_row = (
            supabase.table("weight_entries")
            .select("id, date, weight")
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        
        if not last_row.data:
            return None
            
        deleted_data = last_row.data[0]
        last_id = deleted_data["id"]
        
        # Delete the row matching the retrieved ID
        supabase.table("weight_entries").delete().eq("id", last_id).execute()
        
        # Return the data we just deleted so we can display it
        return deleted_data
    except Exception as e:
        st.error(f"Error deleting last entry: {e}")
        return None