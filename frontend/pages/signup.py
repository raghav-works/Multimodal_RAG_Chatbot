import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Sign Up", layout="centered")
st.title("Create Account")
st.caption("Sign up to start chatting.")

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

with st.form("signup_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign Up")

if submitted:
    if not username or not email or not password:
        st.error("Please fill out all fields.")
    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/signup",
                json={"username": username, "email": email, "password": password},
                timeout=30,
            )
            if response.status_code != 200:
                st.error(response.text)
            else:
                data = response.json()
                st.session_state.token = data.get("token")
                st.session_state.user = data.get("user")
                st.success("Account created.")
                st.switch_page("app.py")
        except requests.RequestException as exc:
            st.error(f"Signup failed: {exc}")

st.page_link("pages/login.py", label="Already have an account? Log in", icon="🔐")
