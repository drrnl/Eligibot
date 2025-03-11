import streamlit as st

st.title("Frequently Asked Questions")

# FAQ items and answers
faqs = [
    {"question": "What is Clinical Optimization?", "answer": "Clinical optimization refers to improving healthcare processes to enhance efficiency, reduce costs, and improve patient outcomes."},
    {"question": "How does this project work?", "answer": "This project uses advanced algorithms to match patients with the most appropriate clinical interventions and treatments."},
    {"question": "Who can use this tool?", "answer": "This tool is designed for healthcare professionals, administrators, and clinical researchers looking to optimize treatment protocols."},
    {"question": "Is this tool free?", "answer": "The availability of this tool depends on the specific healthcare organization or project. Please check with your provider for access details."}
]

# Create an expander for each FAQ
for faq in faqs:
    with st.expander(faq["question"]):
        st.write(faq["answer"])
