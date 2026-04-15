import json
import re
from services.llm import call_llm, build_system_message, build_user_message
from schemas.deal import ClassificationResult

def parse_llm_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"```[a-z]*\n?", "", text).strip("`").strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found in LLM response")

async def classify_deal(conversation: list[dict]) -> ClassificationResult:
    conversation_text = "\n".join(
        f"{msg.get('role', 'unknown')}: {msg.get('text', '')}"
        for msg in conversation
    )

    print("=== LLM CLASSIFICATION INPUT ===")
    print(conversation_text)
    print("================================")

    system_msg = build_system_message("You are a B2B sales deal classifier. You always respond in valid JSON only. No explanation, no markdown.")
    
    user_prompt = f"""Analyze this sales conversation and classify the deal stage.
    
Conversation:
{conversation_text}

Return ONLY this JSON:
{{
  "stage": "<Awareness|Interest|Evaluation|Decision>",
  "confidence": <float between 0.0 and 1.0>,
  "reason": "<one sentence explanation>"
}}

Rules:
- stage = furthest stage the prospect reached
- Awareness = prospect learned about the product
- Interest = prospect asked questions or showed curiosity
- Evaluation = prospect compared options or asked about pricing/features
- Decision = prospect expressed intent to buy or rejected
- confidence = how certain you are (0.0 to 1.0)"""

    user_msg = build_user_message(user_prompt)
    
    response_text = await call_llm([system_msg, user_msg])
    
    print("=== LLM RAW RESPONSE ===")
    print(response_text)
    print("========================")
    
    try:
        data = parse_llm_json(response_text)
    except Exception:
        data = {
            "stage": "Awareness",
            "confidence": 0.0,
            "reason": "Failed to parse LLM response"
        }
        
    valid_stages = ["Awareness", "Interest", "Evaluation", "Decision"]
    stage = data.get("stage", "Awareness")
    if stage not in valid_stages:
        stage = "Awareness"
    
    print(f"=== LLM STAGE: {stage} ===")
        
    return ClassificationResult(
        stage=stage,
        confidence=float(data.get("confidence", 0.0)),
        reason=data.get("reason", "")
    )

async def get_deal_breakdown(conversation: list[dict]) -> dict:
    conversation_text = "\n".join(
        f"{msg.get('role', 'unknown')}: {msg.get('text', '')}"
        for msg in conversation
    )
        
    system_msg = build_system_message("You are a sales coach. Respond in valid JSON only.")
    
    user_prompt = f"""Review this sales conversation and give a one-sentence assessment for each stage.
    
Conversation:
{conversation_text}

Return ONLY this JSON:
{{
  "Awareness": "<Did the prospect become aware of the problem? One sentence.>",
  "Interest": "<Did the prospect show interest in the solution? One sentence.>",
  "Evaluation": "<Did the prospect evaluate the product? One sentence.>",
  "Decision": "<Did the prospect reach a buying decision? One sentence.>"
}}"""

    user_msg = build_user_message(user_prompt)
    response_text = await call_llm([system_msg, user_msg])
    
    try:
        data = parse_llm_json(response_text)
    except Exception:
        data = {
            "Awareness": "Failed to parse response.",
            "Interest": "Failed to parse response.",
            "Evaluation": "Failed to parse response.",
            "Decision": "Failed to parse response."
        }
        
    return data
