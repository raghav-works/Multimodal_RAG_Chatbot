# import os

# import requests
# import streamlit as st


# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# st.set_page_config(page_title="Login", layout="centered")
# st.title("Login")
# st.caption("Sign in to access the chatbot.")

# if "token" not in st.session_state:
#     st.session_state.token = None

# if "user" not in st.session_state:
#     st.session_state.user = None

# with st.form("login_form"):
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     submitted = st.form_submit_button("Log In")

# if submitted:
#     if not username or not password:
#         st.error("Please enter your username and password.")
#     else:
#         try:
#             response = requests.post(
#                 f"{BACKEND_URL}/login",
#                 json={"username": username, "password": password},
#                 timeout=30,
#             )
#             if response.status_code != 200:
#                 st.error(response.text)
#             else:
#                 data = response.json()
#                 st.session_state.token = data.get("token")
#                 st.session_state.user = data.get("user")
#                 st.success("Logged in successfully.")
#                 st.switch_page("app.py")
#         except requests.RequestException as exc:
#             st.error(f"Login failed: {exc}")

# st.page_link("pages/signup.py", label="Don't have an account? Sign up", icon="📝")


import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Login", layout="centered")
st.title("Login")
st.caption("Sign in to access the chatbot.")

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log In")

if submitted:
    if not username or not password:
        st.error("Please enter your username and password.")
    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password": password},
                timeout=30,
            )
            if response.status_code != 200:
                st.error(response.text)
            else:
                data = response.json()
                st.session_state.token = data.get("token")
                st.session_state.user = data.get("user")
                st.success("Logged in successfully.")
                st.switch_page("app.py")
        except requests.RequestException as exc:
            st.error(f"Login failed: {exc}")

st.page_link("pages/signup.py", label="Don't have an account? Sign up", icon="📝")
