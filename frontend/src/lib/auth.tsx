import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, UNAUTHORIZED_EVENT } from './api'
import type { User } from '../types'

type AuthValue = { user: User | null; loading: boolean; setSession: (token: string, user: User) => void; logout: () => void }
const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    const clearExpiredSession = () => setUser(null)
    window.addEventListener(UNAUTHORIZED_EVENT, clearExpiredSession)
    if (!localStorage.getItem('reqlens_token')) {
      setLoading(false)
    } else {
      api<User>('/auth/me').then(setUser).catch(() => localStorage.removeItem('reqlens_token')).finally(() => setLoading(false))
    }
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, clearExpiredSession)
  }, [])
  const setSession = (token: string, next: User) => { localStorage.setItem('reqlens_token', token); setUser(next) }
  const logout = () => { localStorage.removeItem('reqlens_token'); setUser(null) }
  return <AuthContext.Provider value={{ user, loading, setSession, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be inside AuthProvider')
  return value
}

