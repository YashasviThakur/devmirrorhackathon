import { useEffect, useState } from 'react'
import { Mail, RefreshCw, AlertCircle, ExternalLink, Tag } from 'lucide-react'
import PageShell from '../components/PageShell'
import LoadingSpinner from '../components/LoadingSpinner'
import { api, InternshipData } from '../api/client'
import clsx from 'clsx'

const DEMO: InternshipData = {
  summary: 'Found 2 internship/hackathon leads worth following up on.',
  emails: [
    {
      id: '1',
      subject: 'Summer Internship 2026 —Backend Engineering',
      from: 'recruiting@techcorp.com',
      date: '2026-05-27',
      snippet: 'We came across your GitHub profile and would love to chat about...',
      category: 'internship',
      ai_summary: 'Recruiting team at TechCorp reached out about a backend internship. They likely found your GitHub. Worth a polished reply within 48h.',
      action_required: true,
      gmail_link: 'https://mail.google.com/mail/u/0/#inbox',
    },
    {
      id: '2',
      subject: 'WeMakeDevs Hackathon —Pirates of the Coral-bean',
      from: 'noreply@wemakedevs.org',
      date: '2026-05-25',
      snippet: 'You\'re registered! Here\'s everything you need for May 25-31...',
      category: 'hackathon',
      ai_summary: 'Confirmation for the Pirates of the Coral-bean hackathon. Prize: iPad. Track 2 —Personal Agent. You\'re already building DevMirror for this.',
      action_required: false,
      gmail_link: 'https://mail.google.com/mail/u/0/#inbox',
    },
    {
      id: '3',
      subject: 'Google Summer of Code 2026 —Application Open',
      from: 'gsoc@google.com',
      date: '2026-05-20',
      snippet: 'Applications for GSoC 2026 are now open. The deadline is...',
      category: 'internship',
      ai_summary: 'GSoC 2026 applications are open. Deadline approaching. Your Python + AI project experience makes you a strong candidate.',
      action_required: true,
      gmail_link: 'https://mail.google.com/mail/u/0/#inbox',
    },
    {
      id: '4',
      subject: 'MLH Fellowship —Spring 2026 Applications',
      from: 'fellowship@mlh.io',
      date: '2026-05-18',
      snippet: 'Applications for the MLH Fellowship Spring 2026 cohort are...',
      category: 'scholarship',
      ai_summary: 'MLH Fellowship opportunity. Paid remote program, 12 weeks, working on open source. Strong alignment with your current work.',
      action_required: false,
      gmail_link: 'https://mail.google.com/mail/u/0/#inbox',
    },
  ],
}

const catStyle = {
  internship:  { label: 'Internship',  class: 'bg-dm-purple/15 border-dm-purple/30 text-dm-purple-ll' },
  hackathon:   { label: 'Hackathon',   class: 'bg-dm-cyan/10 border-dm-cyan/30 text-dm-cyan' },
  scholarship: { label: 'Scholarship', class: 'bg-dm-amber/10 border-dm-amber/30 text-dm-amber' },
  other:       { label: 'Other',       class: 'bg-dm-border border-dm-border text-dm-muted' },
}

const CATS = ['all', 'internship', 'hackathon', 'scholarship'] as const
type Cat = typeof CATS[number]

