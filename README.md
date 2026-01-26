# Multimodal RAG Chatbot

Simple local multimodal chatbot that supports:
- Document Q&A with RAG (PDF/DOCX/TXT)
- Image Q&A with a vision-language model (PNG/JPG)

## Requirements
- Python 3.10
- Ollama installed and running

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Pull Ollama models:
   - `ollama pull llama3:8b-instruct`
   - `ollama pull llava:latest`

## Run the backend
From the project root:
- `uvicorn backend.main:app --reload`

The API will be available at `http://localhost:8000`.

## Run the frontend
In another terminal:
- `streamlit run frontend/app.py`

The UI will be available at `http://localhost:8501`.

## Usage
1. Sign up or log in on the Streamlit pages.
2. Upload a document or image in the chat page.
3. Ask a question in the message box.
4. The backend routes the request to either:
   - Text RAG pipeline (documents)
   - Vision QA pipeline (images)

## Notes
- The vector database persists to `data/chroma_db`.
- The first run will download the embedding model `BAAI/bge-large-en-v1.5`.
- If Ollama is not running, the backend will return an error.

## Example RAG Prompt Template
```
You are a helpful assistant. Answer using only the context.
If the answer is not in the context, say you do not know.

Context:
{context}

Question:
{question}

Answer:
```
