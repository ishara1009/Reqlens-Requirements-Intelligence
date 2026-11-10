import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { LoaderCircle } from 'lucide-react'

export function Button({ className = '', loading, children, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }) {
  return <button className={`inline-flex items-center justify-center gap-2 rounded-xl bg-ink px-4 py-2.5 text-sm font-bold text-white transition hover:bg-ocean disabled:cursor-not-allowed disabled:opacity-50 ${className}`} disabled={loading || props.disabled} {...props}>{loading && <LoaderCircle size={16} className="animate-spin" />}{children}</button>
}
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) { return <section className={`rounded-2xl border border-slate-200/80 bg-white p-5 shadow-soft ${className}`}>{children}</section> }
export function Badge({ children, tone = 'slate' }: { children: ReactNode; tone?: 'slate' | 'green' | 'amber' | 'red' | 'blue' }) {
  const colors = { slate: 'bg-slate-100 text-slate-600', green: 'bg-emerald-50 text-emerald-700', amber: 'bg-amber-50 text-amber-700', red: 'bg-red-50 text-red-700', blue: 'bg-cyan-50 text-cyan-700' }
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${colors[tone]}`}>{children}</span>
}
export function Empty({ icon, title, text }: { icon: ReactNode; title: string; text: string }) { return <div className="grid min-h-48 place-items-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center"><div><div className="mx-auto mb-3 grid h-11 w-11 place-items-center rounded-xl bg-white text-ocean shadow-sm">{icon}</div><h3 className="font-bold text-ink">{title}</h3><p className="mt-1 max-w-md text-sm text-slate-500">{text}</p></div></div> }

