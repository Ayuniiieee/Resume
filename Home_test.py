import streamlit as st
from supabase import create_client
from typing import Optional, Dict, Any
from config import SUPABASE_URL, SUPABASE_KEY

def connect_db():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_user_details(email: str) -> Optional[Dict[str, Any]]:
    try:
        supabase = connect_db()
        if not supabase:
            return None

        response = supabase.table('users').select('username').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
        
    except Exception as e:
        st.error(f"Error fetching user details: {e}")
        return None

def home():
    if st.session_state.get("logged_in", False):
        st.error("You must be logged in to access this page.")
        st.rerun()
        return

    st.title("Welcome to the Home Page!")
    
    user_email = st.session_state.get("email")
    if user_email:
        user_details = get_user_details(user_email)
        if user_details:
            st.write(f"Welcome back, {user_details['username']}!")
        else:
            st.warning("Could not fetch user details.")
    else:
        st.warning("User email not found in session.")

if __name__ == "__main__":
    home()