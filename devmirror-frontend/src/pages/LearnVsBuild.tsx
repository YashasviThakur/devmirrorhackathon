import { useEffect, useState } from 'react'
import { RefreshCw, Youtube, Github, BookOpen, Hammer } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import PageShell from '../components/PageShell'
import AIReport from '../components/AIReport'
import LoadingSpinner from '../components/LoadingSpinner'
import { api, LearnVsBuildData, getUserId } from '../api/client'
import clsx from 'clsx'

const DEMO: LearnVsBuildData = {
  analysis: `Your learning/building balance is solid for a CS student at your stage.

This week you spent roughly 6 hours learning (YouTube tutorials + study sessions) vs. 3 productive build hours (GitHub commits + project work).

That's a 2:1 learn:build ratio — healthy at your stage. The risk zone is when it flips to 4:1 or higher, where you're consuming but not creating.

Key observation: Your AI-voice-detection-demo-UI commit shows you're applying what you learn, not just watching. That's the compounding loop.

Action: Next week, try to push one more commit. Even a README improvement counts — shipping creates momentum.

Your ratio is not a weakness. It's a launchpad.`,
  learn_score: 65,
  build_score: 35,
  balance: 'learning_heavy',
  github_commits_week: 3,
  youtube_hours_week: 3.5,
  study_hours_week: 6,
  trend: [
    { week: 'Apr W3', learn: 55, build: 45 },
    { week: 'Apr W4', learn: 70, build: 30 },
    { week: 'May W1', learn: 60, build: 40 },
    { week: 'May W2', learn: 45, build: 55 },
    { week: 'May W3', learn: 72, build: 28 },
    { week: 'May W4', learn: 65, build: 35 },
  ],
}

const balanceLabel = {
  learning_heavy: { label: 'Learning Heavy', color: 'text-dm-cyan',   bg: 'bg-dm-cyan/10 border-dm-cyan/30' },
  building_heavy: { label: 'Building Heavy', color: 'text-dm-amber',  bg: 'bg-dm-amber/10 border-dm-amber/30' },
  balanced:       { label: 'Balanced',       color: 'text-dm-green',  bg: 'bg-dm-green/10 border-dm-green/30' },
}

export default function LearnVsBuild() {
  const [data, setData] = useState<LearnVsBuildData | null>(null)
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try { setData(await api.learnVsBuild(getUserId() ?? undefined)) }
    catch { setData(DEMO) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const d = data ?? DEMO
  const bal = balanceLabel[d.balance]

  return (
    <PageShell
      title="Learn vs Build"
      subtitle="Are you consuming more than you're creating?"
      actions={
        <button onClick={load} disabled={loading} className="dm-btn-ghost flex items-center gap-2 text-sm">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      }
    >
      {loading ? <LoadingSpinner fullPage label="Analysing your balance..." /> : (
        <div className="space-y-6">
          {/* Balance bar */}
          <div className="dm-card p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-head font-bold text-xl text-dm-text">Balance Overview</span>
                  <span className={clsx('dm-badge text-xs', bal.bg, bal.color)}>{bal.label}</span>
                </div>
                <p className="text-sm text-dm-muted">Based on GitHub, YouTube, and Google Calendar data</p>
              </div>
            </div>

            {/* Visual bar */}
            <div className="relative mb-4">
              <div className="flex h-8 rounded-full overflow-hidden border border-dm-border">
                <div
                  className="bg-gradient-to-r from-dm-cyan/80 to-dm-cyan flex items-center justify-center text-xs font-bold text-white transition-all duration-700"
                  style={{ width: `${d.learn_score}%` }}
                >
                  {d.learn_score}%
                </div>
                <div
                  className="bg-gradient-to-r from-dm-purple to-dm-purple-l flex items-center justify-center text-xs font-bold text-white transition-all duration-700"
                  style={{ width: `${d.build_score}%` }}
                >
                  {d.build_score}%
                </div>
              </div>
              <div className="flex justify-between mt-2 text-xs text-dm-muted">
                <div className="flex items-center gap-1.5"><BookOpen size={11} className="text-dm-cyan" /> Learning</div>
                <div className="flex items-center gap-1.5"><Hammer size={11} className="text-dm-purple-ll" /> Building</div>
              </div>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-dm-border">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <Youtube size={13} className="text-red-400" />
                  <span className="text-xs text-dm-muted">YouTube</span>
                </div>
                <div className="font-head font-bold text-lg text-dm-text">{d.youtube_hours_week}h</div>
                <div className="text-[10px] text-dm-muted">this week</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <BookOpen size={13} className="text-dm-cyan" />
                  <span className="text-xs text-dm-muted">Study sessions</span>
                </div>
                <div className="font-head font-bold text-lg text-dm-text">{d.study_hours_week}h</div>
                <div className="text-[10px] text-dm-muted">this week</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <Github size={13} className="text-dm-green" />
                  <span className="text-xs text-dm-muted">GitHub commits</span>
                </div>
                <div className="font-head font-bold text-lg text-dm-text">{d.github_commits_week}</div>
                <div className="text-[10px] text-dm-muted">this week</div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Trend chart */}
            <div className="dm-card p-5">
              <div className="dm-label mb-4">6-Week Trend</div>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={d.trend} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                    <defs>
                      <linearGradient id="learnGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#06B6D4" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="buildGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#7C3AED" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#7C3AED" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2D" />
                    <XAxis dataKey="week" tick={{ fill: '#6B7280', fontSize: 10 }} />
                    <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: '#16161F', border: '1px solid #1E1E2D', borderRadius: '8px', fontSize: '12px' }}
                      labelStyle={{ color: '#E2E8F0' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Area type="monotone" dataKey="learn" name="Learning %" stroke="#06B6D4" fill="url(#learnGrad)" strokeWidth={2} dot={false} />
                    <Area type="monotone" dataKey="build" name="Building %" stroke="#7C3AED" fill="url(#buildGrad)" strokeWidth={2} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI analysis */}
            <div className="dm-card overflow-hidden">
              <div className="flex items-center gap-2 px-5 py-4 border-b border-dm-border bg-dm-surface-2/60">
                <div className="w-2 h-2 rounded-full bg-dm-purple animate-pulse-slow" />
                <span className="text-sm font-semibold text-dm-text">AI Analysis</span>
              </div>
              <div className="p-5">
                <AIReport content={d.analysis} typingSpeed={6} />
              </div>
            </div>
          </div>
        </div>
      )}
    </PageShell>
  )
}
