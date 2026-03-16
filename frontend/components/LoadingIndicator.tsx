import { useEffect, useState } from 'react'

interface LoadingIndicatorProps {
  message?: string
}

export default function LoadingIndicator({ message = "Thinking..." }: LoadingIndicatorProps) {
  const [dots, setDots] = useState('')

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.')
    }, 500)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-3 py-4">
      <div className="flex items-center gap-1">
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
      </div>
      <span className="text-slate-600 dark:text-slate-400 text-sm">
        {message}{dots}
      </span>
    </div>
  )
}