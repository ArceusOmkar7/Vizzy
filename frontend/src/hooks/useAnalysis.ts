import { useState, useCallback } from 'react'
import type { AxiosResponse } from 'axios'

interface UseAnalysisReturn<T> {
  data: T | null
  isLoading: boolean
  error: string | null
  fetch: () => Promise<void>
}

export function useAnalysis<T>(
  fetcher: () => Promise<AxiosResponse<T>>
): UseAnalysisReturn<T> {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await fetcher()
      setData(res.data)
    } catch (e: unknown) {
      const axiosError = e as { response?: { data?: { detail?: string } }; message?: string }
      setError(axiosError?.response?.data?.detail || axiosError?.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
    // Intentionally omitting `fetcher` from deps: callers pass inline arrow
    // functions, so including it would trigger infinite re-renders. Callers
    // trigger re-fetches explicitly by calling `fetch()` via useEffect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { data, isLoading, error, fetch }
}
