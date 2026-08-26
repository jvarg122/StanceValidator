# StanceValidator

A tool that validates or invalidates a specific stance they have on a topic (Like "Data Centers use too Much Energy") by researching that supporting or conflicting research and creating a two-sided digest on that topic that improves over time.

Frontend: https://main.dqyjj901j7v3s.amplifyapp.com/

Backend API: http://stance-tool-alb-279767071.us-west-2.elb.amazonaws.com/

## Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Anthropic Claude API
- **Frontend:** React, TypeScript, Vite
- **Infrastructure:** AWS ECS Fargate (backend container), RDS (database), Application
  Load Balancer, CloudFront, Amplify Hosting (frontend), ECR

## Architecture

<img width="3401" height="1899" alt="StanceValidator_Architecture" src="https://github.com/user-attachments/assets/ab95d12f-6c0a-4518-bf4c-6707f96d1dfa" />

## Project structure

```
backend/
├── app/        # main.py (pipeline), models.py,
│               # classify, decompose, retrieve, academic, critique, credibility, reuse
├── scripts/    # init_db.py, seed_topics.py
├── tests/      # test_scoring.py, test_api.py, conftest.py
└── Dockerfile

frontend/
└── src/        # App.tsx, components/SubClaimCard.tsx

amplify.yml     # Amplify build config (frontend subfolder build)
```

## Running it locally

### Backend

```
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/stance_tool
ANTHROPIC_API_KEY=sk-ant-...
MODEL_NAME=claude-haiku-4-5
RATE_LIMIT=5/hour
ALLOWED_ORIGINS=http://localhost:5173
```

Create the tables and seed the topic list, then run the server:

```
python -m scripts.init_db
python -m scripts.seed_topics
uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`. `/docs` gives an interactive page for testing routes
directly.

### Frontend

```
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

```
npm run dev
```

Runs on `http://localhost:5173`.

## Testing

```
cd backend
python -m pytest tests/
```
