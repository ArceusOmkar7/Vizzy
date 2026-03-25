import { useEffect } from 'react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getPreprocessing } from '../../api/client'
import type { PreprocessingResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'

interface Props {
  sessionId: string
}

const priorityStyles: Record<string, string> = {
  high: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  low: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
}

export function Preprocessing({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<PreprocessingResponse>(() => getPreprocessing(sessionId))
  useEffect(() => { fetch() }, [])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data || data.suggestions.length === 0) {
    return (
      <div className="p-6 text-center text-gray-500">
        <p>No preprocessing suggestions available.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-4">
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Preprocessing Suggestions</h2>
      {data.suggestions.map((s, i) => (
        <div key={i} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-2 flex items-center gap-2">
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${priorityStyles[s.priority] || priorityStyles.low}`}>
              {s.priority.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{s.category}</span>
          </div>
          <p className="mb-3 text-sm text-gray-700 dark:text-gray-200">{s.description}</p>
          {s.code_snippet && (
            <pre className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-xs text-green-300">
              <code>{s.code_snippet}</code>
            </pre>
          )}
        </div>
      ))}
    </div>
  )
}
