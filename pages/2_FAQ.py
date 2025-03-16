import streamlit as st

st.title("Frequently Asked Questions")

# FAQ items and answers
generals = [
    {"question": "What is Clinical Optimization?", "answer": "Clinical optimization refers to improving healthcare processes to enhance efficiency, reduce costs, and improve patient outcomes."},
    {"question": "How does this project work?", "answer": "This project uses advanced algorithms to match patients with the most appropriate clinical interventions and treatments."},
    {"question": "Who can use this tool?", "answer": "This tool is designed for patients with ease of use in mind."},
    {"question": "Is this tool free?", "answer": "Patients can sign up for free to use this tool."}
]
models = [
    {"question": "What are the models used in this product?", "answer": "Clinical optimization refers to improving healthcare processes to enhance efficiency, reduce costs, and improve patient outcomes."},
    {"question": "How does the retrieval work?", "answer": "This project uses advanced algorithms to match patients with the most appropriate clinical interventions and treatments."},
    {"question": "How are we ranking clinical trials suitable for you?", "answer": "This tool is designed for healthcare professionals, administrators, and clinical researchers looking to optimize treatment protocols."},
    {"question": "What is the risk factor score?", "answer": "The availability of this tool depends on the specific healthcare organization or project. Please check with your provider for access details."}
]
# Create an expander for each FAQ
st.subheader("General")
for general in generals:
    with st.expander(general["question"]):
        st.write(general["answer"])

st.subheader("Models")
for model in models:
    with st.expander(model["question"]):
        st.write(model["answer"])