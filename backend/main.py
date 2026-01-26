import os

os.environ["CHROMA_TELEMETRY"] = "False"

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.auth import create_access_token, get_current_user, hash_password, verify_password
from backend.document_loader import DocumentLoadError
from backend.rag_pipeline import answer_question_with_document_id, index_document
from backend.user_db import create_user, get_user_by_username, init_db
from backend.vision_pipeline import answer_image_question

app = FastAPI(title="Multimodal RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().strip(".")


def _is_image_file(filename: str) -> bool:
    return _get_extension(filename) in {"png", "jpg", "jpeg"}


def _is_document_file(filename: str) -> bool:
    return _get_extension(filename) in {"pdf", "docx", "txt"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/signup")
def signup(payload: SignupRequest):
    if not payload.username or not payload.password or not payload.email:
        raise HTTPException(status_code=400, detail="All fields are required.")

    existing = get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")

    password_hash = hash_password(payload.password)
    user = create_user(payload.username, payload.email, password_hash)
    token = create_access_token(user["id"], user["username"])
    return {"token": token, "user": user}


@app.post("/login")
def login(payload: LoginRequest):
    user = get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_access_token(user["id"], user["username"])
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "email": user["email"]}}


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")
    if not _is_document_file(file.filename):
        raise HTTPException(status_code=400, detail="Only documents are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        document_id = index_document(file_bytes, file.filename)
        return {"document_id": document_id}
    except DocumentLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Server error: {exc}") from exc


@app.post("/query")
async def query(
    question: str = Form(...),
    document_id: str = Form(None),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
):
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    filename = file.filename if file else ""
    try:
        if file and _is_image_file(filename):
            file_bytes = await file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            answer = answer_image_question(file_bytes, question)
            return {"type": "image", "answer": answer}
        if document_id:
            answer = answer_question_with_document_id(document_id, question)
            return {"type": "document", "answer": answer}
    except DocumentLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Server error: {exc}") from exc

    raise HTTPException(
        status_code=400,
        detail="Provide an image file or a document_id for document queries.",
    )
