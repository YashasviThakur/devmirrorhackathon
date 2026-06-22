# Quick Start — DevMirror GitLab Transcend Hackathon

## 5-Minute Setup

### 1. Prerequisites
- Git, Python 3.10+, Node.js 18+
- GitLab account with personal access token ([create here](https://gitlab.com/-/user_settings/personal_access_tokens))
  - Scopes: `api`, `read_repository`, `read_user`
- Gemini API key ([free tier](https://aistudio.google.com/app/apikey))
- **GitLab Orbit local CLI** ([install](https://docs.gitlab.com/orbit/)) — powers the Code Coach

### 2. Clone & Install

```bash
git clone https://github.com/YashasviThakur/devmirrorhackathon.git
cd devmirrorhackathon

# Backend
cd devmirror-api
pip install -r requirements.txt

# Frontend
cd ../devmirror-frontend
npm install
```

### 2.5 Try the Orbit Code Coach skill (30 seconds, no web stack)

This is the headline artifact — real GitLab Orbit, one command:

```bash
cd devmirror-api
python orbit_coach.py /path/to/any/repo --top 8
# Add the AI narrative:  $env:GEMINI_API_KEY="..."  (PowerShell)  then re-run
```

It runs `orbit index` + `orbit sql` over the repo's knowledge graph and prints
complexity hotspots, blast radius, coupling, and a prioritized coaching report.

### 3. Environment Setup

Create `devmirror-api/.env`:
```
GEMINI_API_KEY=your_key_here
GITLAB_TOKEN=glpat-xxxxx
GOOGLE_CLIENT_ID=your_oauth_id
GOOGLE_CLIENT_SECRET=your_oauth_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
DATABASE_URL=sqlite:///devmirror.db
```

### 4. Run

**Terminal 1 — Backend:**
```bash
cd devmirror-api
python -m uvicorn main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd devmirror-frontend
npm run dev
```

Visit `http://localhost:5173`

### 5. Test GitLab Integration

1. Click "Sign in"
2. Use any test Google account
3. Go to Settings (bottom left)
4. Paste your GitLab username + token
5. Go to GitLab page
6. See your projects & stats

### 6. Test Code Coach

On the GitLab page:
- Find a project ID (from URL: `gitlab.com/user/project/id`)
- Find an MR ID (from MR URL: `.../-/merge_requests/123`)
- Enter both in Code Coach section
- Click "Analyze Merge Request"
- View AI-powered code review

---

## API Endpoints (for manual testing)

### Fetch Orbit Context
```bash
curl "http://localhost:8000/api/data/gitlab/orbit?user_id=1&project_id=123"
```

### Analyze MR
```bash
curl -X POST "http://localhost:8000/api/coach/analyze-mr?user_id=1&project_id=123&mr_iid=45"
```

### Find Technical Debt
```bash
curl -X POST "http://localhost:8000/api/coach/find-debt?user_id=1&project_id=123"
```

### API Docs
Visit `http://localhost:8000/docs` for interactive Swagger UI

---

## Common Issues

**"GitLab token required"**
→ Go to Settings and add your GitLab credentials

**"Gemini API failed"**
→ Check GEMINI_API_KEY in .env is valid and has quota

**Frontend can't reach backend**
→ Ensure backend is running on `http://localhost:8000`

**Database locked**
→ Delete `devmirror.db` and restart

---

## Demo Flow (2 minutes)

1. **Setup** (follow steps above) — 1 min
2. **Sign in with Google** — 30 sec
3. **Add GitLab token** — 30 sec
4. **View your projects** on GitLab page
5. **Analyze a test MR** with Code Coach
6. **See AI feedback** in real time

---

## What's New for Transcend

| Feature | File | Purpose |
|---------|------|---------|
| **Real Orbit client** | `orbit_local_client.py` | `orbit index` + SQL over the knowledge graph |
| **Orbit Coach skill** | `orbit_coach.py` | Orbit graph → Gemini coaching report (AI Catalog artifact) |
| **Code Coach Agent** | `code_coach_agent.py` | MR review on the real diff + Orbit context |
| **Coach API** | `main.py` (`/api/coach/*`, `/api/data/gitlab/orbit`) | Orbit wired into the app |
| **Agent tool** | `agent_tools.py` (`fetch_gitlab_orbit`) | Orbit context inside the AI agent |

---

## Success Criteria

✅ Fetches GitLab Orbit context (project structure, metrics)  
✅ Analyzes MRs with Gemini AI  
✅ Provides actionable code quality insights  
✅ Detects technical debt patterns  
✅ Works end-to-end (backend + frontend + UI)  
✅ Multi-tenant (per user_id)  
✅ Production-ready code  

---

## Questions?

See `GITLAB_TRANSCEND.md` for full documentation.

**Happy hacking! 🚀**
