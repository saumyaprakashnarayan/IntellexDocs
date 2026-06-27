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
    statement = select(Document.id).filter(Document.user_id == current_user.id)
    user_doc_ids = [row[0] for row in await session.execute(statement)]
    allowed_doc_ids = set(request.document_ids or user_doc_ids) & set(user_doc_ids)
    if not allowed_doc_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid documents available for query.")

    answer, sources = await answer_question(request.question, list(allowed_doc_ids), current_user.id)
    chat = Chat(user_id=current_user.id, question=request.question, answer=answer)
    session.add(chat)
    await session.commit()
    return ChatResponse(answer=answer, sources=sources)

@router.get("/history", response_model=list[ChatHistoryResponse])
async def get_history(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[ChatHistoryResponse]:
    statement = select(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.created_at.desc())
    results = await session.scalars(statement)
    return results.all()

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> None:
    statement = delete(Chat).where(Chat.user_id == current_user.id)
    await session.execute(statement)
    await session.commit()
