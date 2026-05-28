import clsx from 'clsx'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  fullPage?: boolean
}

export default function LoadingSpinner({ size = 'md', label, fullPage }: Props) {
  const sizes = { sm: 'w-4 h-4 border-2', md: 'w-8 h-8 border-2', lg: 'w-12 h-12 border-[3px]' }

  const spinner = (
    <div className={clsx('rounded-full border-dm-border border-t-dm-purple animate-spin', sizes[size])} />
  )

  if (fullPage) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 min-h-[40vh]">
        {spinner}
        {label && <p className="text-dm-muted text-sm font-mono">{label}</p>}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3">
      {spinner}
      {label && <span className="text-dm-muted text-sm font-mono">{label}</span>}
    </div>
  )
}
