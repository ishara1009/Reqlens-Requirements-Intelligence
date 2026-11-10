import {
  ArrowRight, Bot, CircleCheck, Database, FileDiff, FileSearch, Fingerprint,
  Layers, LockKeyhole, MessageSquareText, SearchCheck, ShieldCheck,
  Sparkles, TriangleAlert, Users, Workflow,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Logo } from '../../components/Logo'
import { useAuth } from '../../lib/auth'

const audience = ['Business analysts', 'Engineering', 'QA teams', 'Security reviewers', 'Product leaders']

export function LandingPage() {
  const { user } = useAuth()
  const workspacePath = user ? '/app' : '/login'

  return <main className="landing-page min-h-screen overflow-x-hidden bg-[#f8faf7] pt-20 text-ink">
    <header className="landing-nav">
      <div className="landing-container flex h-20 items-center justify-between">
        <Link to="/" aria-label="ReqLens AI home"><Logo /></Link>
        <nav className="hidden items-center gap-8 text-sm font-bold text-slate-600 md:flex" aria-label="Main navigation">
          <a href="#platform" className="landing-nav-link">Platform</a>
          <a href="#workflow" className="landing-nav-link">How it works</a>
          <a href="#security" className="landing-nav-link">Security</a>
        </nav>
        <div className="flex items-center gap-3">
          {!user && <Link to="/login" className="hidden text-sm font-bold text-slate-600 hover:text-ocean sm:block">Sign in</Link>}
          <Link to={workspacePath} className="landing-button landing-button-dark">{user ? 'Open workspace' : 'Start analyzing'}<ArrowRight size={16} /></Link>
        </div>
      </div>
    </header>

    <section className="landing-hero relative pt-16 sm:pt-24 lg:pt-28">
      <div className="landing-glow landing-glow-left" /><div className="landing-glow landing-glow-right" />
      <div className="landing-container relative text-center">
        <div className="landing-pill landing-reveal"><Sparkles size={14} /> Agentic RAG for software requirements</div>
        <h1 className="landing-reveal landing-delay-1 mx-auto mt-7 max-w-5xl font-display text-5xl font-extrabold leading-[.98] tracking-[-.055em] text-ink sm:text-6xl lg:text-[82px]">
          Requirements deserve<br className="hidden sm:block" /> more than a <span className="landing-emphasis">chatbot.</span>
        </h1>
        <p className="landing-reveal landing-delay-2 mx-auto mt-7 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
          ReqLens turns scattered specifications into traceable decisions—finding contradictions, ambiguity, duplication, and change while keeping people in control.
        </p>
        <div className="landing-reveal landing-delay-3 mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link to={workspacePath} className="landing-button landing-button-primary px-6 py-3.5">{user ? 'Go to your workspace' : 'Create your workspace'}<ArrowRight size={18} /></Link>
          <a href="#platform" className="landing-button landing-button-ghost px-6 py-3.5"><FileSearch size={18} /> Explore the platform</a>
        </div>
        <p className="landing-reveal landing-delay-3 mt-4 text-xs font-semibold text-slate-400">AI findings remain reviewable candidates—not automatic truth.</p>

        <ProductPreview />
      </div>
    </section>

    <section className="audience-strip border-y border-slate-200/80 bg-white/70 py-7">
      <div className="landing-container flex flex-col items-center gap-5 lg:flex-row lg:justify-between">
        <p className="text-xs font-extrabold uppercase tracking-[.18em] text-slate-400">One shared evidence layer for</p>
        <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">{audience.map(item => <span key={item} className="flex items-center gap-2 text-sm font-bold text-slate-600"><span className="h-1.5 w-1.5 rounded-full bg-ocean" />{item}</span>)}</div>
      </div>
    </section>

    <section id="platform" className="landing-section">
      <div className="landing-container">
        <SectionIntro eyebrow="Requirements intelligence" title="From document pile to decision system." text="Every capability is built around the work requirements teams actually do: finding issues, proving claims, comparing change, and making a human decision." />
        <div className="mt-14 grid gap-5 lg:grid-cols-12">
          <FeatureCard className="lg:col-span-7" icon={<SearchCheck />} label="AI Audit" title="Surface issues before they become rework." text="Generate reviewable candidates for contradictions, ambiguity, duplicates, and missing acceptance detail—without comparing every sentence to every other sentence." accent="coral">
            <div className="mt-7 rounded-2xl border border-red-100 bg-[#fff8f5] p-4 sm:p-5">
              <div className="flex flex-wrap items-center gap-2"><span className="rounded-full bg-red-100 px-2.5 py-1 text-[11px] font-extrabold text-red-700">POSSIBLE CONTRADICTION</span><span className="text-xs font-semibold text-slate-400">84% confidence</span></div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2"><EvidenceMini source="SRS.pdf · page 17" text="Sessions expire after 30 minutes." /><EvidenceMini source="SecurityPolicy.pdf · page 8" text="Sessions remain active for 24 hours." /></div>
              <div className="mt-4 flex flex-wrap gap-2"><MiniAction text="Approve" tone="green" /><MiniAction text="Reject" tone="red" /><MiniAction text="Need evidence" tone="amber" /></div>
            </div>
          </FeatureCard>
          <FeatureCard className="lg:col-span-5" icon={<MessageSquareText />} label="Ask ReqLens" title="Ask naturally. Answer with evidence." text="Project-scoped retrieval combines semantic meaning, exact identifiers, metadata filters, and bounded query rewriting." accent="ocean">
            <div className="mt-7 space-y-3"><div className="ml-auto w-[88%] rounded-2xl rounded-br-md bg-ink p-3.5 text-sm text-white">Which document defines password lockout rules?</div><div className="w-[94%] rounded-2xl rounded-bl-md border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-600"><span className="mb-2 flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-ocean"><ShieldCheck size={14} /> Grounded answer</span>The account lockout policy is defined in SecurityPolicy v2. <span className="font-bold text-ocean">[Source 1]</span></div></div>
          </FeatureCard>
          <FeatureCard className="lg:col-span-4" icon={<FileDiff />} label="Version intelligence" title="See what changed—and what it means." text="Semantically match two versions to separate added, removed, modified, and unchanged requirement content." accent="violet" />
          <FeatureCard className="lg:col-span-4" icon={<Layers />} label="Traceability" title="Keep every claim tied to origin." text="Filename, version, page, section, requirement ID, and original chunk metadata travel with the evidence." accent="ocean" />
          <FeatureCard className="lg:col-span-4" icon={<Users />} label="Human review" title="AI proposes. Your team decides." text="Persist approval, rejection, needs-evidence decisions, reviewer identity, timestamps, and comments." accent="green" />
        </div>
      </div>
    </section>

    <section id="workflow" className="landing-section border-y border-slate-200 bg-white">
      <div className="landing-container">
        <div className="grid items-start gap-12 lg:grid-cols-[.8fr_1.2fr] lg:gap-20">
          <div className="lg:sticky lg:top-28"><p className="landing-eyebrow">A controlled workflow</p><h2 className="landing-heading mt-4">Move from raw files to reviewed findings.</h2><p className="mt-5 text-lg leading-8 text-slate-600">The process is visible, bounded, and designed to fail safely when evidence is weak.</p><Link to={workspacePath} className="mt-7 inline-flex items-center gap-2 text-sm font-extrabold text-ocean hover:text-ink">Try the complete workflow <ArrowRight size={16} /></Link></div>
          <div className="relative space-y-4 before:absolute before:bottom-10 before:left-6 before:top-10 before:w-px before:bg-slate-200">{[
            ['01', 'Create an isolated project', 'Keep retrieval, documents, conversations, and findings scoped to the right team context.', <Fingerprint />],
            ['02', 'Upload and index evidence', 'Extract PDF, DOCX, and TXT content with page-aware chunks and traceable source metadata.', <Database />],
            ['03', 'Retrieve, analyze, and ground', 'Hybrid retrieval and bounded LangGraph routing find support before generating a claim.', <Workflow />],
            ['04', 'Review and report', 'A person confirms important findings before they appear as approved project knowledge.', <CircleCheck />],
          ].map(([number, title, text, icon]) => <div key={number as string} className="workflow-card relative flex gap-5 rounded-2xl border border-slate-200 bg-[#fbfcfa] p-5 sm:p-6"><span className="relative z-10 grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-ink text-white">{icon}</span><div><span className="text-[11px] font-extrabold uppercase tracking-[.18em] text-ocean">Step {number as string}</span><h3 className="mt-1 font-display text-lg font-extrabold text-ink">{title as string}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{text as string}</p></div></div>)}</div>
        </div>
      </div>
    </section>

    <section id="security" className="landing-section bg-ink text-white">
      <div className="landing-container">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-20">
          <div><p className="landing-eyebrow text-cyan-300">Trust by architecture</p><h2 className="mt-4 font-display text-4xl font-extrabold tracking-[-.04em] sm:text-5xl">Evidence stays scoped.<br />Secrets stay server-side.</h2><p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">ReqLens is designed around project isolation, explicit authorization, source traceability, and prompt-injection resistance—not a single shared chatbot context.</p></div>
          <div className="grid gap-3 sm:grid-cols-2">{[
            [<LockKeyhole />, 'Backend-only credentials', 'OpenAI, Tavily, MongoDB, and JWT secrets never enter the React bundle.'],
            [<Fingerprint />, 'Owner-scoped access', 'Protected project requests verify identity and ownership before data access.'],
            [<ShieldCheck />, 'Untrusted document policy', 'Uploaded content and web results are treated as data, never higher-priority instructions.'],
            [<Database />, 'Project-isolated retrieval', 'Every retrieval query includes a project scope to prevent cross-project evidence leaks.'],
          ].map(([icon, title, text]) => <div key={title as string} className="security-card rounded-2xl border border-white/10 bg-white/[.055] p-5"><span className="text-cyan-300">{icon}</span><h3 className="mt-4 font-bold text-white">{title as string}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{text as string}</p></div>)}</div>
        </div>
      </div>
    </section>

    <section className="landing-section relative overflow-hidden">
      <div className="landing-glow landing-glow-right" />
      <div className="landing-container relative text-center"><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-ocean text-white shadow-xl shadow-ocean/20"><Bot /></div><h2 className="mx-auto mt-6 max-w-3xl font-display text-4xl font-extrabold tracking-[-.04em] text-ink sm:text-5xl">Make every requirement decision easier to defend.</h2><p className="mx-auto mt-5 max-w-xl text-lg leading-8 text-slate-600">Bring your documents. ReqLens will help your team find the questions worth reviewing.</p><Link to={workspacePath} className="landing-button landing-button-primary mt-8 px-7 py-3.5">{user ? 'Open ReqLens' : 'Create a workspace'}<ArrowRight size={18} /></Link></div>
    </section>

    <footer className="border-t border-slate-200 bg-white py-8"><div className="landing-container flex flex-col items-center justify-between gap-5 sm:flex-row"><Logo /><p className="text-center text-xs text-slate-400 sm:text-right">Evidence-first requirements intelligence.<br />AI findings require human judgment.</p></div></footer>
  </main>
}

