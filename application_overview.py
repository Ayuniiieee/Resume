import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

def connect_db():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_applications(user_email):
    """Fetch all applications for jobs posted by the parent"""
    supabase = connect_db()
    if not supabase:
        return []
    
    try:
        # Adjusted query to include necessary joins
        response = (supabase
            .from_('job_applications')
            .select('''
                id,
                job_id (
                    id,
                    job_title,
                    job_subject
                ),
                job_id:job_listings!parent_email,  -- Use this to get parent_email from job_listings
                user_id (full_name),
                resume_path,
                status
            ''')
            .eq('job_id.parent_email', user_email)  # Ensure this references the right email
            .execute()
        )

        if not response.data:
            return []

        # Transform the data to match the expected format
        applications = []
        for item in response.data:
            applications.append({
                'application_id': item['id'],
                'job_title': item['job_id']['job_title'],  # Access via 'job_id'
                'job_subject': item['job_id']['job_subject'],  # Access via 'job_id'
                'parent_email': item['job_listings']['parent_email'],  # Access parent_email
                'full_name': item['user_id']['full_name'],  # Access via 'user_id'
                'resume_path': item['resume_path'],
                'status': item.get('status', 'Pending')
            })

        return applications

    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        return []

def update_application_status(application_id, status):
    """Update the status of an application"""
    supabase = connect_db()
    if not supabase:
        return False
    
    try:
        response = (supabase
            .from_('job_applications')
            .update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', application_id)
            .execute()
        )
        return True if response.data else False
    except Exception as e:
        st.error(f"Error updating application status: {e}")
        return False

def download_resume(resume_path):
    """Handle resume download"""
    try:
        # For Supabase storage
        supabase = connect_db()
        if supabase:
            response = supabase.storage.from_('resumes').download(resume_path)
            return response
    except Exception as e:
        st.error(f"Error downloading resume: {e}")
        return None

def application_overview():
    st.title("Application Overview")

    if not st.session_state.get("logged_in"):
        st.warning("Please log in to view applications.")
        return

    # Get the email from the session state
    user_email = st.session_state.get("email")
    if not user_email:
        st.error("Unable to retrieve your email. Please log in again.")
        return

    # Fetch applications for jobs posted by this user
    applications = fetch_applications(user_email)

    if applications:
        # Prepare data for display
        for app in applications:
            # Create a container for each application
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 3])
                
                with col1:
                    st.write(f"**Name:** {app['full_name']}")
                with col2:
                    st.write(f"**Job Title:** {app['job_title']}")
                with col3:
                    st.write(f"**Subject:** {app['job_subject']}")
                with col4:
                    if app['resume_path']:
                        resume_content = download_resume(app['resume_path'])
                        if resume_content:
                            st.download_button(
                                label="Download Resume",
                                data=resume_content,
                                file_name=f"resume_{app['full_name']}.pdf",
                                mime="application/pdf",
                                key=f"download_{app['application_id']}"
                            )
                with col5:
                    st.write(f"**Status:** {app['status']}")
                    if app['status'] == 'Pending':
                        col5_1, col5_2 = st.columns(2)
                        with col5_1:
                            if st.button(f"Accept {app['application_id']}", key=f"accept_{app['application_id']}"):
                                if update_application_status(app['application_id'], "Accepted"):
                                    st.success("Application accepted!")
                                    st.rerun()
                        with col5_2:
                            if st.button(f"Reject {app['application_id']}", key=f"reject_{app['application_id']}"):
                                if update_application_status(app['application_id'], "Rejected"):
                                    st.success("Application rejected!")
                                    st.rerun()
                
                st.divider()
    else:
        st.info("No applications found for your jobs.")

def main():
    application_overview()

if __name__ == "__main__":
    main()