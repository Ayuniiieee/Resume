import streamlit as st
import bcrypt
import base64
from supabase import create_client

# Define Supabase credentials directly
SUPABASE_URL = "https://duiomhgeqricsyjmeamr.supabase.co"
SUPABASE_KEY = "your_supabase_key_here"

def connect_db():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.warning(f"Could not load background image: {e}")
        return None

def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    background_image = get_base64_image('./Logo/background1.png')
    
    if background_image:
        st.markdown(
            f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Lilita+One&display=swap');
            .stApp {{
                background-image: url("data:image/png;base64,{background_image}");
                background-size: cover;
                background-position: center;
                font-family: sans-serif;
            }}
            .stApp::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 0;
                pointer-events: none;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<h1 style="color: white;">Welcome to EduResume</h1>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    if st.button("Log In", key="login_submit"):
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        supabase = connect_db()
        if not supabase:
            st.error("Unable to connect to the database.")
            return

        try:
            response = supabase.table('users').select('*').eq('email', email).execute()
            if not response.data:
                st.error("No user found with this email.")
                return
                
            user = response.data[0]
            stored_password = user.get('password')
            if not stored_password or not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                st.error("Invalid email or password.")
                return

            st.success(f"Welcome, {email}!")
            st.session_state.update({
                "logged_in": True,
                "email": email,
                "user_type": user.get('user_type', 'unknown'),
                "user_id": user.get('id'),
                "page": "home"
            })
            # Instead of st.rerun(), just set the page
            st.session_state["page"] = "home"

        except Exception as e:
            st.error(f"Login error: {e}")

    if st.button("Sign Up", key="login_page_signup"):
        st.session_state["page"] = "signup"

if __name__ == "__main__":
    login()