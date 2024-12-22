import streamlit as st
import pymysql

# Database connection
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

# Function to fetch user details
def get_user_details(email):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Query to fetch username using email
            cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
            user_details = cursor.fetchone()
            return user_details  # Returns a tuple (username,)
        except pymysql.MySQLError as e:
            st.error(f"Error fetching user details: {e}")
        finally:
            conn.close()
    return None

def home():
    if not st.session_state.get("logged_in", False):
        st.error("You must be logged in to access this page.")
        return

    st.title("Welcome to the Home Page!")

