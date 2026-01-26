import html
import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.set_page_config(page_title="Multimodal RAG Chatbot", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "last_upload" not in st.session_state:
    st.session_state.last_upload = None


def _auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _load_user():
    if not st.session_state.token:
        return
    if st.session_state.user:
        return
    try:
        response = requests.get(f"{BACKEND_URL}/me", headers=_auth_headers(), timeout=10)
        if response.status_code == 200:
            st.session_state.user = response.json()
    except requests.RequestException:
        st.session_state.token = None
        st.session_state.user = None


def _render_bubble(role: str, content: str):
    safe_content = html.escape(content).replace("\n", "<br>")
    col_left, col_right = st.columns([1, 1])
    bubble_class = "bot-bubble" if role == "assistant" else "user-bubble"
    if role == "assistant":
        with col_left:
            st.markdown(
                f'<div class="{bubble_class}">{safe_content}</div>',
                unsafe_allow_html=True,
            )
    else:
        with col_right:
            st.markdown(
                f'<div class="{bubble_class}">{safe_content}</div>',
                unsafe_allow_html=True,
            )


def _file_kind(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().strip(".")
    if ext in {"pdf", "docx", "txt"}:
        return "document"
    if ext in {"png", "jpg", "jpeg"}:
        return "image"
    return "unknown"


if not st.session_state.token:
    st.title("Multimodal RAG Chatbot")
    st.info("Please log in to access the chatbot.")
    st.page_link("pages/login.py", label="Log In", icon="🔐")
    st.page_link("pages/signup.py", label="Sign Up", icon="📝")
    st.stop()


_load_user()
username = st.session_state.user["username"] if st.session_state.user else "there"

st.markdown(
    """
<style>
.chat-container { max-width: 900px; margin: 0 auto; }
.user-bubble {
  background: #e7f0ff;
  border-radius: 16px;
  padding: 10px 14px;
  margin: 6px 0;
  text-align: left;
  color: #111;
}
.bot-bubble {
  background: #f5f5f7;
  border-radius: 16px;
  padding: 10px 14px;
  margin: 6px 0;
  text-align: left;
  color: #111;
}
</style>
""",
    unsafe_allow_html=True,
)

with st.container():
    st.title("Multimodal RAG Chatbot")
    st.caption(f"Hi {username}, how can I assist you today?")

    col_left, col_right = st.columns([4, 1])
    with col_right:
        if st.button("Log Out"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.messages = []
            st.switch_page("pages/login.py")

    uploaded_file = st.file_uploader(
        "Upload a document (PDF/DOCX/TXT) or image (PNG/JPG)",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        file_kind = _file_kind(uploaded_file.name)
        upload_signature = (uploaded_file.name, len(uploaded_file.getvalue()))
        if file_kind == "document":
            if st.session_state.last_upload != upload_signature:
                with st.spinner("Indexing document..."):
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }
                        response = requests.post(
                            f"{BACKEND_URL}/upload",
                            files=files,
                            headers=_auth_headers(),
                            timeout=300,
                        )
                        if response.status_code != 200:
                            st.error(response.text)
                            st.session_state.document_id = None
                        else:
                            st.session_state.document_id = response.json().get(
                                "document_id"
                            )
                            st.session_state.last_upload = upload_signature
                            st.success("Document indexed and ready for questions.")
                    except requests.RequestException as exc:
                        st.error(f"Upload failed: {exc}")
                        st.session_state.document_id = None
        else:
            st.session_state.document_id = None

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        _render_bubble(msg["role"], msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([6, 1])
        with input_col:
            user_question = st.text_input("Message", label_visibility="collapsed")
        with btn_col:
            submitted = st.form_submit_button("Send")

    if submitted and user_question:
        if uploaded_file is None:
            st.warning("Please upload a file before asking a question.")
        else:
            file_kind = _file_kind(uploaded_file.name)
            if file_kind == "document" and not st.session_state.document_id:
                st.warning("Please upload a document first.")
                st.stop()

            st.session_state.messages.append({"role": "user", "content": user_question})
            _render_bubble("user", user_question)

            with st.spinner("Thinking..."):
                try:
                    files = None
                    data = {"question": user_question}
                    if file_kind == "image":
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }
                    if file_kind == "document":
                        data["document_id"] = st.session_state.document_id
                    response = requests.post(
                        f"{BACKEND_URL}/query",
                        files=files,
                        data=data,
                        headers=_auth_headers(),
                        timeout=300,
                    )
                    if response.status_code != 200:
                        st.error(response.text)
                    else:
                        answer = response.json().get("answer", "")
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                        _render_bubble("assistant", answer)
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")
