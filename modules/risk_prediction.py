import requests
import streamlit as st
def get_risk_prediction(study_json):
    url = 'http://98.83.173.84:8000/predict'
    try:
        response = requests.post(url, json=study_json, verify=False)
        if response.status_code == 200:
            preds = response.json().get('predictions', [])
            return preds
        else:
            st.warning(f"Risk model response status: {response.status_code}")
            return []
    except Exception as e:
        st.warning(f"Risk model call failed: {e}")
        return []