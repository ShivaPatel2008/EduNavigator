import { useState } from 'react'
import { X, FileText, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'

interface Source {
  title: string
  content: string
  score?: number
  metadata?: Record<string, any>
}

interface SourcePanelProps {
  sources: Source[]
  isOpen: boolean
  onClose: () => void
}

export default function SourcePanel({ sources, isOpen, onClose }: SourcePanelProps) {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())

  const toggleSource = (index: number) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSources(newExpanded)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-slate-800 border-l border-slate-200 dark:border-slate-700 shadow-xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <FileText size={20} />
          Sources ({sources.length})
        </h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md transition-colors"
        >
          <X size={20} className="text-slate-500 dark:text-slate-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {sources.length === 0 ? (
          <div className="p-6 text-center text-slate-500 dark:text-slate-400">
            No sources available
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {sources.map((source, index) => (
              <div
                key={index}
                className="border border-slate-200 dark:border-slate-600 rounded-lg overflow-hidden"
              >
                {/* Source Header */}
                <div
                  className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
                  onClick={() => toggleSource(index)}
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                      {source.title}
                    </h4>
                    {source.score && (
                      <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        Relevance: {(source.score * 100).toFixed(1)}%
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    {source.metadata?.url && (
                      <a
                        href={source.metadata.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink size={14} />
                      </a>
                    )}
                    {expandedSources.has(index) ? (
                      <ChevronUp size={16} className="text-slate-400" />
                    ) : (
                      <ChevronDown size={16} className="text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Source Content */}
                {expandedSources.has(index) && (
                  <div className="p-3 border-t border-slate-200 dark:border-slate-600">
                    <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                      {source.content}
                    </div>

                    {/* Metadata */}
                    {source.metadata && Object.keys(source.metadata).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-600">
                        <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                          {Object.entries(source.metadata)
                            .filter(([key]) => key !== 'url') // URL is shown in header
                            .map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="capitalize">{key}:</span>
                                <span className="font-mono">{String(value)}</span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}