import streamlit as st

if not st.experimental_user.is_logged_in:
    if st.button("authenticate"):
        st.login('google')


if st.experimental_user.is_logged_in:
    st.json(st.experimental_user)

if st.button('Log Out'):
    st.logout()