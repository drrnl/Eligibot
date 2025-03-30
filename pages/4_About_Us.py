import streamlit as st
import os

st.markdown("""
    <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px; width: 100%; margin : 0 auto; text-align: center;">
        <h3 style="font-size: 60px; font-weight: bold;">Mission Statement</h3>
        <p style="font-size: 18px;">"Empowering patients to discover and access the most promising clinical trials by leveraging frontier technology to identify the best treatment options for their unique circumstances."
</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

team_members = [
    {"name": "Eric Shen", "role":"Project Lead / Modeling", "image": os.path.join("images","Eric.png"), "caption": "I’m excited to lead a project that has potential to profoundly impact patients’ lives. Reshaping the clinical trial landscape is no small feat, but I’m deeply inspired by our team's passion and commitment to drive meaningful change in the industry and empower patients with the resources to navigate their healthcare journey confidently."},
    {"name": "Simone Ong", "role":"Project Manager / AWS Infastructure", "image": os.path.join("images","Simone.png"), "caption": "I’m excited to be able to help out as a PM for this project, while still being able to hone in on my technical modeling abilities and explore a new industry that I have little to no experience in. Being able to improve this process for patients from an outside perspective seems like a feat that is worthy and challenging."},
    {"name": "Jonathan Luo", "role":"Project Manager / Modeling", "image": os.path.join("images","Jonathan.jpeg"), "caption": "I believe that getting the patient community closer to research advances healthcare for all. Through analytics and modeling, I strive to to enable a solution that effectively reforms a field that is people-centric and that I am passionate about."},
    {"name": "Matthew Zhang", "role":"Modeling / AWS Infastructure", "image": os.path.join("images", "Matthew.png"), "caption": "I'm excited to contribute to this project by leveraging artificial intelligence with modeling and AWS infrastructure to build scalable and efficient solutions. I hope to provide an efficient alternative to optimizing clinical trial matching through AI and believe this is both a meaningful challenge and an opportunity to drive real impact in healthcare."},
    {"name": "Darren Lo", "role":"Web Developement / Data Visualization", "image": os.path.join("images","Darren.jpeg"), "caption": "I'm thrilled to dive into web development for this clinical optimization matching project. It's an exciting challenge to apply my skills to improve healthcare processes through AI. I look forward to creating a seamless and impactful solution that enhances efficiency and outcomes."}]




col1, col2 = st.columns(2)

for i , member in enumerate(team_members):
    if i % 2 == 0:
        with col1:
            with st.container(border = True):
                st.title(member['name'])
                st.image(member['image'], width = 300)
                st.write(f"**{member['role']}**")
                st.write(f"**{member['caption']}**")
    else:
        with col2:
            with st.container(border = True):
                st.title(member['name'])
                st.image(member['image'], width = 300)
                st.write(f"**{member['role']}**")
                st.write(f"**{member['caption']}**")
        
