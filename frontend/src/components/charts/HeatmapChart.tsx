import React from 'react'

interface Props {
  columns: string[]
  matrix: number[][]
}

export function HeatmapChart({ columns, matrix }: Props) {
  const cellColor = (val: number) => {
    const abs = Math.abs(val)
    if (val > 0) {
      const r = Math.round(200 - abs * 150)
      return `rgb(${r}, ${Math.round(50 + abs * 150)}, 220)`
    } else {
      return `rgb(220, ${Math.round(50 + abs * 150)}, ${Math.round(200 - abs * 150)})`
    }
  }

  const MAX_COLS = 12
  const cols = columns.slice(0, MAX_COLS)
  const mat = matrix.slice(0, MAX_COLS).map(row => row.slice(0, MAX_COLS))

  return (
    <div className="overflow-x-auto">
      <div
        className="inline-grid gap-px rounded border border-gray-200 bg-gray-200 dark:border-gray-700 dark:bg-gray-700"
        style={{ gridTemplateColumns: `80px repeat(${cols.length}, 48px)` }}
      >
        <div className="bg-gray-50 dark:bg-gray-800" />
        {cols.map(c => (
          <div
            key={c}
            title={c}
            className="truncate bg-gray-50 px-1 py-1 text-center text-[10px] font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300"
          >
            {c.length > 6 ? c.slice(0, 6) + '…' : c}
          </div>
        ))}
        {cols.map((rowCol, i) => (
          <React.Fragment key={`row-${rowCol}`}>
            <div
              title={rowCol}
              className="truncate bg-gray-50 px-1 py-1 text-right text-[10px] font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300"
            >
              {rowCol.length > 10 ? rowCol.slice(0, 10) + '…' : rowCol}
            </div>
            {mat[i]?.map((val, j) => (
              <div
                key={`${i}-${j}`}
                title={`${cols[i]} × ${cols[j]}: ${val.toFixed(3)}`}
                className="flex items-center justify-center text-[10px] font-bold py-1"
                style={{ backgroundColor: cellColor(val), color: Math.abs(val) > 0.5 ? '#fff' : '#333' }}
              >
                {val.toFixed(2)}
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
