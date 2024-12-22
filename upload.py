import streamlit as st
import pymysql
from datetime import datetime
import os
from Home_test import connect_db

def upload():
    st.title("📤 Job Listing Upload")
    
    # Check login status and user type
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        return
    
    if st.session_state.get("user_type", "").lower() != "parent":
        st.error("Access denied. This page is for parents only.")
        return
    
    # Fetch parent's details from session state and database
    parent_email = st.session_state.get("email")
    conn = connect_db()
    parent_details = None
    
    if conn:
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email = %s", (parent_email,))
            parent_details = cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching parent details: {e}")
        finally:
            conn.close()
    
    if not parent_details:
        st.error("Unable to retrieve parent information.")
        return
    
    # Job Upload Form
    with st.form("job_upload_form", clear_on_submit=True):
        st.header("Job Listing Details")
        
        # Personal & Contact Information (Pre-filled)
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=parent_details['full_name'], disabled=True)
        with col2:
            email = st.text_input("Email", value=parent_email, disabled=True)
        
        # Contact Information
        st.subheader("Contact Information")
        privacy_options = ["Optional", "Mandatory"]
        phone_privacy = st.radio("Phone Number Privacy", privacy_options, index=0)
        
        if phone_privacy == "Mandatory":
            phone_number = st.text_input("Phone Number", placeholder="Enter your phone number", required=True)
        else:
            phone_number = st.text_input("Phone Number (Optional)", placeholder="Enter your phone number")
        
        # Location Details
        st.subheader("Location")
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City")
        with col2:
            state = st.text_input("State")
        
        detailed_address = st.text_area("Detailed Address (Optional)")
        
        # Preferred Contact Method
        contact_methods = ["Email", "Phone", "Platform Messaging"]
        preferred_contact = st.selectbox("Preferred Contact Method", contact_methods)
        
        # Job Details
        st.subheader("Job Details")
        job_title = st.text_input("Job Title/Role", placeholder="e.g., Math Tutor for 5th Grade")
        job_description = st.text_area("Job Description", placeholder="Provide detailed description of job duties and expectations")
        
        # Date and Frequency
        col1, col2 = st.columns(2)
        with col1:
            preferred_start_date = st.date_input("Preferred Start Date")
        with col2:
            job_frequency = st.text_input("Frequency and Duration", placeholder="e.g., Twice a week for 2 hours")
        
        # Qualifications
        st.subheader("Qualifications/Requirements")
        required_skills = st.text_area("Specific Skills Needed", placeholder="List required skills and experience")
        educational_background = st.text_input("Educational Background (Optional)")
        age_range = st.text_input("Age Range (Optional)")
        
        # Compensation
        st.subheader("Compensation")
        col1, col2 = st.columns(2)
        with col1:
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=0.5)
        with col2:
            rate_negotiable = st.checkbox("Rate is Negotiable")
        
        # Additional Details
        st.subheader("Additional Details")
        job_subject = st.text_input("Subject or Type of Job", placeholder="e.g., Math, Science, Babysitting")
        special_conditions = st.text_area("Special Conditions (Optional)", placeholder="e.g., Must be comfortable with pets")
        
        # Submit Button
        submitted = st.form_submit_button("Upload Job Listing")
        
        # Form Submission Logic
        if submitted:
            # Validate Required Fields
            if not job_title or not job_description:
                st.error("Job Title and Description are required.")
                return
            
            # Database Connection and Insertion
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql = """
                    INSERT INTO job_listings 
                    (parent_email, full_name, phone_number, 
                    city, state, detailed_address, 
                    preferred_contact, job_title, job_description, 
                    preferred_start_date, job_frequency, 
                    required_skills, educational_background, 
                    age_range, hourly_rate, rate_negotiable, 
                    job_subject, special_conditions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    values = (
                        email, full_name, phone_number, 
                        city, state, detailed_address, 
                        preferred_contact, job_title, job_description, 
                        preferred_start_date, job_frequency, 
                        required_skills, educational_background, 
                        age_range, hourly_rate, rate_negotiable, 
                        job_subject, special_conditions
                    )
                    
                    cursor.execute(sql, values)
                    conn.commit()
                    
                    st.success("Job Listing Uploaded Successfully!")
                    st.balloons()
                
                except Exception as e:
                    st.error(f"Error uploading job listing: {e}")
                
                finally:
                    conn.close()
            else:
                st.error("Failed to connect to database.")

# Ensure this is only run when the script is directly executed
if __name__ == "__main__":
    upload()