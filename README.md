# Teqa — AI Business Intelligence Agent for Egyptian SMBs

> "Every Egyptian SMB owner deserves to understand their business before their competitor does."

Teqa connects to your payment providers, POS systems, and e-commerce stores, then delivers a daily AI-powered WhatsApp report at 8:00 AM summarizing your business performance.

**No dashboards. No spreadsheets. Just actionable intelligence.**

## Architecture

```
├── backend/          # FastAPI + SQLAlchemy + Celery
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── ai/           # OpenAI insight engine
│   │   ├── integrations/ # Adapter pattern (Shopify, Paymob, CSV)
│   │   ├── jobs/         # Celery tasks + scheduler
│   │   ├── models/       # SQLAlchemy models
│   │   ├── repositories/ # Data access layer
│   │   ├── services/     # Business logic
│   │   └── schemas/      # Pydantic schemas
│   └── tests/
├── frontend/         # Next.js 15 + TypeScript + Tailwind + shadcn
│   └── src/app/      # App Router pages
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local backend dev)
- Node.js 20+ (for local frontend dev)

### Run with Docker

```bash
cp .env.example .env
# Edit .env with your API keys

docker compose up -d
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed_data.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

## Demo Account

After running seed data:
- Email: `demo@teqa.app`
- Password: `demo123`

## Environment Variables

See `.env.example` for all required variables.

Key integrations:
- **OpenAI** — GPT-powered insights
- **WhatsApp Cloud API** — Daily report delivery
- **Stripe** — Subscription billing
- **Shopify** — E-commerce data
- **Paymob** — Payment data

## Deployment

| Service | Platform |
|---------|----------|
| Frontend | Vercel |
| Backend | Railway |
| Database | Supabase PostgreSQL |
| Queue | Redis (Railway) |
| Storage | Supabase Storage |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/signup | Create account |
| POST | /api/v1/auth/login | Login |
| GET | /api/v1/auth/me | Current user |
| POST | /api/v1/businesses/ | Create business |
| GET | /api/v1/businesses/ | List businesses |
| POST | /api/v1/integrations/{id}/connect | Connect integration |
| POST | /api/v1/integrations/{id}/csv-upload | Upload CSV data |
| GET | /api/v1/reports/{id} | List reports |
| POST | /api/v1/reports/{id}/generate | Generate report |
| GET | /api/v1/reports/{id}/dashboard | Dashboard overview |
| POST | /api/v1/billing/{id}/subscribe | Create subscription |
| POST | /api/v1/billing/webhook | Stripe webhook |

## Plans

| Plan | Price | Features |
|------|-------|----------|
| Starter | EGP 499/mo | 1 integration, daily reports |
| Growth | EGP 999/mo | 3 integrations, priority support |
| Pro | EGP 2,499/mo | Unlimited, API access |
| Enterprise | Custom | White-label, dedicated |

## License

Proprietary — Teqa © 2024
