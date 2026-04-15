import os
import logging
import httpx
from fastapi import HTTPException
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

USE_LM_STUDIO = os.getenv("USE_LM_STUDIO", "false").lower() == "true"
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logger = logging.getLogger(__name__)

async def call_llm(messages: list[dict]) -> str:
    try:
        if USE_LM_STUDIO:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        LM_STUDIO_URL,
                        json={
                            "model": "local-model",
                            "messages": messages,
                            "max_tokens": 512
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"LM Studio failed: {repr(e)}")
        
        # Fallback to Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
            
        groq_client = AsyncGroq(api_key=GROQ_API_KEY)
        chat_completion = await groq_client.chat.completions.create(
            messages=messages,
            model="llama3-8b-instant",
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq/LLM completely failed: {repr(e)}")
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {repr(e)}")

def build_system_message(content: str) -> dict:
    return {"role": "system", "content": content}

def build_user_message(content: str) -> dict:
    return {"role": "user", "content": content}
