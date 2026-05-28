import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Github, Code2, Trophy, Mail, Calendar, Youtube,
  GitCommit, CheckCircle2, ArrowRight,
} from 'lucide-react'

// ?"??"? GitHub contribution grid ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
function MockGithubGrid() {
  const [cells, setCells] = useState<number[]>([])
  useEffect(() => {
    setCells(Array.from({ length: 364 }, () =>
      Math.random() < 0.4 ? 0 : Math.floor(Math.random() * 5),
    ))
  }, [])
  const shades = ['bg-[#EDE9E1]', 'bg-[#C4BFAF]', 'bg-[#9A9280]', 'bg-[#5C5750]', 'bg-[#1A1A14]']
  return (
    <div>
      <div className="flex gap-0.5 overflow-hidden">
        {Array.from({ length: 52 }, (_, col) => (
          <div key={col} className="flex flex-col gap-0.5">
            {Array.from({ length: 7 }, (_, row) => {
              const v = cells[col * 7 + row] ?? 0
              return <div key={row} className={`w-2.5 h-2.5 ${shades[v]}`} />
            })}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-4 text-xs text-dm-muted font-mono">
        <GitCommit size={11} /> 52 weeks · 364 days tracked
      </div>
    </div>
  )
}

// ?"??"? LeetCode rings ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
function LeetCodeRing({ pct, color, label }: { pct: number; color: string; label: string }) {
  const r = 28, circ = 2 * Math.PI * r
  const [dash, setDash] = useState(0)
  useEffect(() => { const t = setTimeout(() => setDash((pct / 100) * circ), 400); return () => clearTimeout(t) }, [pct, circ])
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={70} height={70} className="-rotate-90">
        <circle cx={35} cy={35} r={r} fill="none" stroke="#E2DFD7" strokeWidth={5} />
        <circle cx={35} cy={35} r={r} fill="none" stroke={color} strokeWidth={5}
          strokeDasharray={circ} strokeDashoffset={circ - dash}
          strokeLinecap="butt" className="transition-all duration-1000 ease-out" />
      </svg>
      <span className="text-[11px] text-dm-muted font-mono">{label}</span>
    </div>
  )
}

// ?"??"? Gmail stream ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
const MOCK_EMAILS = [
  { from: 'recruiting@stripe.com',  subject: 'Summer 2026 Internship - Backend'  },
  { from: 'devrel@google.com',      subject: 'GSoC 2026 Applications Open'        },
  { from: 'noreply@mlh.io',         subject: 'MLH Fellowship - Apply Now'          },
  { from: 'careers@microsoft.com',  subject: 'New Grad SWE - AI Division'          },
  { from: 'hackathon@devpost.com',  subject: 'Build with AI - $50k in prizes'      },
]
function GmailStream() {
  const [visible, setVisible] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setVisible(v => Math.min(v + 1, MOCK_EMAILS.length)), 700)
    return () => clearInterval(t)
  }, [])
  return (
    <div className="space-y-1">
      {MOCK_EMAILS.slice(0, visible).map((e, i) => (
        <div key={i} className="flex items-center gap-3 text-xs bg-white border border-dm-border px-3 py-2.5 animate-slide-up">
          <Mail size={11} className="text-dm-red shrink-0" />
          <span className="text-dm-muted truncate w-28 font-mono">{e.from}</span>
          <span className="text-dm-text truncate flex-1">{e.subject}</span>
        </div>
      ))}
    </div>
  )
}

