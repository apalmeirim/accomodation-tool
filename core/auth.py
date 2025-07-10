import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def login_user(email, password):
    supabase = get_supabase_client()
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return result.user

def signup_user(email, password):
    supabase = get_supabase_client()
    result = supabase.auth.sign_up({"email": email, "password": password})
    return result.user

def get_current_user():
    supabase = get_supabase_client()
    session = supabase.auth.get_session()
    return session.user if session else None