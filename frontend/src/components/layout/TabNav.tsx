const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'missing', label: 'Missing Values' },
  { id: 'distributions', label: 'Distributions' },
  { id: 'correlations', label: 'Correlations' },
  { id: 'categories', label: 'Categories' },
  { id: 'timeseries', label: 'Time Series' },
  { id: 'preprocessing', label: 'Preprocessing' },
  { id: 'ai', label: 'AI Insights' },
]

interface Props {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function TabNav({ activeTab, onTabChange }: Props) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="-mb-px flex overflow-x-auto">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  )
}