// ?"??"? Terminal ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
const TERMINAL_LINES = [
  '$ devmirror --fetch-all',
  '  -> GitHub     [########--]  3 commits',
  '  -> LeetCode   [########--]  streak: 7d',
  '  -> Codeforces [######----]  rating: 1487',
  '  -> Gmail      [##########]  4 leads',
  '  -> Calendar   [########--]  2 sessions',
  '',
  '  * Cohere coaching...',
  '',
  '  "You\'re building AND solving - that\'s rare."',
  '  "Today\'s nudge: try one System Design read."',
  '  "Consistency beats intensity."',
]
function Terminal() {
  const [lines, setLines] = useState<string[]>([])
  useEffect(() => {
    let cursor = 0
    const t = setInterval(() => {
      if (cursor < TERMINAL_LINES.length) {
        const next = TERMINAL_LINES[cursor] ?? ''
        setLines(p => [...p, next])
        cursor++
      } else {
        clearInterval(t)
      }
    }, 100)
    return () => clearInterval(t)
  }, [])
  return (
    <div className="bg-[#111108] border border-white/10">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10">
        <span className="w-3 h-3 rounded-full bg-white/20" />
        <span className="w-3 h-3 rounded-full bg-white/20" />
        <span className="w-3 h-3 rounded-full bg-white/20" />
        <span className="ml-3 text-xs text-white/40 font-mono">devmirror - live pipeline</span>
        <span className="ml-auto text-[10px] font-mono px-2 py-0.5 border border-dm-green/50 text-dm-green">live</span>
      </div>
      <div className="p-5 min-h-[280px] font-mono text-sm space-y-0.5">
        {lines.map((line, idx) => {
          const l = typeof line === 'string' ? line : ''
          return (
            <div key={idx} className={
              l.startsWith('  *') ? 'text-white/90 font-semibold mt-2' :
              l.startsWith('$')   ? 'text-[#A8D8A8]' :
              l.startsWith('  "') ? 'text-white/60 pl-2 italic' :
              l.startsWith('  ->') ? 'text-white/50 pl-2' :
              'text-white/70'
            }>
              {l || '·'}
            </div>
          )
        })}
        {lines.length < TERMINAL_LINES.length && (
          <span className="inline-block w-2 h-4 bg-white/70 animate-blink" />
        )}
      </div>
    </div>
  )
}

// ?"??"? Data sources ticker ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
const SOURCES = [
  { icon: Github,   name: 'GitHub'     },
  { icon: Code2,    name: 'LeetCode'   },
  { icon: Trophy,   name: 'Codeforces' },
  { icon: Mail,     name: 'Gmail'      },
  { icon: Calendar, name: 'Calendar'   },
  { icon: Youtube,  name: 'YouTube'    },
]

const FEATURES = [
  { title: 'Daily AI Growth Report',   desc: 'Cohere analyses all your data and delivers a personalised coaching session every day.' },
  { title: 'Closed-Loop Scheduling',   desc: 'Ask the coach to plan your week and it automatically creates Google Calendar events for you.' },
  { title: 'Internship Radar',          desc: 'Gmail filter surfaces only internship, hackathon, and recruitment emails - zero noise.' },
  { title: 'Multi-Tenant & Encrypted', desc: 'OAuth tokens are Fernet-encrypted at rest. Institution accounts keep team goals isolated.' },
]

