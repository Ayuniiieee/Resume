import streamlit as st
import pymysql
import re
import bcrypt # type: ignore

def connect_db():
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

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    return (
        len(password) >= 8 and 
        any(c.isupper() for c in password) and 
        any(c.islower() for c in password) and 
        any(c.isdigit() for c in password)
    )

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
            # Ensure the password is encoded to bytes before hashing
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Convert to string for database storage if needed
            # Some databases prefer string representation
            hashed_password_str = hashed_password.decode('utf-8')
        except Exception as hash_error:
            st.error(f"Password hashing error: {hash_error}")
            return

        # Database connection and user registration
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                # Check if email already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    st.error("Email already registered. Please use a different email.")
                    return

                # Check if username already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    st.error("Username already taken. Please choose a different username.")
                    return

                # Insert new user into database
                cursor.execute(
                    "INSERT INTO users (email, username, full_name, password, user_type) VALUES (%s, %s, %s, %s, %s)", 
                    (email, username, full_name, hashed_password, user_type)
                )
                conn.commit()

                st.success("Account created successfully!")
                st.session_state["page"] = "login"
                st.rerun()

            except Exception as e:
                st.error(f"Registration error: {e}")
            finally:
                conn.close()