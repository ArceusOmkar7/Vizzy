import { useState, useCallback } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { useInsightStream } from '../../hooks/useInsightStream'
import { postQuery } from '../../api/client'
import type { QueryResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'

interface Props {
  sessionId: string
}

export function AIInsights({ sessionId }: Props) {
  const { text, isStreaming, error: streamError, startStream, clearText } = useInsightStream(sessionId)
  const [question, setQuestion] = useState('')
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)
  const [isQuerying, setIsQuerying] = useState(false)
  const [queryError, setQueryError] = useState<string | null>(null)

  const handleGenerate = useCallback(() => {
    clearText()
    startStream()
  }, [clearText, startStream])

  const handleQuery = useCallback(async () => {
    if (!question.trim()) return
    setIsQuerying(true)
    setQueryError(null)
    setQueryResult(null)
    try {
      const res = await postQuery(sessionId, question)
      setQueryResult(res.data)
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } }; message: string })?.response?.data?.detail || (e as Error).message
      if (msg.toLowerCase().includes('gemini') || msg.toLowerCase().includes('api key') || msg.toLowerCase().includes('not configured')) {
        setQueryError('AI features require a GEMINI_API_KEY. Please configure it in your backend .env file.')
      } else {
        setQueryError(msg)
      }
    } finally {
      setIsQuerying(false)
    }
  }, [sessionId, question])

  return (
    <div className="space-y-6 p-4">
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">AI Insights</h2>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">Generate Insights</h3>
          <button
            onClick={handleGenerate}
            disabled={isStreaming}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4" />
            {isStreaming ? 'Generating…' : 'Generate'}
          </button>
        </div>

        {streamError && streamError.includes('GEMINI') && (
          <div className="mb-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
            AI features require a GEMINI_API_KEY configured in the backend.
          </div>
        )}

        {(text || isStreaming) && (
          <div className="min-h-24 rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
            <p className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-200">
              {text}
              {isStreaming && <span className="animate-pulse">▋</span>}
            </p>
          </div>
        )}

        {!text && !isStreaming && (
          <p className="text-sm text-gray-400">Click "Generate" to get AI-powered insights about your dataset.</p>
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <h3 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-200">Ask a Question</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleQuery()}
            placeholder="e.g. What are the main patterns in this data?"
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
          />
          <button
            onClick={handleQuery}
            disabled={isQuerying || !question.trim()}
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {isQuerying ? 'Asking…' : 'Ask'}
          </button>
        </div>

        {isQuerying && <LoadingSpinner size="sm" />}

        {queryError && (
          <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
            {queryError}
          </div>
        )}

        {queryResult && (
          <div className="mt-3 rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
            <p className="mb-1 text-xs font-semibold text-gray-500 dark:text-gray-400">Answer:</p>
            <p className="text-sm text-gray-700 dark:text-gray-200">{queryResult.answer}</p>
          </div>
        )}
      </div>
    </div>
  )
}
