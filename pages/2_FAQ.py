import streamlit as st

st.title("Frequently Asked Questions")

# FAQ items and answers
generals = [
    {"question": "What is Clinical Optimization?", "answer": "Eligibot is your AI clinical trial buddy, designed to connect you with life-saving treatments. By entering your health details, Eligibot recommends trials that best match your eligibility criteria. Eligibot helps advance medical research by guiding you through the process of enrolling in suitable trials quickly, transparently, and clearly."},
    {"question": "Who can use this tool?", "answer": "Anyone! However, we are focused on patients who are interested in participating in clinical trials."},
    {"question": "Is this tool free?", "answer": "Patients can sign up for free to use this tool."}
]
models = [
    {"question": "What are the models used in this product?", "answer": "First, the retrieval model provides the most relevant recruiting clinical trials to you. Second, our eligibility criteria model provides a ranking of your match to these trials.Third, the risk model provides some context of the average risk and confidence levels associated with participation in these trials."},
    {"question": "How does the retrieval work?", "answer": "We utilize a key-word search to first return trials that are in the relevant space."},
    {"question": "How are we ranking clinical trials suitable for you?", "answer": "Because much of the information about eligibility criteria for the user may be unknown, we prioritize your eligibility criteria match rate rather than the count of eligibility criteria unmet or known. Among trials with similar eligibility criteria match rate, we favor trials that have fewer unmet criteria. Remember that using our recommendations to check and evaluate yourself against eligibility criteria will give you the most complete assessment of your eligibility."},
    {"question": "What is the risk factor score?", "answer": "The risk factor score is a relative measure of adverse outcomes during the course of a clinical trial. Researchers record adverse outcomes as “serious” or “other”. “Serious” AEs are considered life-threatening or permanently disabling. We weight these as 3x as the weight of “other” AEs in our calculation."}
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