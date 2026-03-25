interface Props {
  min: number
  q1: number
  median: number
  q3: number
  max: number
  mean: number
}

export function BoxPlotChart({ min, q1, median, q3, max, mean }: Props) {
  const stats = [
    { label: 'Min', value: min },
    { label: 'Q1', value: q1 },
    { label: 'Median', value: median },
    { label: 'Mean', value: mean },
    { label: 'Q3', value: q3 },
    { label: 'Max', value: max },
  ]
  return (
    <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
      {stats.map(s => (
        <div
          key={s.label}
          className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-center dark:border-gray-700 dark:bg-gray-800"
        >
          <div className="text-xs text-gray-500 dark:text-gray-400">{s.label}</div>
          <div className="mt-1 text-sm font-bold text-gray-800 dark:text-gray-100">
            {Number(s.value).toFixed(2)}
          </div>
        </div>
      ))}
    </div>
  )
}
