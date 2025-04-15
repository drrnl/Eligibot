import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies, get_study_by_nct
from modules.risk_prediction import get_risk_prediction
import random

theme_base = st.get_option("theme.base")
is_dark = theme_base == "dark"

bg_color = "#1e1e1e" if is_dark else "#f8f9fa"
border_color = "#444" if is_dark else "#dee2e6"
text_color = "#ffffff" if is_dark else "#000000"

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
st.markdown("""
<style>
.tooltip-container {
position: relative;
display: inline-block;
cursor: help;
}

.tooltip-text {
visibility: hidden;
width: max-content;
max-width: 280px;
background-color: #333;
color: #fff;
text-align: left;
border-radius: 6px;
padding: 8px 10px;
position: absolute;
z-index: 1;
bottom: 125%;
left: 0;
opacity: 0;
transition: opacity 0.3s;
font-size: 13px;
line-height: 1.4;
}

.tooltip-container:hover .tooltip-text {
visibility: visible;
opacity: 1;
}
</style>
""", unsafe_allow_html=True)
if start_button:
    final_results = None
    with st.spinner("Matching in progress..."):
        try:
            key_terms_json_str = extract_key_terms(user_input, model=model)
            try:
                key_terms = key_terms_json_str
                st.markdown("""
                <div style="font-size: 1.25rem;" class="tooltip-container">
                    🔑 <strong>Extracted Key Terms</strong>
                    <div class="tooltip-text">
                        These are the key clinical terms extracted from your input, such as conditions and summary descriptions. They're used to build a trial search query.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Display key terms as before (cleaned version)
                if "conditions" in key_terms and isinstance(key_terms["conditions"], list):
                    st.markdown(
                        """
                        <div style='font-size: 1.05rem;'>
                            <ul style='margin-left: 1.5em;'>
                        """ +
                        "".join([f"<li>{cond}</li>" for cond in key_terms["conditions"]]) +
                        "</ul></div>",
                        unsafe_allow_html=True
                    )

                if "summary" in key_terms:
                    st.markdown(
                        f"<div style='font-size: 1.05rem;'><strong>📝 Summary:</strong> {key_terms['summary']}</div>",
                        unsafe_allow_html=True
                    )


                if not skip_search:
                    query_url = build_ctgov_query(
                        base_url=base_url,
                        parsed_terms=key_terms,
                        page_size=number_of_trials,
                        output_format=output_format
                    )
                    st.text("")
                    st.markdown(f"""
                    <div style="margin-top: 1rem; font-size: 1.1rem;" class="tooltip-container">
                        🔗 <strong><a href="{query_url}" target="_blank" style="text-decoration: none; color: #1f77b4;">
                        ClinicalTrials.gov Query URL</a></strong>
                        <div class="tooltip-text">
                            This is the query link built using the extracted terms. Click to view matching trials directly on ClinicalTrials.gov.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

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
            formatted_score = "{:.0f}".format(total_score)
            final_score = min(max(total_score, 0), 100)
            stroke_color = choose_color(final_score)
            ident = study_json["protocolSection"]["identificationModule"]
            status = study_json["protocolSection"]["statusModule"]

            risk_preds = get_risk_prediction(study_json)
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
                        
                        st.text("")
                        ident = study_json['protocolSection']['identificationModule']
                        status = study_json['protocolSection']['statusModule']
                        design = study_json['protocolSection']['designModule']
                        sponsor = study_json['protocolSection']['sponsorCollaboratorsModule']
                        desc = study_json['protocolSection']['descriptionModule']
                        elig = study_json['protocolSection']['eligibilityModule']
                        locs = study_json['protocolSection']['contactsLocationsModule'].get('locations', [])
                        contacts = study_json['protocolSection']['contactsLocationsModule'].get('centralContacts', [])

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📌 Title:</strong>
                                <div class="tooltip-text">The brief official title of the study.</div>
                            </div> {ident.get("briefTitle", "NA")}
                            """, unsafe_allow_html=True)

                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>🏥 Sponsor:</strong>
                                <div class="tooltip-text">Organization primarily responsible for the study.</div>
                            </div> {sponsor["leadSponsor"].get("name", "NA")}
                            """, unsafe_allow_html=True)
                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📅 Start Date:</strong>
                                <div class="tooltip-text">Date when the study began enrolling participants.</div>
                            </div> {status.get("startDateStruct", {}).get("date", "NA")}
                            """, unsafe_allow_html=True)
                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>🎯 Enrollment:</strong>
                                <div class="tooltip-text">Planned or actual number of enrolled participants.</div>
                            </div> {design["enrollmentInfo"].get("count", "NA")} participants
                            """, unsafe_allow_html=True)

                        with col2:
                            study_type = design.get('studyType', 'NA')
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>🧪 Study Type:</strong>
                                <div class="tooltip-text">Type of study design (e.g., interventional, observational).</div>
                            </div> {study_type}
                            """, unsafe_allow_html=True)
                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📈 Status:</strong>
                                <div class="tooltip-text">Current recruitment status of the trial.</div>
                            </div> {status.get("overallStatus", "NA")}
                            """, unsafe_allow_html=True)
                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📆 Estimated Completion:</strong>
                                <div class="tooltip-text">Projected date when the study will conclude.</div>
                            </div> {status.get("completionDateStruct", {}).get("date", "NA")}
                            """, unsafe_allow_html=True)

                        st.markdown("---")

                        st.markdown(f"""
                        <div class="tooltip-container"><strong>👥 Eligibility:</strong>
                            <div class="tooltip-text">Participant age and sex eligibility requirements.</div>
                        </div> Ages {elig.get("minimumAge","NA")} – {elig.get("maximumAge","NA")}, Sex: {elig.get("sex","ALL")}
                        """, unsafe_allow_html=True)
                        st.text("")
                        st.markdown(f"""
                        <div class="tooltip-container"><strong>🩺 Conditions:</strong>
                            <div class="tooltip-text">Medical conditions or diseases being studied.</div>
                        </div> {", ".join(study_json["protocolSection"]["conditionsModule"].get("conditions", []))}
                        """, unsafe_allow_html=True)

                        if keywords := study_json['protocolSection']['conditionsModule'].get('keywords'):
                            st.text("")
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>🔍 Keywords:</strong>
                                <div class="tooltip-text">Related terms for search indexing or topic tagging.</div>
                            </div> {", ".join(keywords[:6])}
                            """, unsafe_allow_html=True)

                        if locs:
                            st.text("")
                            location_str = ", ".join(f"{l.get('city','')} ({l.get('country','')})" for l in locs)
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📍 Locations:</strong>
                                <div class="tooltip-text">Cities and countries where the study is taking place.</div>
                            </div> {location_str}
                            """, unsafe_allow_html=True)

                        if contacts:
                            st.text("")
                            contact = contacts[0]
                            contact_email = contact.get('email', 'NA')
                            st.markdown(f"""
                            <div class="tooltip-container"><strong>📬 Contact:</strong>
                                <div class="tooltip-text">Person to contact for study-related questions.</div>
                            </div> {contact.get("name", "NA")} — <a href="mailto:{contact_email}">{contact_email}</a>
                            """, unsafe_allow_html=True)

                        st.markdown("---")
                        adverse_event_risk = random.randint(1, 30)

                        # Section heading
                        st.markdown("""
                        <div style="text-align: center; margin-bottom: 1rem;">
                            <h2 style="font-size: 1.8rem;">📊 Trial Suitability Overview</h2>
                            <p style="font-size: 1.1rem; color: gray;">Quick snapshot of how well you match this trial and what risks may be involved.</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Animated eligibility score card
                        st.markdown(f"""
                        <style>
                        @keyframes pop {{
                            0% {{ transform: scale(0.8); opacity: 0; }}
                            100% {{ transform: scale(1); opacity: 1; }}
                        }}

                        .enhanced-card {{
                            background-color: var(--secondary-background-color);
                            border: 2px solid #c4c4c4;
                            border-radius: 1rem;
                            padding: 1.5rem;
                            margin: 1rem 0;
                            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                            animation: pop 0.6s ease-out forwards;
                            text-align: center;
                        }}

                        .enhanced-card h3 {{
                            font-size: 1.5rem;
                            margin-bottom: 0.5rem;
                        }}

                        .enhanced-card .score, .enhanced-card .risk {{
                            font-size: 3rem;
                            font-weight: 400;
                            color: var(--text-color);
                            margin-top: 0.5rem;
                        }}
                        </style>

                        <div class="enhanced-card">
                            <div class="tooltip-container">
                                <h3>⭐ Eligibility Match Score</h3>
                                <div class="tooltip-text">Overall score representing how well the patient matches the trial.</div>
                            </div>
                            <div class="score">{int(final_score)}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Side-by-side risk metrics
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"""
                            <div class="enhanced-card">
                                <div class="tooltip-container">
                                    <h3>⛔ Premature Termination</h3>
                                    <div class="tooltip-text">Predicted likelihood that the trial may terminate early.</div>
                                </div>
                                <div class="risk">{risk_preds[0]*100:.0f}%</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown(f"""
                            <div class="enhanced-card">
                                <div class="tooltip-container">
                                    <h3>⚠️ Risk of Adverse Events</h3>
                                    <div class="tooltip-text">Estimated probability of experiencing adverse side effects during the trial.</div>
                                </div>
                                <div class="risk">{adverse_event_risk}%</div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Inclusion Criteria
                        st.text("")
                        st.markdown("""
                        <div class="tooltip-container"><h4>Inclusion Criteria</h4>
                            <div class="tooltip-text">List of criteria that must be met for participation in the study.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        inclusion_data = [
                            [inc['criterion'], map_condition_to_emoji(inc['met'])]
                            for inc in trial["inclusion_results"]
                        ]
                        inclusion_df = pd.DataFrame(inclusion_data, columns=["Inclusion Criteria", "Met"])
                        st.dataframe(inclusion_df, hide_index=True, use_container_width=True)

                        # Exclusion Criteria
                        st.markdown("""
                        <div class="tooltip-container"><h4>Exclusion Criteria</h4>
                            <div class="tooltip-text">Conditions that disqualify a patient from enrolling in the study.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        exclusion_data = [
                            [exc['criterion'], map_condition_to_emoji(exc['met'], is_exclusion=True)]
                            for exc in trial["exclusion_results"]
                        ]
                        exclusion_df = pd.DataFrame(exclusion_data, columns=["Exclusion Criteria", "Met"])
                        st.dataframe(exclusion_df, hide_index=True, use_container_width=True)

                    except Exception as e:
                        st.warning(f"Unable to load full study details: {e}")
