import { ElementType, ReactNode, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Radar, Flame, AlertTriangle, Waypoints, Ruler,
  RefreshCw, Loader, LogIn,
} from 'lucide-react'
import clsx from 'clsx'
import PageShell from '../components/PageShell'
import LoadingSpinner from '../components/LoadingSpinner'
import { api, OrbitContext } from '../api/client'
import { useUserId } from '../hooks/useUserId'

const fmt = (n: number) => n.toLocaleString()

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-dm-border p-4 bg-white">
      <div className="text-2xl font-black text-dm-text tracking-tight">{fmt(value)}</div>
      <div className="text-[11px] text-dm-muted font-mono uppercase tracking-widest mt-1">{label}</div>
    </div>
  )
}

function Panel({ icon: Icon, title, accent, children }: {
  icon: ElementType; title: string; accent: string; children: ReactNode
}) {
  return (
    <div className="border border-dm-border bg-white">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-dm-border">
        <Icon size={15} style={{ color: accent }} />
        <h3 className="text-sm font-bold text-dm-text">{title}</h3>
      </div>
      <div className="p-4 space-y-2">{children}</div>
    </div>
  )
}

function Bar({ label, sub, value, max, accent }: {
  label: string; sub?: string; value: number; max: number; accent: string
}) {
  const pct = max > 0 ? Math.max(4, Math.round((value / max) * 100)) : 0
  return (
    <div>
      <div className="flex items-baseline justify-between gap-2 mb-1">
        <span className="text-xs font-medium text-dm-text truncate" title={label}>{label}</span>
        <span className="text-xs font-mono text-dm-muted shrink-0">
          {value}{sub ? <span className="text-dm-muted/60"> {sub}</span> : null}
        </span>
      </div>
      <div className="h-1.5 bg-dm-border/60">
        <div className="h-full" style={{ width: `${pct}%`, background: accent }} />
      </div>
    </div>
  )
}

const base = (p: string) => p.split('/').pop() || p

export default function OrbitInsights() {
  const navigate = useNavigate()
  const userId = useUserId()

  const [data, setData]           = useState<OrbitContext | null>(null)
  const [loading, setLoading]     = useState(true)
  const [refreshing, setRefresh]  = useState(false)
  const [error, setError]         = useState('')

  async function load(uid: number) {
    setError('')
    try {
      setData(await api.orbit(uid))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
      setRefresh(false)
    }
  }

  useEffect(() => {
    if (userId) load(userId)
    else setLoading(false)
  }, [userId])

  if (!userId) {
    return (
      <PageShell title="Orbit Insights">
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <Radar className="text-dm-muted mb-4" size={32} />
          <p className="text-dm-muted mb-4">Sign in to view the Orbit knowledge graph.</p>
          <button onClick={() => navigate('/login')}
            className="flex items-center gap-2 px-4 py-2 bg-dm-text text-white text-sm font-medium">
            <LogIn size={14} /> Sign in
          </button>
        </div>
      </PageShell>
    )
  }

  if (loading) return <PageShell title="Orbit Insights"><LoadingSpinner /></PageShell>

  const refreshBtn = (
    <button
      onClick={() => { setRefresh(true); if (userId) load(userId) }}
      disabled={refreshing}
      className="flex items-center gap-2 px-3 py-1.5 border border-dm-border text-xs text-dm-muted hover:text-dm-text transition-colors"
    >
      <RefreshCw size={13} className={clsx(refreshing && 'animate-spin')} /> Refresh
    </button>
  )

  const unavailable = !data || data.available === false
  if (unavailable) {
    return (
      <PageShell title="Orbit Insights"
        subtitle="GitLab Orbit knowledge graph" actions={refreshBtn}>
        <div className="border border-dm-border bg-amber-50 p-6 flex gap-3">
          <AlertTriangle className="text-amber-500 shrink-0" size={20} />
          <div>
            <p className="text-sm font-semibold text-dm-text">Orbit graph not available on the server</p>
            <p className="text-sm text-dm-muted mt-1">
              {data?.detail || error ||
               'Install the GitLab Orbit CLI and index a repo (orbit index .) where the backend runs.'}
            </p>
            <p className="text-xs text-dm-muted/70 mt-2 font-mono">docs.gitlab.com/orbit</p>
          </div>
        </div>
      </PageShell>
    )
  }

  const stats   = data.stats
  const hotspots = data.raw?.hotspots ?? []
  const blast    = data.raw?.blast_radius ?? []
  const coupling = data.raw?.coupling ?? []
  const longFns  = data.raw?.long_functions ?? []

  const maxDefs    = Math.max(1, ...hotspots.map(h => h.definitions))
  const maxCallers = Math.max(1, ...blast.map(b => b.callers))
  const maxImp     = Math.max(1, ...coupling.map(c => c.importers))
  const maxSpan    = Math.max(1, ...longFns.map(f => f.span))

  return (
    <PageShell
      title="Orbit Insights"
      subtitle="GitLab Orbit knowledge graph · architecture-aware coaching"
      actions={refreshBtn}
    >
      {data.summary && (
        <p className="text-sm text-dm-muted font-mono mb-6">{data.summary}</p>
      )}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <StatCard label="Files"       value={stats.gl_file} />
          <StatCard label="Definitions" value={stats.gl_definition} />
          <StatCard label="Imports"     value={stats.gl_imported_symbol} />
          <StatCard label="Graph edges" value={stats.gl_edge} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Panel icon={Flame} title="Complexity hotspots" accent="#6366f1">
          {hotspots.map(h => (
            <Bar key={h.file_path} label={base(h.file_path)} value={h.definitions}
                 sub="defs" max={maxDefs} accent="#6366f1" />
          ))}
        </Panel>

        <Panel icon={AlertTriangle} title="Highest blast radius (fan-in)" accent="#f97316">
          {blast.map(b => (
            <Bar key={b.file_path + b.name} label={`${b.name}  ·  ${base(b.file_path)}`}
                 value={b.callers} sub="callers" max={maxCallers} accent="#f97316" />
          ))}
        </Panel>

        <Panel icon={Waypoints} title="Most-coupled modules" accent="#10b981">
          {coupling.map(c => (
            <Bar key={c.import_path} label={c.import_path} value={c.importers}
                 sub="importers" max={maxImp} accent="#10b981" />
          ))}
        </Panel>

        <Panel icon={Ruler} title="Longest functions" accent="#f59e0b">
          {longFns.map(f => (
            <Bar key={f.file_path + f.name} label={`${f.name}  ·  ${base(f.file_path)}`}
                 value={f.span} sub="lines" max={maxSpan} accent="#f59e0b" />
          ))}
        </Panel>
      </div>

      <p className="text-[11px] text-dm-muted/60 font-mono mt-6">
        Powered by GitLab Orbit · DevMirror Code Coach
      </p>
    </PageShell>
  )
}
