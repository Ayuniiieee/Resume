import streamlit as st
from supabase import create_client
from typing import Optional, Dict, Any

def connect_db():
    try:
        # Create Supabase client
        supabase = create_client(
            st.secrets["supabase"]["https://duiomhgeqricsyjmeamr.supabase.co"],
            st.secrets["supabase"]["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1aW9taGdlcXJpY3N5am1lYW1yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NDczNTMsImV4cCI6MjA1MDUyMzM1M30.VRVw8jQLSQ3IzWhb2NonPHEQ2Gwq-k7WjvHB3WcLe48"]
        )
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_user_details(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user details from Supabase using email."""
    try:
        supabase = connect_db()
        if not supabase:
            return None

        # Query to fetch username using email
        response = supabase.table('users').select('username').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]  # Returns the first matching user
        return None
        
    except Exception as e:
        st.error(f"Error fetching user details: {e}")
        return None

def home():
    """Display the home page content."""
    if not st.session_state.get("logged_in", False):
        st.error("You must be logged in to access this page.")
        return

    st.title("Welcome to the Home Page!")
    
    # Get current user's email from session state
    user_email = st.session_state.get("email")
    if user_email:
        # Fetch user details
        user_details = get_user_details(user_email)
        if user_details:
            st.write(f"Welcome back, {user_details['username']}!")
        else:
            st.warning("Could not fetch user details.")
    else:
        st.warning("User email not found in session.")

if __name__ == "__main__":
    home()