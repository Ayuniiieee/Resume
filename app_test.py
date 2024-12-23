import streamlit as st
import sys
import os
import Check
from supabase import create_client

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add some error handling for imports
try:
    from Home_test import home
    from pages.login_test import login
    from pages.sign_test import signup
    from upload import upload
    from feedback import feedback
    from application_overview import application_overview
    from applied_jobs import main as applied_jobs
    from about_us import about_us
    from apply import apply 
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

def connect_db():
    try:
        # Create Supabase client
        supabase = create_client(
            st.secrets["https://duiomhgeqricsyjmeamr.supabase.co"],
            st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1aW9taGdlcXJpY3N5am1lYW1yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NDczNTMsImV4cCI6MjA1MDUyMzM1M30.VRVw8jQLSQ3IzWhb2NonPHEQ2Gwq-k7WjvHB3WcLe48"]
        )
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def create_header():
    if st.session_state.get("logged_in", False):
        st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <link rel="stylesheet" href="path_to_your_css_file.css">
        <style>
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: #f1f1f1;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header-items {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .badge {
            background-color: red;
            color: white;
            border-radius: 50%;
            padding: 5px 10px;
            font-size: 12px;
            margin-left: 5px;
        }
        .search-bar input {
            padding: 8px;
            width: 250px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

def perform_job_search(search_query, search_type):
    try:
        supabase = connect_db()
        if supabase:
            if search_type == "location":
                response = supabase.table('job_listings').select('*').or_(
                    f"city.ilike.%{search_query}%,state.ilike.%{search_query}%"
                ).execute()
            elif search_type == "job_title":
                response = supabase.table('job_listings').select('*').ilike(
                    'job_title', f'%{search_query}%'
                ).execute()
            elif search_type == "job_subject":
                response = supabase.table('job_listings').select('*').ilike(
                    'job_subject', f'%{search_query}%'
                ).execute()
            return response.data
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

def display_search_results(results):
    if not results:
        st.warning("No job listings found matching your search.")
        return
    
    st.subheader(f"Found {len(results)} Job Listing(s)")
    
    for job in results:
        with st.expander(f"{job['job_title']} - {job['city']}, {job['state']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Job Title:** {job['job_title']}")
                st.write(f"**Subject:** {job['job_subject']}")
                st.write(f"**Location:** {job['city']}, {job['state']}")
            with col2:
                st.write(f"**Company:** {job.get('company', 'N/A')}")
                st.write(f"**Salary Range:** {job.get('salary_range', 'Not specified')}")

def create_search_bar():
    if st.session_state.get("logged_in", False):
        col1, col2 = st.columns([3, 1])  # Adjust the ratio as needed

        with col1:
            # Use a unique key for the search query
            search_query = st.text_input("Search Job Listings", placeholder="Job Title, Location, etc.", key="search_query")

        with col2:
            # Use a unique key for the search type
            search_type = st.selectbox(
                "Search By", 
                ["Location", "Job Title", "Job Subject"],
                key="search_type"
            )

        if st.button("Search Jobs", key="search_jobs_button"):
            if search_query:
                type_map = {
                    "Location": "location",
                    "Job Title": "job_title", 
                    "Job Subject": "job_subject"
                }
                results = perform_job_search(search_query, type_map[search_type])
                display_search_results(results)
            else:
                st.warning("Please enter a search term")

# Function to log out the user
def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["email"] = None
    st.session_state["page"] = "login"
    st.session_state["user_type"] = None
    st.session_state["username"] = None

def main():
    create_header()
    create_search_bar()
    # Sidebar Design
    with st.sidebar:
        # Remove unwanted default upper sidebar section
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True,
        )

