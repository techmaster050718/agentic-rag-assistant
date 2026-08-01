import os, uuid, shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, AsyncSessionLocal
from app.models.document import Document as DocumentModel, DocumentStatus
from app.schemas.document import DocumentResponse
from app.services.ingestion.parser import parse_document
from app.services.ingestion.chunker import chunk_documents
from app.services.ingestion.embedder import get_embeddings
from app.services.retrieval.vector_store import vector_store
from app.core.logging import get_logger
from app.core.rate_limiter import limiter

router = APIRouter()
logger = get_logger(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_document(document_id: uuid.UUID, file_path: str, file_type: str):
    async with AsyncSessionLocal() as db:
        try:
            raw_docs = parse_document(file_path, file_type)
            if not raw_docs: raise ValueError("No content extracted")
            chunks = chunk_documents(raw_docs)
            if not chunks: raise ValueError("Document resulted in zero chunks")
            
            embeddings_model = get_embeddings()
            texts = [chunk.page_content for chunk in chunks]
            metadatas, chunk_ids = [], []
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                chunk_ids.append(chunk_id)
                meta = chunk.metadata.copy()
                meta["document_id"] = str(document_id)
                meta["source"] = meta.get("source", file_path)
                meta["file_type"] = file_type
                metadatas.append(meta)
            
            embeddings = await embeddings_model.aembed_documents(texts)
            vector_store.add_documents(ids=chunk_ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
            
            doc = await db.get(DocumentModel, document_id)
            if doc:
                doc.status = DocumentStatus.COMPLETED
                await db.commit()
            logger.info("Document processed successfully", document_id=document_id)
        except Exception as e:
            logger.error("Failed to process document", document_id=document_id, error=str(e))
            doc = await db.get(DocumentModel, document_id)
            if doc:
                doc.status = DocumentStatus.FAILED
                await db.commit()
        finally:
            if os.path.exists(file_path): os.remove(file_path)

@router.post("/upload", response_model=DocumentResponse, status_code=202)
@limiter.limit("10/minute")
async def ingest_document(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename: raise HTTPException(status_code=400, detail="No filename provided")
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "txt", "doc", "docx"]: raise HTTPException(status_code=400, detail="Unsupported file type")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    
    new_doc = DocumentModel(title=file.filename, filename=f"{file_id}.{file_ext}", file_type=file_ext, status=DocumentStatus.PROCESSING)
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    background_tasks.add_task(process_document, new_doc.id, file_path, file_ext)
    return new_doc
