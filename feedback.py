import streamlit as st
from supabase import create_client
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY

def connect_db():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

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
    return full_star * int(rating) + empty_star * (5 - int(rating))

def submit_feedback(supabase, full_name, user_email, rating, comment):
    """
    Submit feedback to the database
    """
    try:
        data = {
            'full_name': full_name,
            'user_email': user_email,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('feedback').insert(data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")
        return False

def fetch_feedbacks(supabase):
    """
    Fetch all feedbacks from the database
    """
    try:
        response = supabase.table('feedback').select('*').order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching feedbacks: {e}")
        return []

def get_user_details(supabase, email):
    """
    Fetch user details from Supabase
    """
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error fetching user details: {e}")
        return None

def feedback():
    """
    Main feedback page function
    """
    st.title("Community Feedbacks")

    # Connect to Supabase
    supabase = connect_db()
    if not supabase:
        st.error("Unable to connect to the database.")
        return

    try:
        # Feedback Submission Section (only for logged-in users)
        if st.session_state.get("logged_in", False):
            st.subheader("Share Your Experience")
            
            # Get user details from session state
            user_email = st.session_state.get("email", "")
            
            # Fetch user details from Supabase
            user_details = get_user_details(supabase, user_email) if user_email else None
            full_name = user_details.get('full_name', '') if user_details else ''

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
                    if submit_feedback(supabase, full_name, user_email, rating, comment):
                        st.success("Thank you for your feedback!")
                        st.rerun()  # Refresh to show the new feedback
                else:
                    st.warning("Please select a rating.")

            st.markdown("---")
        else:
            st.info("Log in to share your experience!")

        # Feedback List Section
        st.subheader("Community Feedbacks")

        # Fetch and display feedbacks
        feedbacks = fetch_feedbacks(supabase)
        
        if feedbacks:
            for feedback in feedbacks:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{feedback['full_name']}**")
                        
                    with col2:
                        st.write(render_stars(feedback['rating']))
                    
                    # Comment
                    st.write(f"*{feedback['comment']}*")
                    
                    # Date
                    created_at = datetime.fromisoformat(feedback['created_at'].replace('Z', '+00:00'))
                    st.caption(f"Posted on: {created_at.strftime('%Y-%m-%d %H:%M')}")
                
                st.markdown("---")
        else:
            st.info("No feedbacks yet.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    feedback()