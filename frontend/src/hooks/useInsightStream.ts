import { useState, useCallback } from 'react'
import { BASE_URL } from '../api/client'

interface UseInsightStreamReturn {
  text: string
  isStreaming: boolean
  error: string | null
  startStream: () => void
  clearText: () => void
}

export function useInsightStream(sessionId: string | null): UseInsightStreamReturn {
  const [text, setText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startStream = useCallback(() => {
    if (!sessionId) return
    setText('')
    setIsStreaming(true)
    setError(null)
    const es = new EventSource(`${BASE_URL}/api/insights/${sessionId}`)
    es.onmessage = (event) => {
      setText(prev => prev + event.data)
    }
    es.onerror = () => {
      setIsStreaming(false)
      setError('Streaming error occurred')
      es.close()
    }
    es.addEventListener('done', () => {
      setIsStreaming(false)
      es.close()
    })
  }, [sessionId])

  return { text, isStreaming, error, startStream, clearText: () => setText('') }
}
