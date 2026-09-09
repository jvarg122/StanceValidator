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

![Image](https://i.imgur.com/7cOflbs.png)

## StanceValidator Workflow Overview
![Image](https://i.imgur.com/3h1894R.png)

| Step | Workflow |
|---|---|
| 1 | Start the workflow. |
| 2 | Receive a POST request at `/stances`. |
| 3 | Normalize the submitted text. |
| 4 | Check whether an exact duplicate stance already exists.<br>- If a duplicate exists, return the existing digest and end.<br>- If no duplicate exists, continue to topic classification. |
| 5 | Classify the stance topic. |
| 6 | Determine whether the topic is matched and in scope.<br>- If the topic is not matched, return an out-of-scope response and end.<br>- If the topic is matched, decompose the stance into sub-claims. |
| 7 | Iterate through each sub-claim. |
| 8 | Check whether a similar sub-claim already has evidence.<br>- If similar evidence exists, reuse it.<br>- If no similar evidence exists, find new evidence. |
| 9 | Review whether the evidence is sufficient. |
| 10 | If evidence is insufficient, retry research until the limit. Then mark the sub-claim possibly incomplete. |
| 11 | Score and classify the available evidence. |
| 12 | Compute the strength of the current sub-claim. |
| 13 | Check whether more sub-claims remain.<br>- If more remain, process the next sub-claim.<br>- If none remain, compute the overall stance lean. |
| 14 | Build and return the response as JSON. |
| 15 | End the workflow. |

## Evidence Pipeline

Submit a stance -> it's classified into one of 7 topics, decomposed into sub-claims, and
each sub-claim gets researched via web search (scoped to that topic's curated trusted
domains) and academic search (Semantic Scholar). A bounded critique loop conducts additional research if
the evidence for a sub-claim looks biased or insufficient (the sub-claim is flagged as possibly incomplete).

Each sub-claim gets a strength label (supported/disputed/mixed/insufficient evidence).
Each piece of evidence also receives a credibility score and source type
tag (e.g., government, academic, advocacy, journalism) based on its domain, along with a required supporting
quote for grounding to determine the overall verdict for the stance.

Each web citation is verified against the search results. Citations that cannot be matched to an actual search result are discarded, preventing unsupported or hallucinated sources from entering the evidence set.

Reuse enabled across related stances. When a new sub-claim is similar enough to a previously researched sub-claim within the same topic the existing evidence set is reused instead of initiating a new research pass.

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
