import { useEffect, useState } from 'react'
import { Clock } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { getTimeSeries } from '../../api/client'
import type { TimeSeriesResponse } from '../../api/client'
import { LoadingSpinner } from '../shared/LoadingSpinner'
import { ErrorMessage } from '../shared/ErrorMessage'
import { LineChartComponent } from '../charts/LineChart'

interface Props {
  sessionId: string
}

export function TimeSeries({ sessionId }: Props) {
  const { data, isLoading, error, fetch } = useAnalysis<TimeSeriesResponse>(() => getTimeSeries(sessionId))
  const [selectedCol, setSelectedCol] = useState('')

  useEffect(() => { fetch() }, [])
  useEffect(() => {
    if (data && data.value_columns.length > 0 && !selectedCol) setSelectedCol(data.value_columns[0])
  }, [data])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={fetch} />
  if (!data) return null

  if (!data.has_datetime) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 p-12 text-center">
        <Clock className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-600 dark:text-gray-300">No Datetime Columns</h3>
        <p className="max-w-sm text-sm text-gray-500 dark:text-gray-400">
          This dataset doesn't have any datetime columns. Time series analysis requires at least one column with date or time values.
        </p>
      </div>
    )
  }

  const seriesData = selectedCol ? (data.series[selectedCol] || []) : []

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Time Series</h2>
        {data.value_columns.length > 0 && (
          <select
            value={selectedCol}
            onChange={e => setSelectedCol(e.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
          >
            {data.value_columns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        )}
      </div>

      {seriesData.length > 0 ? (
        <LineChartComponent data={seriesData} />
      ) : (
        <div className="p-4 text-gray-500">No data available for selected column.</div>
      )}
    </div>
  )
}
