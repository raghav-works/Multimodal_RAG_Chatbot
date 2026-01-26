import os

os.environ["CHROMA_TELEMETRY"] = "False"

from typing import Optional

from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, UploadFile
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


class QueryRequest(BaseModel):
    document_id: Optional[str] = None
    question: str


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
    return {"access_token": token, "user": user}


@app.post("/login")
def login(payload: LoginRequest):
    user = get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_access_token(user["id"], user["username"])
    return {
        "access_token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
    }


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}


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
    payload: QueryRequest = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")
    if not payload.document_id:
        raise HTTPException(status_code=400, detail="document_id is required.")

    try:
        answer = answer_question_with_document_id(payload.document_id, payload.question)
        return {"answer": answer}
    except DocumentLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Server error: {exc}") from exc


@app.post("/image_query")
async def image_query(
    question: str = Form(...),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not image or not image.filename:
        raise HTTPException(status_code=400, detail="Image file is required.")
    if not _is_image_file(image.filename):
        raise HTTPException(status_code=400, detail="Only PNG and JPG images are supported.")
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    file_bytes = await image.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        answer = answer_image_question(file_bytes, question)
        return {"answer": answer}
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Server error: {exc}") from exc