function ProductPreview() {
  return <div className="product-frame landing-reveal landing-delay-4 mx-auto mt-16 max-w-6xl text-left sm:mt-20">
    <div className="flex h-11 items-center gap-2 border-b border-slate-200 bg-slate-50 px-4"><span className="h-2.5 w-2.5 rounded-full bg-red-300" /><span className="h-2.5 w-2.5 rounded-full bg-amber-300" /><span className="h-2.5 w-2.5 rounded-full bg-emerald-300" /><span className="ml-3 rounded-md bg-white px-3 py-1 text-[10px] font-semibold text-slate-400 shadow-sm">app.reqlens.ai / projects / payments-v2</span></div>
    <div className="grid min-h-[470px] md:grid-cols-[190px_1fr]">
      <div className="hidden bg-ink p-4 text-white md:block"><div className="flex items-center gap-2 text-sm font-extrabold"><span className="grid h-7 w-7 place-items-center rounded-lg bg-ocean"><FileSearch size={15} /></span>ReqLens <span className="text-cyan-300">AI</span></div><div className="mt-10 space-y-2 text-xs font-semibold text-slate-400"><div className="rounded-lg px-3 py-2">Overview</div><div className="rounded-lg bg-white/10 px-3 py-2 text-white">Projects</div><div className="mt-6 px-3 text-[9px] uppercase tracking-widest text-slate-500">Workspace</div><div className="rounded-lg px-3 py-2">Documents</div><div className="rounded-lg px-3 py-2">Findings</div><div className="rounded-lg px-3 py-2">Ask ReqLens</div></div></div>
      <div className="bg-[#f7f8f5] p-4 sm:p-7"><div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-[10px] font-extrabold uppercase tracking-widest text-ocean">Payments modernization</p><h3 className="mt-1 font-display text-xl font-extrabold text-ink">Requirements overview</h3></div><span className="inline-flex w-fit items-center gap-1.5 rounded-lg bg-ink px-3 py-2 text-[11px] font-bold text-white"><Sparkles size={13} /> Run AI audit</span></div>
        <div className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">{[['Documents','8'],['Requirements','142'],['Findings','17'],['Pending','6']].map(([label,value], index) => <div key={label} className="rounded-xl border border-slate-200 bg-white p-3"><span className={`mb-3 block h-1 w-8 rounded-full ${index === 3 ? 'bg-coral' : 'bg-ocean'}`} /><p className="text-xl font-extrabold text-ink">{value}</p><p className="text-[10px] font-semibold text-slate-400">{label}</p></div>)}</div>
        <div className="mt-4 grid gap-4 xl:grid-cols-[1.25fr_.75fr]"><div className="rounded-2xl border border-slate-200 bg-white p-4"><div className="flex items-center justify-between"><p className="text-xs font-extrabold text-ink">Finding candidates</p><span className="text-[10px] font-bold text-ocean">View all</span></div><div className="mt-3 space-y-2"><PreviewFinding icon={<TriangleAlert size={15} />} tone="red" title="Conflicting session duration" meta="SRS v2 ↔ Security Policy" /><PreviewFinding icon={<SearchCheck size={15} />} tone="amber" title="Ambiguous availability target" meta="Platform Requirements · p. 12" /><PreviewFinding icon={<Layers size={15} />} tone="violet" title="Potential duplicate payment rule" meta="API Spec ↔ Client Notes" /></div></div><div className="rounded-2xl bg-ink p-4 text-white"><p className="text-[10px] font-extrabold uppercase tracking-widest text-cyan-300">Evidence coverage</p><p className="mt-3 text-3xl font-extrabold">92%</p><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full w-[92%] rounded-full bg-cyan-300" /></div><p className="mt-4 text-[11px] leading-5 text-slate-400">Approved findings with traceable document evidence.</p></div></div>
      </div>
    </div>
  </div>
}

