# DevMirror × GitLab Transcend Hackathon 2026

## 🚀 Overview

DevMirror is an AI-powered developer growth platform that now integrates **GitLab Orbit** and **Duo Agent Platform** to provide intelligent code analysis and coaching. This submission showcases how GitLab Orbit's structured codebase context enables AI agents to deliver actionable insights for code quality, technical debt detection, and developer growth.

**Deadline:** June 24, 2026  
**Prize Track:** Showcase Track (Agents, Flows, and Skills)

---

## 🎯 Core Features

### 1. **GitLab Orbit Integration** 
Fetches and processes structured codebase context via GitLab Orbit's GraphQL API:
- Project structure and file hierarchy
- Code complexity metrics
- Repository statistics
- Merge request context and impact analysis

**File:** `devmirror-api/gitlab_orbit_client.py`

```python
# Fetch project context from GitLab Orbit
orbit_context = gitlab_orbit_client.fetch_orbit_context(project_id, token)

# Analyze code complexity for specific files
complexity = gitlab_orbit_client.analyze_code_complexity(
    project_id, "src/main.py", token
)

# Get MR context with impact metrics
mr_context = gitlab_orbit_client.get_merge_request_context(
    project_id, mr_iid, token
)
```

### 2. **AI Code Coach Agent** 
Provides intelligent code review and technical debt detection using Gemini 2.5 Flash:

#### **Merge Request Analysis** (`POST /api/coach/analyze-mr`)
- Analyzes MR scope (additions, deletions, files changed)
- Generates AI-powered code review with:
  - Code quality score (1-10)
  - Key improvement areas
  - Risk factors
  - Concrete next actions

```bash
curl -X POST "http://localhost:8000/api/coach/analyze-mr?user_id=1&project_id=123&mr_iid=45"
```

**Response:**
```json
{
  "success": true,
  "mr_title": "feat: add new API endpoint",
  "mr_author": "john_doe",
  "changes": {
    "additions": 245,
    "deletions": 32,
    "files_changed": 8
  },
  "ai_analysis": "Code quality: 8/10. Strong implementation with good test coverage. Consider: 1) Add type hints to utility functions 2) Extract repeated validation logic 3) Document the edge case handling in README"
}
```

#### **Technical Debt Detection** (`POST /api/coach/find-debt`)
- Scans project for common technical debt patterns
- Provides priority-ordered improvement opportunities
- Actionable next steps for debt reduction

```bash
curl -X POST "http://localhost:8000/api/coach/find-debt?user_id=1&project_id=123"
```

### 3. **Agent Tool Integration**
New Gemini agent tool: `fetch_gitlab_orbit`

Agents can now access Orbit context within the DevMirror Coach conversation:

```
User: "Analyze my latest MR for code quality"
Agent: [calls fetch_gitlab_orbit tool] → provides context-aware coaching
```

### 4. **Web UI Dashboard**
Enhanced GitLab page with Code Coach interface:
- Real-time MR analysis
- Visual code quality insights
- One-click access to analysis results

---

## 📁 Project Structure

```
devmirror-gitlab/
├── devmirror-api/
│   ├── main.py                    # FastAPI app with new endpoints
│   ├── gitlab_client.py           # Basic GitLab API (stats, commits)
│   ├── gitlab_orbit_client.py     # ✨ NEW: Orbit context fetching
│   ├── code_coach_agent.py        # ✨ NEW: AI code analysis
│   ├── agent_tools.py             # Agent tool definitions
│   └── models.py                  # SQLAlchemy ORM
│
├── devmirror-frontend/
│   ├── src/pages/
│   │   ├── GitLab.tsx             # ✨ ENHANCED: Code Coach UI
│   │   └── Coach.tsx              # AI coaching conversation
│   └── src/api/
│       └── client.ts              # API client
│
└── GITLAB_TRANSCEND.md            # This file
```

---

## 🛠 API Endpoints

### GitLab Orbit Context
```
GET /api/data/gitlab/orbit?user_id=1&project_id=123
```
Returns: Project context, complexity metrics, file structure

### Code Coach - Analyze MR
```
POST /api/coach/analyze-mr
Query params: user_id, project_id, mr_iid
Returns: Code quality analysis, improvement suggestions
```

