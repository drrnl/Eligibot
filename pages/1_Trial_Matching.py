import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies

#Setting OpenAi Key
openai.api_key = st.secrets["openai"]["api_key"]


st.title('Trial Matching')


#Configurations for Retrieval
model = "ft:gpt-4o-2024-08-06:personal::B9xotD4N"
base_url = "https://clinicaltrials.gov/api/v2"
number_of_trials = 10
skip_search = False  # Set to True to skip calling the clinicaltrials.gov API
output_format = "json"

text_to_process = None

with st.container():
    st.write("Step 1: Please enter or upload your information.")

    # Field to accept free text input
    free_text = st.text_area("Enter some free text:")
    
    # Option to upload a file (CSV, TXT)
    upload_button = st.button("Uploaded file")
    
    uploaded_file = None
    if upload_button:
        uploaded_file = st.file_uploader("Upload a CSV or TXT file", type=["csv", "txt"])
        if uploaded_file is not None:
            st.write(f"File {uploaded_file.name} uploaded successfully.")
        else:
            st.write("Please upload a file.")
    


with st.container():
    st.write('')
    st.write("Step 2: Click to begin matching!")
    start_button = st.button("Start Matching", use_container_width = True)

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

if start_button:
    final_results = None
    with st.spinner("Matching in progress..."):
        try:
            key_terms_json_str = extract_key_terms(free_text, model=model)
            try:
                key_terms = key_terms_json_str
                st.subheader("Extracted Key Terms:")
                st.json(key_terms)
                # Optionally, build query URL and run search if desired.
                if not skip_search:
                    query_url = build_ctgov_query(
                        base_url=base_url,
                        parsed_terms=key_terms,
                        page_size=number_of_trials,
                        output_format=output_format
                    )
                    st.write("Query URL for clinicaltrials.gov:")
                    st.write(query_url)

                    # Save retrieval JSON output
                    trials_json = query_and_save_results(query_url)
                    try:
                        with open('clinical_trials_results.json', "r") as f:
                            ctgov_data = json.load(f)

                        final_results = evaluate_patient_eligibility_for_studies(
                            patient_summary=free_text,
                            ctgov_data=ctgov_data,
                            model="gpt-4o-mini"
                        )
                    except Exception as e:
                        st.error(f"Error matching criteria: {e}")
            except json.JSONDecodeError:
                st.error("The model did not return valid JSON. Raw output:")
                st.text(key_terms_json_str)
        except Exception as e:
            st.error(f"Error extracting key terms: {e}")
   
    with open(final_results, 'r') as file:
        data = json.load(file)

    trials = []
    for trial_id, trial_data in data.items():
        trials.append({
            "trial_id": trial_id,
            "total_score": trial_data['ranking']['total_score'],
            "inclusion_results": trial_data['inclusion_results'],
            "exclusion_results": trial_data['exclusion_results']
        })

    # Sort the trials by total_score in descending order
    sorted_trials = sorted(trials, key=lambda x: x['total_score'], reverse=True)

    # Get top 3 trials (or fewer if there are less than 3 trials)
    top_trials = sorted_trials[:3]           