function PreviewFinding({ icon, tone, title, meta }: { icon: React.ReactNode; tone: 'red' | 'amber' | 'violet'; title: string; meta: string }) {
  const colors = { red: 'bg-red-50 text-red-600', amber: 'bg-amber-50 text-amber-700', violet: 'bg-violet-50 text-violet-700' }
  return <div className="flex items-center gap-3 rounded-xl border border-slate-100 p-2.5"><span className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${colors[tone]}`}>{icon}</span><div className="min-w-0"><p className="truncate text-[11px] font-extrabold text-ink">{title}</p><p className="truncate text-[9px] text-slate-400">{meta}</p></div><span className="ml-auto h-2 w-2 rounded-full bg-amber-400" /></div>
}

function SectionIntro({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="max-w-3xl"><p className="landing-eyebrow">{eyebrow}</p><h2 className="landing-heading mt-4">{title}</h2><p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">{text}</p></div>
}

function FeatureCard({ icon, label, title, text, accent, className = '', children }: { icon: React.ReactNode; label: string; title: string; text: string; accent: 'coral' | 'ocean' | 'violet' | 'green'; className?: string; children?: React.ReactNode }) {
  const colors = { coral: 'bg-orange-50 text-coral', ocean: 'bg-cyan-50 text-ocean', violet: 'bg-violet-50 text-violet-700', green: 'bg-emerald-50 text-emerald-700' }
  return <article className={`feature-card rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_22px_60px_rgba(16,42,67,.06)] sm:p-8 ${className}`}><div className="flex items-center gap-3"><span className={`grid h-11 w-11 place-items-center rounded-2xl ${colors[accent]}`}>{icon}</span><span className="text-xs font-extrabold uppercase tracking-[.16em] text-slate-400">{label}</span></div><h3 className="mt-6 max-w-xl font-display text-2xl font-extrabold tracking-[-.025em] text-ink">{title}</h3><p className="mt-3 max-w-xl text-sm leading-7 text-slate-500">{text}</p>{children}</article>
}

function EvidenceMini({ source, text }: { source: string; text: string }) { return <div className="rounded-xl border border-red-100 bg-white p-3"><p className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">{source}</p><p className="mt-2 text-sm font-semibold leading-6 text-ink">“{text}”</p></div> }
function MiniAction({ text, tone }: { text: string; tone: 'green' | 'red' | 'amber' }) { const colors = { green: 'bg-emerald-50 text-emerald-700', red: 'bg-red-50 text-red-700', amber: 'bg-amber-50 text-amber-700' }; return <span className={`rounded-lg px-3 py-2 text-[11px] font-extrabold ${colors[tone]}`}>{text}</span> }

