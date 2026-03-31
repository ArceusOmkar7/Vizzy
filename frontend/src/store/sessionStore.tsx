import { createContext, useContext, useReducer } from 'react'
import type { ReactNode } from 'react'

interface SessionState {
  sessionId: string | null
  filename: string | null
  rows: number | null
  columns: number | null
  memoryMb: number | null
  nullCount: number | null
  colorPalette: string
  darkMode: boolean
}

type SessionAction =
  | { type: 'SET_SESSION'; payload: Partial<SessionState> }
  | { type: 'SET_PALETTE'; payload: string }
  | { type: 'TOGGLE_DARK' }
  | { type: 'CLEAR' }

const initialState: SessionState = {
  sessionId: null,
  filename: null,
  rows: null,
  columns: null,
  memoryMb: null,
  nullCount: null,
  colorPalette: 'indigo',
  darkMode: false,
}

function reducer(state: SessionState, action: SessionAction): SessionState {
  switch (action.type) {
    case 'SET_SESSION':
      return { ...state, ...action.payload }
    case 'SET_PALETTE':
      return { ...state, colorPalette: action.payload }
    case 'TOGGLE_DARK':
      return { ...state, darkMode: !state.darkMode }
    case 'CLEAR':
      return initialState
    default:
      return state
  }
}

interface SessionContextValue {
  state: SessionState
  dispatch: React.Dispatch<SessionAction>
}

const SessionContext = createContext<SessionContextValue | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return (
    <SessionContext.Provider value={{ state, dispatch }}>
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error('useSession must be used within SessionProvider')
  return ctx
}
