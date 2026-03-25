import { useState, useCallback } from 'react'
import type { AxiosProgressEvent } from 'axios'
import { apiClient } from '../api/client'
import type { UploadResponse } from '../api/client'

interface UseFileUploadReturn {
  upload: (file: File) => Promise<UploadResponse>
  progress: number
  isUploading: boolean
  error: string | null
}

/** Hook for managing file upload state and progress */
export function useFileUpload(): UseFileUploadReturn {
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const upload = useCallback(async (file: File): Promise<UploadResponse> => {
    setIsUploading(true)
    setError(null)
    setProgress(0)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await apiClient.post<UploadResponse>('/api/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt: AxiosProgressEvent) => {
          if (evt.total) {
            setProgress(Math.round((evt.loaded * 100) / evt.total))
          }
        },
      })
      return res.data
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } }; message: string })?.response?.data?.detail || (e as Error).message
      setError(msg)
      throw e
    } finally {
      setIsUploading(false)
    }
  }, [])

  return { upload, progress, isUploading, error }
}
