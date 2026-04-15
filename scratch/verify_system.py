import httpx
import asyncio
import json
import traceback

async def verify_system():
    url = "http://localhost:8000"
    
    print("--- 1. Testing GET /deals ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{url}/deals")
            print(f"Status: {resp.status_code}")
            deals = resp.json()
            print(f"Count: {len(deals)}")
    except Exception as e:
        print(f"Error checking GET /deals: {e}")
        traceback.print_exc()
        return

    print("\n--- 2. Testing POST /deals ---")
    test_deal = {
        "prospect": "Hackathon Tester",
        "conversation": [
            {"role": "sales", "text": "Hi, I noticed you were looking for a CRM solution."},
            {"role": "prospect", "text": "Yes, we are evaluating a few options right now."},
            {"role": "sales", "text": "Great! Have you looked at our pricing page?"},
            {"role": "prospect", "text": "Not yet, but I would like to see a demo first."}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{url}/deals", json=test_deal)
            print(f"Status: {resp.status_code}")
            result = resp.json()
            print(f"Classification Result: {result}")
            deal_id = result.get("id")
    except Exception as e:
        print(f"Error checking POST /deals: {e}")
        traceback.print_exc()
        return

    if deal_id:
        print(f"\n--- 3. Testing GET /deals/{deal_id} ---")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{url}/deals/{deal_id}")
                print(f"Status: {resp.status_code}")
                deal_detail = resp.json()
                print(f"Prospect: {deal_detail.get('prospect')}")
                print(f"Stage: {deal_detail.get('stage')}")
                print(f"Breakdown: {deal_detail.get('breakdown')}")
                print(f"Conversation stored as list: {isinstance(deal_detail.get('conversation'), list)}")
        except Exception as e:
            print(f"Error checking GET /deals/id: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_system())
