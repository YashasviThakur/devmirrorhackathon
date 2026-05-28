import { useEffect, useState } from 'react'
import { Sparkles, RefreshCw, Github, Code2, Trophy, Calendar, Clock } from 'lucide-react'
import PageShell from '../components/PageShell'
import AIReport from '../components/AIReport'
import LoadingSpinner from '../components/LoadingSpinner'
import StatCard from '../components/StatCard'
import { api, GrowthReportData, getUserId } from '../api/client'

const DEMO: GrowthReportData = {
  report: `Yashasvi, what an exciting growth report!

Your repo AI-voice-detection-demo-UI showcases your Python + HTML skills — that's portfolio gold that any recruiter will notice.

This Week At a Glance:
  → GitHub: 3 commits across active repos
  → LeetCode: 11 total problems · 2-day streak · 4 mediums cracked
  → Codeforces: Holding at 1200 (Pupil) · solid foundation
  → Study time: 4 sessions logged in Google Calendar
  → Internship leads: 2 emails worth following up on

The Pattern I See:
You're building AND solving — that's rare. Most devs do one or the other. You're doing both, which means your interview prep and your portfolio are growing together.

11 LeetCode problems with a 2-day streak. That's the habit that compounds. At this rate: 77 by end of month.

Today's Nudge:
Try one LeetCode Medium tonight. Not because you're behind — you're not. Because that's the next step for someone at your level.

"Consistency beats intensity."

Keep going. The mirror doesn't lie — you're growing.`,
  github:     { repos: 8, commits_week: 3, top_repo: 'AI-voice-detection-demo-UI', languages: ['Python', 'HTML', 'JavaScript'] },
  leetcode:   { total: 11, easy: 5, medium: 4, hard: 2, streak: 2 },
  codeforces: { rating: 1200, rank: 'Pupil', solved: 23 },
  calendar:   { study_hours_week: 6, upcoming: [{ title: 'DSA Practice', time: 'Today 8 PM' }, { title: 'System Design Study', time: 'Tomorrow 7 PM' }] },
  generated_at: new Date().toISOString(),
}

export default function GrowthReport() {
  const [data, setData] = useState<GrowthReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const d = await api.growthReport(getUserId() ?? undefined)
      setData(d)
    } catch {
      setData(DEMO)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const d = data ?? DEMO

  return (
    <PageShell
      title="Growth Report"
      subtitle="AI-generated daily coaching · Powered by Cohere"
      actions={
        <button onClick={load} disabled={loading} className="dm-btn-ghost flex items-center gap-2 text-sm">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Regenerate
        </button>
      }
    >
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
        <StatCard label="LeetCode Solved" value={d.leetcode?.total ?? 0} sub={`${d.leetcode?.streak ?? 0}-day streak`}       icon={Code2}    accent="cyan"   loading={loading} />
        <StatCard label="Codeforces"      value={d.codeforces?.rating ?? 0} sub={d.codeforces?.rank ?? 'unrated'}              icon={Trophy}   accent="amber"  loading={loading} />
        <StatCard label="GitHub Commits"  value={d.github?.commits_week ?? 0} sub="This week"                                  icon={Github}   accent="green"  loading={loading} />
        <StatCard label="Study Hours"     value={`${d.calendar?.study_hours_week ?? 0}h`} sub="This week"                      icon={Calendar} accent="purple" loading={loading} />
      </div>

      {/* Main report */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* AI Report Panel */}
        <div className="lg:col-span-2 dm-card overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-dm-border bg-dm-surface-2/60">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-dm-purple animate-pulse-slow" />
              <span className="text-sm font-semibold text-dm-text font-head">Cohere Report</span>
            </div>
            {d.generated_at && (
              <div className="flex items-center gap-1.5 text-xs text-dm-muted font-mono">
                <Clock size={11} />
                {new Date(d.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            )}
          </div>
          <div className="p-6 min-h-[400px]">
            {loading ? (
              <LoadingSpinner fullPage label="AI is analysing your data..." />
            ) : (
              <AIReport content={d.report} typingSpeed={6} />
            )}
          </div>
        </div>

        {/* Sidebar: Sources */}
        <div className="space-y-4">
          <div className="dm-card p-4">
            <div className="dm-label mb-3">GitHub</div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-dm-muted">Top repo</span>
                <span className="text-dm-text font-mono text-xs truncate max-w-[140px]">{d.github?.top_repo ?? '?'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-dm-muted">Commits</span>
                <span className="text-dm-green font-mono">{d.github?.commits_week ?? 0} this week</span>
              </div>
              <div className="flex gap-1.5 mt-2 flex-wrap">
                {(d.github?.languages ?? []).map(l => (
                  <span key={l} className="dm-badge-purple">{l}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="dm-card p-4">
            <div className="dm-label mb-3">LeetCode Breakdown</div>
            <div className="space-y-2">
              {[
                { label: 'Easy',   val: d.leetcode?.easy ?? 0,   color: 'bg-dm-green',  pct: ((d.leetcode?.easy ?? 0) / Math.max(d.leetcode?.total ?? 1, 1)) * 100 },
                { label: 'Medium', val: d.leetcode?.medium ?? 0, color: 'bg-dm-amber',  pct: ((d.leetcode?.medium ?? 0) / Math.max(d.leetcode?.total ?? 1, 1)) * 100 },
                { label: 'Hard',   val: d.leetcode?.hard ?? 0,   color: 'bg-red-500',   pct: ((d.leetcode?.hard ?? 0) / Math.max(d.leetcode?.total ?? 1, 1)) * 100 },
              ].map(({ label, val, color, pct }) => (
                <div key={label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-dm-muted">{label}</span>
                    <span className="text-dm-text font-mono">{val}</span>
                  </div>
                  <div className="h-1.5 bg-dm-border rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="dm-card p-4">
            <div className="dm-label mb-3">Upcoming Sessions</div>
            <div className="space-y-2">
              {(d.calendar?.upcoming ?? []).map(e => (
                <div key={e.title} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-dm-purple shrink-0" />
                  <div className="flex-1">
                    <div className="text-xs text-dm-text">{e.title}</div>
                    <div className="text-[10px] text-dm-muted font-mono">{e.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="dm-card p-4 bg-dm-purple-dim border-dm-purple/20">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={14} className="text-dm-purple-ll" />
              <span className="text-sm font-semibold text-dm-purple-ll">Today's Nudge</span>
            </div>
            <p className="text-xs text-dm-text/80 leading-relaxed">
              Try one LeetCode Medium tonight. Consistency beats intensity.
            </p>
          </div>
        </div>
      </div>
    </PageShell>
  )
}
