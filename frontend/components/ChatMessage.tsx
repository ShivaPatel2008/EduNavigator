import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, Lightbulb, ExternalLink } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  queryType?: string
  highlightedChunks?: string[]
  timestamp: Date
}

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [showSources, setShowSources] = useState(false)

  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-2xl bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-br-md shadow-sm">
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 mb-8">
      {/* Main Answer */}
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <div className="text-slate-900 dark:text-slate-100 leading-relaxed text-lg">
          {message.content.split('\n').map((paragraph, index) => (
            <p key={index} className="mb-4 last:mb-0">
              {paragraph}
            </p>
          ))}
        </div>
      </div>

      {/* Query Type Badge */}
      {message.queryType && (
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs font-medium rounded-full">
            <Lightbulb size={12} />
            <span className="capitalize">{message.queryType} query</span>
          </div>
        </div>
      )}

      {/* Sources Section */}
      {(message.sources?.length || message.highlightedChunks?.length) && (
        <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors mb-3"
          >
            {showSources ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <FileText size={16} />
            <span>
              {message.sources?.length || 0} sources • {message.highlightedChunks?.length || 0} references
            </span>
          </button>

          {showSources && (
            <div className="space-y-4">
              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-3">
                    Sources
                  </h4>
                  <div className="grid gap-2">
                    {message.sources.map((source, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                      >
                        <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded flex items-center justify-center flex-shrink-0">
                          <FileText size={12} className="text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-900 dark:text-slate-100 truncate">
                            {source}
                          </p>
                        </div>
                        <ExternalLink size={14} className="text-slate-400 flex-shrink-0" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Highlighted Chunks */}
              {message.highlightedChunks && message.highlightedChunks.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-3">
                    Key References
                  </h4>
                  <div className="space-y-2">
                    {message.highlightedChunks.slice(0, 3).map((chunk, index) => (
                      <div
                        key={index}
                        className="p-3 bg-yellow-50 dark:bg-yellow-900/10 border-l-4 border-yellow-400 rounded-r-lg"
                      >
                        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                          {chunk.length > 150 ? `${chunk.substring(0, 150)}...` : chunk}
                        </p>
                      </div>
                    ))}
                    {message.highlightedChunks.length > 3 && (
                      <p className="text-xs text-slate-500 dark:text-slate-400 pl-3">
                        ... and {message.highlightedChunks.length - 3} more references
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}