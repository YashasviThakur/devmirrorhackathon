<div align="center">

<img src="https://img.shields.io/badge/version-2.0.8-6366f1?style=flat-square" />
<img src="https://img.shields.io/badge/demo-live-22c55e?style=flat-square" />
<img src="https://img.shields.io/badge/backend-railway-0B0D0E?style=flat-square&logo=railway&logoColor=white" />
<img src="https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/license-MIT-f59e0b?style=flat-square" />

<br /><br />

# DevMirror

### Not your critic. Your coach.

One dashboard for your GitHub, GitLab, LeetCode, Codeforces, Gmail, Calendar, and YouTube — powered by a multi-step Gemini 3 agent that knows your goals, coaches you daily, and schedules your week.

<br />

[**Live Demo →**](https://dev-mirror-two.vercel.app) &nbsp;·&nbsp; [**Report a Bug**](https://github.com/YashasviThakur/DevMirror/issues) &nbsp;·&nbsp; [**Request a Feature**](https://github.com/YashasviThakur/DevMirror/issues)

</div>

---

## What is DevMirror?

Most developers have 6 tabs open just to check their own progress — GitHub here, LeetCode there, emails buried somewhere else. DevMirror collapses all of that into one place, adds a Gemini-powered AI coach that knows your actual goals, and tells you what to focus on today.

Built for developers who are serious about their growth.

---

## Features

### Dashboard
- GitHub contribution grid (52 weeks), top repositories, commit activity, language breakdown, followers
- LeetCode solved count, difficulty ring charts, streak counter, acceptance rate, recent submissions
- Codeforces rating, rank, avatar, recent verdict history
- Google Calendar events for the week ahead
- Editable goal cards — set 3 personal focus areas visible across every page

### GitLab Integration
- Private repo activity, merge request count, commit velocity
- Displayed alongside GitHub in the same unified view
- Authenticated via Personal Access Token (`read_api`, `read_user`, `read_repository`)

### Gmail Radar
- Automatically filters your inbox for **internships, hackathons, and scholarships**
- Smart categorisation: Internship / Hackathon / Fellowship / Other
- Direct deep-link into Gmail for any flagged thread

### YouTube Analyser
- Analyse your liked videos to see how much watch time goes to **technical learning vs. entertainment**
- Upload your Google Takeout watch history JSON for deeper analysis
- Category breakdown with bar charts

### AI Coach (Gemini 3 Agent)
- Multi-step agent powered by **Gemini 2.5 Flash** — fetches live data from GitHub, GitLab, LeetCode, Codeforces, Gmail, and Calendar before every answer
- Knows your 3 personal goals at all times
- Can **schedule study sessions directly to your Google Calendar** from the chat
- Daily nudge: one personalised sentence every morning based on your real activity
- Growth Report: 150-word AI coaching report built from your cross-platform data
- Focus Today & Learn vs Build analysis

### DSA Progress
- Combined LeetCode + Codeforces view
- Ring charts by difficulty, streak tracking, rating graph

---

## Architecture

```
Browser
  └── React + Vite (Vercel)
        └── /api/* → FastAPI (Railway)
                ├── Google OAuth2 (login, Gmail, Calendar, YouTube)
                ├── GitHub REST API
                ├── GitLab REST API
                ├── LeetCode GraphQL API
                ├── Codeforces API
                ├── MongoDB Atlas  (user profiles, encrypted tokens)
                └── Gemini 2.5 Flash  (multi-step agent via REST)
```

### Multi-step Gemini Agent

The AI Coach is not a single-shot prompt — it's an agentic loop (`agent_tools.py`) that:

1. Receives your question
2. Calls Gemini with a tool manifest (GitHub, GitLab, LeetCode, Codeforces, Gmail, Calendar)
3. Gemini decides which tools to call and in what order
4. Each tool fetches live data for your account
5. Results are fed back to Gemini
6. Loop continues for up to 6 turns until a final answer is produced
7. If a scheduling intent is detected, Calendar events are created automatically

```python
# agent_tools.py — core loop (simplified)
for turn in range(max_turns):
    response = gemini.generate_content(contents, tools=TOOL_DECLARATIONS)
    if response.has_tool_calls:
        results = execute_tool_calls(response.tool_calls, user_ctx)
        contents.append(tool_results(results))
    else:
        return response.text  # final answer
```

### Security

- All OAuth tokens (Google, GitLab, GitHub) are **Fernet-encrypted** before being written to MongoDB
- Tokens are decrypted in-memory only at the moment of an API call — never logged
- CORS locked to the deployed frontend origin
- Multi-tenant: each user's data is fully isolated by `user_id`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS v3, Vite |
| Backend | FastAPI, Python 3.11+, SQLAlchemy |
| Database | MongoDB Atlas |
| Auth | Google OAuth2 (login + Gmail + Calendar + YouTube scopes) |
| AI | **Gemini 2.5 Flash** — multi-step agent (direct REST, no SDK caching) |
| Encryption | `cryptography.fernet` — all OAuth tokens encrypted at rest |
| Deploy | Vercel (frontend) · Railway (backend) |
| Google APIs | Gmail API, Google Calendar API, YouTube Data API v3 |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Cloud project with OAuth2 credentials and the following APIs enabled:
  - Gmail API
  - Google Calendar API
  - YouTube Data API v3
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/app/apikey))
- A MongoDB Atlas cluster (free tier works)

