import bcrypt
import streamlit as st

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(user_id, username, role):
    st.session_state['user_id'] = user_id
    st.session_state['username'] = username
    st.session_state['role'] = role
    st.session_state['logged_in'] = True
    
def logout():
    for key in ['user_id', 'username', 'role']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['logged_in'] = False
