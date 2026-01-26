# import html
# import os

# import requests
# import streamlit as st


# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# st.set_page_config(page_title="Multimodal RAG Chatbot", layout="wide")

# if "token" not in st.session_state:
#     st.session_state.token = None
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "document_id" not in st.session_state:
#     st.session_state.document_id = None
# if "last_upload" not in st.session_state:
#     st.session_state.last_upload = None


# def _auth_headers():
#     return {"Authorization": f"Bearer {st.session_state.token}"}


# def _load_user():
#     if not st.session_state.token:
#         return
#     if st.session_state.user:
#         return
#     try:
#         response = requests.get(f"{BACKEND_URL}/me", headers=_auth_headers(), timeout=10)
#         if response.status_code == 200:
#             st.session_state.user = response.json()
#     except requests.RequestException:
#         st.session_state.token = None
#         st.session_state.user = None


# def _render_bubble(role: str, content: str):
#     safe_content = html.escape(content).replace("\n", "<br>")
#     col_left, col_right = st.columns([1, 1])
#     bubble_class = "bot-bubble" if role == "assistant" else "user-bubble"
#     if role == "assistant":
#         with col_left:
#             st.markdown(
#                 f'<div class="{bubble_class}">{safe_content}</div>',
#                 unsafe_allow_html=True,
#             )
#     else:
#         with col_right:
#             st.markdown(
#                 f'<div class="{bubble_class}">{safe_content}</div>',
#                 unsafe_allow_html=True,
#             )


# def _file_kind(filename: str) -> str:
#     ext = os.path.splitext(filename)[1].lower().strip(".")
#     if ext in {"pdf", "docx", "txt"}:
#         return "document"
#     if ext in {"png", "jpg", "jpeg"}:
#         return "image"
#     return "unknown"


# if not st.session_state.token:
#     st.title("Multimodal RAG Chatbot")
#     st.info("Please log in to access the chatbot.")
#     st.page_link("pages/login.py", label="Log In", icon="🔐")
#     st.page_link("pages/signup.py", label="Sign Up", icon="📝")
#     st.stop()


# _load_user()
# username = st.session_state.user["username"] if st.session_state.user else "there"

# st.markdown(
#     """
# <style>
# .chat-container { max-width: 900px; margin: 0 auto; }
# .user-bubble {
#   background: #e7f0ff;
#   border-radius: 16px;
#   padding: 10px 14px;
#   margin: 6px 0;
#   text-align: left;
#   color: #111;
# }
# .bot-bubble {
#   background: #f5f5f7;
#   border-radius: 16px;
#   padding: 10px 14px;
#   margin: 6px 0;
#   text-align: left;
#   color: #111;
# }
# </style>
# """,
#     unsafe_allow_html=True,
# )

# with st.container():
#     st.title("Multimodal RAG Chatbot")
#     st.caption(f"Hi {username}, how can I assist you today?")

#     col_left, col_right = st.columns([4, 1])
#     with col_right:
#         if st.button("Log Out"):
#             st.session_state.token = None
#             st.session_state.user = None
#             st.session_state.messages = []
#             st.switch_page("pages/login.py")

#     uploaded_file = st.file_uploader(
#         "Upload a document (PDF/DOCX/TXT) or image (PNG/JPG)",
#         type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
#     )

#     if uploaded_file is not None:
#         file_kind = _file_kind(uploaded_file.name)
#         upload_signature = (uploaded_file.name, len(uploaded_file.getvalue()))
#         if file_kind == "document":
#             if st.session_state.last_upload != upload_signature:
#                 with st.spinner("Indexing document..."):
#                     try:
#                         files = {
#                             "file": (
#                                 uploaded_file.name,
#                                 uploaded_file.getvalue(),
#                                 uploaded_file.type,
#                             )
#                         }
#                         response = requests.post(
#                             f"{BACKEND_URL}/upload",
#                             files=files,
#                             headers=_auth_headers(),
#                             timeout=300,
#                         )
#                         if response.status_code != 200:
#                             st.error(response.text)
#                             st.session_state.document_id = None
#                         else:
#                             st.session_state.document_id = response.json().get(
#                                 "document_id"
#                             )
#                             st.session_state.last_upload = upload_signature
#                             st.success("Document indexed and ready for questions.")
#                     except requests.RequestException as exc:
#                         st.error(f"Upload failed: {exc}")
#                         st.session_state.document_id = None
#         else:
#             st.session_state.document_id = None

