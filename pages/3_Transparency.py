import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import os
import base64

    
st.title("Transparency")

st.subheader("Project Architecture")

def project_architecture():
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                background-color: rgba(249, 246, 238);  /* Grey with 50% transparency */
                padding: 20px;
                border-radius: 10px;  /* rounded corners */
                display: inline-block;
                width: 100%;  /* Ensure the container spans full width */
                text-align: center;  /* Center the image */
            }
            """,
    ):
        st.image(os.path.join("images","project_architecture.png"))
project_architecture()

st.write("Some description of the architecture and then maybe bullet points about the individual models ")

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

