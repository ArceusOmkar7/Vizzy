import { useEffect } from 'react'
import { Grid, Hash, AlertCircle, Copy } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getOverview } from '../../api/client'
import type { OverviewResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { MetricCard } from '../shared/MetricCard'
import { QualityBadge } from '../shared/QualityBadge'
import { formatNumber, formatPct } from '../../utils/formatters'

interface Props {
  sessionId: string
}

export function DataOverview({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<OverviewResponse>(() => getOverview(sessionId))

  useEffect(() => { fetch() }, [])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data) return null

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Data Overview</h2>
        <QualityBadge grade={data.quality_grade} score={data.quality_score} />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <MetricCard title="Rows" value={formatNumber(data.total_rows)} icon={<Grid className="h-4 w-4" />} />
        <MetricCard title="Columns" value={data.total_columns} icon={<Hash className="h-4 w-4" />} />
        <MetricCard title="Total Nulls" value={formatNumber(data.total_nulls)} icon={<AlertCircle className="h-4 w-4" />} colorClass="text-amber-600 dark:text-amber-400" />
        <MetricCard title="Duplicates" value={formatNumber(data.duplicate_rows)} icon={<Copy className="h-4 w-4" />} colorClass="text-red-600 dark:text-red-400" />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard title="Numeric Cols" value={data.numeric_columns} />
        <MetricCard title="Categorical Cols" value={data.categorical_columns} />
        <MetricCard title="Datetime Cols" value={data.datetime_columns} />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Column Summary</h3>
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                {['Column', 'Type', 'Nulls', 'Null %', 'Unique', 'Sample Values'].map(h => (
                  <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 dark:text-gray-400">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {data.column_summaries.slice(0, 20).map(col => (
                <tr key={col.name} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">{col.name}</td>
                  <td className="px-3 py-2"><span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">{col.dtype}</span></td>
                  <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{formatNumber(col.null_count)}</td>
                  <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{formatPct(col.null_pct)}</td>
                  <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{formatNumber(col.unique_count)}</td>
                  <td className="px-3 py-2 text-gray-400 dark:text-gray-500 max-w-xs truncate">{col.sample_values?.slice(0, 3).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