#     st.markdown('<div class="chat-container">', unsafe_allow_html=True)
#     for msg in st.session_state.messages:
#         _render_bubble(msg["role"], msg["content"])
#     st.markdown("</div>", unsafe_allow_html=True)

#     with st.form("chat_form", clear_on_submit=True):
#         input_col, btn_col = st.columns([6, 1])
#         with input_col:
#             user_question = st.text_input("Message", label_visibility="collapsed")
#         with btn_col:
#             submitted = st.form_submit_button("Send")

#     if submitted and user_question:
#         if uploaded_file is None:
#             st.warning("Please upload a file before asking a question.")
#         else:
#             file_kind = _file_kind(uploaded_file.name)
#             if file_kind == "document" and not st.session_state.document_id:
#                 st.warning("Please upload a document first.")
#                 st.stop()

#             st.session_state.messages.append({"role": "user", "content": user_question})
#             _render_bubble("user", user_question)

#             with st.spinner("Thinking..."):
#                 try:
#                     files = None
#                     data = {"question": user_question}
#                     if file_kind == "image":
#                         files = {
#                             "file": (
#                                 uploaded_file.name,
#                                 uploaded_file.getvalue(),
#                                 uploaded_file.type,
#                             )
#                         }
#                     if file_kind == "document":
#                         data["document_id"] = st.session_state.document_id
#                     response = requests.post(
#                         f"{BACKEND_URL}/query",
#                         files=files,
#                         data=data,
#                         headers=_auth_headers(),
#                         timeout=300,
#                     )
#                     if response.status_code != 200:
#                         st.error(response.text)
#                     else:
#                         answer = response.json().get("answer", "")
#                         st.session_state.messages.append(
#                             {"role": "assistant", "content": answer}
#                         )
#                         _render_bubble("assistant", answer)
#                 except requests.RequestException as exc:
#                     st.error(f"Request failed: {exc}")


import html
import os
import uuid

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.set_page_config(page_title="RAG Assistant", layout="wide")

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "chats" not in st.session_state:
    st.session_state.chats = []
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None


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


def _get_active_chat():
    """Get the currently active chat"""
    for chat in st.session_state.chats:
        if chat["chat_id"] == st.session_state.active_chat_id:
            return chat
    return None


def _create_new_chat():
    """Create a new empty chat"""
    new_chat = {
        "chat_id": str(uuid.uuid4()),
        "title": "New Chat",
        "document_id": None,
        "filename": None,
        "messages": []
    }
    st.session_state.chats.append(new_chat)
    st.session_state.active_chat_id = new_chat["chat_id"]
    st.rerun()


def _delete_chat(chat_id):
    """Delete a chat and its associated document"""
    chat_to_delete = None
    for chat in st.session_state.chats:
        if chat["chat_id"] == chat_id:
            chat_to_delete = chat
            break
    
    if chat_to_delete:
        # Call backend to delete document if exists
        if chat_to_delete["document_id"]:
            try:
                requests.post(
                    f"{BACKEND_URL}/delete_document",
                    json={"document_id": chat_to_delete["document_id"]},
                    headers=_auth_headers(),
                    timeout=10
                )
            except requests.RequestException:
                pass  # Silently fail if delete doesn't work
        
        # Remove chat from list
        st.session_state.chats = [c for c in st.session_state.chats if c["chat_id"] != chat_id]
        
        # Update active chat
        if st.session_state.active_chat_id == chat_id:
            if st.session_state.chats:
                st.session_state.active_chat_id = st.session_state.chats[0]["chat_id"]
            else:
                st.session_state.active_chat_id = None
        
        st.rerun()