// ?"??"? Main ?"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"??"?
export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-white text-dm-text overflow-x-hidden">

      {/* ?"??"? Nav ?"??"? */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white border-b border-dm-border">
        <div className="max-w-[1400px] mx-auto px-8 h-16 flex items-center justify-between">
          <span className="font-black text-xl tracking-tighter">DevMirror</span>
          <div className="hidden md:flex items-center">
            <div className="w-px h-7 bg-dm-border mx-8" />
            <div className="flex items-center gap-8 text-sm font-medium text-dm-muted">
              <a href="#platforms" className="hover:text-dm-text transition-colors">Platforms</a>
              <a href="#features"  className="hover:text-dm-text transition-colors">Features</a>
              <a href="#accounts"  className="hover:text-dm-text transition-colors">Accounts</a>
            </div>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="bg-[#1A1A14] text-white text-sm font-semibold px-5 py-2.5 hover:opacity-80 transition-opacity"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* ?"??"? Hero - dark section ?"??"? */}
      <section className="bg-[#1A1A14] pt-36 pb-28 px-8">
        <div className="max-w-[1400px] mx-auto">
          <p className="text-dm-dim text-[11px] font-mono uppercase tracking-widest mb-10">
            Cohere · FastAPI · Multi-tenant · Fernet Encrypted
          </p>
          <h1 className="text-display text-white mb-10 max-w-4xl">
            Built to track.<br />Built to grow.
          </h1>
          <div className="flex flex-col lg:flex-row gap-10 items-start">
            <p className="text-white/55 text-lg font-light leading-relaxed max-w-md">
              DevMirror connects GitHub, LeetCode, Codeforces, Gmail, Calendar, and YouTube -
              then sends it all to Cohere to coach you, schedule your week, and surface real internship leads.
            </p>
            <div className="flex gap-4 shrink-0">
              <button
                onClick={() => navigate('/login')}
                className="border border-white text-white text-sm font-semibold px-8 py-4
                           hover:bg-white hover:text-[#1A1A14] transition-colors"
              >
                Get Started Free
              </button>
              <a
                href="https://github.com/YashasviThakur/DevMirror"
                target="_blank" rel="noopener noreferrer"
                className="border border-white/30 text-white/60 text-sm font-semibold px-8 py-4
                           flex items-center gap-2 hover:border-white/60 transition-colors"
              >
                <Github size={15} /> Source
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ?"??"? Platforms ticker ?"??"? */}
      <section id="platforms" className="border-b border-dm-border overflow-hidden">
        <div className="flex animate-ticker whitespace-nowrap select-none">
          {[...SOURCES, ...SOURCES, ...SOURCES, ...SOURCES].map((s, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-3 px-10 py-5 border-r border-dm-border text-sm font-medium text-dm-muted shrink-0"
            >
              <s.icon size={15} /> {s.name}
            </span>
          ))}
        </div>
      </section>

      {/* ?"??"? Section 1 - GitHub - cream ?"??"? */}
      <section className="bg-[#F5F0E8] py-28 px-8">
        <div className="max-w-[1400px] mx-auto grid lg:grid-cols-2 gap-20 items-center">
          <div>
            <p className="dm-label mb-6">GitHub Integration</p>
            <h2 className="text-display-md text-dm-text mb-8">
              Every commit,<br />every streak.
            </h2>
            <p className="text-dm-muted text-lg font-light leading-relaxed max-w-md">
              Your full contribution grid, weekly commit count, top repositories, and language
              breakdown - pulled live from the GitHub API and reflected back in one view.
            </p>
            <div className="flex items-center gap-2 mt-6 text-sm font-medium">
              <CheckCircle2 size={15} className="text-dm-green" />
              <span className="text-dm-muted">Public repos · Commit events · Language stats</span>
            </div>
          </div>
          <div className="bg-white border border-dm-border p-8">
            <div className="dm-label mb-6">Contribution Grid - Last 52 Weeks</div>
            <MockGithubGrid />
          </div>
        </div>
      </section>

      {/* ?"??"? Section 2 - AI Coach - dark ?"??"? */}
      <section className="bg-[#1A1A14] py-28 px-8">
        <div className="max-w-[1400px] mx-auto grid lg:grid-cols-2 gap-20 items-center">
          <div className="order-2 lg:order-1">
            <Terminal />
          </div>
          <div className="order-1 lg:order-2">
            <p className="dm-label text-dm-dim mb-6">Cohere</p>
            <h2 className="text-display-md text-white mb-8">
              AI that coaches,<br />not just reports.
            </h2>
            <p className="text-white/55 text-lg font-light leading-relaxed max-w-md">
              Ask the coach to plan your week and it creates Google Calendar events automatically.
              Every day starts with a personalised session built from your real data.
            </p>
          </div>
        </div>
      </section>

      {/* ?"??"? Section 3 - LeetCode + Gmail - white ?"??"? */}
      <section className="bg-white py-28 px-8">
        <div className="max-w-[1400px] mx-auto grid lg:grid-cols-2 gap-20 items-start">
          {/* LeetCode */}
          <div>
            <p className="dm-label mb-6">LeetCode & Codeforces</p>
            <h2 className="text-display-md text-dm-text mb-8">
              Problems solved,<br />streaks alive.
            </h2>
            <p className="text-dm-muted text-lg font-light leading-relaxed mb-10">
              Ring charts, streak counters, difficulty breakdowns, and Codeforces rating -
              all in one DSA progress view.
            </p>
            <div className="bg-[#F5F0E8] border border-dm-border p-8">
              <div className="flex items-center justify-around">
                <LeetCodeRing pct={45} color="#2D6A4F" label="Easy"   />
                <LeetCodeRing pct={36} color="#B45309" label="Medium" />
                <LeetCodeRing pct={18} color="#CC2200" label="Hard"   />
              </div>
              <div className="flex items-center justify-center gap-2 mt-6 text-xs text-dm-muted font-mono">
                <CheckCircle2 size={11} className="text-dm-green" /> 7-day streak active
              </div>
            </div>
          </div>

          {/* Gmail */}
          <div>
            <p className="dm-label mb-6">Gmail Radar</p>
            <h2 className="text-display-md text-dm-text mb-8">
              Internships,<br />surfaced daily.
            </h2>
            <p className="text-dm-muted text-lg font-light leading-relaxed mb-10">
              Smart Gmail filter isolates internship, hackathon, and recruitment emails
              from the noise - categorised and action-flagged automatically.
            </p>
            <div className="bg-[#F5F0E8] border border-dm-border p-6">
              <div className="dm-label mb-4">Live opportunity stream</div>
              <GmailStream />
            </div>
          </div>
        </div>
      </section>

      {/* ?"??"? Features grid - cream ?"??"? */}
      <section id="features" className="bg-[#F5F0E8] py-28 px-8">
        <div className="max-w-[1400px] mx-auto">
          <div className="mb-16">
            <p className="dm-label mb-5">Platform Capabilities</p>
            <h2 className="text-display-md text-dm-text max-w-2xl">
              Hardworking tools<br />for serious devs.
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 border border-dm-border">
            {FEATURES.map(({ title, desc }, i) => (
              <div
                key={title}
                className={`bg-white p-8 ${i < 3 ? 'border-r border-dm-border' : ''}`}
              >
                <div className="w-2 h-2 bg-[#1A1A14] mb-6" />
                <h3 className="font-bold text-base leading-tight tracking-tight mb-3">{title}</h3>
                <p className="text-sm text-dm-muted font-light leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ?"??"? Account tiers - dark / white ?"??"? */}
      <section id="accounts" className="bg-white py-28 px-8">
        <div className="max-w-[1400px] mx-auto">
          <div className="mb-16">
            <p className="dm-label mb-5">Account Types</p>
            <h2 className="text-display-md text-dm-text">
              Individual or<br />institutional.
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Personal - dark card */}
            <div className="bg-[#1A1A14] p-10 flex flex-col">
              <p className="dm-label text-dm-dim mb-6">Personal</p>
              <h3 className="font-black text-3xl text-white tracking-tight mb-5 leading-tight">
                Track your<br />individual growth.
              </h3>
              <p className="text-white/55 font-light leading-relaxed mb-10 flex-1">
                Set 3 personal focus goals, connect all six data sources, and get a daily AI
                coaching session tailored to exactly where you are right now.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="self-start border border-white text-white text-sm font-semibold px-6 py-3
                           hover:bg-white hover:text-[#1A1A14] transition-colors flex items-center gap-2"
              >
                Get Started <ArrowRight size={14} />
              </button>
            </div>

            {/* Institutional - cream card */}
            <div className="bg-[#F5F0E8] border border-dm-border p-10 flex flex-col">
              <p className="dm-label mb-6">Institutional</p>
              <h3 className="font-black text-3xl text-dm-text tracking-tight mb-5 leading-tight">
                For colleges<br />and bootcamps.
              </h3>
              <p className="text-dm-muted font-light leading-relaxed mb-10 flex-1">
                Register under your institution name. Each student's OAuth tokens remain
                individually isolated and Fernet-encrypted. Track cohort progress as a unit.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="self-start border border-dm-text text-dm-text text-sm font-semibold px-6 py-3
                           hover:bg-dm-text hover:text-white transition-colors flex items-center gap-2"
              >
                Sign in as Institution <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ?"??"? CTA - orange ?"??"? */}
      <section className="bg-[#F04E00] py-28 px-8">
        <div className="max-w-[1400px] mx-auto grid lg:grid-cols-2 gap-20 items-center">
          <h2 className="text-display text-white">
            Start your<br />growth story.
          </h2>
          <div>
            <p className="text-white/70 text-lg font-light leading-relaxed mb-10 max-w-md">
              One click. Your entire developer journey - GitHub, LeetCode, Codeforces, Gmail,
              Calendar, YouTube - reflected back with AI coaching.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="border border-white text-white text-sm font-semibold px-8 py-4
                         hover:bg-white hover:text-[#F04E00] transition-colors flex items-center gap-2"
            >
              Get Started - it's free <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </section>

      {/* ?"??"? Footer ?"??"? */}
      <footer className="bg-[#1A1A14] border-t border-white/10 px-8 py-8">
        <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-black text-white text-xl tracking-tighter">DevMirror</span>
          <span className="text-dm-dim text-xs font-mono">
            Pirates of the Coral-bean Hackathon · May 2026 · Powered by Cohere · FastAPI · Fernet
          </span>
        </div>
      </footer>
    </div>
  )
}

