"""
app/rag/pipeline.py
===================
The retrieval-augmented generation (RAG) pipeline.

RAG works by finding document chunks that are semantically similar to the
user's question, injecting those chunks as context into an LLM prompt, and
returning the model's answer alongside citations to the source pages.

The three public functions cover the complete lifecycle of a document:
  ingest_document        — PDF → chunks → embeddings → stored
  answer_question        — question → retrieval → LLM → answer + citations
  generate_document_summary — all chunks → LLM → structured summary
"""

import asyncio
from functools import partial
from pathlib import Path
from typing import Any

from sqlalchemy import select

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.db.models import DocumentChunk
from app.utils.chroma_client import ChromaClient
from app.utils.embeddings import EmbeddingService
from app.utils.pdf_utils import extract_text_pages
from app.rag.prompts import PROMPT_TEMPLATE, SUMMARY_PROMPT

# All users' chunks share one collection; the user_id metadata field separates them
COLLECTION_NAME = "document_chunks"

# ---------------------------------------------------------------------------
# Lazy singletons
# ---------------------------------------------------------------------------
# ChromaClient and EmbeddingService are created on first use, not at import
# time.  Instantiating them at module level caused the server to crash during
# startup whenever the Gemini API was temporarily unreachable, because
# EmbeddingService.__init__() contacts the API to validate the key.
# Lazy initialisation defers that network call to the first actual request,
# so the server starts reliably and individual request failures are isolated.

_chroma_client: ChromaClient | None = None
_embedding_service: EmbeddingService | None = None


def _get_chroma_client() -> ChromaClient:
    """Returns the shared ChromaDB client, creating it on first call."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaClient()
    return _chroma_client


def _get_embedding_service() -> EmbeddingService:
    """Returns the shared embedding service, creating it on first call."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


# ---------------------------------------------------------------------------
# Async helpers for blocking I/O
# ---------------------------------------------------------------------------

async def _run_sync(func, *args):
    """
    Runs a synchronous (blocking) function in a thread-pool executor so it
    does not block the FastAPI event loop.

    The Gemini embedding SDK and pypdf both perform blocking I/O (network
    calls and disk reads respectively).  Calling them directly inside an
    async function would freeze the event loop and stall all concurrent
    requests.  asyncio.get_event_loop().run_in_executor() moves the work
    to a background thread so the event loop stays responsive.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args))


async def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Vectorises a batch of texts without blocking the event loop."""
    service = _get_embedding_service()
    return await _run_sync(service.embed_texts, texts)


async def _embed_query(query: str) -> list[float]:
    """Vectorises a single query string without blocking the event loop."""
    service = _get_embedding_service()
    return await _run_sync(service.embed_query, query)


async def _extract_pages(file_path: Path) -> list[tuple[int, str]]:
    """Extracts page text from a PDF without blocking the event loop."""
    return await _run_sync(extract_text_pages, file_path)


# ---------------------------------------------------------------------------
# Public pipeline functions
# ---------------------------------------------------------------------------

async def ingest_document(
    document_id: int,
    file_path: Path,
    user_id: int,
    session: Any,
) -> None:
    """
    Converts a raw PDF into searchable vector representations.

    The text is chunked rather than stored whole because:
      - Embedding models have a context length limit
      - Smaller chunks produce more focused similarity scores
      - Overlapping windows prevent important sentences from being split across
        two chunks and losing context on both sides
    """
    # PDF extraction runs in a thread pool so it doesn't block the event loop
    pages = await _extract_pages(file_path)

    # RecursiveCharacterTextSplitter tries paragraph breaks first, then sentence
    # breaks, then word breaks — in that order — before falling back to characters,
    # which produces more natural splits than a hard character count alone
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    texts: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []
    all_chunks: list[DocumentChunk] = []

    for page_number, page_text in pages:
        if not page_text:
            # Image-only pages produce no extractable text, so they are skipped
            # rather than creating empty chunks that would skew similarity scores
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk_idx, chunk in enumerate(page_chunks, start=1):
            # ChromaDB requires all metadata values to be strings, not integers
            metadata = {
                "user_id":     str(user_id),
                "document_id": str(document_id),
                "filename":    file_path.name,
                "page":        str(page_number),
                "chunk_id":    str(chunk_idx),
            }

            # The Postgres copy is used by generate_document_summary(), which
            # needs ordered page-by-page access that ChromaDB doesn't support
            chunk_record = DocumentChunk(
                document_id=document_id,
                page_number=page_number,
                chunk_index=chunk_idx,
                content=chunk,
                chunk_metadata=str(metadata),
            )
            session.add(chunk_record)
            all_chunks.append(chunk_record)

            texts.append(chunk)
            metadatas.append(metadata)
            # The ID encodes its origin so debugging a bad retrieval is straightforward
            ids.append(f"{document_id}_{page_number}_{chunk_idx}")

    await session.commit()

    if texts:
        # Embedding runs in a thread pool so the Gemini HTTP call does not block
        # the event loop — this is the most time-consuming step in ingestion
        embeddings = await _embed_texts(texts)
        chroma = _get_chroma_client()
        chroma.add(
            collection_name=COLLECTION_NAME,
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )


