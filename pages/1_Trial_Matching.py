import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 

st.title('Trial Matching')



with st.container():
    st.write("Step 1: Please enter or upload your information.")

    # Field to accept free text input
    free_text = st.text_area("Enter some free text:")

    # Option to upload a file (CSV, TXT)
    uploaded_file = st.file_uploader("Upload a CSV or TXT file", type=["csv", "txt"])

trials = [
    {"trial": "Trial1", "info": "This will contain information, ranking, risk and link to trial"},
    {"trial": "Trial2", "info": "This will contain information, ranking, risk and link to trial"},
    {"trial": "Trial3", "info": "This will contain information, ranking, risk and link to trial."}
]

# Create an expander for each trial
for trial in trials:
    with st.container():
        with st.expander(trial["trial"]):
            st.write(trial["info"])
    


# Process the uploaded file (if any)
if uploaded_file is not None:
    # If the file is a CSV
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.subheader("CSV File Content:")
        st.write(df)
    
    # If the file is a TXT
    elif uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
        st.subheader("TXT File Content:")
        st.write(text)
