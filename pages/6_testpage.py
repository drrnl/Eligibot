import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import openai
import pandas as pd
import os, requests, json, io
from modules.retrieval import extract_key_terms, build_ctgov_query, query_and_save_results 
from modules.matching import evaluate_criteria, find_trial_id, get_score, rank_trials, get_results, evaluate_patient_eligibility_for_studies
import bcrypt
import os
import bcrypt
import streamlit as st

# Function to verify the user credentials
def verify_user(username, password):
    # Retrieve the stored username and hashed password from GitHub Secrets
    stored_username = os.getenv(f"{username.upper()}_USERNAME")
    stored_hashed_password = os.getenv(f"{username.upper()}_PASSWORD")
    
    if stored_username and stored_hashed_password:
        # Check if the provided username matches the stored username
        if stored_username == username:
            # Compare the provided password with the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True
            else:
                return False
    return False

# Streamlit UI for login/signup
st.title("Login/Signup Form")

# Create a radio button to toggle between Login and SignUp
form_type = st.radio("Choose an option", ("Login", "Sign Up"))

# Handle login form
if form_type == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type = 'password')
    
    if st.button("Login"):
        if verify_user(username, password):
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid username or password.")
    
# Handle signup form (we'll simulate signup in this example)
elif form_type == "Sign Up":
    st.subheader("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type = 'password')
    
    if st.button("Sign Up"):
        # Here you could handle the signup logic (e.g., add to the database or secret storage)
        st.success(f"Account created successfully for {username}!")
        # Note: In real applications, don't store passwords in plain text, always hash them!

if st.button("authenticate"):
    st.login('google')