# Enhanced Sidebar Design - with scoped styling
    with st.sidebar:
        st.markdown(
            """
            <style>
            /* Remove default sidebar nav */
            [data-testid="stSidebarNav"] {
                display: none;
            }
            
            /* Scope styles to sidebar only using .stSidebar */
            .stSidebar .stButton button {
                width: 100%;
                padding: 10px 15px;
                margin: 5px 0;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                font-size: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
                justify-content: flex-start;
                color: #000000;
            }
            
            .stSidebar .stButton button:hover {
                background-color: #f0f2f6;
                border-color: #c0c0c0;
                transform: translateX(3px);
            }
            
            .stSidebar .sidebar-divider {
                margin: 15px 0;
                border-top: 1px solid #e0e0e0;
            }
            
            .stSidebar .user-info {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                margin-bottom: 15px;
                color: #000000;
            }

            /* Reset main content container width */
            .main .block-container {
                max-width: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Custom sidebar header
        st.markdown("<h2 style='text-align: left; color: #000000;'>EduResume</h2>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        # User info section if logged in
        if st.session_state.get("logged_in", False):
            st.markdown(
                f"""
                <div class='user-info'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 24px; filter: grayscale(100%);'>👤</span>
                        <div>
                            <div style='font-weight: bold;'>{st.session_state.get('email')}</div>
                            <div style='font-size: 0.8em; color: #666;'>{st.session_state.get('user_type', '').title()}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Common buttons for both user types
            if st.button("⌂  Home", key="home_button", use_container_width=True):
                st.session_state["page"] = "home"
                st.rerun()
            
            # User-specific buttons
            if st.session_state.get("user_type", "").lower() == "user":
                if st.button("☰  Check", key="check_button", use_container_width=True):
                    st.session_state["page"] = "check"
                    st.rerun()
                if st.button("□  Applied Jobs", key="applied_jobs_button", use_container_width=True):
                    st.session_state["page"] = "applied_jobs"
                    st.rerun()
            elif st.session_state.get("user_type", "").lower() == "parent":
                if st.button("↑  Upload", key="upload_button", use_container_width=True):
                    st.session_state["page"] = "upload"
                    st.rerun()
                if st.button("◈  Application Overview", key="application_overview_button", use_container_width=True):
                    st.session_state["page"] = "application_overview"
                    st.rerun()
            
            st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
            
            if st.button("✉  Feedback", key="feedback_button", use_container_width=True):
                st.session_state["page"] = "feedback"
                st.rerun()
            if st.button("⇥  Log Out", key="logout_button", use_container_width=True):
                logout_user()
                st.rerun()
        
        else:  # If not logged in
            if st.button("⌂  Home", key="home_button_not_logged_in", use_container_width=True):
                st.session_state["page"] = "home"
                st.rerun()
            if st.button("⌹  Log In", key="login_button", use_container_width=True):
                st.session_state["page"] = "login"
                st.rerun()
            if st.button("✎  Sign Up", key="signup_button", use_container_width=True):
                st.session_state["page"] = "signup"
                st.rerun()
            st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
            if st.button("✉  Feedback", key="feedback_button_not_logged_in", use_container_width=True):
                st.session_state["page"] = "feedback"
                st.rerun()
            if st.button("ⓘ  About Us", key="about_us_button", use_container_width=True):
                st.session_state["page"] = "about_us"
                st.rerun()

    # Page routing
    if st.session_state.get("page") == "home":
        home()
    elif st.session_state.get("page") == "login":
        login()
    elif st.session_state.get("page") == "signup":
        signup()
    elif st.session_state.get("page") == "check":
        Check.check()
        Check.run()
    elif st.session_state.get("page") == "upload":
        upload()
    elif st.session_state.get("page") == "feedback":
        feedback()
    elif st.session_state.get("page") == "application_overview":
        application_overview()  # Redirect to application_overview.py
    elif st.session_state.get("page") == "applied_jobs":
        applied_jobs()  # Redirect to applied_jobs.py
    elif st.session_state.get("page") == "about_us":
        about_us()  # Redirect to about_us.py
    elif st.session_state.get("page") == "apply":
        apply()  # Call the apply function
  

if __name__ == "__main__":
    # Initialize session state variables if not already present
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "email" not in st.session_state:
        st.session_state["email"] = None
    if "user_type" not in st.session_state:
        st.session_state["user_type"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    if "username" not in st.session_state:  # Add this line
        st.session_state["username"] = None

    main()