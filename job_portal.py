import streamlit as st
import mysql.connector
import time

# --- DB Connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sarah@1710",
    database="JOB"
)
cursor = conn.cursor(dictionary=True)

# --- Custom Styling ---
st.set_page_config(page_title="Job Portal", page_icon="💼", layout="centered")
st.markdown("""
    <style>
    .title { font-size: 40px; font-weight: bold; color: #4CAF50; text-align: center; margin-bottom: 20px; }
    .subtitle { font-size: 22px; font-weight: 600; margin-top: 20px; }
    .job-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin: 10px 0; background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #4CAF50; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.markdown('<div class="title">🚀 Job Portal App</div>', unsafe_allow_html=True)

# --- Session State for Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "login"

# --- Show Application Success Page ---
if st.session_state.page == "success":
    st.balloons()
    st.markdown("<h2 style='text-align:center; color:green;'>🎉 Application Submitted Successfully!</h2>", unsafe_allow_html=True)
    st.info("📧 Please check your email for confirmation.")
    if st.button("🔙 Back to Jobs"):
        st.session_state.page = "login"
    st.stop()

# --- Login Section ---
login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

with login_tab:
    st.markdown('<div class="subtitle">Login to Your Account</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        user_type = st.selectbox("Login as", ["Job Seeker", "Employer"])
    with col2:
        email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

    if login:
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s AND user_type=%s", 
                       (email, password, user_type.replace(" ", "")))
        user = cursor.fetchone()

        if user:
            st.success(f"Welcome {user['first_name']}! Logged in as {user_type} 💼")

            # --- DASHBOARD ---
            if user_type == "Job Seeker":
                st.markdown('<div class="subtitle">📋 Available Jobs</div>', unsafe_allow_html=True)
                cursor.execute("SELECT * FROM jobs WHERE status='Approved' ORDER BY post_date DESC LIMIT 5")
                jobs = cursor.fetchall()

                for job in jobs:
                    with st.expander(f"{job['job_title']} at {job['location']}"):
                        st.markdown(f"**Description:** {job['job_description']}")
                        st.markdown(f"**Type:** {job['job_type']} | **Salary:** {job['salary_range']}")
                        apply_btn = st.button(f"Apply for Job ID {job['job_id']}", key=f"apply_{job['job_id']}")
                        if apply_btn:
                            cursor.execute("SELECT seeker_id FROM job_seekers WHERE user_id=%s", (user['user_id'],))
                            seeker = cursor.fetchone()
                            if seeker:
                                cursor.execute("SELECT * FROM job_applications WHERE job_id=%s AND seeker_id=%s", 
                                               (job['job_id'], seeker['seeker_id']))
                                existing_app = cursor.fetchone()
                                if existing_app:
                                    st.info("⚠️ You have already applied to this job.")
                                else:
                                    cursor.execute("INSERT INTO job_applications (job_id, seeker_id) VALUES (%s, %s)", 
                                                   (job['job_id'], seeker['seeker_id']))
                                    conn.commit()
                                    st.session_state.page = "success"
                                    st.experimental_rerun()

            elif user_type == "Employer":
                st.markdown('<div class="subtitle">📢 Post a New Job</div>', unsafe_allow_html=True)
                job_title = st.text_input("Job Title")
                job_desc = st.text_area("Job Description")
                job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract"])
                location = st.text_input("Location")
                salary = st.text_input("Salary Range")
                post_btn = st.button("Post Job")

                if post_btn:
                    cursor.execute("SELECT employer_id FROM employers WHERE user_id=%s", (user['user_id'],))
                    employer = cursor.fetchone()
                    if employer:
                        cursor.execute("""
                            INSERT INTO jobs (employer_id, job_title, job_description, job_type, location, salary_range, status)
                            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
                        """, (employer['employer_id'], job_title, job_desc, job_type, location, salary))
                        conn.commit()
                        st.success("✅ Job Posted. Awaiting Admin Approval!")

        else:
            st.error("Invalid credentials or user type ❌")

# --- Footer ---
st.markdown("---")
st.info("© 2025 Job Portal App | Built with ❤️ using Streamlit")

# --- Close DB Connection ---
cursor.close()
conn.close()
