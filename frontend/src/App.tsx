import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from './lib/auth'
import { AuthPage } from './features/auth/AuthPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { ProjectPage } from './features/projects/ProjectPage'
import { Logo } from './components/Logo'

function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="grid min-h-screen place-items-center bg-paper"><div className="animate-pulse"><Logo /></div></div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return <Routes>
    <Route path="/login" element={<AuthPage />} />
    <Route path="/" element={<Protected><DashboardPage /></Protected>} />
    <Route path="/projects/:id" element={<Protected><ProjectPage /></Protected>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}

