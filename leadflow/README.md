# LeadFlow — AI-Powered CRM & Conversation Intelligence Platform

> **Final-year engineering project** — Enterprise-grade CRM and sales intelligence platform with AI-powered conversation analysis, agentic analytics, and structured lead scoring.

---

## Product Story

LeadFlow transforms unstructured customer conversations into structured CRM intelligence.

```
Customer Conversation
        ↓
Speech-to-Text (faster-whisper)
        ↓
AI Understanding (Gemini via LangChain)
        ↓
Structured Intelligence (Pydantic schemas)
        ↓
Lead Scoring (0–100)
        ↓
CRM Automation (MongoDB)
        ↓
Follow-up Generation
        ↓
Sales Analytics (deterministic)
        ↓
Agentic Insights (3-agent pipeline)
        ↓
Manager Decision Support
```

---

## Features

### Current MVP

| Feature | Description |
|---|---|
| Excel/CSV Lead Import | Validation, duplicate detection, preview before import |
| CRM Lead Management | Full CRUD, search, filter, sort, pagination |
| Call Recording Upload | .wav, .mp3, .m4a support |
| Speech-to-Text | faster-whisper (offline, CPU-capable) |
| AI Conversation Analysis | Gemini via LangChain → Pydantic structured output |
| Lead Scoring | 0–100 framework with intent, sentiment, timeline factors |
| CRM Auto-Update | Status, score, priority, intent updated from analysis |
| Follow-up Generation | AI-recommended follow-ups with due dates |
| Role-Based Access Control | Admin, Sales Manager, Sales Executive, Support |
| Agentic Analytics | Analytics Agent → Insight Agent → Action Agent pipeline |
| AI Query Interface | "Ask LeadFlow" — answers grounded in real CRM data |
| Manager Dashboard | KPIs, pipeline, sentiment, high-priority leads |

### Future Scope

- Twilio/Exotel telephony integration
- Automatic calling / predictive dialing
- Live call analysis (real-time STT + AI)
- External CRM integrations (Salesforce, HubSpot)
- Cloud deployment (Kubernetes, Docker)
- Event-driven architecture (Kafka)
- Multi-tenant workspace support

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop UI | PySide6, Qt Model/View, QSS |
| Backend | FastAPI, Pydantic v2 |
| Database | MongoDB, PyMongo |
| Auth | JWT, bcrypt, RBAC |
| AI | Google Gemini API, LangChain |
| STT | faster-whisper |
| Data Import | pandas, openpyxl |
| HTTP | httpx |
| Logging | Python logging |
| Testing | pytest |
| Packaging | PyInstaller |

---

## Project Architecture

```
leadflow/
├── app/
│   ├── main.py                    # Entry point
│   ├── config.py                  # Settings from .env
│   ├── desktop/                   # PySide6 UI
│   │   ├── main_window.py         # Application shell
│   │   ├── login_window.py        # Auth UI
│   │   ├── app_services.py        # Service registry / DI
│   │   ├── styles.py              # Enterprise dark theme QSS
│   │   ├── components/widgets.py  # Reusable UI components
│   │   ├── dashboard/             # Dashboard page
│   │   ├── leads/                 # Lead management + detail
│   │   ├── calls/                 # Call upload + analysis
│   │   ├── followups/             # Follow-up management
│   │   ├── analytics/             # Agentic analytics
│   │   └── users/                 # User management
│   ├── backend/
│   │   ├── models/domain.py       # Pydantic domain models
│   │   └── services/              # Auth, import services
│   ├── ai/
│   │   ├── transcription.py       # STT provider layer
│   │   ├── gemini_service.py      # Gemini API wrapper
│   │   ├── langchain_pipeline.py  # Analysis orchestration
│   │   └── prompts.py             # Centralized prompts
│   ├── analytics_engine/
│   │   ├── metrics.py             # Deterministic calculations
│   │   └── orchestrator.py        # 3-agent analytics pipeline
│   ├── database/
│   │   ├── mongodb.py             # Connection + indexes
│   │   └── repositories/          # Data access layer
│   └── utils/
├── scripts/
│   └── seed_demo.py               # Demo data seeder
├── tests/
│   └── test_core.py               # Unit tests
├── uploads/recordings/            # Audio files
├── requirements.txt
├── .env.example
└── run.py
```

---

## Installation

### Prerequisites

- Python 3.12+
- MongoDB 6.0+ (running locally)
- Gemini API key (free tier)

### 1. Clone and set up environment

```bash
git clone <repo>
cd leadflow
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on faster-whisper**: If you encounter issues, ensure you have the correct version:
> ```bash
> pip install faster-whisper==0.10.0
> ```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_actual_key_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=leadflow
```

### 4. Start MongoDB

