import streamlit as st
import re
import bcrypt
from supabase import create_client
from typing import Optional

# Supabase configuration
supabase_url = "https://duiomhgeqricsyjmeamr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1aW9taGdlcXJpY3N5am1lYW1yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NDczNTMsImV4cCI6MjA1MDUyMzM1M30.VRVw8jQLSQ3IzWhb2NonPHEQ2Gwq-k7WjvHB3WcLe48"

def connect_db():
    """Create and return Supabase client."""
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def is_valid_password(password: str) -> bool:
    """Validate password requirements."""
    return (
        len(password) >= 8 and 
        any(c.isupper() for c in password) and 
        any(c.islower() for c in password) and 
        any(c.isdigit() for c in password)
    )

def check_existing_user(supabase, email: str, username: str) -> Optional[str]:
    """Check if email or username already exists."""
    try:
        # Check email
        email_response = supabase.table('users').select("*").eq('email', email).execute()
        if email_response.data and len(email_response.data) > 0:
            return "Email already registered. Please use a different email."

        # Check username
        username_response = supabase.table('users').select("*").eq('username', username).execute()
        if username_response.data and len(username_response.data) > 0:
            return "Username already taken. Please choose a different username."

        return None
    except Exception as e:
        st.error(f"Error checking existing user: {e}")
        return "Database error occurred"

def signup():
    st.subheader("Sign Up")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input("Email", placeholder="Enter your email")
        username = st.text_input("Username", placeholder="Choose a username")
        full_name = st.text_input("Full Name", placeholder="Enter your full name")

    with col2:
        password = st.text_input("Password", placeholder="Create a password", type="password")
        confirm_password = st.text_input("Confirm Password", placeholder="Confirm your password", type="password")
        user_type = st.selectbox("User Type", ["", "User", "Parent"])

    # Signup button
    if st.button("Sign Up", key="signup_submit"):
        # Validation checks
        if not all([email, username, full_name, password, confirm_password, user_type]):
            st.error("All fields are required.")
            return
        
        if not is_valid_email(email):
            st.error("Please enter a valid email address.")
            return
        
        if not is_valid_password(password):
            st.error("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        try:
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')
        except Exception as hash_error:
            st.error(f"Password hashing error: {hash_error}")
            return

        # Get Supabase client
        supabase = connect_db()
        if not supabase:
            return

        # Check for existing user
        error_message = check_existing_user(supabase, email, username)
        if error_message:
            st.error(error_message)
            return

        try:
            # Insert new user into Supabase
            user_data = {
                'email': email,
                'username': username,
                'full_name': full_name,
                'password': hashed_password_str,
                'user_type': user_type
            }
            
            response = supabase.table('users').insert([user_data]).execute()  # Note the [user_data] wrapped in list
            
            if response and response.data:
                st.success("Account created successfully!")
                st.session_state["page"] = "login"
                st.rerun()
            else:
                st.error("Failed to create account. Please try again.")

        except Exception as e:
            st.error(f"Registration error: {e}")

if __name__ == "__main__":
    signup()