def _remove_file_from_chat():
    """Remove file from active chat"""
    active_chat = _get_active_chat()
    if active_chat and active_chat["document_id"]:
        # Call backend to delete document
        try:
            requests.post(
                f"{BACKEND_URL}/delete_document",
                json={"document_id": active_chat["document_id"]},
                headers=_auth_headers(),
                timeout=10
            )
        except requests.RequestException:
            pass
        
        # Clear file from chat
        active_chat["document_id"] = None
        active_chat["filename"] = None
        st.rerun()


def _switch_chat(chat_id):
    """Switch to a different chat"""
    st.session_state.active_chat_id = chat_id
    st.rerun()


def _file_kind(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().strip(".")
    if ext in {"pdf", "docx", "txt"}:
        return "document"
    if ext in {"png", "jpg", "jpeg"}:
        return "image"
    return "unknown"


def _generate_chat_title(first_message: str) -> str:
    """Generate a chat title from the first user message"""
    title = first_message[:40].strip()
    if len(first_message) > 40:
        title += "..."
    return title


# Check authentication
if not st.session_state.token:
    st.title("RAG Assistant")
    st.info("Please log in to access the chatbot.")
    st.page_link("pages/login.py", label="Log In", icon="🔐")
    st.page_link("pages/signup.py", label="Sign Up", icon="📝")
    st.stop()


_load_user()
username = st.session_state.user["username"] if st.session_state.user else "there"

# Create initial chat if none exist
if not st.session_state.chats:
    _create_new_chat()

# Ensure active chat is set
if not st.session_state.active_chat_id and st.session_state.chats:
    st.session_state.active_chat_id = st.session_state.chats[0]["chat_id"]

active_chat = _get_active_chat()

# CSS Styling
st.markdown(
    """
<style>
/* Global styles */
.main {
    background-color: #f8f9fa;
}

/* Top bar styling */
.top-bar {
    background: #ffffff;
    padding: 16px 24px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
}

.top-bar-title {
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
}

.top-bar-user {
    font-size: 14px;
    color: #666;
    margin-right: 12px;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #ffffff;
    padding: 16px;
}

/* Chat list item */
.chat-item {
    background: #f5f5f7;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background 0.2s;
}

.chat-item:hover {
    background: #e8e8ea;
}

.chat-item-active {
    background: #007aff;
    color: #ffffff;
}

.chat-item-active:hover {
    background: #0066dd;
}

.chat-title {
    font-size: 14px;
    font-weight: 500;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Chat bubbles */
.user-bubble {
    background: #007aff;
    color: #ffffff;
    border-radius: 18px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 70%;
    float: right;
    clear: both;
    text-align: left;
    word-wrap: break-word;
}

.bot-bubble {
    background: #e9ecef;
    color: #1a1a1a;
    border-radius: 18px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 70%;
    float: left;
    clear: both;
    text-align: left;
    word-wrap: break-word;
}

/* Chat container */
.chat-container {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
}

/* File indicator */
.file-indicator {
    background: #e7f3ff;
    border: 1px solid #007aff;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 12px 0;
    display: inline-block;
    font-size: 14px;
    color: #007aff;
}

/* Greeting text */
.greeting {
    font-size: 18px;
    color: #666;
    margin: 24px 0;
    text-align: center;
}

/* Typing indicator */
.typing-indicator {
    background: #e9ecef;
    color: #666;
    border-radius: 18px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 70px;
    float: left;
    clear: both;
    text-align: center;
    font-size: 20px;
}

/* Input area */
.stTextInput > div > div > input {
    border-radius: 24px;
    padding: 12px 20px;
    border: 1px solid #e0e0e0;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
</style>
""",
    unsafe_allow_html=True,
)

# Top Bar
col1, col2, col3 = st.columns([2, 5, 1])
with col1:
    st.markdown('<div class="top-bar-title">RAG Assistant</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="top-bar-user">Logged in as: <strong>{username}</strong></div>', unsafe_allow_html=True)
with col3:
    if st.button("Logout", key="logout_btn", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.chats = []
        st.session_state.active_chat_id = None
        st.switch_page("pages/login.py")

st.markdown("---")

# Layout: Sidebar + Main Area
sidebar_col, main_col = st.columns([1, 3])

# Sidebar - Chat List
with sidebar_col:
    st.markdown("### Chats")
    
    if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
        _create_new_chat()
    
    st.markdown("---")
    
    # Display all chats
    for chat in st.session_state.chats:
        is_active = chat["chat_id"] == st.session_state.active_chat_id
        
        col_title, col_delete = st.columns([4, 1])
        
        with col_title:
            if st.button(
                chat["title"],
                key=f"chat_{chat['chat_id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                _switch_chat(chat["chat_id"])
        
        with col_delete:
            if st.button("🗑️", key=f"del_{chat['chat_id']}", help="Delete chat"):
                _delete_chat(chat["chat_id"])

# Main Chat Area
with main_col:
    if active_chat:
        # Greeting
        if not active_chat["messages"]:
            st.markdown(
                f'<div class="greeting">Hi {username}, how can I assist you today?</div>',
                unsafe_allow_html=True
            )
        
        # File indicator
        if active_chat["filename"]:
            col_file, col_remove = st.columns([3, 1])
            with col_file:
                st.markdown(
                    f'<div class="file-indicator">📄 File: {active_chat["filename"]}</div>',
                    unsafe_allow_html=True
                )
            with col_remove:
                if st.button("Remove File", key="remove_file_btn"):
                    _remove_file_from_chat()
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload a document (PDF/DOCX/TXT) or image (PNG/JPG)",
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
            key=f"uploader_{active_chat['chat_id']}"
        )
        
        # Handle file upload
        if uploaded_file is not None:
            file_kind = _file_kind(uploaded_file.name)
            
            # Only process document uploads (images are handled per-query)
            if file_kind == "document":
                # Check if this is a new file
                if active_chat["filename"] != uploaded_file.name:
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
                                active_chat["document_id"] = None
                                active_chat["filename"] = None
                            else:
                                active_chat["document_id"] = response.json().get("document_id")
                                active_chat["filename"] = uploaded_file.name
                                st.success("Document indexed and ready for questions.")
                                st.rerun()
                        except requests.RequestException as exc:
                            st.error(f"Upload failed: {exc}")
                            active_chat["document_id"] = None
                            active_chat["filename"] = None
        
        # Chat messages container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for msg in active_chat["messages"]:
            safe_content = html.escape(msg["content"]).replace("\n", "<br>")
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">{safe_content}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bot-bubble">{safe_content}</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Input form
        with st.form("chat_form", clear_on_submit=True):
            input_col, btn_col = st.columns([6, 1])
            with input_col:
                user_question = st.text_input("Message", label_visibility="collapsed", placeholder="Type your message...")
            with btn_col:
                submitted = st.form_submit_button("Send")
        
        # Handle message submission
        if submitted and user_question:
            # Check if file is needed
            if not uploaded_file:
                st.warning("Please upload a file before asking a question.")
            else:
                file_kind = _file_kind(uploaded_file.name)
                
                if file_kind == "document" and not active_chat["document_id"]:
                    st.warning("Please wait for the document to be indexed.")
                    st.stop()
                
                # Update chat title if this is the first message
                if not active_chat["messages"]:
                    active_chat["title"] = _generate_chat_title(user_question)
                
                # Add user message
                active_chat["messages"].append({"role": "user", "content": user_question})
                
                # Show user message immediately
                safe_content = html.escape(user_question).replace("\n", "<br>")
                st.markdown(
                    f'<div class="user-bubble">{safe_content}</div>',
                    unsafe_allow_html=True
                )
                
                # Show typing indicator
                st.markdown(
                    '<div class="typing-indicator">...</div>',
                    unsafe_allow_html=True
                )
                
                # Query backend
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
                    elif file_kind == "document":
                        data["document_id"] = active_chat["document_id"]
                    
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
                        active_chat["messages"].append({"role": "assistant", "content": answer})
                        st.rerun()
                
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")
    else:
        st.info("No active chat. Click 'New Chat' to start.")