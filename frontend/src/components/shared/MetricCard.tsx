import type { ReactNode } from 'react'

interface Props {
  title: string
  value: string | number
  icon?: ReactNode
  subtitle?: string
  colorClass?: string
}

export function MetricCard({ title, value, icon, subtitle, colorClass = 'text-indigo-600 dark:text-indigo-400' }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
        {icon}
        <span className="text-sm font-medium">{title}</span>
      </div>
      <div className={`mt-1 text-2xl font-bold ${colorClass}`}>{value}</div>
      {subtitle && <div className="mt-0.5 text-xs text-gray-400">{subtitle}</div>}
    </div>
  )
}
