import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import os
import base64

    
st.title("Transparency")

st.subheader("Project Architecture")

st.image(os.path.join("images","project_architecture.png"))

st.subheader("User Inputs")
st.write("You can put any information you want into the app. However, we recommend using clinical doctor notes, which provides complete information for the best results. Eligibot will internally break down medical jargon and acronyms to find the best match.")

st.subheader("Data Sources")
st.write("We use data from MIMIC-IV and ClinicalTrials.gov. MIMIC IV allows us to process detailed clinical notes of patients to understand, in-depth, the histories and attributes of our patients.")

st.subheader("The Retrieval System")
st.write("Our retrieval system analyzes your medical summary to extract key symptoms, conditions, and diagnoses. It leverages advanced natural language processing techniques that have been fine-tuned on a curated subset of real clinical notes from the MIMIC-IV database to accurately identify relevant medical information. This extracted data is then used to search ClinicalTrials.gov for actively recruiting clinical trials, ensuring that you receive highly relevant trial recommendations. For optimal results, providing detailed information about your specific diagnoses and conditions will greatly enhance the system's ability to match you with the best clinical trial options.")

st.subheader("Eligibility Matching & Trial Ranking")
st.write("Once the relevant clinical trials are pulled in from the retrieval model, the eligibility ranking model evaluates your medical information against each trials’ individual eligibility criteria to produce a score or rank for you to look at the best fit trials for your personal needs. In other words, for each inclusive eligibility criteria, the model will output a 1 if you meet the criteria, 0 if you do not meet the criteria, or 0.5 if the model is unable to determine whether you meet the criteria or not and is unknown. Note that an inverse relationship exists for exclusive criteria where the model will output a 1 if you do not meet the criteria, 0 if you meet the criteria, or a 0.5 if the model is unable to determine whether you meet the criteria or not and is unknown. The score is calculated based on the sum of “met” criteria divided by the number of criteria for each trial such that: Let Si represent the eligibility score for each trial i, ni as the number of criteria for trial i, and cij denotes the evaluated output score for the j-th criterion for each trial i.")

st.subheader("Covid 19 information and how it affects the data we are using")
st.write("Given the significant impacts of the COVID-19 pandemic on clinical trial outcomes and management, we attempt to control for the pandemic by implementing the Oxford Stringency Index, which measures the degree of government regulations, which is closely correlated control in clinical trial administration.")

st.subheader("A W231 Collaboration - Ethics Review")
st.write("Report written by: Joseph Chan")
pdf_path = os.path.join("images","Capstone_Audit_by_Joseph_Chan.pdf")

# Allow users to download the PDF
with open(pdf_path, "rb") as file:
    st.download_button(
        label="Download PDF",
        data=file,
        file_name="EthicReview.pdf",
        mime="application/pdf"
    )

def display_pdf(pdf_file):
    with open(pdf_file, "rb") as file:
        pdf_bytes = file.read()
    
    # Encoding PDF to base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="500"></iframe>'
    
    # Embed the PDF in the Streamlit app
    st.markdown(pdf_display, unsafe_allow_html=True)

display_pdf(pdf_path)

