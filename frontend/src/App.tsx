import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect, type ReactNode } from 'react'
import { useAuth } from './lib/auth'
import { AuthPage } from './features/auth/AuthPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { ProjectPage } from './features/projects/ProjectPage'
import { LandingPage } from './features/landing/LandingPage'
import { Logo } from './components/Logo'

function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname])

  return null
}
function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="grid min-h-screen place-items-center bg-paper"><div className="animate-pulse"><Logo /></div></div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return <>
    <ScrollToTop />
    <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<AuthPage />} />
    <Route path="/app" element={<Protected><DashboardPage /></Protected>} />
    <Route path="/app/projects/:id" element={<Protected><ProjectPage /></Protected>} />
    <Route path="/projects/:id" element={<Navigate to="/app" replace />} />
    <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </> 
}

