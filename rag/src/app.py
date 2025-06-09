import os
import logging

from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings
from src.chroma import ChromaVectorDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmbedRequest(BaseModel):
    index_name: str
    chunk_size: Optional[int] = 400
    chunk_overlap: Optional[int] = 40


class SearchRequest(BaseModel):
    query: str
    index_name: str
    k: Optional[int] = 2


@app.post("/api/embed")
def embed(request: EmbedRequest, background_tasks: BackgroundTasks):
    try:

        def background_upload():
            embedding = OllamaEmbeddings(
                model="nomic-embed-text",
                base_url=os.getenv("OPENAI_API_URL"),
            )
            vector_db = ChromaVectorDB(
                index_name=request.index_name, embedding=embedding
            )

            documents = ChromaVectorDB.load_documents("data")
            chunks = ChromaVectorDB.split_documents(
                documents, request.chunk_size, request.chunk_overlap
            )
            vector_db.add_documents(
                documents=chunks,
                metadata=[
                    {
                        "user:editor": False,
                        "user:owner": True,
                        "user:admin": True,
                        "user:superadmin": True,
                        "user:root": True,
                        "user:system": True,
                        "user:anonymous": True,
                    }
                ],
            )

        background_tasks.add_task(background_upload)
        return {"success": True, "message": "Upload started in background"}
    except Exception as e:
        logger.error(f"Error in /api/embed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/search")
def search(request: SearchRequest):
    try:
        embedding = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=os.getenv("OPENAI_API_URL"),
        )
        vector_db = ChromaVectorDB(index_name=request.index_name, embedding=embedding)

        # Search with optional metadata filtering for allowed users
        results_editor = vector_db.search(
            query=request.query, k=request.k, filter={"user:editor": True}
        )

        # Search with optional metadata filtering for allowed users
        results_owner = vector_db.search(
            query=request.query, k=request.k, filter={"user:owner": True}
        )

        # Search (I no see any documents)

        return {
            "success": True,
            "results_editor": results_editor,
            "results_owner": results_owner,
        }
    except Exception as e:
        logger.error(f"Error in /api/search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
