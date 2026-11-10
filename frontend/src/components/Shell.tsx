import type { ReactNode } from 'react'
import { ChartNoAxesColumnIncreasing, BookOpenCheck, LogOut, Menu, Settings, X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { Logo } from './Logo'
import { useAuth } from '../lib/auth'

export function Shell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const nav = <>
    <Link onClick={() => setOpen(false)} to="/app" className={`nav-link ${location.pathname === '/app' ? 'nav-active' : ''}`}><ChartNoAxesColumnIncreasing size={19} /> Overview</Link>
    <div className="mt-7 px-3 text-[11px] font-extrabold uppercase tracking-[.16em] text-slate-500">Workspace</div>
    <Link onClick={() => setOpen(false)} to="/app" className="nav-link"><BookOpenCheck size={19} /> Projects</Link>
    <span className="nav-link cursor-not-allowed opacity-45"><Settings size={19} /> Settings <span className="ml-auto text-[10px]">SOON</span></span>
  </>
  return <div className="min-h-screen bg-paper">
    <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-ink p-5 text-slate-300 transition-transform lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className="flex items-center justify-between"><Logo light /><button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation"><X /></button></div>
      <nav className="mt-10 space-y-1">{nav}</nav>
      <div className="absolute bottom-5 left-5 right-5 rounded-2xl bg-white/5 p-3">
        <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-full bg-ocean font-bold text-white">{user?.name.charAt(0).toUpperCase()}</span><div className="min-w-0"><p className="truncate text-sm font-bold text-white">{user?.name}</p><p className="truncate text-xs text-slate-400">{user?.email}</p></div></div>
        <button onClick={logout} className="mt-3 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-xs font-bold hover:bg-white/10"><LogOut size={15} /> Sign out</button>
      </div>
    </aside>
    <div className="lg:pl-64"><header className="sticky top-0 z-30 flex h-16 items-center border-b border-slate-200 bg-paper/90 px-4 backdrop-blur lg:hidden"><button onClick={() => setOpen(true)} aria-label="Open navigation"><Menu /></button><div className="ml-4"><Logo /></div></header><main className="mx-auto max-w-[1440px] p-4 sm:p-7 lg:p-10">{children}</main></div>
    {open && <button className="fixed inset-0 z-30 bg-black/30 lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation overlay" />}
  </div>
}