async def answer_question(
    question: str,
    document_ids: list[int],
    user_id: int,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Finds the most relevant document chunks and asks the LLM to answer from them.

    Fetching 2× the desired K and filtering afterwards produces more accurate
    top-K results than asking ChromaDB for exactly K with a combined where clause,
    because the ownership filter is applied before the similarity ranking.
    """
    # Query embedding runs in a thread pool to avoid blocking the event loop
    query_embedding = await _embed_query(question)

    chroma = _get_chroma_client()

    # user_id filter is applied inside ChromaDB, not in Python, so the similarity
    # index is searched only over this user's documents — a hard security boundary
    search_results = chroma.search(
        COLLECTION_NAME,
        query_embedding,
        n_results=settings.semantic_search_k * 2,
        filter={"user_id": str(user_id)},
    )

    docs      = search_results.get("documents", [])
    metadatas = search_results.get("metadatas", [])
    distances = search_results.get("distances", [])

    # Secondary filter narrows results to the documents the user actually requested
    allowed_ids = set(str(d) for d in document_ids)
    filtered_items = [
        (doc, meta, dist)
        for doc, meta, dist in zip(docs, metadatas, distances)
        if meta.get("document_id") in allowed_ids
    ]

    # Trim to the configured top-K now that irrelevant documents have been removed
    filtered_items = filtered_items[:settings.semantic_search_k]

    if not filtered_items:
        return (
            "I could not find relevant information in the selected documents.",
            [],
        )

    docs, metadatas, distances = zip(*filtered_items)

    context_sections: list[str] = []
    sources: list[dict[str, Any]] = []

    for chunk, metadata, distance in zip(docs, metadatas, distances):
        if not chunk:
            continue

        page     = metadata.get("page", "?")
        filename = metadata.get("filename", "unknown")

        # Each context block is labelled with its source so the LLM can
        # include page references in its answer
        context_sections.append(f"[Page {page} from '{filename}']: {chunk}")

        # Cosine distance lies in [0, 2]; subtracting from 1 gives a similarity
        # score in [-1, 1] where 1 means identical vectors
        similarity = float(1 - distance) if isinstance(distance, (float, int)) else 0.0

        sources.append({
            "document":   filename,
            "page":       int(metadata.get("page", 0)),
            "chunk_id":   int(metadata.get("chunk_id", 0)),
            "similarity": round(similarity, 4),
        })

    prompt = PROMPT_TEMPLATE.format(
        context="\n\n".join(context_sections),
        question=question,
    )
    answer = await _call_llm(prompt)
    return answer, sources


async def generate_document_summary(
    document_id: int,
    user_id: int,
    session: Any,
) -> dict[str, Any]:
    """
    Reads all stored chunks for a document in page order and asks the LLM
    to produce a structured summary.

    Chunks are read from Postgres rather than ChromaDB because Postgres
    supports ORDER BY page_number, whereas ChromaDB returns results sorted
    by similarity score — wrong order for producing a coherent summary.
    """
    result = await session.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.page_number, DocumentChunk.chunk_index)
    )
    chunks = result.all()

    if not chunks:
        return {
            "document_id": document_id,
            "summary":     "No text content found for this document.",
            "key_points":  [],
            "findings":    [],
        }

    combined_text = "\n\n".join(chunk.content for chunk in chunks)
    prompt = SUMMARY_PROMPT.format(context=combined_text)
    raw_summary = await _call_llm(prompt)

    # The prompt instructs the model to use exact section headers so the
    # structured fields can be parsed back out without a separate NLP step
    clean_summary = raw_summary
    if "Summary:" in raw_summary:
        after_summary_header = raw_summary.split("Summary:", 1)[1]
        clean_summary = after_summary_header.split("Key points:")[0].strip()

    key_points: list[str] = []
    findings:   list[str] = []

    if "Key points:" in raw_summary:
        after_header = raw_summary.split("Key points:", 1)[1]
        section = after_header.split("Important findings:")[0]
        key_points = [
            line.strip().lstrip("-•* ")
            for line in section.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    if "Important findings:" in raw_summary:
        after_header = raw_summary.split("Important findings:", 1)[1]
        findings = [
            line.strip().lstrip("-•* ")
            for line in after_header.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    return {
        "document_id": document_id,
        # Falls back to the full raw response if the model didn't follow the format
        "summary":     clean_summary or raw_summary,
        "key_points":  key_points,
        "findings":    findings,
    }


async def _call_llm(prompt: str) -> str:
    """
    Sends a single prompt to the configured Gemini model and returns the text.

    temperature=0 makes the model deterministic — the same prompt produces
    the same answer on repeated calls, which is important for factual Q&A
    where creative variation would produce inconsistent citations.

    ainvoke() is the async variant of invoke(); using it prevents the Gemini
    HTTP call from blocking the FastAPI event loop while waiting for a response.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content
