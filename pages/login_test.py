import streamlit as st
import bcrypt
import base64
from supabase import create_client

def connect_db():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return encoded
    except Exception as e:
        st.warning(f"Could not load background image: {e}")
        return None

background_image = get_base64_image('./Logo/background1.png')

def login():
    # Styling
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

    st.markdown(
        """
        <style>
            .welcome-text {
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                color: white;
                text-shadow: 2px 2px 0 black, -2px -2px 0 black, 2px -2px 0 black, -2px 2px 0 black;
                display: inline;
                margin-right: 10px;
            }
            .edu-title {
                font-size: 36px;
                font-weight: bold;
                text-align: center;
                color: #00BFFF;
                text-shadow: 2px 2px 0 black, -2px -2px 0 black, 2px -2px 0 black, -2px 2px 0 black;
                display: inline;
            }
            .title-container {
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="title-container"><span class="welcome-text">Welcome to</span><span class="edu-title">EduResume</span></div>', unsafe_allow_html=True)

    # Input Fields
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
            # Execute Supabase Query
            response = supabase.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                st.error("No user found with this email.")
                return
                
            user = response.data[0]
            stored_password = user.get('password')
            
            if not stored_password:
                st.error("Invalid user data.")
                return
                
            # Convert stored password to bytes if it's a string
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            # Verify Password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                st.success(f"Welcome, {email}!")
                # Set session state
                st.session_state.update({
                    "logged_in": True,
                    "email": email,
                    "user_type": user.get('user_type', 'unknown'),
                    "user_id": user.get('id'),
                    "page": "home"
                })
                st.rerun()
            else:
                st.error("Invalid password.")
                
        except Exception as e:
            st.error(f"Login error: {e}")
            return

    st.markdown("Don't have an account?")
    if st.button("Sign Up", key="login_page_signup"):
        st.session_state["page"] = "signup"
        st.rerun()

if __name__ == "__main__":
    login()