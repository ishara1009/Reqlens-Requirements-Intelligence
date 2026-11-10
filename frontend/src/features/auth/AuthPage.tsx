import { useState, type FormEvent } from 'react'
import { ArrowRight, CircleCheck, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react'
import { Navigate } from 'react-router-dom'
import { api, json } from '../../lib/api'
import { useAuth } from '../../lib/auth'
import { Logo } from '../../components/Logo'
import { Button } from '../../components/Ui'
import type { User } from '../../types'

export function AuthPage() {
  const { user, setSession } = useAuth()
  const [register, setRegister] = useState(false)
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  if (user) return <Navigate to="/app" replace />

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setError('')
    const values = Object.fromEntries(new FormData(event.currentTarget))
    try {
      const result = await api<{ access_token: string; user: User }>(register ? '/auth/register' : '/auth/login', json('POST', values))
      setSession(result.access_token, result.user)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not continue') } finally { setLoading(false) }
  }

  return <main className="grid min-h-screen bg-paper lg:grid-cols-[1.05fr_.95fr]">
    <section className="relative hidden overflow-hidden bg-ink p-14 text-white lg:flex lg:flex-col lg:justify-between">
      <div className="auth-grid absolute inset-0 opacity-20" /><div className="absolute -right-32 top-1/4 h-80 w-80 rounded-full bg-ocean/30 blur-3xl" />
      <div className="relative"><Logo light /></div>
      <div className="relative max-w-xl"><div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-widest text-cyan-100"><Sparkles size={14} /> Evidence-first AI</div><h1 className="font-display text-5xl font-extrabold leading-[1.08] tracking-tight">Turn scattered requirements into clear decisions.</h1><p className="mt-5 text-lg leading-relaxed text-slate-300">Analyze documents, surface contradictions, trace every claim to evidence, and keep humans in control.</p><div className="mt-9 grid gap-4 text-sm text-slate-200 sm:grid-cols-2">{['Project-isolated retrieval', 'Human review workflows', 'Source-linked answers', 'Version intelligence'].map(item => <span className="flex items-center gap-2" key={item}><CircleCheck size={17} className="text-cyan-300" />{item}</span>)}</div></div>
      <p className="relative text-xs text-slate-500">Requirements intelligence, without the black box.</p>
    </section>
    <section className="flex items-center justify-center p-5 sm:p-10"><div className="w-full max-w-md"><div className="mb-10 lg:hidden"><Logo /></div><div className="mb-8"><span className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-cyan-50 text-ocean"><ShieldCheck /></span><h2 className="font-display text-3xl font-extrabold text-ink">{register ? 'Create your workspace' : 'Welcome back'}</h2><p className="mt-2 text-slate-500">{register ? 'Start reviewing requirements with traceable AI.' : 'Sign in to continue to your projects.'}</p></div>
      <form onSubmit={submit} className="space-y-4">{register && <label className="field-label">Full name<input className="field" name="name" minLength={2} required placeholder="Alex Morgan" /></label>}<label className="field-label">Work email<input className="field" name="email" type="email" required placeholder="you@company.com" /></label><label className="field-label">Password<div className="relative"><input className="field pr-12" name="password" type={show ? 'text' : 'password'} minLength={8} required placeholder="Minimum 8 characters" /><button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-3 text-slate-400" aria-label="Toggle password visibility">{show ? <EyeOff size={19} /> : <Eye size={19} />}</button></div></label>{error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}<Button loading={loading} className="w-full py-3">{register ? 'Create account' : 'Sign in'}<ArrowRight size={17} /></Button></form>
      <p className="mt-7 text-center text-sm text-slate-500">{register ? 'Already have an account?' : 'New to ReqLens?'} <button onClick={() => { setRegister(!register); setError('') }} className="font-bold text-ocean hover:underline">{register ? 'Sign in' : 'Create an account'}</button></p>
    </div></section>
  </main>
}

