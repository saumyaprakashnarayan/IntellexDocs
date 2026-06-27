from pathlib import Path
from typing import Any
from sqlalchemy import select
<<<<<<< HEAD
from langchain.chat_models import GoogleGeminiChat
=======
from langchain_google_genai import ChatGoogleGenerativeAI
>>>>>>> 33502da (chore)
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.db.models import DocumentChunk
from app.utils.chroma_client import ChromaClient
from app.utils.embeddings import EmbeddingService
from app.utils.pdf_utils import extract_text_pages
from app.rag.prompts import PROMPT_TEMPLATE, SUMMARY_PROMPT

chroma_client = ChromaClient()
embedding_service = EmbeddingService()

COLLECTION_NAME = "document_chunks"

async def ingest_document(document_id: int, file_path: Path, user_id: int, session: Any) -> None:
    pages = extract_text_pages(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    texts = []
    metadatas = []
    ids = []
    all_chunks = []

    index = 0
    for page_number, page_text in pages:
        if not page_text:
            continue
        page_chunks = splitter.split_text(page_text)
        for chunk_idx, chunk in enumerate(page_chunks, start=1):
            metadata = {
                "user_id": str(user_id),
                "document_id": str(document_id),
                "filename": file_path.name,
                "page": page_number,
                "chunk_id": chunk_idx,
            }
            chunk_record = DocumentChunk(
                document_id=document_id,
                page_number=page_number,
                chunk_index=chunk_idx,
                content=chunk,
                metadata=str(metadata),
            )
            session.add(chunk_record)
            all_chunks.append(chunk_record)
            texts.append(chunk)
            metadatas.append(metadata)
            ids.append(f"{document_id}_{page_number}_{chunk_idx}")
            index += 1

    await session.commit()

    embeddings = embedding_service.embed_texts(texts)
    chroma_client.add(collection_name=COLLECTION_NAME, ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

async def answer_question(question: str, document_ids: list[int], user_id: int) -> tuple[str, list[dict[str, Any]]]:
    query_embedding = embedding_service.embed_query(question)
    filter_metadata = {"user_id": str(user_id)}
    search_results = chroma_client.search(COLLECTION_NAME, query_embedding, n_results=settings.semantic_search_k * 2, filter=filter_metadata)

    docs = search_results.get("documents", [])
    metadatas = search_results.get("metadatas", [])
    distances = search_results.get("distances", [])

    filtered_items = []
    for doc, metadata, distance in zip(docs, metadatas, distances):
        if int(metadata.get("document_id", 0)) in document_ids:
            filtered_items.append((doc, metadata, distance))

    docs, metadatas, distances = zip(*filtered_items) if filtered_items else ([], [], [])

    context_sections = []
    sources = []
    for idx, chunk in enumerate(docs):
        if not chunk:
            continue
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else 0.0
        context_sections.append(f"Page {metadata.get('page', '?')} from {metadata.get('filename', 'unknown')}: {chunk}")
        sources.append(
            {
                "document": metadata.get("filename", "unknown"),
                "page": int(metadata.get("page", 0)),
                "chunk_id": int(metadata.get("chunk_id", 0)),
                "similarity": float(1 - distance) if isinstance(distance, (float, int)) else 0.0,
            }
        )

    prompt = PROMPT_TEMPLATE.format(context="\n\n".join(context_sections), question=question)
    answer = await _call_llm(prompt)
    return answer, sources

async def generate_document_summary(document_id: int, user_id: int, session: Any) -> Any:
    result = await session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.page_number)
    )
    chunks = result.all()
    combined_text = "\n\n".join([chunk.content for chunk in chunks])
    prompt = SUMMARY_PROMPT.format(context=combined_text)
    raw_summary = await _call_llm(prompt)
    key_points = []
    findings = []
    if "Key points:" in raw_summary:
        split = raw_summary.split("Key points:")
        key_points = [line.strip().lstrip("- ") for line in split[1].splitlines() if line.strip()]
    if "Important findings:" in raw_summary:
        split = raw_summary.split("Important findings:")
        findings = [line.strip().lstrip("- ") for line in split[1].splitlines() if line.strip()]
    return {
        "document_id": document_id,
        "summary": raw_summary,
        "key_points": key_points,
        "findings": findings,
    }

async def _call_llm(prompt: str) -> str:
<<<<<<< HEAD
    llm = GoogleGeminiChat(model=settings.gemini_model, api_key=settings.gemini_api_key)
=======
    llm = ChatGoogleGenerativeAI(model=settings.gemini_model, google_api_key=settings.gemini_api_key)
>>>>>>> 33502da (chore)
    response = llm([HumanMessage(content=prompt)])
    return response.content
