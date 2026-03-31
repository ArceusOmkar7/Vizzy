import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { SessionProvider } from './store/sessionStore'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <SessionProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard/:sessionId" element={<DashboardPage />} />
        </Routes>
      </BrowserRouter>
    </SessionProvider>
  )
}

export default App
