import streamlit as st
import sys
import os
import base64
import json
import datetime
from supabase import create_client

# Add the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import error handling and other modules
try:
    from Home_test import home
    from pages.login_test import login
    from pages.sign_test import signup
    from feedback import feedback
    from applied_jobs import main as applied_jobs
    from about_us import about_us
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()
    
def validate_user_session():
    if not st.session_state.get("logged_in") or not st.session_state.get("user_id"):
        st.error("You must be logged in to access this page. Redirecting to login.")
        st.session_state["page"] = "login"
        st.rerun()

# Session State Initialization
def initialize_session():
    defaults = {
        "step": 1,
        "form_data": {},
        "availability_rows": [{"day": "", "time": None}],
        "logged_in": False,
        "email": None,
        "user_id": None,
        "page": "login",
        "selected_job_title": "Unknown Job",
        "selected_job_subject": "Unknown Subject",
        "selected_job_location": "Unknown Location",
        "selected_job_skills": "Not specified",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Database Connection
def connect_db():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def handle_login(email, password):
    supabase = connect_db()
    if not supabase:
        return None

    try:
        response = supabase.from_("users").select("id").eq("email", email).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            user_id = response.data[0]['id']
            st.session_state["user_id"] = user_id  # Set the user_id in session state
            return user_id
        else:
            st.error("Invalid credentials.")
            return None
    except Exception as e:
        st.error(f"Error during login: {e}")
        return None

# Sidebar Navigation
def sidebar_navigation():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Main Application Logic
def main():
    initialize_session()
    sidebar_navigation()

    page = st.session_state["page"]
    if page == "home":
        home()
    elif page == "login":
        login()
    elif page == "signup":
        signup()
    elif page == "feedback":
        feedback()
    elif page == "applied_jobs":
        applied_jobs()
    elif page == "about_us":
        about_us()
    elif page == "apply":
        apply()
    else:
        st.error("Page not found. Please check your navigation.")

# Function to log out the user
def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["email"] = None
    st.session_state["page"] = "login"

# Function to save uploaded resume
def save_uploaded_resume(uploaded_file):
    if uploaded_file is not None:
        os.makedirs('uploads', exist_ok=True)
        filename = f"resume_{os.urandom(8).hex()}.pdf"
        file_path = os.path.join('uploads', filename)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# Function to display PDF
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to submit job application
def submit_application(user_id):
    availability_json = json.dumps(st.session_state.form_data['availability'])
    supabase = connect_db()
    
    if supabase:
        try:
            # Fetch the job_id based on the current selected job
            selected_job_title = st.session_state.get('selected_job_title', 'Unknown')
            selected_job_location = st.session_state.get('selected_job_location', 'Unknown')
            city = selected_job_location.split(',')[0].strip()
            state = selected_job_location.split(',')[1].strip() if ',' in selected_job_location else 'Unknown'

            # Fetch job_id from job_listings
            job_result = supabase.from_("job_listings").select("id").eq("job_title", selected_job_title).eq("city", city).eq("state", state).execute()

            if not job_result.data:
                st.error("Could not find the selected job. Please try again.")
                return

            job_id = job_result.data[0]['id']

            # Insert job application
            sql = """INSERT INTO job_applications 
                    (user_id, job_id, resume_path, teaching_style, availability, is_confirmed, created_at, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'Pending')"""
            supabase.from_("job_applications").insert({
                'user_id': user_id,
                'job_id': job_id,
                'resume_path': st.session_state.form_data['resume_path'],
                'teaching_style': st.session_state.form_data['teaching_style'],
                'availability': availability_json,
                'is_confirmed': 0  # Pending
            }).execute()

            st.success("Application submitted successfully!")
            st.session_state["page"] = "applied_jobs"
            st.rerun()
        except Exception as e:
            st.error(f"Error submitting application: {e}")

# Apply Page Functionality
def apply():
    if not st.session_state.get("logged_in"):
        st.error("Please log in to apply for a job.")
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("No user ID found. Please log in again.")
        return
    st.title("Job Application Form")

    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

    if 'availability_rows' not in st.session_state:
        st.session_state.availability_rows = [{"day": "", "time": None}]

    # STEP 1: Upload Resume
    if st.session_state.step == 1:
        st.header("Step 1: Upload Resume")
        uploaded_resume = st.file_uploader("Upload your Resume (PDF)", type=['pdf'], key="resume_uploader")
        
        if uploaded_resume:
            resume_path = save_uploaded_resume(uploaded_resume)
            st.session_state.form_data['resume_path'] = resume_path
            
            st.subheader("Resume Preview")
            display_pdf(resume_path)
            
            if st.button("Proceed to Next Step", key="next_step_1"):
                st.session_state.step = 2
                st.rerun()

    # STEP 2: Add Details
    elif st.session_state.step == 2:
        st.header("Step 2: Additional Details")

        teaching_style = st.text_area("Briefly explain your teaching style", key="teaching_style_input")

        st.subheader("Availability")
        for idx, row in enumerate(st.session_state.availability_rows):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                default_day = row["day"] if row["day"] else "Monday"
                row["day"] = st.selectbox(f"Day {idx + 1}", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                        index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(default_day),
                                        key=f"day_{idx}")
            with col2:
                default_time = row["time"] if row["time"] is not None else datetime.time(9, 0)
                row["time"] = st.time_input(f"Time {idx + 1}", value=default_time, key=f"time_{idx}")
            with col3:
                if st.button("Delete", key=f"delete_{idx}"):
                    st.session_state.availability_rows.pop(idx)

        if st.button("Add Another Availability Slot"):
            st.session_state.availability_rows.append({"day": "", "time": None})

        st.session_state.form_data['teaching_style'] = teaching_style
        st.session_state.form_data['availability'] = [
            {"day": row["day"], "time": row["time"].strftime('%H:%M') if row["time"] else None} for row in st.session_state.availability_rows
        ]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Resume Upload", key="back_to_resume"):
                st.session_state.step = 1
                st.rerun()
        
        with col2:
            if st.button("Proceed to Review", key="proceed_to_review"):
                if teaching_style and st.session_state.form_data['availability']:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.warning("Please fill in all fields")

    # STEP 3: Review and Submit
    elif st.session_state.step == 3:
        st.header("Step 3: Review Application")
        
        st.subheader("Uploaded Resume")
        display_pdf(st.session_state.form_data['resume_path'])
        
        st.subheader("Application Details")
        st.write(f"**Teaching Style:** {st.session_state.form_data['teaching_style']}")

        availability_list = st.session_state.form_data['availability']
        formatted_availability = [f"{entry['day']} at {entry['time']}" for entry in availability_list]
        st.write("**Availability:**")
        st.write(", ".join(formatted_availability))
        
        confirmation = st.checkbox("I confirm that the information provided is accurate and complete to the best of my knowledge.", key="confirmation_checkbox")
        
        st.warning("*Double-check your details before submission. Changes cannot be made after submission.*")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Details", key="back_to_details"):
                st.session_state.step = 2
                st.rerun()
        
        with col2:
            if confirmation:
                if st.button("Submit Application", key="submit_application"):
                    submit_application(user_id)

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        user_id = handle_login(email, password)
        if user_id:
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["user_id"] = user_id
            st.session_state["page"] = "home"

if __name__ == "__main__":
    main()