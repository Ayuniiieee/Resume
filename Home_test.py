import streamlit as st
from supabase import create_client
from typing import Optional, Dict, Any

# Supabase configuration
supabase_url = "YOUR_SUPABASE_URL"
supabase_key = "YOUR_SUPABASE_KEY"

def connect_db():
    """Create and return Supabase client."""
    try:
        return create_client(supabase_url, supabase_key)
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