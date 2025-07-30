import streamlit as st

def show_landing():
    st.header("BRANDFORGE")
    st.subheader("Forge your brand identity in seconds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            st.session_state.show_login = True
            st.session_state.show_signup = False
    
    with col2:
        if st.button("Signup"):
            st.session_state.show_signup = True
            st.session_state.show_login = False