export default function Internship() {
  const [data, setData] = useState<InternshipData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState<Cat>('all')

  async function load() {
    setLoading(true)
    try { setData(await api.internship()) }
    catch { setData(DEMO) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const d = data ?? DEMO
  const filtered = filter === 'all' ? d.emails : d.emails.filter(e => e.category === filter)
  const active = d.emails.find(e => e.id === selected) ?? d.emails[0]

  return (
    <PageShell
      title="Internship Radar"
      subtitle={d.summary}
      actions={
        <button onClick={load} disabled={loading} className="dm-btn-ghost flex items-center gap-2 text-sm">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      }
    >
      {loading ? <LoadingSpinner fullPage label="Scanning Gmail for opportunities..." /> : (
        <div className="space-y-5">
          {/* Filter tabs */}
          <div className="flex gap-2 flex-wrap">
            {CATS.map(c => (
              <button
                key={c}
                onClick={() => setFilter(c)}
                className={clsx(
                  'px-4 py-1.5 rounded-full text-xs font-medium border transition-all duration-150',
                  filter === c
                    ? 'bg-dm-purple border-dm-purple text-white shadow-glow-sm'
                    : 'bg-transparent border-dm-border text-dm-muted hover:border-dm-purple/40 hover:text-dm-text',
                )}
              >
                {c.charAt(0).toUpperCase() + c.slice(1)}
                {c !== 'all' && (
                  <span className="ml-1.5 text-[10px] opacity-70">
                    {d.emails.filter(e => e.category === c).length}
                  </span>
                )}
              </button>
            ))}
          </div>

          <div className="grid lg:grid-cols-5 gap-5">
            {/* Email list */}
            <div className="lg:col-span-2 space-y-2">
              {filtered.length === 0 ? (
                <div className="dm-card p-8 text-center text-dm-muted text-sm">No emails in this category.</div>
              ) : (
                filtered.map(email => (
                  <button
                    key={email.id}
                    onClick={() => setSelected(email.id)}
                    className={clsx(
                      'w-full text-left dm-card p-4 transition-all duration-150',
                      (selected ?? d.emails[0]?.id) === email.id
                        ? 'border-dm-purple/40 shadow-glow-sm bg-dm-surface-2'
                        : 'hover:border-dm-border/80 hover:bg-dm-surface-2/50',
                    )}
                  >
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2 min-w-0">
                        {email.action_required && (
                          <AlertCircle size={12} className="text-dm-amber shrink-0" />
                        )}
                        <span className="text-xs font-semibold text-dm-text truncate">{email.subject}</span>
                      </div>
                      <span className={clsx('dm-badge shrink-0 text-[10px]', catStyle[email.category].class)}>
                        {catStyle[email.category].label}
                      </span>
                    </div>
                    <div className="text-[10px] text-dm-muted font-mono mb-1.5">{email.from}</div>
                    <div className="text-xs text-dm-muted line-clamp-2">{email.snippet}</div>
                    <div className="text-[10px] text-dm-dim font-mono mt-2">{email.date}</div>
                  </button>
                ))
              )}
            </div>

            {/* Email detail */}
            {active && (
              <div className="lg:col-span-3 dm-card overflow-hidden">
                <div className="px-5 py-4 border-b border-dm-border bg-dm-surface-2/60 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Mail size={14} className="text-dm-muted" />
                    <span className="text-sm font-semibold text-dm-text truncate">{active.subject}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={clsx('dm-badge text-xs', catStyle[active.category].class)}>
                      <Tag size={9} className="inline mr-1" />{catStyle[active.category].label}
                    </span>
                    {active.action_required && (
                      <span className="dm-badge bg-dm-amber/10 border-dm-amber/30 text-dm-amber text-xs">
                        <AlertCircle size={9} className="inline mr-1" />Action needed
                      </span>
                    )}
                  </div>
                </div>

                <div className="p-5 space-y-5">
                  <div className="flex gap-6 text-xs text-dm-muted font-mono">
                    <span>From: <span className="text-dm-text">{active.from}</span></span>
                    <span>Date: <span className="text-dm-text">{active.date}</span></span>
                  </div>

                  <div className="p-4 rounded-lg bg-dm-surface-2 border border-dm-border text-sm text-dm-text/80 leading-relaxed italic">
                    "{active.snippet}"
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-2 h-2 rounded-full bg-dm-purple animate-pulse-slow" />
                      <span className="dm-label">AI Summary</span>
                    </div>
                    <div className="p-4 rounded-lg bg-dm-purple-dim border border-dm-purple/20 text-sm text-dm-text leading-relaxed">
                      {active.ai_summary}
                    </div>
                  </div>

                  {active.action_required && (
                    <div className="flex gap-3">
                      <button className="dm-btn-primary text-sm flex items-center gap-2">
                        <ExternalLink size={13} /> Open in Gmail
                      </button>
                      <button className="dm-btn-ghost text-sm">Mark Done</button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </PageShell>
  )
}
