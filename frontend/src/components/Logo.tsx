import { ScanSearch } from 'lucide-react'

export function Logo({ light = false }: { light?: boolean }) {
  return <div className={`flex items-center gap-2.5 font-display text-xl font-extrabold tracking-tight ${light ? 'text-white' : 'text-ink'}`}>
    <span className="grid h-9 w-9 place-items-center rounded-xl bg-ocean text-white shadow-lg shadow-ocean/20"><ScanSearch size={20} /></span>
    ReqLens <span className="text-ocean">AI</span>
  </div>
}

