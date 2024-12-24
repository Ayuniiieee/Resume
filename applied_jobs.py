import streamlit as st
import pandas as pd
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

def fetch_applied_jobs(user_id):
    supabase = connect_db()
    if not supabase:
        return []

    try:
        # Fetch job applications for the specific user with job details using Supabase's query builder
        response = (supabase
            .from_('job_applications')
            .select('''
                job_listings(
                    job_title,
                    job_subject,
                    city,
                    state,
                    job_frequency
                ),
                status
            ''')
            .eq('user_id', user_id)
            .execute()
        )

        if not response.data:
            return []

        # Transform the data to match the expected format
        jobs = []
        for item in response.data:
            job_listing = item.get('job_listings', {})
            status = item.get('status', 'Pending')
            
            jobs.append({
                'job_title': job_listing.get('job_title'),
                'job_subject': job_listing.get('job_subject'),
                'city': job_listing.get('city'),
                'state': job_listing.get('state'),
                'job_frequency': job_listing.get('job_frequency'),
                'status': status
            })

        return jobs

    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        return []

def main():
    st.title("Applied Jobs")

    # Check if user is logged in
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to view your applied jobs.")
        return

    # Get the user ID from the session state
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Unable to retrieve your user ID. Please log in again.")
        return

    # Fetch applied jobs for the logged-in user
    jobs = fetch_applied_jobs(user_id)

    if jobs:
        # Prepare data for display
        job_data = []
        for index, job in enumerate(jobs, start=1):
            job_data.append({
                "No": index,
                "Job Title": job['job_title'],
                "Job Subject": job['job_subject'],
                "City": job['city'],
                "State": job['state'],
                "Job Frequency": job['job_frequency'],
                "Status": job['status']
            })

        # Convert to DataFrame and display without index
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No applied jobs found.")

if __name__ == "__main__":
    main()