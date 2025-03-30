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
      
final_results = '18367270-DS-6.json'

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
            
            st.subheader("Inclusion Criteria:")
            for inclusion in trial["inclusion_results"]:
                st.write(f"- {inclusion['criterion']} (Met: {inclusion['met']})")
                
            st.subheader("Exclusion Criteria:")
            for exclusion in trial["exclusion_results"]:
                st.write(f"- {exclusion['criterion']} (Met: {exclusion['met']})")
            
            st.markdown('</div>', unsafe_allow_html=True)
