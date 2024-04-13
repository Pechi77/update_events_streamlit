from io import StringIO, BytesIO
import base64

import pandas as pd
from stqdm import stqdm

import streamlit as st

import utils


st.title('DogSportsRecords')

option = st.selectbox("Select Uploader", ["Events Data Uploader", "Club Directory Data Uploader"])
if utils.check_password():
    title, type = utils.get_subheader(option)
    st.subheader(title, divider='rainbow')
    uploaded_file = st.file_uploader("Choose a file", type={"csv"})
    if uploaded_file is not None:
        df_processed = utils.process_file(uploaded_file, option)
        st.write(df_processed)
        if "event_address" in df_processed:
            df_processed = df_processed[df_processed["event_address"].ne("mocked_event_address")]
        button = st.button("Submit to Database")
        download_button = st.download_button("Download consolidated file", df_processed.to_csv(index=False).encode('utf-8'), "consolidated.csv", "text/csv", help="Download the consolidated file")
        if button:
            st.write("Inserting/Updating records to database")
            values = df_processed.to_dict(orient="records")
            for index in stqdm(range(0, len(df_processed), 10)):
                temp_values = values[index:index+10]
                utils.insert_to_database(temp_values, type)

            st.success("Completed!")
            
    
    
# if option == "Events Data Uploader":
#     if utils.check_password():
#         st.subheader('Events Data Uploader', divider='rainbow')
#         uploaded_file = st.file_uploader("Choose a file", type={"csv"})
#         if uploaded_file is not None:
#             df_processed = utils.process_file(uploaded_file)
#             st.write(df_processed)
#             button = st.button("Submit to Database")
#             download_button = st.download_button("Download consolidated file", df_processed.to_csv(index=False).encode('utf-8'), "consolidated.csv", "text/csv", help="Download the consolidated file")

#             if button:
#                 st.write("Inserting new events to database")
#                 values = df_processed.to_dict(orient="records")
#                 for index in stqdm(range(0, len(df_processed), 10)):
#                     temp_values = values[index:index+10]
#                     utils.insert_to_database(temp_values)

#                 st.success("Completed!")

elif option == "Club Directory Data Uploader":
    # Add code for Club Data Uploader functionality here
    if utils.check_password():
        st.subheader('Club Directory Data Uploader', divider='rainbow')
        uploaded_file = st.file_uploader("Choose a file", type={"csv"})
        if uploaded_file is not None:
            ...
                

# st.subheader('Events Data Uploader', divider='rainbow')


# if utils.check_password():
    
#     uploaded_file = st.file_uploader("Choose a file", type={"csv"})
#     if uploaded_file is not None:
#         df_processed = utils.process_file(uploaded_file)
#         st.write(df_processed)
#         button = st.button("Submit to Database")
#         download_button = st.download_button("Download consolidated file", df_processed.to_csv(index=False).encode('utf-8'), "consolidated.csv", "text/csv", help="Download the consolidated file")
        
#         if button:
#             st.write("Inserting new events to database")
#             # utils.insert_to_database(df_processed)

#             values = df_processed.to_dict(orient="records")
#             for index in stqdm(range(0, len(df_processed), 10)):
#                 temp_values = values[index:index+10]
#                 utils.insert_to_database(temp_values)
    
#             st.success("Completed!")
