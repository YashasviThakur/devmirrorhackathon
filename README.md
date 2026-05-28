<div align="center">

<img src="https://img.shields.io/badge/version-2.0.8-6366f1?style=flat-square" />
<img src="https://img.shields.io/badge/deployed-netlify-00C7B7?style=flat-square&logo=netlify&logoColor=white" />
<img src="https://img.shields.io/badge/backend-railway-0B0D0E?style=flat-square&logo=railway&logoColor=white" />
<img src="https://img.shields.io/badge/license-MIT-f59e0b?style=flat-square" />

<br /><br />

# DevMirror

### Not your critic. Your coach.

One dashboard for your GitHub, LeetCode, Codeforces, Gmail, YouTube, and an AI coach that actually knows your goals.

<br />

[**Live Demo →**](https://dev-mirror.netlify.app) &nbsp;·&nbsp; [**Report a Bug**](https://github.com/YashasviThakur/DevMirror/issues) &nbsp;·&nbsp; [**Request a Feature**](https://github.com/YashasviThakur/DevMirror/issues)

</div>

---

## What is DevMirror?

Most developers have 6 tabs open just to check their own progress — GitHub here, LeetCode there, emails buried somewhere else. DevMirror collapses all of that into one place, adds an AI coach that knows your actual goals, and tells you what to focus on today.

Built for the **WeMakeDevs Pirates of the Coral-bean Hackathon** (May 2026).

---

## Features

### Dashboard
- GitHub contribution grid, top repositories, commit activity, languages, followers
- LeetCode solved count, difficulty breakdown, acceptance rate, recent submissions
- Codeforces rating, rank, recent verdict history
- Google Calendar events for the week ahead
- Editable goal cards (your 3 focus areas, always visible)

### Gmail Radar
- Automatically filters your inbox for **internships, hackathons, and scholarships**
- AI-generated one-line summaries for each opportunity
- Direct deep-link into Gmail for any email

### YouTube Analyser
- Upload your Google Takeout watch history JSON
- See exactly how much of your time was spent on **technical learning vs. entertainment**
- Category breakdown with bar charts

### AI Coach
- Powered by **Cohere** — knows your 3 goals and your live data
- Ask anything: *"What should I focus on today?"*, *"How do I improve my LeetCode streak?"*
- Can **schedule study sessions directly to your Google Calendar** from the chat
- Daily nudge card on load

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS v3, Vite |
| Backend | FastAPI 2.0, SQLAlchemy 2.0, Python 3.11+ |
| Database | SQLite (dev) · PostgreSQL (prod) |
| Auth | Google OAuth2 |
| AI | Cohere |
| Encryption | `cryptography.fernet` — all OAuth tokens encrypted at rest |
| Deploy | Netlify (frontend) · Railway (backend) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Cloud project with OAuth2 credentials
- A Cohere API key

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
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
FERNET_KEY=          # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
GEMINI_API_KEY=your_gemini_key
FRONTEND_URL=http://localhost:5173
DATABASE_URL=sqlite:///./devmirror.db
```

Start the backend:

```bash
uvicorn main:app --reload
```

### 3. Frontend setup

```bash
cd devmirror-frontend
npm install
```

```bash
cp .env.example .env.local
# Set VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and sign in with Google.

---

## Project Structure

```
DevMirror/
├── devmirror-api/          # FastAPI backend
│   ├── main.py             # All API routes & data fetchers
│   ├── models.py           # SQLAlchemy ORM (User, LinkedAccount)
│   ├── auth_router.py      # Google OAuth2 flow
│   └── .env.example
│
├── devmirror-frontend/     # React frontend
│   └── src/
│       ├── pages/          # Dashboard, Gmail, YouTube, Coach, ...
│       ├── components/     # Shared UI components
│       ├── api/            # API client + TypeScript types
│       └── hooks/          # useUserId, etc.
│
└── devmirror-landing.html  # Static landing page
```

---

## Environment Variables

### Backend (`devmirror-api/.env`)

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth2 client secret |
| `GOOGLE_REDIRECT_URI` | Yes | Must match Google Cloud Console exactly |
| `FERNET_KEY` | Yes | Encryption key for stored OAuth tokens |
| `GEMINI_API_KEY` | Yes | Gemini API key for AI coach fallback |
| `FRONTEND_URL` | Yes | Frontend origin (for CORS) |
| `DATABASE_URL` | No | Defaults to SQLite |

### Frontend (`devmirror-frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Backend URL (empty string in dev with Vite proxy) |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

Please open an issue first for major changes so we can discuss the approach.

---

## Roadmap

- [ ] Mobile-responsive layout
- [ ] GitHub Actions / CI pipeline stats
- [ ] Weekly email digest
- [ ] Public profile shareable link
- [ ] Institution dashboard (aggregate analytics)

---

<div align="center">

Built by [Yashasvi Thakur](https://github.com/YashasviThakur) &nbsp;·&nbsp; Powered by [Cohere](https://cohere.com)

⭐ Star this repo if DevMirror helped you — it means a lot.

</div>
