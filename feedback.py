import streamlit as st
import pymysql
from Home_test import connect_db
from datetime import datetime

def star_rating_widget(label, max_stars=5, default_rating=3):
    """
    Custom star rating widget
    """
    st.write(label)
    rating = st.session_state.get("current_rating", default_rating)
    
    cols = st.columns(max_stars)
    for i in range(max_stars):
        star_label = "★" if i < rating else "☆"
        if cols[i].button(star_label, key=f"star_{i+1}"):
            st.session_state["current_rating"] = i + 1
            rating = i + 1

    return st.session_state.get("current_rating", default_rating)

def render_stars(rating):
    """
    Render star rating display
    """
    full_star = "★"
    empty_star = "☆"
    return full_star * rating + empty_star * (5 - rating)

def submit_feedback(conn, full_name, user_email, rating, comment):
    """
    Submit feedback to the database
    """
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO feedback 
        (full_name, user_email, rating, comment, created_at) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (full_name, user_email, rating, comment, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")
        return False

def fetch_feedbacks(conn):
    """
    Fetch all feedbacks from the database
    """
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
        SELECT full_name, user_email, rating, comment, created_at 
        FROM feedback 
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching feedbacks: {e}")
        return []

def feedback():
    """
    Main feedback page function
    """
    st.title("Community Feedbacks")

    # Connect to the database
    conn = connect_db()
    if not conn:
        st.error("Unable to connect to the database.")
        return

    try:
        # Feedback Submission Section (only for logged-in users)
        if st.session_state.get("logged_in", False):
            st.subheader("Share Your Experience")
            
            # Get user details from session state
            user_email = st.session_state.get("email", "")
            full_name = st.session_state.get("full_name", "")

            # Fetch full name from database if not in session state
            if not full_name and user_email:
                try:
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    cursor.execute("SELECT full_name FROM users WHERE email = %s", (user_email,))
                    user = cursor.fetchone()
                    if user:
                        full_name = user["full_name"]
                        st.session_state["full_name"] = full_name
                    else:
                        st.error("User details not found.")
                except Exception as e:
                    st.error(f"Error fetching user details: {e}")

            # Display user information
            st.write(f"**Name:** {full_name}")
            st.write(f"**Email:** {user_email}")

            # Rate experience
            st.write("Rate Your Experience:")
            rating = star_rating_widget("Your Rating", max_stars=5)

            # Comment input
            comment = st.text_area("Explain Your Experience", height=100)

            # Submit button
            if st.button("Submit Feedback"):
                if rating > 0:
                    # Submit feedback
                    if submit_feedback(conn, full_name, user_email, rating, comment):
                        st.success("Thank you for your feedback!")
                else:
                    st.warning("Please select a rating.")

            st.markdown("---")
        else:
            st.info("Log in to share your experience!")

        # Feedback List Section
        st.subheader("Community Feedbacks")

        # Fetch and display feedbacks
        feedbacks = fetch_feedbacks(conn)
        
        if feedbacks:
            for feedback in feedbacks:
                # Feedback card layout
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{feedback['full_name']}**")
                        
                    with col2:
                        st.write(render_stars(feedback['rating']))
                    
                    # Comment
                    st.write(f"*{feedback['comment']}*")
                    
                    # Date
                    st.caption(f"Posted on: {feedback['created_at'].strftime('%Y-%m-%d %H:%M')}")
                
                # Separator between feedback entries
                st.markdown("---")
        else:
            st.info("No feedbacks yet.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    finally:
        # Always close the database connection
        conn.close()

# This allows the page to be imported and used in the main app
if __name__ == "__main__":
    feedback()
