import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies

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
      
final_results_path = '/workspaces/Eligibot/18367270-DS-6.json'
trials = []
with open(final_results_path, 'r') as file:
    final_results = json.load(file)
for trial_id, trial_data in final_results.items():
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