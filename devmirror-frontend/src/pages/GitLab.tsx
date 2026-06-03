import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GitBranch, GitMerge, Star, ExternalLink, RefreshCw, Settings2, ChevronRight, LogIn } from 'lucide-react'
import clsx from 'clsx'
import PageShell from '../components/PageShell'
import LoadingSpinner from '../components/LoadingSpinner'
import { api, GitLabData } from '../api/client'
import { useUserId } from '../hooks/useUserId'

export default function GitLab() {
  const navigate = useNavigate()
  const userId   = useUserId()

  const [data,        setData]        = useState<GitLabData | null>(null)
  const [loading,     setLoading]     = useState(true)
  const [refreshing,  setRefreshing]  = useState(false)
  const [error,       setError]       = useState('')
  const [showSetup,   setShowSetup]   = useState(false)
  const [glUsername,  setGlUsername]  = useState('')
  const [glToken,     setGlToken]     = useState('')
  const [saving,      setSaving]      = useState(false)

  async function load(uid: number) {
    setLoading(true)
    setError('')
    try {
      const d = await api.gitlab(uid)
      setData(d)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('not connected') || msg.includes('400')) {
        setShowSetup(true)
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) load(userId)
    else setLoading(false)
  }, [userId])

  async function handleSave() {
    if (!userId || !glUsername.trim() || !glToken.trim()) return
    setSaving(true)
    try {
      await api.updateGitlabHandle(userId, glUsername.trim(), glToken.trim())
      setShowSetup(false)
      await load(userId)
    } catch {
      setError('Failed to save GitLab credentials.')
    } finally {
      setSaving(false)
    }
  }

  async function handleRefresh() {
    if (!userId) return
    setRefreshing(true)
    await load(userId)
    setRefreshing(false)
  }

  if (!userId) {
    return (
      <div className="min-h-screen bg-dm-bg flex items-center justify-center px-6">
        <div className="text-center max-w-sm">
          <div className="w-14 h-14 rounded-2xl bg-dm-purple/15 flex items-center justify-center mx-auto mb-5">
            <LogIn size={24} className="text-dm-purple-ll" />
          </div>
          <h2 className="font-head font-bold text-xl text-dm-text mb-2">Sign in to view GitLab</h2>
          <button onClick={() => navigate('/login')} className="dm-btn-primary flex items-center gap-2 mx-auto text-sm">
            Sign in <ChevronRight size={13} />
          </button>
        </div>
      </div>
    )
  }

  return (
    <PageShell
      title="GitLab"
      subtitle="Projects, commits, and merge requests from your GitLab account"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => setShowSetup(v => !v)} className={clsx('dm-btn-ghost flex items-center gap-2 text-sm', showSetup && 'border-dm-purple/50 text-dm-purple-ll')}>
            <Settings2 size={14} /> Configure
          </button>
          <button onClick={handleRefresh} disabled={refreshing || loading} className="dm-btn-ghost flex items-center gap-2 text-sm">
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      }
    >
      {/* Setup panel */}
      {showSetup && (
        <div className="dm-card p-6 mb-6 border-dm-purple/25 bg-dm-purple-dim">
          <div className="dm-label mb-4">Connect GitLab Account</div>
          <div className="grid md:grid-cols-2 gap-4 mb-5">
            <div>
              <label className="dm-label block mb-1.5">GitLab Username</label>
              <input value={glUsername} onChange={e => setGlUsername(e.target.value)} placeholder="your-gitlab-username" className="dm-input text-sm h-9" />
            </div>
            <div>
              <label className="dm-label block mb-1.5">Personal Access Token</label>
              <input value={glToken} onChange={e => setGlToken(e.target.value)} type="password" placeholder="glpat-xxxxxxxxxxxxxxxxxxxx" className="dm-input text-sm h-9" />
              <p className="text-[10px] text-dm-muted mt-1">Scopes needed: read_api, read_user, read_repository</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={handleSave} disabled={saving} className="dm-btn-primary text-sm flex items-center gap-2">
              {saving ? <RefreshCw size={13} className="animate-spin" /> : null}
              Save &amp; Connect
            </button>
            <button onClick={() => setShowSetup(false)} className="dm-btn-ghost text-sm">Cancel</button>
          </div>
        </div>
      )}

      {error && (
        <div className="dm-card p-4 mb-5 border-red-500/30 bg-red-500/5 text-red-400 text-sm">{error}</div>
      )}

      {loading ? (
        <LoadingSpinner fullPage label="Fetching GitLab data..." />
      ) : !data ? (
        <div className="dm-card p-10 text-center">
          <GitBranch size={32} className="text-dm-muted mx-auto mb-4" />
          <div className="font-semibold text-dm-text mb-1">GitLab not connected</div>
          <div className="text-sm text-dm-muted mb-4">Add your GitLab username and personal access token to get started.</div>
          <button onClick={() => setShowSetup(true)} className="dm-btn-primary text-sm mx-auto flex items-center gap-2">
            Connect GitLab <ChevronRight size={13} />
          </button>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Stats bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Projects',      value: data.total_projects, color: 'text-dm-purple-ll' },
              { label: 'Commits / week',value: data.commits_week,   color: 'text-dm-green'    },
              { label: 'Open MRs',      value: data.open_mrs,       color: 'text-dm-amber'    },
              { label: 'Top project',   value: data.top_project || '—', color: 'text-dm-cyan', isText: true },
            ].map(({ label, value, color, isText }) => (
              <div key={label} className="dm-card p-4">
                <div className={clsx('font-head font-bold mb-0.5', isText ? 'text-base truncate' : 'text-2xl', color)}>{value}</div>
                <div className="text-[10px] text-dm-muted">{label}</div>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {/* Projects */}
            <div className="dm-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch size={14} className="text-dm-purple-ll" />
                <span className="text-sm font-semibold text-dm-text">Projects</span>
                <span className="dm-badge-purple ml-auto text-[10px]">{data.total_projects} total</span>
              </div>
              <div className="space-y-3">
                {data.projects.length === 0 ? (
                  <div className="text-sm text-dm-muted">No public projects found.</div>
                ) : (
                  data.projects.map((p, i) => (
                    <div key={i} className="flex items-start gap-3 pb-3 border-b border-dm-border last:border-0 last:pb-0">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-dm-text truncate">{p.name}</span>
                          <a href={p.web_url} target="_blank" rel="noreferrer" className="text-dm-muted hover:text-dm-purple-ll ml-auto shrink-0">
                            <ExternalLink size={11} />
                          </a>
                        </div>
                        {p.description && <div className="text-xs text-dm-muted mt-0.5 truncate">{p.description}</div>}
                        <div className="flex items-center gap-3 mt-1.5 text-[10px] text-dm-muted">
                          <span className="flex items-center gap-1"><Star size={9} />{p.stars}</span>
                          <span className="flex items-center gap-1"><GitBranch size={9} />{p.forks}</span>
                          <span className="ml-auto font-mono">{p.last_activity}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
              {data.languages.length > 0 && (
                <div className="flex gap-1.5 flex-wrap mt-4 pt-4 border-t border-dm-border">
                  {data.languages.map(l => (
                    <span key={l} className="dm-badge-purple text-[10px]">{l}</span>
                  ))}
                </div>
              )}
            </div>

            {/* Merge Requests */}
            <div className="dm-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <GitMerge size={14} className="text-dm-amber" />
                <span className="text-sm font-semibold text-dm-text">Open Merge Requests</span>
                <span className="ml-auto dm-badge bg-dm-amber/10 border-dm-amber/30 text-dm-amber text-[10px]">
                  {data.open_mrs} open
                </span>
              </div>
              {data.recent_mrs.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 gap-2">
                  <GitMerge size={24} className="text-dm-muted" />
                  <div className="text-sm text-dm-muted">No open merge requests</div>
                </div>
              ) : (
                <div className="space-y-3">
                  {data.recent_mrs.map((mr, i) => (
                    <div key={i} className="pb-3 border-b border-dm-border last:border-0 last:pb-0">
                      <div className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-dm-green mt-1.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-dm-text truncate flex-1">{mr.title}</span>
                            <a href={mr.web_url} target="_blank" rel="noreferrer" className="text-dm-muted hover:text-dm-purple-ll shrink-0">
                              <ExternalLink size={10} />
                            </a>
                          </div>
                          <div className="text-[10px] text-dm-muted mt-0.5 font-mono">{mr.project} · {mr.created_at}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Profile link */}
          <div className="dm-card p-4 flex items-center gap-3">
            {data.avatar_url && (
              <img src={data.avatar_url} alt={data.name} className="w-8 h-8 rounded-full border border-dm-border" />
            )}
            <div>
              <div className="text-sm font-semibold text-dm-text">{data.name}</div>
              <div className="text-xs text-dm-muted font-mono">@{data.username}</div>
            </div>
            <a href={data.profile_url} target="_blank" rel="noreferrer"
              className="ml-auto dm-btn-ghost text-xs flex items-center gap-1.5">
              View on GitLab <ExternalLink size={11} />
            </a>
          </div>
        </div>
      )}
    </PageShell>
  )
}
