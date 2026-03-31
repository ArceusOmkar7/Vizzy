import { useEffect } from 'react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getNulls } from '../../api/client'
import type { NullsResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { MetricCard } from '../shared/MetricCard'
import { BarChartComponent } from '../charts/BarChart'
import { formatNumber, formatPct } from '../../utils/formatters'

interface Props {
  sessionId: string
}

export function MissingValues({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<NullsResponse>(() => getNulls(sessionId))
  useEffect(() => { fetch() }, [])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data) return null

  const chartData = data.null_columns.slice(0, 20).map(c => ({
    label: c.column,
    value: c.null_pct,
  }))

  return (
    <div className="space-y-6 p-4">
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Missing Values</h2>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <MetricCard title="Total Nulls" value={formatNumber(data.total_nulls)} colorClass="text-amber-600 dark:text-amber-400" />
        <MetricCard title="Columns with Nulls" value={data.columns_with_nulls} colorClass="text-orange-600 dark:text-orange-400" />
      </div>

      {chartData.length === 0 ? (
        <div className="rounded-lg border border-green-200 bg-green-50 p-6 text-center dark:border-green-800 dark:bg-green-950">
          <p className="text-green-700 dark:text-green-300">No missing values found! 🎉</p>
        </div>
      ) : (
        <>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Null % by Column</h3>
            <BarChartComponent data={chartData} color="#f59e0b" horizontal />
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Column Details</h3>
            <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    {['Column', 'Null Count', 'Null %'].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 dark:text-gray-400">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {data.null_columns.map(c => (
                    <tr key={c.column} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <td className="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">{c.column}</td>
                      <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{formatNumber(c.null_count)}</td>
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                            <div className="h-full bg-amber-500" style={{ width: `${Math.min(c.null_pct, 100)}%` }} />
                          </div>
                          <span className="text-gray-600 dark:text-gray-300">{formatPct(c.null_pct)}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
