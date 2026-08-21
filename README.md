# AegisGrid — Full Hackathon Project

AegisGrid is a proactive cyber-resilience control plane for connected critical infrastructure.

This implementation expands the supplied 10-slide concept into a runnable full-stack demo:
**Understand → Detect → Assess → Contain → Recover**

## Major features
- Direct-entry dashboard for the built-in demo user (no authentication page)
- Executive dashboard with network risk, threats, critical assets and sectors
- Interactive cross-sector infrastructure graph
- Attack-path analysis
- Context-aware risk scoring using criticality, vulnerability, exposure and behavior
- Threat queue with severity and simulated telemetry
- What-if response simulator
- Recovery/service restoration tracking
- AI Security Copilot
- AI features for:
  - incident explanation
  - attack-path summarization
  - containment recommendation
  - recovery prioritization
  - cross-sector risk explanation
- Hospital, Power/SCADA, Water and Emergency Services model
- SQLite seed database
- FastAPI backend
- React/Vite frontend
- Docker Compose
- Deterministic local AI fallback so the demo works without an API key

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open:
http://localhost:5173

The dashboard opens directly into the built-in demo session. The legacy JWT
authentication endpoints remain available for API testing, but the UI no longer
exposes login or registration.

### Optional LLM mode
Copy `backend/.env.example` to `backend/.env` and set:
`OPENAI_API_KEY=...`

The AI layer remains restricted to the controlled simulation. It explains and recommends; it does not execute infrastructure actions.

## Docker
```bash
docker compose up --build
```

## Architecture

Frontend:
- React
- Vite
- Axios
- Recharts
- Lucide icons

Backend:
- FastAPI
- SQLAlchemy
- SQLite
- JWT
- NetworkX
- optional OpenAI-compatible chat completion

## Production roadmap
For real deployments, add PostgreSQL, Redis/background jobs, OIDC/SSO, RBAC/ABAC, secrets management, signed audit logs, rate limiting, HTTPS, SIEM/EDR connectors, threat intelligence, streaming telemetry, observability, and a separate human-approved response control plane.
