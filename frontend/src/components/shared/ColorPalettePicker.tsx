import { useSession } from '../../store/sessionStore'

const PALETTES = [
  { name: 'indigo', label: 'Indigo', color: '#6366f1' },
  { name: 'teal', label: 'Teal', color: '#14b8a6' },
  { name: 'orange', label: 'Orange', color: '#f97316' },
  { name: 'rose', label: 'Rose', color: '#f43f5e' },
  { name: 'purple', label: 'Purple', color: '#a855f7' },
  { name: 'green', label: 'Green', color: '#22c55e' },
]

export function ColorPalettePicker() {
  const { state, dispatch } = useSession()
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Color Palette</p>
      <div className="flex flex-wrap gap-2">
        {PALETTES.map(p => (
          <button
            key={p.name}
            title={p.label}
            onClick={() => dispatch({ type: 'SET_PALETTE', payload: p.name })}
            className={`h-6 w-6 rounded-full border-2 transition-transform hover:scale-110 ${
              state.colorPalette === p.name ? 'border-gray-800 dark:border-white scale-110' : 'border-transparent'
            }`}
            style={{ backgroundColor: p.color }}
          />
        ))}
      </div>
    </div>
  )
}
