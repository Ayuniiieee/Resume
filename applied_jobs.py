import streamlit as st
import pymysql
import pandas as pd  # Import pandas

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

def fetch_applied_jobs(user_id):
    connection = get_db_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            # Fetch job applications for the specific user with job details
            query = """
                SELECT 
                    jl.job_title,
                    jl.job_subject,
                    jl.city,
                    jl.state,
                    jl.job_frequency,
                    IFNULL(ja.status, 'Pending') AS status
                FROM 
                    job_applications ja
                JOIN 
                    job_listings jl ON ja.job_id = jl.id
                WHERE 
                    ja.user_id = %s
            """
            cursor.execute(query, (user_id,))
            jobs = cursor.fetchall()
            return jobs
    except pymysql.Error as e:
        st.error(f"Error fetching jobs: {e}")
        return []
    finally:
        connection.close()

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
            job_title, job_subject, city, state, job_frequency, status = job
            
            job_data.append({
                "No": index,
                "Job Title": job_title,
                "Job Subject": job_subject,
                "City": city,
                "State": state,
                "Job Frequency": job_frequency,
                "Status": status
            })

        # Convert to DataFrame and display without index
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No applied jobs found.")

if __name__ == "__main__":
    main()