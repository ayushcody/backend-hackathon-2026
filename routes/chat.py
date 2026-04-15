from fastapi import APIRouter
from schemas.deal import ChatRequest
from services.chat_agent import get_sales_reply

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    conversation_dicts = [{"role": msg.role, "text": msg.text} for msg in request.conversation]
    product = request.product or "B2B SaaS platform"
    reply = await get_sales_reply(conversation_dicts, product)
    return {"reply": reply}