### Code Coach - Find Debt
```
POST /api/coach/find-debt
Query params: user_id, project_id
Returns: Technical debt patterns, prioritized improvements
```

---

## 🔧 Tech Stack

### Backend
- **FastAPI 2.0** — High-performance async API
- **SQLAlchemy 2.0** — Multi-tenant ORM
- **Gemini 2.5 Flash** — LLM for code analysis
- **GitLab REST API v4 + GraphQL** — Orbit context access
- **PostgreSQL/SQLite** — Persistent storage

### Frontend
- **React 18** — UI framework
- **Vite** — Build tooling
- **TypeScript** — Type safety
- **Tailwind CSS** — Styling

### Deployment
- **Backend:** Railway (FastAPI)
- **Frontend:** Netlify (Vite build)
- **Database:** PostgreSQL (production)

---

## 🚀 Getting Started

### Prerequisites
1. **GitLab Account** with personal access token
   - Scopes: `api`, `read_repository`, `read_user`
   
2. **Gemini API Key**
   - Free tier available via Google AI Studio
   
3. **Environment Variables**
   ```bash
   GEMINI_API_KEY=your_gemini_key
   GITLAB_TOKEN=your_gitlab_token
   FRONTEND_URL=http://localhost:5173
   DATABASE_URL=sqlite:///devmirror.db  # dev
   ```

### Local Development

**Backend:**
```bash
cd devmirror-api
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Frontend:**
```bash
cd devmirror-frontend
npm install
npm run dev
```

Visit `http://localhost:5173` and log in with Google OAuth.

---

## 📊 Demo Workflow

1. **Connect GitLab** 
   - Sign in → Settings → Add GitLab token

2. **Navigate to GitLab page**
   - View projects, commits, MRs

3. **Use Code Coach**
   - Enter Project ID and MR IID
   - Click "Analyze Merge Request"
   - Get AI-powered code review instantly

4. **View Suggestions**
   - Code quality score
   - Top improvement areas
   - Risk factors
   - Next actions

---

## 🎨 Key Innovation: Orbit-Powered AI

**Traditional approach:** Generic code review rules  
**DevMirror approach:** AI understands codebase structure via Orbit → context-aware coaching

When analyzing code, the agent now has:
- ✅ Project architecture knowledge
- ✅ Complexity metrics per file
- ✅ Dependency relationships
- ✅ Commit history patterns
- ✅ Team contribution context

This enables **truly intelligent** suggestions tailored to the project's specific needs.

---

## 🔐 Security & Privacy

- **Encrypted credentials:** GitLab tokens stored with Fernet encryption
- **User-scoped data:** All pipelines are multi-tenant via user_id
- **OAuth 2.0:** Google authentication for user identity
- **No token logging:** Credentials never written to logs
- **Rate limiting:** Respects GitLab API limits (600 requests/min)

---

## 📈 Future Enhancements

1. **Automated MR reviews** on new PRs
2. **Team analytics** — code quality trends across projects
3. **Custom training** — agents learn your project's conventions
4. **GitLab CI/CD integration** — automatic analysis on pipeline
5. **Skills marketplace** — community-contributed agents

---

## 📝 Notes for Evaluators

### What makes this submission strong:

1. **Real-world utility** — Solves actual developer pain (code review)
2. **Orbit-first design** — Built specifically to leverage Orbit's advantages
3. **Production-ready** — Deployed FastAPI, database, frontend stack
4. **Multi-agent extensible** — Easy to add new analysis agents
5. **User-centric** — Deployed to real users on Netlify/Railway

### How to evaluate:

1. Clone the repo: `git clone https://github.com/YashasviThakur/devmirror-gitlab.git`
2. Follow setup instructions above
3. Connect your GitLab account
4. Create a test MR and run analysis
5. Check `/api/docs` for full API docs

---

## 📞 Support

**Author:** Yashasvi Thakur  
**GitHub:** https://github.com/YashasviThakur  
**Demo Site:** [Deployed on Netlify]  

Questions? Open an issue on the repo!

---

*Submitted for GitLab Transcend Hackathon 2026 — Showcase Track*
