import { useEffect } from 'react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getCorrelations } from '../../api/client'
import type { CorrelationsResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { HeatmapChart } from '../charts/HeatmapChart'

interface Props {
  sessionId: string
}

export function Correlations({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<CorrelationsResponse>(() => getCorrelations(sessionId))
  useEffect(() => { fetch() }, [])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data || data.columns.length < 2) {
    return <div className="p-4 text-gray-500">Need at least 2 numeric columns for correlation analysis.</div>
  }

  return (
    <div className="space-y-6 p-4">
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Correlations</h2>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Correlation Heatmap</h3>
        <HeatmapChart columns={data.columns} matrix={data.matrix} />
      </div>

      {data.top_pairs && data.top_pairs.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Top Correlated Pairs</h3>
          <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  {['Column 1', 'Column 2', 'Correlation'].map(h => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 dark:text-gray-400">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {data.top_pairs.map((p, i) => (
                  <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">{p.col1}</td>
                    <td className="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">{p.col2}</td>
                    <td className="px-3 py-2">
                      <span className={`font-bold ${Math.abs(p.correlation) > 0.7 ? 'text-red-600 dark:text-red-400' : Math.abs(p.correlation) > 0.4 ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-300'}`}>
                        {p.correlation.toFixed(4)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
