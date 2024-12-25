import streamlit as st
import pandas as pd
from datetime import datetime
from Home_test import connect_db

def download_resume(resume_path):
    """Handle resume download from Supabase storage"""
    supabase = connect_db()
    if not supabase:
        return None
    
    try:
        # Get the file from Supabase storage
        response = supabase.storage.from_('resumes').download(resume_path)
        if response:
            return response
        return None
    except Exception as e:
        st.error(f"Error downloading resume: {e}")
        return None

def fetch_applications(user_email):
    """Fetch all applications for jobs posted by the parent"""
    supabase = connect_db()
    if not supabase:
        return []
    
    try:
        # First, get the job IDs for the parent's email
        jobs_response = (supabase
            .from_("job_listings")
            .select("id")
            .eq("parent_email", user_email)
            .execute()
        )
        
        if not jobs_response.data:
            return []
            
        job_ids = [job['id'] for job in jobs_response.data]
        
        # Then fetch applications for those job IDs
        applications_response = (supabase
            .from_("job_applications")
            .select('''
                id,
                job_id,
                user_id (
                    full_name,
                    email
                ),
                resume_path,
                status,
                created_at,
                job_listings!inner (
                    job_title,
                    job_description
                )
            ''')
            .in_("job_id", job_ids)
            .order('created_at', desc=True)
            .execute()
        )

        if not applications_response.data:
            return []

        # Transform the data to match the expected format
        applications = []
        for item in applications_response.data:
            applications.append({
                'application_id': item['id'],
                'job_id': item['job_id'],
                'full_name': item['user_id']['full_name'],
                'email': item['user_id']['email'],
                'resume_path': item['resume_path'],
                'status': item.get('status', 'Pending'),
                'job_title': item['job_listings']['job_title'],
                'created_at': item['created_at']
            })

        return applications

    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        return []

def update_application_status(application_id, new_status):
    """Update the status of an application"""
    supabase = connect_db()
    if not supabase:
        return False
    
    try:
        # Update the application status
        response = (supabase
            .from_("job_applications")
            .update({
                'status': new_status,
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', application_id)
            .execute()
        )

        # If successful, send notification (you can implement this later)
        if response.data:
            # TODO: Implement notification system
            return True
        return False

    except Exception as e:
        st.error(f"Error updating application status: {e}")
        return False

def application_overview():
    st.title("Application Overview")

    if not st.session_state.get("logged_in"):
        st.warning("Please log in to view applications.")
        return

    user_email = st.session_state.get("email")
    if not user_email:
        st.error("Unable to retrieve your email. Please log in again.")
        return

    # Fetch applications
    applications = fetch_applications(user_email)

    if applications:
        # Add filters
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Approved", "Rejected"],
            key="status_filter"
        )

        # Filter applications based on selected status
        filtered_applications = applications
        if status_filter != "All":
            filtered_applications = [app for app in applications if app['status'] == status_filter]

        # Display applications
        for app in filtered_applications:
            with st.container():
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown(f"**Job Title:** {app['job_title']}")
                    st.markdown(f"**Applicant:** {app['full_name']}")
                    st.markdown(f"**Email:** {app['email']}")
                    st.markdown(f"**Applied on:** {datetime.fromisoformat(app['created_at']).strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.markdown(f"**Status:** {app['status']}")
                if app['status'] == 'Pending':
                    if st.button("Approve", key=f"approve_{app['application_id']}"):
                        if update_application_status(app['application_id'], "Approved"):
                            st.success("Application approved!")
                            st.rerun()  # Use st.rerun() if experimental_rerun() causes issues
                    if st.button("Reject", key=f"reject_{app['application_id']}"):
                        if update_application_status(app['application_id'], "Rejected"):
                            st.success("Application rejected!")
                            st.rerun()  # Use st.rerun() if experimental_rerun() causes issues
                    
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
                
                st.divider()
    else:
        st.info("No applications found for your jobs.")

def main():
    application_overview()

if __name__ == "__main__":
    main()