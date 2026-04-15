# Deal AI

A confident and concise B2B SaaS Sales Simulator backed by LLMs and a FastAPI PostgreSQL stack. Practice your pitching against "Alex" the AI prospect, and automatically classify your deals across conversational funnels.

## Demo Flow
1. Open the [Frontend Panel](http://localhost:8000/frontend/index.html) after starting the API server.
2. Select **"Start New Deal"** and enter a prospect name.
3. Chat with the prospect regarding the DealFlow Pro CRM platform. The AI will respond dynamically to test your sales methodology!
4. Once satisfied, click **"End Deal"**. The Analyzer Service automatically categorizes the result (e.g. `Awareness`, `Decision`, `WON/LOST`).
5. From the **Deals Dashboard**, view past assessments or retrieve full multi-stage funnel breakdowns of any specific run.

## Tech Stack
| Tier     | Tech Used |
| -------- | ------- |
| **Frontend** | Vanilla JS, Pure HTML/CSS, Direct State Lifecycle Rendering |
| **Backend** | FastAPI, Uvicorn, Python 3.10+ |
| **Database** | PostgreSQL (asyncpg), SQLAlchemy ORM |
| **LLMs**  | Groq API (`llama3-8b-8192`), LM Studio (Local Failover) |

## Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:
* Python 3.10 or higher
* PostgreSQL Database running

### 2. Install & Configure
Clone this repo and install standard dependencies:
```bash
pip install -r requirements.txt
```

Rename `.env.example` to `.env` and fill in the required keys:
```properties
# Your PostgreSQL Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dealai

# Optional Local Hosting 
USE_LM_STUDIO=true
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions

# External LLM Engine
GROQ_API_KEY=your_key_here
```

### 3. Run the Service
Initialize the backend server. The internal SQLAlchemy models will automatically ensure tables sync on startup.
```bash
python main.py
```
> Go to `http://localhost:8000/frontend/index.html` to begin playing!

---

## API Reference

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API Sanity Check|
| `POST` | `/chat` | Conversational interface returning assistant dialogue |
| `POST` | `/deals` | Classifies conversational history JSON and syncs DB state |
| `GET` | `/deals` | Retrieves list of all prior recorded deals + preview slices |
| `GET` | `/deals/{id}` | Fetches a designated run mapping its internal stage breakdown |

## LLM Fallback Architecture
For high availability, the inference layer is configured with dual redundancy. If `USE_LM_STUDIO=true`, the API routes to local models via `httpx` first. If instances are dead, hit connection timeouts, or fail to respond cleanly, internal logic wraps into a 503 trap and automatically catches execution via `llama3-8b-8192` served through the fast `Groq` API Python SDK.

## Troubleshooting
* **Database connection errors?** Ensure you are strictly using `postgresql://`. The `db/database.py` file automatically transforms the string via regex into `postgresql+asyncpg://` compatibility mode for native async. 
* **LM Studio not responding?** Double check the URL port mapping on your app, typically it aligns safely to `http://localhost:1234/v1/chat/completions`.
* **Groq Rate Limits Exhausted?** Ensure you rotate keys or increase standard tiering via your cloud console account if making extremely aggressive polling queries.
