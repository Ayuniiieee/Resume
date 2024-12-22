import streamlit as st
import pymysql
import pandas as pd
import os
from datetime import datetime

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password123',  # Use the password you set above
            db='cv',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_applications(user_email):
    """Fetch all applications for jobs posted by the parent"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    ja.id AS application_id,
                    jl.job_title,
                    jl.job_subject,
                    u.full_name,
                    ja.resume_path,
                    IFNULL(ja.status, 'Pending') AS status
                FROM 
                    job_applications ja
                JOIN 
                    job_listings jl ON ja.job_id = jl.id
                JOIN 
                    users u ON ja.user_id = u.id
                WHERE 
                    jl.parent_email = %s  -- filter by parent's email
            """
            cursor.execute(query, (user_email,))  # Use the provided email
            return cursor.fetchall()
    except pymysql.Error as e:
        st.error(f"Error fetching applications: {e}")
        return []
    finally:
        connection.close()

def update_application_status(application_id, status):
    """Update the status of an application"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE job_applications 
                SET status = %s, 
                    updated_at = %s 
                WHERE id = %s
            """
            cursor.execute(query, (status, datetime.now(), application_id))
            connection.commit()
            return True
    except pymysql.Error as e:
        st.error(f"Error updating application status: {e}")
        return False
    finally:
        connection.close()

def download_resume(resume_path):
    """Handle resume download"""
    try:
        with open(resume_path, 'rb') as file:
            return file.read()
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
        for index, app in enumerate(applications):
            app_id, job_title, job_subject, full_name, resume_path, status = app
            
            # Create a container for each application
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 3])
                
                with col1:
                    st.write(f"**Name:** {full_name}")
                with col2:
                    st.write(f"**Job Title:** {job_title}")
                with col3:
                    st.write(f"**Subject:** {job_subject}")
                with col4:
                    if resume_path and os.path.exists(resume_path):
                        resume_content = download_resume(resume_path)
                        if resume_content:
                            st.download_button(
                                label="Download Resume",
                                data=resume_content,
                                file_name=f"resume_{full_name}.pdf",
                                mime="application/pdf",
                                key=f"download_{app_id}"  # Unique key for each download button
                            )
                with col5:
                    st.write(f"**Status:** {status}")
                    if status == 'Pending':
                        col5_1, col5_2 = st.columns(2)
                        with col5_1:
                            if st.button(f"Accept {app_id}", key=f"accept_{app_id}"):
                                if update_application_status(app_id, "Accepted"):
                                    st.success("Application accepted!")
                                    st.rerun()  # Updated to use st.rerun()
                        with col5_2:
                            if st.button(f"Reject {app_id}", key=f"reject_{app_id}"):
                                if update_application_status(app_id, "Rejected"):
                                    st.success("Application rejected!")
                                    st.rerun()  # Updated to use st.rerun()
                
                st.divider()
    else:
        st.info("No applications found for your jobs.")

def main():
    application_overview()

if __name__ == "__main__":
    main()