import { useEffect, useState } from 'react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getCategories } from '../../api/client'
import type { CategoriesResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { BarChartComponent } from '../charts/BarChart'

interface Props {
  sessionId: string
}

export function Categories({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<CategoriesResponse>(() => getCategories(sessionId))
  const [selected, setSelected] = useState('')

  useEffect(() => { fetch() }, [])
  useEffect(() => {
    if (data && data.columns.length > 0 && !selected) setSelected(data.columns[0])
  }, [data])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data || data.columns.length === 0) {
    return <div className="p-4 text-gray-500">No categorical columns found.</div>
  }

  const cats = data.categories[selected] || []
  const chartData = cats.slice(0, 15).map(c => ({ label: c.value, value: c.count }))

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Categories</h2>
        <select
          value={selected}
          onChange={e => setSelected(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          {data.columns.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <BarChartComponent data={chartData} color="#8b5cf6" horizontal />

      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {['Value', 'Count', '%'].map(h => (
                <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 dark:text-gray-400">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {cats.slice(0, 15).map(c => (
              <tr key={c.value} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">{c.value}</td>
                <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{c.count.toLocaleString()}</td>
                <td className="px-3 py-2 text-gray-600 dark:text-gray-300">{c.pct.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
