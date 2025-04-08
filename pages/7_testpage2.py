import streamlit as st

if st.button("Authenticate"):
    st.login("google")
    st.login("google")

st.json(st.experimental_user)

if st.button('log out'):
    st.logout()