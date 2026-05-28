import clsx from 'clsx'
import { LucideIcon } from 'lucide-react'

interface Props {
  label: string
  value: string | number
  sub?: string
  icon?: LucideIcon
  accent?: 'purple' | 'green' | 'cyan' | 'amber'
  loading?: boolean
}

const accentMap = {
  purple: 'text-dm-purple-ll',
  green:  'text-dm-green',
  cyan:   'text-dm-cyan',
  amber:  'text-dm-amber',
}

const iconBg = {
  purple: 'bg-dm-purple/15 text-dm-purple-ll',
  green:  'bg-dm-green/10 text-dm-green',
  cyan:   'bg-dm-cyan/10 text-dm-cyan',
  amber:  'bg-dm-amber/10 text-dm-amber',
}

export default function StatCard({ label, value, sub, icon: Icon, accent = 'purple', loading }: Props) {
  return (
    <div className="dm-card p-4 flex items-center gap-4">
      {Icon && (
        <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center shrink-0', iconBg[accent])}>
          <Icon size={18} />
        </div>
      )}
      <div className="min-w-0">
        <div className="dm-label mb-1">{label}</div>
        {loading ? (
          <div className="h-7 w-16 bg-dm-border rounded animate-pulse" />
        ) : (
          <div className={clsx('font-head font-bold text-2xl leading-none', accentMap[accent])}>{value}</div>
        )}
        {sub && <div className="text-xs text-dm-muted mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}
