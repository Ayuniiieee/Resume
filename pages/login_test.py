import streamlit as st
import bcrypt
import base64
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def connect_db():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded

background_image = get_base64_image('./Logo/background1.png')

def login():
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

    st.markdown("""
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
    """, unsafe_allow_html=True)

    st.markdown('<div class="title-container"><span class="welcome-text">Welcome to</span><span class="edu-title">EduResume</span></div>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    if st.button("Log In", key="login_submit"):
        supabase = connect_db()
        if supabase:
            try:
                response = supabase.table('users').select('*').eq('email', email).execute()
                
                if response.data and len(response.data) > 0:
                    user = response.data[0]
                    stored_password = user['password']
                    if isinstance(stored_password, str):
                        stored_password = stored_password.encode('utf-8')
                    
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        st.success(f"Welcome, {email}!")
                        st.session_state["logged_in"] = True
                        st.session_state["email"] = email
                        st.session_state["user_type"] = user['user_type']
                        st.session_state["user_id"] = user['id']
                        st.session_state["page"] = "home"
                        st.rerun()
                    else:
                        st.error("Invalid password.")
                else:
                    st.error("No user found with this email.")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

    st.markdown("Don't have an account?")
    if st.button("Sign Up", key="login_page_signup"):
        st.session_state["page"] = "signup"
        st.rerun()

if __name__ == "__main__":
    login()