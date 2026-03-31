import { useEffect, useState } from 'react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getDistributions } from '../../api/client'
import type { DistributionsResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { HistogramChart } from '../charts/HistogramChart'
import { BoxPlotChart } from '../charts/BoxPlotChart'
import { MetricCard } from '../shared/MetricCard'

interface Props {
  sessionId: string
}

export function Distributions({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<DistributionsResponse>(() => getDistributions(sessionId))
  const [selected, setSelected] = useState('')

  useEffect(() => { fetch() }, [])
  useEffect(() => {
    if (data && data.columns.length > 0 && !selected) {
      setSelected(data.columns[0])
    }
  }, [data])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data || data.columns.length === 0) {
    return <div className="p-4 text-gray-500">No numeric columns found.</div>
  }

  const dist = data.distributions[selected]

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Distributions</h2>
        <select
          value={selected}
          onChange={e => setSelected(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          {data.columns.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {dist && (
        <>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Histogram</h3>
            <HistogramChart bins={dist.bins} counts={dist.counts} />
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">Box Plot Statistics</h3>
            <BoxPlotChart
              min={dist.min} q1={dist.q1} median={dist.median}
              q3={dist.q3} max={dist.max} mean={dist.mean}
            />
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricCard title="Mean" value={dist.mean.toFixed(3)} />
            <MetricCard title="Std Dev" value={dist.std.toFixed(3)} />
            <MetricCard title="Skewness" value={dist.skewness.toFixed(3)} />
            <MetricCard title="Kurtosis" value={dist.kurtosis.toFixed(3)} />
          </div>
        </>
      )}
    </div>
  )
}
