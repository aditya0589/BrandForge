import streamlit as st
import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect('brandforge.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT UNIQUE, password BLOB)''')
    conn.commit()
    return conn

def show_login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="loggin-button"):
        if username and password:
            conn = init_db()
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = c.fetchone()
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.session_state.show_login = False
            else:
                st.error("Invalid username or password")
        else:
            st.error("Please fill in all fields")