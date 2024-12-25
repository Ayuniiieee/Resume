import streamlit as st
import pandas as pd
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def connect_db():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_all_jobs(supabase, user_id):
    try:
        # Fetch all job applications for the logged-in user
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
                status,
                user_id
            ''')
            .eq('user_id', user_id)  # Only fetch jobs for the current user
            .execute()
        )

        if not response.data:
            return []

        # Transform the data
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
    st.markdown("""
        <style>
        .title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #1E88E5;
        }
        .stDataFrame {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="title">Applied Jobs Overview</p>', unsafe_allow_html=True)

    # Connect to Supabase
    supabase = connect_db()
    if not supabase:
        st.error("Unable to connect to the database.")
        return
    
    # Check if the user is logged in
    if not st.session_state.get("logged_in"):
        st.warning("You are not logged in. Please log in to view this page.")
        st.session_state["page"] = "login"
        st.rerun()
        return

    # Retrieve user ID
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Your session appears invalid. Please log in again.")
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"
        st.rerun()
        return

    # Fetch all jobs
    jobs = fetch_all_jobs(supabase, user_id)

    if jobs:
        job_data = []
        for index, job in enumerate(jobs, start=1):
            job_data.append({
                "No": index,
                "Job Title": job['job_title'],
                "Job Subject": job['job_subject'],
                "Location": f"{job['city']}, {job['state']}",
                "Job Frequency": job['job_frequency'],
                "Status": job['status']
            })

        df = pd.DataFrame(job_data)
        
        # Add filtering options
        col1, col2 = st.columns(2)
        with col1:
            subject_filter = st.multiselect(
                "Filter by Subject",
                options=sorted(df["Job Subject"].unique())
            )
        
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(df["Status"].unique())
            )

        # Apply filters
        filtered_df = df
        if subject_filter:
            filtered_df = filtered_df[filtered_df["Job Subject"].isin(subject_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

        # Display the filtered dataframe
        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No jobs match the selected filters.")
            
        # Add some statistics
        st.markdown("### Quick Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Applications", len(df))
        with col2:
            st.metric("Pending Applications", len(df[df["Status"] == "Pending"]))
        with col3:
            st.metric("Accepted Applications", len(df[df["Status"] == "Accepted"]))
            
    else:
        st.info("No job applications found in the system.")
        st.markdown("""
            ### Getting Started
            - Browse available jobs
            - Submit your applications
            - Track your application status here
        """)

if __name__ == "__main__":
    main()