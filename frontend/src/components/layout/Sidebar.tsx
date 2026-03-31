import { Download, FileText, Rows, Columns, Database, AlertCircle } from 'lucide-react'
import { useSession } from '../../store/sessionStore'
import { ColorPalettePicker } from '../shared/ColorPalettePicker'
import { exportPdf } from '../../api/client'
import { formatNumber, formatMb } from '../../utils/formatters'
import toast from 'react-hot-toast'

export function Sidebar() {
  const { state } = useSession()

  const handleExport = async () => {
    if (!state.sessionId) return
    try {
      const res = await exportPdf(state.sessionId)
      const url = URL.createObjectURL(res.data as Blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${state.filename || 'report'}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('PDF exported!')
    } catch {
      toast.error('PDF export failed')
    }
  }

  return (
    <aside className="flex w-64 flex-col gap-6 border-r border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
      <div>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Dataset</h2>
        <p className="truncate text-sm font-medium text-gray-700 dark:text-gray-200">
          {state.filename || '—'}
        </p>
      </div>

      <div className="space-y-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Metrics</h2>
        {[
          { icon: <Rows className="h-4 w-4" />, label: 'Rows', value: state.rows != null ? formatNumber(state.rows) : '—' },
          { icon: <Columns className="h-4 w-4" />, label: 'Columns', value: state.columns != null ? String(state.columns) : '—' },
          { icon: <Database className="h-4 w-4" />, label: 'Memory', value: state.memoryMb != null ? formatMb(state.memoryMb) : '—' },
          { icon: <AlertCircle className="h-4 w-4" />, label: 'Nulls', value: state.nullCount != null ? formatNumber(state.nullCount) : '—' },
          { icon: <FileText className="h-4 w-4" />, label: 'File', value: state.filename ? state.filename.split('.').pop()?.toUpperCase() || '—' : '—' },
        ].map(m => (
          <div key={m.label} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
              {m.icon} {m.label}
            </span>
            <span className="font-medium text-gray-800 dark:text-gray-100">{m.value}</span>
          </div>
        ))}
      </div>

      <ColorPalettePicker />

      <div className="mt-auto">
        <button
          onClick={handleExport}
          disabled={!state.sessionId}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700 disabled:opacity-40"
        >
          <Download className="h-4 w-4" />
          Export PDF
        </button>
      </div>
    </aside>
  )
}
