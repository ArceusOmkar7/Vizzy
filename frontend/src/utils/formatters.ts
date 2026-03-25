export function formatNumber(n: number): string {
  return n.toLocaleString()
}

export function formatMb(mb: number): string {
  return `${mb.toFixed(2)} MB`
}

export function formatPct(pct: number): string {
  return `${pct.toFixed(1)}%`
}

export function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

export function round(n: number, decimals = 2): number {
  const factor = Math.pow(10, decimals)
  return Math.round(n * factor) / factor
}

export function gradeColor(grade: string): string {
  switch (grade) {
    case 'A': return 'text-green-600 dark:text-green-400'
    case 'B': return 'text-blue-600 dark:text-blue-400'
    case 'C': return 'text-yellow-600 dark:text-yellow-400'
    case 'D': return 'text-orange-600 dark:text-orange-400'
    default: return 'text-red-600 dark:text-red-400'
  }
}
