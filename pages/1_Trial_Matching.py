import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies, get_study_by_nct
status_legend = pd.DataFrame(
    {
        "Icon" : ['✅', '❌', '❓'],
        "Inclusion": ["Met", "Not Met", "Unknown"],
        "Exclusion": ["Not Met", "Met", "Unknown"],
    }
)
with st.sidebar:
    if st.button("Log out"):
        st.logout()
    
    st.subheader("Criteria Status")
    st.dataframe(status_legend, hide_index = True)
    
if not st.experimental_user.is_logged_in:
    st.warning('Please authenticate.')
    st.stop()
    
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

def map_condition_to_emoji(condition, is_exclusion = False):
    if is_exclusion:
        if condition == 'true':
            return '❌'
        elif condition == 'false':
            return '✅'
    else:
        if condition == 'true':
            return '✅'
        elif condition == 'false':
            return '❌'
    return '❓'

            
#Configurations for Retrieval
model = "ft:gpt-4o-2024-08-06:personal::B9xotD4N"
base_url = "https://clinicaltrials.gov/api/v2"
number_of_trials = 5
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
                if not skip_search:
                    query_url = build_ctgov_query(
                        base_url=base_url,
                        parsed_terms=key_terms,
                        page_size=number_of_trials,
                        output_format=output_format
                    )
                    st.subheader("Query URL for clinicaltrials.gov:")
                    st.write(query_url)

                    trials_json = query_and_save_results(query_url)
                    try:
                        with open('clinical_trials_results.json', "r") as f:
                            ctgov_data = json.load(f)

                        final_results = evaluate_patient_eligibility_for_studies(
                            patient_summary=user_input,
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

    if final_results:
        # Theme-aware text color
        theme_base = st.get_option("theme.base")
        is_dark = theme_base == "dark"
        text_color = "#ffffff" if is_dark else "#000000"

        st.markdown("""
        <style>
        .trial-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            width: 100%;
            margin-bottom: 0.5rem;
        }
        .circular-progress {
            width: 60px;
            height: 60px;
            position: relative;
        }
        .circular-progress svg {
            transform: rotate(-90deg);
        }
        .circular-progress circle {
            cx: 30;
            cy: 30;
            r: 26;
            stroke-width: 8;
            fill: none;
            stroke-linecap: round;
        }
        .circular-progress circle.bg {
            stroke: #ddd;
        }
        .circular-progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            font-size: 14px;
        }
        </style>
        """, unsafe_allow_html=True)

        trials = []
        for trial_id, trial_data in final_results.items():
            trials.append({
                "trial_id": trial_id,
                "total_score": trial_data['ranking']['total_score'],
                "inclusion_results": trial_data['inclusion_results'],
                "exclusion_results": trial_data['exclusion_results']
            })

        top_trials = sorted(trials, key=lambda x: x['total_score'], reverse=True)[:3]
        enriched_trials = []           # will hold (trial_dict, full_study_json)

        for trial in top_trials:
            nct_id = trial["trial_id"]
            full_study = get_study_by_nct(ctgov_data, nct_id)
            if full_study:                           # found it
                enriched_trials.append((trial, full_study))
            else:                                    # fall‑back (should be rare)
                enriched_trials.append((trial, {"error": "Study not found in ctgov_data"}))
        
        for trial, study_json in enriched_trials:
            trial_id = trial["trial_id"]
            total_score = trial["total_score"]
            formatted_score = "{:.1f}".format(total_score)
            final_score = min(max(total_score, 0), 100)
            stroke_color = choose_color(final_score)
            ident = study_json["protocolSection"]["identificationModule"]
            status = study_json["protocolSection"]["statusModule"]

            radius = 26
            circumference = 2 * 3.14159 * radius
            dasharray_final = (final_score / 100) * circumference
            dasharray_rest = circumference - dasharray_final
            keyframe_name = f"progress-animation-{trial_id}"

            st.markdown(f"""
            <style>
            .circular-progress-{trial_id} circle.fg {{
                stroke: #{stroke_color};
                stroke-dasharray: 0 {circumference};
                animation: {keyframe_name} 2s ease forwards;
            }}
            .circular-progress-{trial_id} .circular-progress-text {{
                color: {text_color};
            }}
            @keyframes {keyframe_name} {{
                to {{
                    stroke-dasharray: {dasharray_final} {dasharray_rest};
                }}
            }}
            </style>
            """, unsafe_allow_html=True)

            with stylable_container(
                key=f"{trial_id}",
                css_styles=f"""
                    {{
                        border: 2px solid #{stroke_color};
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        margin-bottom: 1rem;
                    }}
                """,
            ):
                header_html = f"""
                <div class="trial-header">
                  <h3 style="margin: 0;">Trial ID: {trial_id}</h3>
                  <div class="circular-progress">
                    <svg class="circular-progress-{trial_id}" viewBox="0 0 60 60">
                      <circle class="bg"></circle>
                      <circle class="fg"></circle>
                    </svg>
                    <div class="circular-progress-text">{int(final_score)}%</div>
                  </div>
                </div>
                """
                st.markdown(header_html, unsafe_allow_html=True)

                with st.expander("🔍  See Study Details", expanded=False):
                    try:
                        ident = study_json['protocolSection']['identificationModule']
                        status = study_json['protocolSection']['statusModule']
                        design = study_json['protocolSection']['designModule']
                        sponsor = study_json['protocolSection']['sponsorCollaboratorsModule']
                        desc = study_json['protocolSection']['descriptionModule']
                        elig = study_json['protocolSection']['eligibilityModule']
                        locs = study_json['protocolSection']['contactsLocationsModule'].get('locations', [])
                        contacts = study_json['protocolSection']['contactsLocationsModule'].get('centralContacts', [])

                        # Layout: two-column summary
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**📌  Title:** {ident.get('briefTitle', 'NA')}")
                            st.markdown(f"**🏥  Sponsor:** {sponsor['leadSponsor'].get('name', 'NA')}")
                            st.markdown(f"**📅  Start Date:** {status.get('startDateStruct', {}).get('date', 'NA')}")
                            st.markdown(f"**🎯  Enrollment:** {design['enrollmentInfo'].get('count', 'NA')} participants")
                        with col2:
                            study_type = design.get('studyType', 'NA')
                            st.markdown(f"**🧪  Study Type:** {study_type}")
                            st.markdown(f"**📈  Status:** {status.get('overallStatus', 'NA')}")
                            st.markdown(f"**📆  Estimated Completion:** {status.get('completionDateStruct', {}).get('date', 'NA')}")

                        # Eligibility summary
                        st.markdown("---")
                        st.markdown(f"**👥 Eligibility:** Ages {elig.get('minimumAge','NA')} – {elig.get('maximumAge','NA')}, Sex: {elig.get('sex','ALL')}")
                        st.markdown(f"**🩺 Conditions:** {', '.join(study_json['protocolSection']['conditionsModule'].get('conditions', []))}")
                        if keywords := study_json['protocolSection']['conditionsModule'].get('keywords'):
                            st.markdown(f"**🔍 Keywords:** {', '.join(keywords[:6])}")

                        # Location summary
                        if locs:
                            location_str = ", ".join(f"{l.get('city','')} ({l.get('country','')})" for l in locs)
                            st.markdown(f"**📍  Locations:** {location_str}")

                        # Main contact
                        if contacts:
                            contact = contacts[0]
                            contact_email = contact.get('email', 'NA')
                            st.markdown(f"**📬  Contact:** {contact.get('name', 'NA')} — [{contact_email}](mailto:{contact_email})")

                        # Score
                        st.markdown("---")
                        st.markdown(f"**⭐  Eligibility Score:** {formatted_score}")

                        # Inclusion Criteria
                        st.markdown("### Inclusion Criteria")
                        inclusion_data = [
                            [inc['criterion'], map_condition_to_emoji(inc['met'])]
                            for inc in trial["inclusion_results"]
                        ]
                        inclusion_df = pd.DataFrame(inclusion_data, columns=["Inclusion Criteria", "Met"])
                        st.dataframe(inclusion_df, hide_index=True, use_container_width=True)

                        # Exclusion Criteria
                        st.markdown("### Exclusion Criteria")
                        exclusion_data = [
                            [exc['criterion'], map_condition_to_emoji(exc['met'], is_exclusion=True)]
                            for exc in trial["exclusion_results"]
                        ]
                        exclusion_df = pd.DataFrame(exclusion_data, columns=["Exclusion Criteria", "Met"])
                        st.dataframe(exclusion_df, hide_index=True, use_container_width=True)

                    except Exception as e:
                        st.warning(f"Unable to load full study details: {e}")
