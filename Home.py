import streamlit as st
import os
import base64

def get_base64_encoded_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
image_path = os.path.join("images", "eligibot.png")

page_bg_style = f"""
<style>
    /* Full-page background */
    .stApp {{
        background: url("data:image/png;base64,{get_base64_encoded_image(image_path)}");
        background-size: 100%;
        background-attachment: fixed;
        background-position: 270px -270px;
        background-repeat: no-repeat;
        width: 100 vw;
        height: 100vh;
    }}

    /* Create a "hero" container in the center */
    .hero-container {{
        position: relative;
        top: 50%;
        left: 50%;
        transform: translate(-5%, 130%);
        text-align: center;
        color: #FFFFFF; /* Adjust text color as needed */
        background: rgba(0, 0, 0, 0.2); /* Optional: translucent background behind text */
        padding: 2rem 2rem 4rem 2rem;
        border-radius: 0.5rem;
        max-width: 500px; /* Constrain width if you like */
    }}

    /* Larger heading */
    .hero-title {{
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }}

    /* Subheading text */
    .hero-subtitle {{
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }}

    /* Center the button */
    .stButton > button {{
        font-size: 1.2rem;
        padding: 0.75rem 1.5rem;
        background-color: #f39c12;  /* Change button color */
        border: none;
        border-radius: 0.5rem;
        color: white;
        cursor: pointer;
        transition: background-color 0.3s ease;
        position: relative; /* Needed for pixel adjustments */
        top: 230px; /* Moves the button down 50px from its normal position */
        left: 515px; /* Moves the button right 20px from its normal position */
    }}

    /* Button hover effect */
    .stButton > button:hover {{
        background-color: #e67e22;
    }}
</style>
"""

# Inject the CSS
st.markdown(page_bg_style, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-container">
        <h1 class="hero-title">Welcome to Eligibot</h1>
        <p class="hero-subtitle">Matching you with the right clinical trials.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Create a container for the button and use it within the hero section
with st.container():
    # Create the "Get Started" button inside the container
    if st.button("Get Started"):
        st.login()
        st.switch_page(os.path.join("pages", "1_Trial_Matching.py"))

