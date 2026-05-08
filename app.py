# IMPORT LIBRARIES
import streamlit as st
import pandas as pd
import ast
import fitz
import matplotlib.pyplot as plt

st.title("AI Job Recovery Assistant")
df = pd.read_csv("jobs_data.csv")

df["Skills"] = df["Skills"].apply(ast.literal_eval)
df["Skills"] = df["Skills"].apply(lambda x:[skill.lower() for skill in x])

# EXTRACT ALL UNIQUE SKILLS

all_skills = set()
for skills in df["Skills"]:
    for skill in skills:
        all_skills.add(skill)

# SMART SKILL ALIASES
skill_aliases = {
    "machine learning": ["ml"],
    "deep learning" : ["dl"],
    "power bi": ["powerbi" , "pbi"],
    "sql": ["mysql" , "postgresql"],
    "python": ["py"],
    "excel": ["ms excel"]
}


def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(),
                    filetype = "pdf")
    for page in pdf:
        text += page.get_text()
        
    return text.lower()
    

def extract_skills_from_resume(text,all_skills):
    found_skills = []

    for skill in all_skills:
        if skill in text:
            found_skills.append(skill) 

        elif skill in skill_aliases:
            for alias in skill_aliases[skill]:
                if alias in text:
                    found_skills.append(skill)

    return list(set(found_skills))

# USER INPUT

st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
user_input = st.text_input("🚀 Enter your skills (comma seperated)", placeholder="e.g. Python,SQL,Excel")


if uploaded_file or user_input:
    if uploaded_file:
        
    
        resume_text = extract_text_from_pdf(uploaded_file)
        user_skills = extract_skills_from_resume(resume_text,all_skills)
        st.write("📌 Skills detected from resume:")
        st.write(", ".join([skill.upper() for skill in user_skills]))

    else:
        user_skills = [skill.strip().lower() for skill in user_input.split(",")]
    
# JOB MATCHING LOGIC
    results = []
    
    for index,row in df.iterrows():
        role = row["Role"]
       
        required_skills = row["Skills"]

      
        matched = set(user_skills).intersection(set(required_skills))
       
                   
    
        score = (len(matched)/len(required_skills))*100
        
        missing = list(set(required_skills)-matched)
    
        
    
        results.append({
            "Role" : role,
            "Match %" : round(score,2),
            "Missing Skills" : missing
        })
    results_df = pd.DataFrame(results)
    results_df = results_df[results_df["Match %"] >= 30]
    results_df = results_df.sort_values(by = "Match %", ascending = False)
    
    top_jobs = results_df.head(5)
    
    if len(top_jobs) == 0:
        st.write("❌ No matching jobs found . Try adding more skills.")
    else:
        # BEST JOB MATCH
        st.subheader("🔥 Best Job Match")
        
        best_job = top_jobs.iloc[0]
    
        st.markdown(f"""
        <div
        style = 'background:linear-gradient(135deg,#d4edda,#c3e6cb);
        padding:20px;border-radius:15px;margin-bottom:20px'>
        
        <h2>💼{best_job['Role']}</h2>
        <p><b>Match Score:</b> {best_job['Match %']}%</p>
        </div>
        """,unsafe_allow_html=True)

        st.progress(int(best_job["Match %"]))

        # WHY THIS JOB MATCHES

        st.subheader("🧠 Why this job matches you")

        required_skills = df[df["Role"] == best_job["Role"]]["Skills"].values[0]
            
        matched = list(set(user_skills).intersection(set(required_skills)))

        missing = best_job["Missing Skills"]

        if len(matched) > 0:
            st.write("✅ You already know:")
            st.write(", ".join([skill.upper() for skill in matched]))

            if len(missing) > 0:
                st.write("❌ You need to learn:")
                st.write(", ".join([skill.upper() for skill in missing]))
       
        # SKILLS TO IMPROVE
    
        if len(best_job["Missing Skills"])>0:
            skills_html = " ".join([
                f"""<span style='background:#fff3cd;
                padding:6px 12px;
                border-radius:20px;
                margin:4px;
                display:inline-block;
                font-weight:500'>
                {skill.upper()}</span>"""
                for skill in best_job["Missing Skills"]
            ])

            st.markdown(f"""
            <div style = 'margin-top : 10px;margin-bottom:20px'>
            <b>⚠️ Skills to Improve:</b><br><br>
            {skills_html}
            </div>
            """,unsafe_allow_html=True)


        else:
            st.success("🎉 You are fully ready for this role!")


        # RECOMMENDED SKILLS    
        
        st.subheader("📌 Recommended Skills to Learn")
   

        suggestions = best_job["Missing Skills"][:3]
        if len(suggestions) > 0:
            for skill in suggestions:
                st.write(f"👉 Focus on learning: **{skill.upper()}**")
         
        else:
            st.write("🎉 You are already job-ready!")
          

        # OTHER JOB OPPORTUNITIES
        
        st.subheader("📊 Other Job Opportunities")
        for index,row in top_jobs.iloc[1:].iterrows():
           
      
            progress_value = int(row["Match %"])

            skills_html = " ".join([
                f"""<span style='background:#e0f7fa;
                padding:5px 10px;
                border-radius:15px;
                margin:3px;
                display:inline-block'>
                {skill.upper()}
                </span>"""
                for skill in row["Missing Skills"]
            ])    

            st.markdown(f"""
            <div style = 'background:#f8f9fa;
            padding : 15px;
            border-radius:12px;
            margin-bottom:10px'>
            <h4>💼 {row['Role']}</h4>
            <p><b>Match Score:</b> {row['Match %']}%</p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(int(row["Match %"]))
            if len(row["Missing Skills"])>0:
                

                st.markdown(f"""
                <div style = 'margin-bottom:20px'>
                <b>Missing Skills:</b><br>
                {skills_html}
                </div>
                """, unsafe_allow_html = True)

            else:
                st.success("No missing skills!")
            st.divider()

    # JOB MATCH VISUALIZATION
    
    st.subheader("📊 Job Match Comparison")
    roles = top_jobs["Role"]
    scores = top_jobs["Match %"]
    fig, ax = plt.subplots()
    
    ax.barh(roles,scores)
    ax.set_xlabel("Match Percentage")
    ax.set_title("Top Job Matches")
    st.pyplot(fig)

        
