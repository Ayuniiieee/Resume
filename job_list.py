import streamlit as st
from datetime import datetime
from Home_test import connect_db

def list_jobs():
    st.title("📋 Your Uploaded Job Listings")
    
    # Check login status and user type
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        return
    
    if st.session_state.get("user_type", "").lower() != "parent":
        st.error("Access denied. This page is for parents only.")
        return
    
    parent_email = st.session_state.get("email")
    supabase = connect_db()
    
    if supabase:
        try:
            response = supabase.from_("job_listings").select("*").eq("parent_email", parent_email).execute()
            if response.data:
                for job in response.data:
                    st.subheader(job['job_title'])
                    st.write(f"**Description:** {job['job_description']}")
                    st.write(f"**Location:** {job['city']}, {job['state']}")
                    st.write(f"**Contact:** {job['preferred_contact']}")
                    st.write(f"**Status:** {job['status']}")
                    st.write("---")
            else:
                st.info("No job listings found.")
        except Exception as e:
            st.error(f"Error fetching job listings: {e}")

if __name__ == "__main__":
    list_jobs()