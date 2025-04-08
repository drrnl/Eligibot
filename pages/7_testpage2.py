import streamlit as st

if st.button("Authenticate"):
    st.login()
else:
    st.write(f"Hello {st.experimental_user.is_logged_in}")

st.json(st.experimental_user)

if st.button('log out'):
    st.logout()