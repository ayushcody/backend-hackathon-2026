import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.database import get_db
from models.deal import Deal
from schemas.deal import DealCreate
from services.analyzer import classify_deal, get_deal_breakdown

router = APIRouter()

@router.post("/deals")
async def create_deal(deal_create: DealCreate, db: AsyncSession = Depends(get_db)):
    # Validate conversation is not empty
    if not deal_create.conversation or len(deal_create.conversation) == 0:
        raise HTTPException(status_code=400, detail="Conversation empty")

    conversation_dicts = [{"role": msg.role, "text": msg.text} for msg in deal_create.conversation]
    
    print("=" * 50)
    print("POST /deals — Saving conversation:")
    print(f"  Prospect: {deal_create.prospect}")
    print(f"  Messages: {len(conversation_dicts)}")
    print("=" * 50)
    
    # Step 1: Classify the deal via LLM
    try:
        result = await classify_deal(conversation_dicts)
        print(f"  Classification result: stage={result.stage}, confidence={result.confidence}")
    except Exception as e:
        print(f"  ERROR classifying deal: {e}")
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
    
    # Step 2: Convert conversation to JSON string for storage
    conversation_str = json.dumps(conversation_dicts)
    
    print("  Conversation JSON:", conversation_str[:200])
    
    # Step 3: Store in PostgreSQL — NO status column
    deal = Deal(
        prospect=deal_create.prospect,
        conversation=conversation_str,
        stage=result.stage
    )
    
    try:
        db.add(deal)
        await db.commit()
        await db.refresh(deal)
        print(f"  === DEAL SAVED === ID: {deal.id}, Stage: {deal.stage}")
    except Exception as e:
        await db.rollback()
        print(f"  ERROR saving to DB: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Step 4: Return result
    return {
        "id": deal.id,
        "prospect": deal.prospect,
        "stage": result.stage,
        "confidence": result.confidence,
        "reason": result.reason
    }

@router.get("/deals")
async def get_deals(db: AsyncSession = Depends(get_db)):
    stmt = select(Deal).order_by(Deal.created_at.desc())
    result = await db.execute(stmt)
    deals = result.scalars().all()
    
    print(f"GET /deals — Found {len(deals)} deals")
    
    response = []
    for d in deals:
        response.append({
            "id": d.id,
            "prospect": d.prospect,
            "conversation": d.conversation,
            "stage": d.stage,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })
    
    print("DEALS:", response)
    return response

@router.get("/deals/{id}")
async def get_deal(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Deal).where(Deal.id == id)
    result = await db.execute(stmt)
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        conversation = json.loads(deal.conversation)
    except Exception:
        conversation = []
    
    try:
        breakdown = await get_deal_breakdown(conversation)
    except Exception:
        breakdown = {}
    
    return {
        "id": deal.id,
        "prospect": deal.prospect,
        "stage": deal.stage,
        "conversation": conversation,
        "breakdown": breakdown,
        "created_at": deal.created_at.isoformat() if deal.created_at else None
    }
