"""
app/api/chat.py
===============
Routes for querying documents with natural language and managing chat history.
The query endpoint runs the full RAG pipeline and persists the result so the
history endpoint can return it later.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.models import Chat, Document, User
from app.db.session import get_session
from app.rag.pipeline import answer_question
from app.schemas.chat_schemas import ChatHistoryResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def query_documents(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """
    Runs the RAG pipeline and returns an AI answer with source citations.
    The document_ids in the request are intersected with the user's actual
    document IDs — this prevents a client from passing a different user's
    document ID and reading their content.
    """
    user_doc_ids_result = await session.execute(
        select(Document.id).filter(Document.user_id == current_user.id)
    )
    user_doc_ids = [row[0] for row in user_doc_ids_result]

    if not user_doc_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have no uploaded documents.",
        )

    # Set intersection means the client can only query documents they own;
    # if no document_ids were specified the full owned set is used
    if request.document_ids:
        allowed_doc_ids = set(request.document_ids) & set(user_doc_ids)
    else:
        allowed_doc_ids = set(user_doc_ids)

    if not allowed_doc_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="None of the specified document IDs belong to your account.",
        )

    answer, sources = await answer_question(
        question=request.question,
        document_ids=list(allowed_doc_ids),
        user_id=current_user.id,
    )

    # Persisting the Q&A pair makes it available via GET /chat/history
    chat = Chat(
        user_id=current_user.id,
        question=request.question,
        answer=answer,
    )
    session.add(chat)
    await session.commit()

    return ChatResponse(answer=answer, sources=sources)


@router.get("/history", response_model=list[ChatHistoryResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ChatHistoryResponse]:
    """
    Returns all Q&A exchanges for the current user, most recent first.
    The user_id filter ensures a user can only see their own conversation history.
    """
    statement = (
        select(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
    )
    results = await session.scalars(statement)
    return results.all()


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Permanently deletes all chat history rows for the current user.
    204 No Content is the standard REST response for a DELETE that returns
    no body — returning 200 with an empty body would also be valid but 204
    is more precise about the absence of a response body.
    """
    statement = delete(Chat).where(Chat.user_id == current_user.id)
    await session.execute(statement)
    await session.commit()
