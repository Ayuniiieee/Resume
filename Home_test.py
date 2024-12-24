import streamlit as st
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def connect_db():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def home():
    # Custom CSS
    st.markdown("""
        <style>
        /* Logo and title styling */
        .eduresume-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .cap-icon {
            color: #FFD700;
            font-size: 40px;
        }
        .eduresume-text {
            color: #87CEEB;
            font-size: 48px;
            font-weight: bold;
            margin: 0;
        }
        .welcome-text {
            color: white;
            font-size: 16px;
            margin-top: 20px;
            line-height: 1.6;
        }
        /* Container styling */
        .main-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
        }
        /* Button styling */
        .stButton > button {
            background-color: #2196F3;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            margin: 10px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #1976D2;
        }
        /* Dark overlay for background */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("background-image.jpg");
            background-size: cover;
        }
        </style>
        """, unsafe_allow_html=True)

    # Logo and Title
    st.markdown("""
        <div class="eduresume-logo">
            <span class="cap-icon">🎓</span>
            <h1 class="eduresume-text">EduResume</h1>
        </div>
        """, unsafe_allow_html=True)

    # Welcome Text
    st.markdown("""
        <div class="welcome-text">
        Selamat datang ke Edu Resume – platform pintar yang direka khas untuk membantu anda membina dan 
        meningkatkan peluang pekerjaan dalam bidang pendidikan anda! Di sini, kami memudahkan anda 
        memilih kerjaya, pilihan anda melibatkan pengalaman, kemahiran, dan kelayakan anda dalam bidang 
        pendidikan. Hanya dengan beberapa langkah mudah, anda boleh memuat naik butiran akademik dan 
        profesional anda, dan sistem kami akan memberi cadangan kerjeya di dalam menjadi tutor peribadi. 
        Serta kami dan mula bina profil yang dapat membuka lebih banyak peluang kerjeya pendidikan untuk masa 
        depan yang cerah!
        </div>
        """, unsafe_allow_html=True)

    # Create two columns for the buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Periksa Resume", use_container_width=True):
            st.session_state["page"] = "check"
            st.rerun()

    with col2:
        if st.button("Muat Naik Kerja", use_container_width=True):
            st.session_state["page"] = "upload"
            st.rerun()

    # Add the resume image to the right side
    st.sidebar.image("./resumegrafik.png", 
                    use_column_width=True)

if __name__ == "__main__":
    home()