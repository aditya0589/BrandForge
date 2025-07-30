import streamlit as st
import sqlite3
import bcrypt
from services.logo_generator import show_logo_generator
from services.image_editor import show_image_editor
from services.brand_story_generator import show_brand_story_generator
from services.brand_kit_generator import show_brand_kit_generator

# Database setup
def init_db():
    conn = sqlite3.connect('brandforge.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

# User authentication
def register_user(username, password):
    conn = sqlite3.connect('brandforge.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('brandforge.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

def main():
    # Custom CSS for navbar and app styling
    st.markdown(
        """
        <style>
        .navbar {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .stSidebar .stSelectbox {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            padding: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    init_db()
    st.title("BRANDFORGE")
    st.subheader("Forge your brand identity in seconds")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        choice = st.selectbox("Select Action", ["Login", "Signup"], key="auth_action")
        
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        
        if choice == "Signup":
            if st.button("Signup", key="signup_button"):
                if username and password:
                    if register_user(username, password):
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Please enter both username and password.")
        
        elif choice == "Login":
            if st.button("Login", key="login_button"):
                if username and password:
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("Please enter both username and password.")
    
    else:
        # Navbar in sidebar
        st.sidebar.markdown('<div class="navbar">ImageProAI Navigation</div>', unsafe_allow_html=True)
        page = st.sidebar.selectbox(
            "Select a Tool",
            ["Logo Generator", "Image Editor", "Brand Story Generator", "Brand Kit Generator"],
            key="navbar_select"
        )
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
        
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        # Display selected page
        if page == "Logo Generator":
            show_logo_generator()
        elif page == "Image Editor":
            show_image_editor()
        elif page == "Brand Story Generator":
            show_brand_story_generator()
        elif page == "Brand Kit Generator":
            show_brand_kit_generator()

if __name__ == "__main__":
    main()