import { useEffect, useState, useRef } from 'react'
import clsx from 'clsx'

interface Props {
  content: string
  typingSpeed?: number
  className?: string
}

export default function AIReport({ content, typingSpeed = 8, className }: Props) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)
  const idx = useRef(0)
  const timer = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    idx.current = 0
    setDisplayed('')
    setDone(false)

    function tick() {
      if (idx.current < content.length) {
        const chunk = content.slice(idx.current, idx.current + 3)
        setDisplayed(prev => prev + chunk)
        idx.current += 3
        timer.current = setTimeout(tick, typingSpeed)
      } else {
        setDone(true)
      }
    }

    timer.current = setTimeout(tick, 200)
    return () => clearTimeout(timer.current)
  }, [content, typingSpeed])

  return (
    <div className={clsx('font-mono text-sm leading-relaxed text-dm-text whitespace-pre-wrap', className)}>
      {displayed}
      {!done && <span className="inline-block w-2 h-4 bg-dm-purple ml-0.5 animate-blink" />}
    </div>
  )
}