```bash
mongod --dbpath /path/to/your/data
```

Or with Docker:
```bash
docker run -d -p 27017:27017 --name leadflow-mongo mongo:6
```

### 5. Seed demo data

```bash
python scripts/seed_demo.py
```

This creates 8 users, 75 leads, 25 call analyses, and 30 follow-ups.

### 6. Run the application

```bash
python run.py
```

---

## Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@leadflow.local | admin123 |
| Sales Manager | manager@leadflow.local | manager123 |
| Sales Executive | rahul@leadflow.local | exec123 |
| Support | support@leadflow.local | support123 |

---

## Gemini API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a project and enable the Gemini API
3. Generate an API key
4. Add it to `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
```

The model is configurable — change `GEMINI_MODEL` to switch.

---

## Whisper Setup

faster-whisper runs offline and on CPU:

```env
WHISPER_MODEL_SIZE=small    # tiny, base, small, medium, large
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
```

First run will download the model automatically.

---

## Running Tests

```bash
cd leadflow
pytest tests/ -v
```

---

## Complete Demo Workflow

1. **Login** as Sales Executive (`rahul@leadflow.local`)
2. Open **Leads** → browse the seeded pipeline
3. Click **↑ Import** → upload a sample CSV/Excel
4. Open a lead → click **↑ Upload Recording**
5. Upload a `.wav` or `.mp3` file
6. Watch the processing pipeline:
   - Transcription
   - AI Analysis
   - Validation
   - CRM Update
   - Follow-up Generation
7. View the complete analysis result
8. Login as Sales Manager (`manager@leadflow.local`)
9. Open **Analytics** → click **▶ Run Analysis**
10. Watch the 3-agent pipeline execute
11. Open **Ask LeadFlow** → type: *"Why are high-value leads not converting?"*

---

## AI Pipeline

### Conversation Analysis

```
Audio File (.wav/.mp3/.m4a)
         ↓
  faster-whisper STT
         ↓
     Transcript
         ↓
  LangChain + Gemini
         ↓
  Pydantic Validation (strict schema)
         ↓
  MongoDB Storage
         ↓
  Lead CRM Update
```

### Structured Output Schema

The AI output is validated against a strict Pydantic model:

```python
class CallAnalysis(BaseModel):
    summary: str
    intent: CallIntent          # PURCHASE | INQUIRY | DEMO_REQUEST | ...
    sentiment: CallSentiment    # POSITIVE | NEUTRAL | NEGATIVE | MIXED
    requirements: list[str]
    objections: list[str]
    purchase_timeline: str | None
    lead_score: int             # 0–100 (validated)
    priority: LeadPriority      # LOW | MEDIUM | HIGH
    follow_up_required: bool
    follow_up_reason: str | None
    recommended_action: str
    confidence: float           # 0.0–1.0 (validated)
```

---

## Agentic Analytics Architecture

```
           Analytics Orchestrator
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
Analytics Agent  Insight Agent  Action Agent
     │              │              │
MongoDB/Python   Gemini API    Gemini API
(deterministic)  (patterns)  (recommendations)
     │              │              │
     └──────────────┼──────────────┘
                    ▼
             Final AI Report
```

**Analytics Agent**: Computes metrics deterministically from MongoDB (no AI).

**Insight Agent**: Receives pre-computed metrics, uses Gemini to identify patterns.

**Action Agent**: Generates manager-facing recommendations based on verified patterns.

> Rule: Basic calculations (counts, averages, rates) are **never** sent to Gemini. Only interpretation and pattern-finding use AI.

---

## MongoDB Collections

| Collection | Purpose |
|---|---|
| users | Authentication and RBAC |
| leads | CRM lead records |
| call_records | Uploaded recording metadata |
| call_analyses | AI analysis results |
| follow_ups | Follow-up tasks |
| audit_logs | Activity logging |

---

## Security

- Passwords: bcrypt hashed
- Auth: JWT tokens (configurable expiry)
- API keys: environment variables only (never in code)
- File validation: extension + size checks
- RBAC: enforced in services, not just UI
- No plaintext secrets in source

---

## Environment Variables Reference

```env
# Required
GEMINI_API_KEY=         # Google Gemini API key
MONGODB_URI=            # MongoDB connection string
DATABASE_NAME=          # MongoDB database name

# Optional — defaults shown
JWT_SECRET_KEY=         # Change in production
JWT_EXPIRE_MINUTES=480  # Token lifetime
WHISPER_MODEL_SIZE=small
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
MAX_UPLOAD_SIZE_MB=100
LOG_LEVEL=INFO
```

---

## Packaging

```bash
pyinstaller --onefile --windowed run.py --name leadflow
```

---

*LeadFlow — AI-Powered CRM & Conversation Intelligence Platform*
