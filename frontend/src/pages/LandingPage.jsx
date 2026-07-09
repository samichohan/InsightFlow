import { Link } from "react-router-dom";
import { ArrowRight, BarChart3, Brain, Shield, Zap, FileText, MessageCircle } from "lucide-react";
import { Button } from "../components/UI";

const FEATURES = [
  { icon: "🧹", title: "Data Cleaning", desc: "Auto-detect missing values, duplicates, outliers with one-click cleaning" },
  { icon: "📊", title: "EDA & Statistics", desc: "Mean, median, correlation matrix, distributions — fully automated" },
  { icon: "📈", title: "8 Chart Types", desc: "Interactive Plotly charts: Bar, Line, Pie, Scatter, Box, Heatmap, Area, Histogram" },
  { icon: "💡", title: "AI Insights", desc: "Groq LLM generates 8-10 detailed business insights from your data" },
  { icon: "🎯", title: "Recommendations", desc: "Actionable business recommendations with expected ROI" },
  { icon: "🔮", title: "ML Forecasting", desc: "Linear & Polynomial Regression with R² score and accuracy metrics" },
  { icon: "💬", title: "Chat with Data", desc: "Ask questions in English, Urdu, Hindi. Voice input + TTS output" },
  { icon: "📄", title: "Reports (PDF/DOCX/PPTX)", desc: "Professional reports with charts, insights, and recommendations" },
  { icon: "🗄️", title: "SQL Agent", desc: "Natural language → SQL query → executed on your dataset instantly" },
  { icon: "🐼", title: "Pandas Agent", desc: "Natural language → Python/Pandas code → real calculations" },
];

const AGENTS = [
  { n: "01", name: "Data Cleaning", color: "from-rose-500/20 to-rose-600/5", text: "text-rose-300" },
  { n: "02", name: "EDA Agent", color: "from-fuchsia-500/20 to-fuchsia-600/5", text: "text-fuchsia-300" },
  { n: "03", name: "Visualization", color: "from-amber-500/20 to-amber-600/5", text: "text-amber-300" },
  { n: "04", name: "AI Insights", color: "from-emerald-500/20 to-emerald-600/5", text: "text-emerald-300" },
  { n: "05", name: "Recommendations", color: "from-orange-500/20 to-orange-600/5", text: "text-orange-300" },
  { n: "06", name: "Forecasting", color: "from-sky-500/20 to-sky-600/5", text: "text-sky-300" },
  { n: "07", name: "Report Generator", color: "from-violet-500/20 to-violet-600/5", text: "text-violet-300" },
  { n: "08", name: "SQL Agent", color: "from-blue-500/20 to-blue-600/5", text: "text-blue-300" },
  { n: "09", name: "Pandas Agent", color: "from-green-500/20 to-green-600/5", text: "text-green-300" },
  { n: "10", name: "Dashboard Agent", color: "from-pink-500/20 to-pink-600/5", text: "text-pink-300" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Navbar */}
      <header className="border-b border-border-subtle bg-bg-base/80 backdrop-blur-md sticky top-0 z-30">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent-blue to-accent-violet text-xl">🧠</div>
            <span className="font-display text-lg font-bold text-white">AI Data Analyst Pro</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login"><Button variant="ghost" size="sm">Login</Button></Link>
            <Link to="/signup"><Button size="sm">Get Started Free</Button></Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden py-24 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-accent-blue/5 to-transparent pointer-events-none" />
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent-blue/30 bg-accent-blue/10 px-4 py-2 text-sm text-accent-blue">
            <Zap size={14} /> Production-Level AI Data Platform
          </div>
          <h1 className="font-display text-5xl font-extrabold leading-tight text-white sm:text-6xl">
            Turn Any Dataset Into{" "}
            <span className="bg-gradient-to-r from-accent-blue to-accent-violet bg-clip-text text-transparent">
              Business Intelligence
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
            Upload a CSV, Excel, JSON, or PDF. Our 10 AI agents automatically clean, analyze,
            visualize, forecast, and generate professional reports — in seconds.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to="/signup">
              <Button size="lg" icon={<ArrowRight size={18} />}>
                Start Analyzing Free
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="secondary" size="lg">Login to Dashboard</Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { n: "10", label: "AI Agents" },
              { n: "8+", label: "Chart Types" },
              { n: "3", label: "Report Formats" },
              { n: "100%", label: "Free to Use" },
            ].map(s => (
              <div key={s.label} className="rounded-2xl border border-border-subtle bg-bg-card px-4 py-5 text-center">
                <p className="font-mono text-3xl font-bold text-accent-blue">{s.n}</p>
                <p className="mt-1 text-sm text-slate-500">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 10 Agents */}
      <section className="py-20 px-6">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-center font-display text-3xl font-bold text-white mb-4">10 Specialized AI Agents</h2>
          <p className="text-center text-slate-400 mb-12">Each agent is an expert — they work together as a pipeline</p>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
            {AGENTS.map(a => (
              <div key={a.n} className={`rounded-2xl border border-border-subtle bg-gradient-to-br ${a.color} p-4 text-center`}>
                <p className={`font-mono text-2xl font-bold ${a.text}`}>{a.n}</p>
                <p className="mt-1 text-sm font-medium text-slate-300">{a.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6 bg-bg-card/30">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-center font-display text-3xl font-bold text-white mb-12">Everything You Need</h2>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(f => (
              <div key={f.title} className="rounded-2xl border border-border-subtle bg-bg-card p-6 hover:border-border-glow transition-colors">
                <div className="mb-3 text-3xl">{f.icon}</div>
                <h3 className="font-display text-base font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 text-center px-6">
        <div className="mx-auto max-w-2xl">
          <h2 className="font-display text-4xl font-bold text-white mb-4">Ready to Analyze Your Data?</h2>
          <p className="text-slate-400 mb-8">No credit card. No setup. Just upload and go.</p>
          <Link to="/signup">
            <Button size="lg" icon={<ArrowRight size={18} />}>Create Free Account</Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border-subtle py-8 text-center text-slate-500 text-sm">
        <p>AI Data Analyst Pro — Built with FastAPI + React + Groq LLM</p>
      </footer>
    </div>
  );
}
