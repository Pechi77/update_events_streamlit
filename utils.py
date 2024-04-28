import os

import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

import constants
# Load the .env file into the environment
load_dotenv()


HOST = st.secrets["server"][constants.server]



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


def read_file(file):
    try:
        df = pd.read_csv(file)
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="iso8859")
    return df

def process_events_file(file):
    CHILD_EVENTS_DICT = {}
    def grouped_operation(grouped_df):
    
        last_row = grouped_df.iloc[-1]  # Get the last row of the group
        grouped_df["closing_day"] = last_row["start_day"]
        grouped_df["closing_date"] = last_row["start_date"]
        parent_event = grouped_df["event_number"].iloc[0]
        CHILD_EVENTS_DICT[parent_event] = grouped_df["event_number"].astype(str).str.cat(sep=",")
        return grouped_df.iloc[0, :]
    
    
    df = read_file(file)
        
    df.columns = df.columns.str.strip()
    df = df.rename(columns=constants.RENAME_DICT)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df = df.sort_values(by=["hostclub", "start_date"])
    df["hostclub"] = df["hostclub"].apply(str.strip)
    # df = df.drop_duplicates(subset=["hostclub", "start_date"])
    # df.reset_index(drop=True, inplace=True)
    # df_final = df.groupby(["hostclub", df.groupby('hostclub')["start_date"].diff().bfill()], as_index=False).apply(grouped_operation)
    df_final = df.groupby(["hostclub", df.groupby('hostclub')["start_date"].diff().dt.days.bfill().replace({1:0}).ne(0).cumsum()], as_index=False).apply(grouped_operation)
    df_final["entry_fee"] = df_final["entry_fee"].fillna("$").apply(lambda row: row.strip("$"))
    df_final["entry_fee"] = df_final["entry_fee"].replace({"":0})
    df_final["entry_fee"] = df_final["entry_fee"].astype(float)
    df_final["start_date"] = df_final["start_date"].dt.strftime("%Y-%m-%d")
    df_final["closing_date"] = df_final["closing_date"].dt.strftime("%Y-%m-%d")
    df_final["timezone"] = df_final["timezone"].ffill()
    df_final["event_type"] = df_final["event_type"].str.strip()
    df_final["chairperson"] = df_final["chairperson"].fillna("")
    df_final["chairperson"] = df_final["chairperson"].fillna("")
    df_final["chairperson_email"] = df_final["chairperson_email"].fillna("")
    df_final["chairperson_phone"] = df_final["chairperson_phone"].fillna("")
    df_final["child_events"] = df_final["event_number"].map(CHILD_EVENTS_DICT)
    df_final["event_type"] = df_final["event_type"].replace({"FCAT":"FastCAT"})
    if df_final.shape[0] == 1:
        # Add a new row with mocked values for all columns
        new_row = {
            'hostclub': 'mocked hostclub, will not insert into database', 
            'event_number': 1234567890, 
            'event_address': 'mocked_event_address', 
            'city': 'mocked_city',
            'state':'mocked_state',
            'start_day': 'Monday', 
            'start_date': '2024-01-01', 
            'timezone': 'Central', 
            'chairperson': 'Denise',
            'chairperson_phone': '9876543210', 
            'chairperson_email': 'john_doe@abc.com', 
            'eligible_breeds': 'Eligible breeds',
            'entry_fee': 25.0, 
            'event_type': 'FastCAT', 
            'closing_day': 'Monday', 
            'closing_date': '2024-01-01',
            'child_events': '1234567890'
            # Add more columns and mocked values as needed
        }
        new_df = pd.DataFrame(new_row, index=[1])
        df_final = pd.concat([df_final, new_df], ignore_index=True)
    return df_final


def process_club_file(file):
    df = read_file(file)
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns=constants.CLUB_RENAME_DICT)
    df["id"] = df["clubNumber"]
    
    return df


def process_file(file, option):
    if option == "Events Data Uploader":
        return process_events_file(file)
    else:
        return process_club_file(file)
        
    


def insert_to_database(data, endpoint):
    try:
        response = requests.post(HOST+f"/{endpoint}", json=data)
        print(response.status_code)
        print("response")
        print(HOST)
        print(response.text)
        if response.status_code != 200:
            breakpoint()
    except Exception as e:
        print(e)

        # import traceback
        # print(traceback.format_exc())
        # import json
        # print(json.dumps(data))
        print("*"*15)


def get_subheader(option):
    if option == "Events Data Uploader":
        return 'Events Data Uploader', "events"
    elif option == "Club Directory Data Uploader":
        return 'Club Directory Data Uploader', "clubs_bulk"
    else:
        return 'Select Uploader', _