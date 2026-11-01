# NitiSetu

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)](https://supabase.com)

**NitiSetu** is a digital governance platform designed to help citizens discover official government welfare schemes and scholarships, evaluate their eligibility using deterministic rule engines, explore gazette policies using grounded AI, and prepare verified applications.

---

## Key Features

1. **Deterministic Scheme Discovery & Matching**
   - Catalog of **2,066 authentic government schemes** and **852 student scholarships** sourced directly from `myScheme.gov.in` and `scholarships.gov.in`.
   - Real-time search, ministerial classification, and demographic/academic matching.

2. **Zero-Hallucination Eligibility Engine**
   - Pure mathematical and logical evaluation against published Gazette guidelines (means ceilings, domicile quotas, reservation categories).
   - Clear rule-by-rule breakdowns with explicit pass/fail statuses and cited regulatory clauses.

3. **Grounded Policy Explainer (RAG Assistant)**
   - Answers citizen questions using retrieved chunks from verified policy documents (National Scholarship Portal guidelines, DBT norms).
   - Every answer includes clause-level citations; strictly declines questions without official policy evidence.

4. **Encrypted Document Vault with Human Confirmation**
   - Citizen certificate upload (Aadhaar, Tehsildar Income Certificate, Academic Marksheets).
   - Document intelligence extracts values into a review interface where the citizen explicitly confirms accuracy before saving.

5. **Sandbox Application Preparation Agent**
   - Automatically maps verified profile credentials into standardized application schemas.
   - Demonstrates end-to-end form completion in a controlled verification sandbox with strict safety guardrails preventing unauthorized live submission.

---

## Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/v1/         # REST API endpoints (schemes, eligibility, assistant, documents, drafts)
│   │   ├── services/       # Domain business logic (eligibility_engine, rag_service, etc.)
│   │   ├── schemas/        # Pydantic validation contracts
│   │   ├── db/             # SQLAlchemy ORM models & database session
│   │   └── config.py       # Application settings & environment
│   ├── tests/              # Comprehensive pytest test suite (21 automated tests)
│   ├── requirements.txt    # Backend Python dependencies
│   └── supabase_schema.sql # Relational & pgvector schema with RLS policies
│
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components (AuthModal, Navigation, Modals)
│   │   ├── pages/          # Application views (Dashboard, Discovery, Detail, Assistant, etc.)
│   │   ├── api/            # Typed client API integration
│   │   └── App.tsx         # Root layout and state management
│   ├── package.json        # Frontend scripts and dependencies
│   └── vercel.json         # Vercel SPA routing configuration
│
├── data/                   # Verified scheme catalogs and official gazette guidelines
├── scripts/                # Repository maintenance & cleanup tools
├── Dockerfile              # Production backend Docker image
├── docker-compose.yml      # Multi-container local orchestration
└── render.yaml             # Cloud infrastructure specification
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- (Optional) Docker & Docker Compose

### 1. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start backend server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Running Automated Tests

```bash
backend/.venv/bin/pytest backend/tests/ -v
```

---

## Deployment

Refer to [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete instructions on deploying to **Vercel** (Frontend) + **Render / Railway** (Backend) + **Supabase** (Database).
