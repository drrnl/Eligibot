import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies

#Setting OpenAi Key
openai.api_key = st.secrets["openai"]["api_key"]

def choose_color(total_score):
      if total_score >= 90:
            return 'B2E3AF'
      elif total_score >= 80:
            return 'D6FAC3'
      elif total_score >= 70:
            return 'E9FFCF'
      elif total_score >= 60:
            return 'ECBC68'
      else:
            return 'EDE4CA'
      
st.title('Trial Matching')


#Configurations for Retrieval
model = "ft:gpt-4o-2024-08-06:personal::B9xotD4N"
base_url = "https://clinicaltrials.gov/api/v2"
number_of_trials = 10
skip_search = False  # Set to True to skip calling the clinicaltrials.gov API
output_format = "json"

user_input = None

with st.container():
    st.write("Step 1: Please enter or upload your information.")

    # Field to accept free text input
    free_text = st.text_area("Enter some free text:")
    if free_text:
        user_input = free_text

    
    # Option to upload a file (CSV, TXT)
    uploaded_file = st.file_uploader("Upload a CSV or TXT file", type=["csv", "txt"])
        
    if uploaded_file:
        user_input = uploaded_file.read().decode("utf-8")
        st.write(f"File {uploaded_file.name} uploaded successfully.")
    else:
        st.write("Please upload a file.")
    

with st.container():
    st.write('')
    st.write("Step 2: Click to begin matching!")
    start_button = st.button("Start Matching", use_container_width = True)

_= '''
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
'''
if start_button:
    final_results = None
    with st.spinner("Matching in progress..."):
        try:
            key_terms_json_str = extract_key_terms(user_input, model=model)
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
                    st.subheader("Query URL for clinicaltrials.gov:")
                    st.write(query_url)

                    # Save retrieval JSON output
                    trials_json = query_and_save_results(query_url)
                    try:
                        with open('clinical_trials_results.json', "r") as f:
                            ctgov_data = json.load(f)

                        final_results = evaluate_patient_eligibility_for_studies(
                            patient_summary= user_input,
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

    trials = []
    for trial_id, trial_data in final_results.items():
        trials.append({
            "trial_id": trial_id,
            "total_score": trial_data['ranking']['total_score'],
            "inclusion_results": trial_data['inclusion_results'],
            "exclusion_results": trial_data['exclusion_results']
        })

    # Sort the trials by total_score in descending order
    # sorted_trials = sorted(trials, key=lambda x: x['total_score'], reverse=True)

    # Get top 3 trials (or fewer if there are less than 3 trials)
    top_trials = trials[:3]

    for trial in top_trials:
        # Get the color based on the total_score
        container_color = choose_color(trial["total_score"])
        formatted_score = "{:.1f}".format(trial["total_score"])

    # Apply the color to the container using the markdown method
        with stylable_container(
            key = f"{trial['trial_id']}",

            css_styles = f"""
                    {{
                        border: 2px solid #{container_color};
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px)
                    }}  
            """,
        ):
        
            # Expander with trial_id and total_score in the title
            with st.expander(f"Trial ID: {trial['trial_id']} | Eligibility Score: {formatted_score}"):
                st.markdown(f'<div class="container_{trial["trial_id"]}">', unsafe_allow_html=True)

            # Display trial details (inclusion, exclusion, and score)
                st.write(f"**Eligibility Score**: {formatted_score}")

            # Create DataFrame for Inclusion Criteria
                inclusion_data = []
                for inclusion in trial["inclusion_results"]:
                    inclusion_data.append([inclusion['criterion'], inclusion['met']])
            
                inclusion_df = pd.DataFrame(inclusion_data, columns=["Inclusion Criteria", "Met"])
                st.write("### Inclusion Criteria")
                st.dataframe(inclusion_df, hide_index=True) 

            # Create DataFrame for Exclusion Criteria
                exclusion_data = []
                for exclusion in trial["exclusion_results"]:
                    exclusion_data.append([exclusion['criterion'], exclusion['met']])
            
                exclusion_df = pd.DataFrame(exclusion_data, columns=["Exclusion Criteria", "Met"])
                st.write("### Exclusion Criteria")
                st.dataframe(exclusion_df, hide_index=True) 

                st.markdown('</div>', unsafe_allow_html=True)           