### 1. Clone the repo

```bash
git clone https://github.com/YashasviThakur/DevMirror.git
cd DevMirror
```

### 2. Backend setup

```bash
cd devmirror-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Google OAuth2
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Fernet — generate with:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=your-fernet-key

# Gemini (Google AI Studio)
GEMINI_API_KEY=your-gemini-api-key

# MongoDB Atlas
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/

# GitLab PAT (scopes: read_api, read_user, read_repository)
GITLAB_TOKEN=your-gitlab-pat

# GitHub PAT — optional, raises rate limit from 60 to 5000 req/hr
GITHUB_TOKEN=your-github-pat

FRONTEND_URL=http://localhost:5173
```

Start the backend:

```bash
uvicorn main:app --reload
```

### 3. Frontend setup

```bash
cd devmirror-frontend
npm install
cp .env.example .env.local
# Set VITE_API_URL=http://localhost:8000
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and sign in with Google.

---

## Project Structure

```
DevMirror/
├── devmirror-api/              # FastAPI backend
│   ├── main.py                 # All API routes + data fetchers
│   ├── agent_tools.py          # Multi-step Gemini agent loop + tool declarations
│   ├── auth_router.py          # Google OAuth2 flow
│   ├── models.py               # SQLAlchemy ORM (User, LinkedAccount)
│   ├── database.py             # MongoDB + SQLite connection
│   └── .env.example
│
└── devmirror-frontend/         # React frontend
    └── src/
        ├── pages/              # Dashboard, GitLab, Gmail, YouTube, Coach, DSAProgress, ...
        ├── components/         # Sidebar, shared UI
        ├── api/                # Typed API client
        └── hooks/              # useUserId, etc.
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check + service status |
| `GET` | `/api/user/{id}` | User profile + linked accounts |
| `PATCH` | `/api/user/{id}/goals` | Update 3 focus goals |
| `PATCH` | `/api/user/{id}/handles` | Update LeetCode / Codeforces handles |
| `PATCH` | `/api/user/{id}/gitlab-handle` | Update GitLab username |
| `GET` | `/api/data/github` | GitHub stats (grid, repos, languages) |
| `GET` | `/api/data/leetcode` | LeetCode stats + submissions |
| `GET` | `/api/data/codeforces` | Codeforces rating + submissions |
| `GET` | `/api/data/gitlab` | GitLab MRs, commits, projects |
| `GET` | `/api/data/gmail` | Filtered internship / hackathon emails |
| `GET` | `/api/data/calendar` | Upcoming Google Calendar events |
| `GET` | `/api/data/youtube` | YouTube liked videos + categories |
| `POST` | `/api/coach/ask` | Multi-step Gemini agent |
| `POST` | `/api/growth-report` | AI growth report |
| `POST` | `/api/focus-today` | AI focus recommendation |
| `POST` | `/api/learn-vs-build` | Learn vs Build analysis |

---

## Environment Variables Reference

### Backend (`devmirror-api/.env`)

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth2 client secret |
| `GOOGLE_REDIRECT_URI` | Yes | Must match Google Cloud Console exactly |
| `FERNET_KEY` | Yes | Encryption key for OAuth token storage |
| `GEMINI_API_KEY` | Yes | Gemini 2.5 Flash — powers the AI agent |
| `GEMINI_MODEL` | No | Model override (default: `gemini-2.5-flash`) |
| `MONGODB_URI` | Yes | MongoDB Atlas connection string |
| `GITLAB_TOKEN` | No | GitLab PAT for private repo access |
| `GITHUB_TOKEN` | No | GitHub PAT — raises rate limit to 5000 req/hr |
| `FRONTEND_URL` | Yes | Frontend origin (CORS) |

### Frontend (`devmirror-frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Backend URL (`http://localhost:8000` for dev) |

---

## Deployment

### Backend — Railway

1. Connect your GitHub repo to Railway
2. Set all environment variables in the Railway dashboard
3. Railway auto-deploys on every push to `main`

Start command (set in `railway.json`):
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend — Vercel

1. Connect your GitHub repo to Vercel
2. Set `VITE_API_URL` to your Railway backend URL
3. Vercel auto-deploys on every push to `main`

---

## Roadmap

- [ ] Mobile-responsive layout
- [ ] Public shareable profile link
- [ ] Weekly email digest
- [ ] Institution dashboard (cohort analytics)
- [ ] GitHub Actions / CI pipeline stats
- [ ] Codeforces contest calendar sync

---

<div align="center">

Built by [Yashasvi Thakur](https://github.com/YashasviThakur)

Powered by [Gemini](https://deepmind.google/technologies/gemini/) · [MongoDB Atlas](https://www.mongodb.com/atlas) · [FastAPI](https://fastapi.tiangolo.com) · [React](https://react.dev)

⭐ Star this repo if DevMirror helped you — it means a lot.

</div>
