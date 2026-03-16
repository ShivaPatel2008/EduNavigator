'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, BookOpen, Sparkles, RefreshCw } from 'lucide-react'
import ChatMessage from './ChatMessage'
import MessageInput from './MessageInput'
import LoadingIndicator from './LoadingIndicator'
import { sendMessage, ChatResponse } from '../lib/api'
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  queryType?: string
  highlightedChunks?: string[]
  timestamp: Date
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId] = useState(() => Math.random().toString(36).substring(7))
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response: ChatResponse = await sendMessage(content, conversationId)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        queryType: response.query_type,
        highlightedChunks: response.highlighted_chunks,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const clearConversation = () => {
    setMessages([])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  EduNavigator AI
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Ask anything about courses & education
                </p>
              </div>
            </div>

            {messages.length > 0 && (
              <button
                onClick={clearConversation}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md transition-colors"
                title="New conversation"
              >
                <RefreshCw size={16} />
                New
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {messages.length === 0 ? (
          /* Welcome Screen */
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
                <Sparkles size={32} className="text-white" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                Welcome to EduNavigator AI
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                Your intelligent guide to courses, programs, and educational opportunities.
                Ask me anything about admissions, curriculum, fees, or career paths.
              </p>
            </div>

            {/* Example Questions */}
            <div className="grid md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <button
                onClick={() => handleSendMessage("What courses are available for computer science?")}
                className="p-4 text-left bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all"
              >
                <div className="font-medium text-slate-900 dark:text-slate-100 mb-1">
                  What courses are available?
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  Explore our computer science programs
                </div>
              </button>

              <button
                onClick={() => handleSendMessage("What are the admission requirements?")}
                className="p-4 text-left bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all"
              >
                <div className="font-medium text-slate-900 dark:text-slate-100 mb-1">
                  Admission requirements
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  Learn about our application process
                </div>
              </button>
            </div>
          </div>
        ) : (
          /* Conversation View */
          <div className="space-y-6">
            {messages.map((message, index) => (
              <div key={message.id} className="space-y-4">
                <ChatMessage message={message} />
                {index === messages.length - 1 && isLoading && (
                  <LoadingIndicator />
                )}
              </div>
            ))}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Search/Input Bar - Fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-t border-slate-200 dark:border-slate-700">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search size={20} className="text-slate-400" />
            </div>
            <MessageInput
              onSendMessage={handleSendMessage}
              disabled={isLoading}
            />
          </div>
        </div>
      </div>

      {/* Add padding to account for fixed input bar */}
      <div className="h-24" />
    </div>
  )
}