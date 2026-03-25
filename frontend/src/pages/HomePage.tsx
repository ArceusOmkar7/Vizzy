import { useState, useCallback } from 'react'
import type { DragEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileSpreadsheet, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileUpload } from '../hooks/useFileUpload'
import { useSession } from '../store/sessionStore'

const SAMPLE_DATASETS = [
  { name: 'Titanic', description: '891 passengers, survival analysis', file: 'titanic.csv' },
  { name: 'Iris', description: '150 flowers, 4 numeric features', file: 'iris.csv' },
  { name: 'Sales Data', description: 'E-commerce transactions with dates', file: 'sales_data.csv' },
  { name: 'Housing', description: 'Boston housing prices dataset', file: 'housing.csv' },
  { name: 'Employee', description: 'HR data with mixed types', file: 'employee_data.csv' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const { upload, progress, isUploading } = useFileUpload()
  const { dispatch } = useSession()
  const [isDragging, setIsDragging] = useState(false)

  const handleFile = useCallback(async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
      toast.error('Only CSV and Excel files are supported')
      return
    }
    try {
      const data = await upload(file)
      dispatch({
        type: 'SET_SESSION',
        payload: {
          sessionId: data.session_id,
          filename: data.filename,
          rows: data.rows,
          columns: data.columns,
          memoryMb: data.memory_mb,
          nullCount: data.null_count,
        },
      })
      toast.success(`Uploaded ${data.filename} (${data.rows.toLocaleString()} rows)`)
      navigate(`/dashboard/${data.session_id}`)
    } catch {
      toast.error('Upload failed. Please try again.')
    }
  }, [upload, dispatch, navigate])

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }, [handleFile])

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="mx-auto max-w-3xl px-4 py-16">
        <div className="mb-12 text-center">
          <div className="mb-4 flex justify-center">
            <div className="rounded-2xl bg-indigo-600 p-3">
              <FileSpreadsheet className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="mb-3 text-4xl font-bold text-gray-900 dark:text-white">Vizzy</h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Upload your CSV or Excel file and get instant AI-powered data analysis with 8 comprehensive views.
          </p>
        </div>

        <div
          onDrop={handleDrop}
          onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          className={`relative mb-8 rounded-2xl border-2 border-dashed p-12 text-center transition-colors ${
            isDragging
              ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950'
              : 'border-gray-300 bg-white hover:border-indigo-400 dark:border-gray-600 dark:bg-gray-800'
          }`}
        >
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleInputChange}
            disabled={isUploading}
            className="absolute inset-0 cursor-pointer opacity-0"
          />
          <Upload className="mx-auto mb-3 h-10 w-10 text-gray-400 dark:text-gray-500" />
          <p className="mb-1 text-base font-medium text-gray-700 dark:text-gray-200">
            {isUploading ? 'Uploading…' : 'Drop your file here, or click to browse'}
          </p>
          <p className="text-sm text-gray-400">CSV, XLSX, XLS • Max 50MB</p>

          {isUploading && (
            <div className="mt-4">
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className="h-full bg-indigo-600 transition-all duration-200"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="mt-1 text-sm text-gray-500">{progress}%</p>
            </div>
          )}
        </div>

        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            Or try a sample dataset
          </h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {SAMPLE_DATASETS.map(ds => (
              <button
                key={ds.name}
                disabled={isUploading}
                className="rounded-xl border border-gray-200 bg-white p-3 text-left transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800 disabled:opacity-50"
                onClick={async () => {
                  try {
                    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
                    const response = await fetch(`${BASE_URL}/sample_data/${ds.file}`)
                    if (!response.ok) throw new Error('Sample not available')
                    const blob = await response.blob()
                    const file = new File([blob], ds.file, { type: 'text/csv' })
                    await handleFile(file)
                  } catch {
                    toast.error(`Sample dataset '${ds.name}' not available on this server`)
                  }
                }}
              >
                <div className="font-medium text-gray-800 dark:text-gray-100">{ds.name}</div>
                <div className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{ds.description}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-8 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <p>Make sure the backend is running at <code className="font-mono">http://localhost:8000</code> before uploading.</p>
        </div>
      </div>
    </div>
  )
}
