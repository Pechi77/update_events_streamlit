import os

import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

import constants
# Load the .env file into the environment
load_dotenv()

HOST = os.getenv("HOST")


def check_password():
    """Returns `True` if the user had the correct password."""
    # print(st.secrets)
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["passwords"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    
def process_file(file):

    def grouped_operation(grouped_df):
        last_row = grouped_df.iloc[-1]  # Get the last row of the group
        grouped_df["closing_day"] = last_row["start_day"]
        grouped_df["closing_date"] = last_row["start_date"]
        return grouped_df.iloc[0, :]
    
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=constants.RENAME_DICT)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df = df.sort_values(by=["hostclub", "start_date"])
    df["hostclub"] = df["hostclub"].apply(str.strip)
    df = df.drop_duplicates(subset=["hostclub", "start_date"])
    df.reset_index(drop=True, inplace=True)
    df_final = df.groupby(["hostclub", df.groupby('hostclub')["start_date"].diff().bfill()], as_index=False).apply(grouped_operation)
    df_final["entry_fee"] = df_final["entry_fee"].fillna("$").apply(lambda row: row.strip("$"))
    df_final["entry_fee"] = df_final["entry_fee"].replace({"":0})
    df_final["entry_fee"] = df_final["entry_fee"].astype(int)
    df_final["start_date"] = df_final["start_date"].dt.strftime("%Y-%m-%d")
    df_final["closing_date"] = df_final["closing_date"].dt.strftime("%Y-%m-%d")
    df_final["timezone"] = df_final["timezone"].ffill()
    return df_final

def insert_to_database(data):

    try:
        response = requests.post(HOST+"/events", json=data)
        print(response.status_code)
        print("response")
    except Exception as e:
        print(e)
        import traceback
        print(traceback.format_exc())
