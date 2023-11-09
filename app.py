from io import StringIO, BytesIO
import base64

from stqdm import stqdm

import streamlit as st

import utils


st.title('DogSportsRecords')
st.subheader('Events Data Uploader', divider='rainbow')


if utils.check_password():
    global option
    
    uploaded_file = st.file_uploader("Choose a file", type={"csv"})
    if uploaded_file is not None:
        df_processed = utils.process_file(uploaded_file)
        
        st.write(df_processed)
        button = st.button("Submit to Database")
        if button:
            st.write("Inserting new events to database")
            # utils.insert_to_database(df_processed)

            values = df_processed.to_dict(orient="records")
            for index in stqdm(range(0, len(df_processed), 10)):
                temp_values = values[index:index+10]
                utils.insert_to_database(temp_values)
    
            st.success("Completed!")
