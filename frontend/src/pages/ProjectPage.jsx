import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Download, FileOutput, RefreshCw, Loader2, Send,
  Mic, MicOff, Volume2, VolumeX, Sparkles, Lock,
  TrendingUp, BarChart3, Target, MessageCircle, Lightbulb,
  FileText, LayoutDashboard, Search, Database
} from "lucide-react";
import Navbar from "../components/Navbar";
import PlotlyChart from "../components/PlotlyChart";
import { Button, Panel, StatCard, ErrorAlert, Skeleton, EmptyState, Badge } from "../components/UI";
import { analysisApi, chatApi, projectApi } from "../lib/api";
import { useSpeechRecognition, useTextToSpeech } from "../hooks/useSpeechRecognition";

const TABS = [
  { key: "overview",   label: "Overview",        icon: "📊" },
  { key: "quality",    label: "Data Quality",     icon: "📐" },
  { key: "eda",        label: "EDA",              icon: "☑️" },
  { key: "charts",     label: "Charts",           icon: "🎨" },
  { key: "dashboard",  label: "Dashboard",        icon: "🗄️" },
  { key: "insights",   label: "Insights",         icon: "💡" },
  { key: "recommend",  label: "Recommendations",  icon: "🎯" },
  { key: "forecast",   label: "Forecast",         icon: "🔮" },
  { key: "chat",       label: "Chat",             icon: "💬" },
  { key: "report",     label: "Reports",          icon: "📄" },
];

export default function ProjectPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Tab data caches
  const cache = useRef({});
  const getCache = (key) => cache.current[key];
  const setCache = (key, val) => { cache.current[key] = val; };

  useEffect(() => {
    projectApi.get(projectId).then(setProject).catch(e => {
      setError(e.message); setLoading(false);
    }).finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <div className="flex h-screen items-center justify-center"><div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" /></div>;
  if (!project && error) return <div className="p-8"><ErrorAlert message={error} /></div>;

  const handleDownloadCleaned = async () => {
    window.open(analysisApi.downloadDataset(projectId), "_blank");
  };

  return (
    <div className="min-h-screen pb-20">
      <Navbar />
      {/* Top Bar */}
      <div className="border-b border-border-subtle bg-bg-base/90 backdrop-blur-md sticky top-[57px] z-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <div className="text-2xl">🧠</div>
              <div>
                <p className="font-display font-semibold text-white leading-none">{project?.filename}</p>
                <p className="text-xs text-slate-500 mt-0.5">AI Data Analyst Pro</p>
              </div>
              {project?.total_rows && (
                <div className="flex gap-2 ml-2">
                  <Badge color="blue">{project.total_rows?.toLocaleString()} rows</Badge>
                  <Badge color="violet">{project.total_columns} cols</Badge>
                  {project.quality_score && <Badge color="green">{project.quality_score}/100 quality</Badge>}
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button onClick={handleDownloadCleaned} className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/20 transition-colors">
                <Download size={14} /> Cleaned CSV
              </button>
              <button onClick={() => navigate("/dashboard")} className="flex items-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-300 hover:bg-rose-500/20 transition-colors">
                <RefreshCw size={14} /> New Dataset
              </button>
            </div>
          </div>
          {/* Tab Strip */}
          <div className="flex gap-1 overflow-x-auto pb-2 scrollbar-hide">
            {TABS.map(t => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={`flex flex-shrink-0 items-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-medium transition-all whitespace-nowrap
                  ${activeTab === t.key ? "bg-bg-raised text-white border border-accent-blue/30" : "text-slate-400 hover:bg-bg-card hover:text-slate-200"}`}>
                <span>{t.icon}</span>{t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        {error && <ErrorAlert message={error} />}
        {activeTab === "overview"  && <OverviewTab projectId={projectId} project={project} cache={cache} />}
        {activeTab === "quality"   && <QualityTab projectId={projectId} cache={cache} />}
        {activeTab === "eda"       && <EdaTab projectId={projectId} cache={cache} />}
        {activeTab === "charts"    && <ChartsTab projectId={projectId} cache={cache} />}
        {activeTab === "dashboard" && <DashboardTab projectId={projectId} cache={cache} />}
        {activeTab === "insights"  && <InsightsTab projectId={projectId} cache={cache} onlyInsights />}
        {activeTab === "recommend" && <InsightsTab projectId={projectId} cache={cache} onlyRecommendations />}
        {activeTab === "forecast"  && <ForecastTab projectId={projectId} project={project} cache={cache} />}
        {activeTab === "chat"      && <ChatTab projectId={projectId} project={project} />}
        {activeTab === "report"    && <ReportTab projectId={projectId} />}
      </div>
    </div>
  );
}

// ── Overview Tab ──────────────────────────────────────────────────────────────
function OverviewTab({ projectId, project, cache }) {
  const [quality, setQuality] = useState(cache.current.quality);
  const [loading, setLoading] = useState(!quality);
  const [error, setError] = useState("");

  useEffect(() => {
    if (quality) return;
    analysisApi.getQuality(projectId).then(d => { setQuality(d); cache.current.quality = d; })
      .catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="grid grid-cols-4 gap-4">{[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}</div>;

  const scoreAccent = quality?.data_quality_score >= 90 ? "green" : quality?.data_quality_score >= 70 ? "amber" : "rose";

  return (
    <div className="space-y-6">
      <ErrorAlert message={error} />
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Rows" value={quality?.total_rows?.toLocaleString()} icon="📋" accent="blue" />
        <StatCard label="Columns" value={quality?.total_columns} icon="📊" accent="violet" />
        <StatCard label="Duplicates" value={quality?.duplicate_rows} icon="📋" accent={quality?.duplicate_rows > 0 ? "rose" : "green"} />
        <StatCard label="Quality Score" value={quality?.data_quality_score} suffix="/100" icon="✅" accent={scoreAccent} />
      </div>
      <Panel title="Column Data Types" subtitle="Detected type for each column">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border-subtle text-left">
              <th className="pb-3 pr-4 text-xs uppercase tracking-wider text-slate-500 font-medium">Column</th>
              <th className="pb-3 text-xs uppercase tracking-wider text-slate-500 font-medium">Data Type</th>
            </tr></thead>
            <tbody>{Object.entries(quality?.data_types || {}).map(([col, dt]) => (
              <tr key={col} className="border-b border-border-subtle/50 last:border-0">
                <td className="py-2.5 pr-4 font-mono text-slate-300">{col}</td>
                <td className="py-2.5"><span className="rounded-md bg-bg-raised px-2 py-0.5 font-mono text-xs text-accent-blue">{dt}</span></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </Panel>
      {project?.preview && (
        <Panel title="Data Preview" subtitle="First 10 rows">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-border-subtle">
                {(project.columns || []).map(c => <th key={c} className="whitespace-nowrap pb-2 pr-4 text-left text-xs uppercase tracking-wider text-slate-500 font-medium">{c}</th>)}
              </tr></thead>
              <tbody>{(project.preview || []).map((row, i) => (
                <tr key={i} className="border-b border-border-subtle/50 last:border-0">
                  {(project.columns || []).map(c => <td key={c} className="whitespace-nowrap py-2 pr-4 font-mono text-xs text-slate-400">{String(row[c] ?? "—")}</td>)}
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  );
}

// ── Quality Tab ───────────────────────────────────────────────────────────────
function QualityTab({ projectId, cache }) {
  const [quality, setQuality] = useState(cache.current.quality);
  const [loading, setLoading] = useState(!quality);
  const [cleaning, setCleaning] = useState(false);
  const [cleanResult, setCleanResult] = useState(null);
  const [error, setError] = useState("");
  const [strategy, setStrategy] = useState("auto");

  useEffect(() => {
    if (quality) return;
    analysisApi.getQuality(projectId).then(d => { setQuality(d); cache.current.quality = d; })
      .catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  const handleClean = async () => {
    setCleaning(true); setError("");
    try {
      const r = await analysisApi.clean(projectId, strategy);
      setCleanResult(r);
      const refreshed = await analysisApi.getQuality(projectId);
      setQuality(refreshed); cache.current.quality = refreshed;
    } catch (e) { setError(e.message); } finally { setCleaning(false); }
  };

  if (loading) return <Skeleton className="h-48" />;

  const hasMissing = Object.keys(quality?.missing_values || {}).length > 0;

  return (
    <div className="space-y-6">
      <ErrorAlert message={error} />
      {hasMissing ? (
        <Panel title="Missing Values">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border-subtle text-left">
              {["Column","Missing Count","Missing %"].map(h => <th key={h} className="pb-3 pr-4 text-xs uppercase tracking-wider text-slate-500 font-medium">{h}</th>)}
            </tr></thead>
            <tbody>{Object.entries(quality.missing_values).map(([col, info]) => (
              <tr key={col} className="border-b border-border-subtle/50 last:border-0">
                <td className="py-2.5 pr-4 font-mono text-slate-300">{col}</td>
                <td className="py-2.5 pr-4 text-rose-300">{info.count}</td>
                <td className="py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-24 overflow-hidden rounded-full bg-bg-raised">
                      <div className="h-full rounded-full bg-rose-400" style={{ width: `${Math.min(info.percent, 100)}%` }} />
                    </div>
                    <span className="text-xs text-slate-400">{info.percent}%</span>
                  </div>
                </td>
              </tr>
            ))}</tbody>
          </table>
        </Panel>
      ) : (
        <div className="flex items-center gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4 text-emerald-300">
          ✅ No missing values found!
        </div>
      )}
      <Panel title="Cleaning Suggestions" subtitle="AI-detected recommendations">
        <ul className="space-y-2 mb-6">
          {(quality?.suggestions || []).map((s, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
              <Sparkles size={14} className="mt-0.5 flex-shrink-0 text-accent-blue" />{s}
            </li>
          ))}
        </ul>
        <div className="flex flex-wrap items-center gap-4 border-t border-border-subtle pt-5">
          <div className="flex items-center gap-1 rounded-xl bg-bg-raised p-1">
            {["auto","drop"].map(s => (
              <button key={s} onClick={() => setStrategy(s)}
                className={`rounded-lg px-3.5 py-1.5 text-sm font-medium capitalize transition-colors ${strategy === s ? "bg-accent-blue text-bg-base" : "text-slate-400 hover:text-white"}`}>{s}</button>
            ))}
          </div>
          <Button onClick={handleClean} loading={cleaning}>Clean Dataset Now</Button>
          {cleanResult && <span className="text-sm text-emerald-300">✓ {cleanResult.rows_before} → {cleanResult.rows_after} rows</span>}
        </div>
      </Panel>
    </div>
  );
}

// ── EDA Tab ───────────────────────────────────────────────────────────────────
function EdaTab({ projectId, cache }) {
  const [eda, setEda] = useState(cache.current.eda);
  const [loading, setLoading] = useState(!eda);
  const [error, setError] = useState("");

  useEffect(() => {
    if (eda) return;
    analysisApi.getEDA(projectId).then(d => { setEda(d); cache.current.eda = d; })
      .catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Skeleton className="h-64" />;

  return (
    <div className="space-y-6">
      <ErrorAlert message={error} />
      {Object.keys(eda?.descriptive_stats || {}).length > 0 && (
        <Panel title="Descriptive Statistics" subtitle="Per numeric column">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-border-subtle text-left">
                {["Column","Mean","Median","Mode","Std Dev","Min","Max","Skewness"].map(h =>
                  <th key={h} className="pb-3 pr-4 text-xs uppercase tracking-wider text-slate-500 font-medium">{h}</th>
                )}
              </tr></thead>
              <tbody>{Object.entries(eda.descriptive_stats).map(([col, s]) => (
                <tr key={col} className="border-b border-border-subtle/50 last:border-0">
                  <td className="py-2.5 pr-4 font-mono text-slate-300">{col}</td>
                  <td className="py-2.5 pr-4 font-mono text-accent-blue">{s.mean}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-400">{s.median}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-400">{s.mode}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-400">{s.std}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-500 text-xs">{s.min}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-500 text-xs">{s.max}</td>
                  <td className="py-2.5 pr-4 font-mono text-slate-500 text-xs">{s.skewness}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      )}
      <Panel title="Strong Correlations" subtitle="|r| ≥ 0.6">
        {eda?.strong_correlations?.length ? (
          <div className="space-y-2">
            {eda.strong_correlations.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl bg-bg-raised px-4 py-3">
                <span className="font-mono text-sm text-slate-300">{c.col1} ↔ {c.col2}</span>
                <span className={`font-mono text-sm font-semibold ${c.type === "positive" ? "text-emerald-400" : "text-rose-400"}`}>
                  {c.correlation > 0 ? "+" : ""}{c.correlation}
                </span>
              </div>
            ))}
          </div>
        ) : <p className="text-sm text-slate-500">No strong correlations found.</p>}
      </Panel>
      {Object.keys(eda?.category_distribution || {}).length > 0 && (
        <Panel title="Category Distributions" subtitle="Top values per categorical column">
          <div className="grid gap-5 sm:grid-cols-2">
            {Object.entries(eda.category_distribution).map(([col, dist]) => {
              const entries = Object.entries(dist);
              const max = Math.max(...entries.map(([,v]) => v));
              return (
                <div key={col}>
                  <p className="mb-2 font-mono text-xs uppercase tracking-wider text-slate-500">{col}</p>
                  <div className="space-y-1.5">
                    {entries.slice(0,6).map(([label, count]) => (
                      <div key={label} className="flex items-center gap-2">
                        <span className="w-20 flex-shrink-0 truncate text-xs text-slate-400">{label}</span>
                        <div className="h-2 flex-1 overflow-hidden rounded-full bg-bg-raised">
                          <div className="h-full rounded-full bg-gradient-to-r from-accent-blue to-accent-violet" style={{ width: `${(count/max)*100}%` }} />
                        </div>
                        <span className="w-8 text-right font-mono text-xs text-slate-500">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Panel>
      )}
    </div>
  );
}

// ── Charts Tab ────────────────────────────────────────────────────────────────
function ChartsTab({ projectId, cache }) {
  const [charts, setCharts] = useState(cache.current.charts);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true); setError("");
    try {
      const r = await analysisApi.getCharts(projectId);
      setCharts(r.interactive); cache.current.charts = r.interactive;
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const CHART_LABELS = {
    bar_chart: "Bar Chart", line_chart: "Line Chart — Trend",
    pie_chart: "Pie Chart — Distribution", histogram: "Histogram",
    scatter_plot: "Scatter Plot", box_plot: "Box Plot",
    heatmap: "Correlation Heatmap", area_chart: "Area Chart",
  };

  return (
    <div className="space-y-6">
      <Panel title="Auto-Generated Visualizations" subtitle="8 chart types, automatically chosen based on your data"
        action={<Button onClick={generate} loading={loading} icon={<Sparkles size={16} />}>{charts ? "Regenerate" : "Generate Charts"}</Button>}>
        <ErrorAlert message={error} />
        {!charts && !loading && <p className="text-sm text-slate-500">Click "Generate Charts" to visualize your dataset.</p>}
      </Panel>
      {charts && (
        <div className="grid gap-5 sm:grid-cols-2">
          {Object.entries(charts).map(([key, figure]) => (
            <div key={key} className="rounded-2xl border border-border-subtle bg-bg-card p-4 animate-fade-up">
              <PlotlyChart figure={figure} title={CHART_LABELS[key] || key} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Dashboard KPI Tab ─────────────────────────────────────────────────────────
function DashboardTab({ projectId, cache }) {
  const [data, setData] = useState(cache.current.dashboard);
  const [loading, setLoading] = useState(!data);
  const [error, setError] = useState("");

  useEffect(() => {
    if (data) return;
    analysisApi.getDashboard(projectId).then(d => { setData(d); cache.current.dashboard = d; })
      .catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">{[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}</div>;

  const ACCENT_MAP = ["blue","green","amber","violet","pink","rose","blue","green"];

  return (
    <div className="space-y-6">
      <ErrorAlert message={error} />
      {data?.executive_summary && (
        <div className="rounded-2xl border border-accent-blue/20 bg-accent-blue/5 px-6 py-5">
          <h3 className="font-display text-base font-semibold text-accent-blue mb-2">📋 Executive Summary</h3>
          <p className="text-sm leading-relaxed text-slate-300">{data.executive_summary}</p>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {(data?.kpi_cards || []).map((kpi, i) => (
          <StatCard key={i} label={kpi.title} value={
            kpi.format === "currency" ? `$${Number(kpi.value).toLocaleString()}` : kpi.value?.toLocaleString()
          } accent={ACCENT_MAP[i % ACCENT_MAP.length]} change={kpi.change} />
        ))}
      </div>
      {data?.top_performers?.data && (
        <Panel title={`Top ${data.top_performers.category}`} subtitle={`By ${data.top_performers.metric}`}>
          <div className="space-y-2">
            {Object.entries(data.top_performers.data).slice(0,5).map(([name, val], i) => {
              const max = Math.max(...Object.values(data.top_performers.data));
              return (
                <div key={name} className="flex items-center gap-3">
                  <span className="w-5 text-xs text-slate-500 font-mono">#{i+1}</span>
                  <span className="w-32 truncate text-sm text-slate-300">{name}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-bg-raised">
                    <div className="h-full rounded-full bg-gradient-to-r from-accent-blue to-accent-violet" style={{ width: `${(val/max)*100}%` }} />
                  </div>
                  <span className="font-mono text-xs text-slate-400 w-20 text-right">{Number(val).toLocaleString()}</span>
                </div>
              );
            })}
          </div>
        </Panel>
      )}
      {data?.key_insights?.length > 0 && (
        <Panel title="Key Insights">
          <ul className="space-y-2">
            {data.key_insights.map((ins, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                <Lightbulb size={14} className="mt-0.5 flex-shrink-0 text-accent-amber" />{ins}
              </li>
            ))}
          </ul>
        </Panel>
      )}
    </div>
  );
}

// ── Insights + Recommendations Tab ────────────────────────────────────────────
function InsightsTab({ projectId, cache, onlyInsights, onlyRecommendations }) {
  const [insights, setInsights] = useState(cache.current.insights);
  const [recs, setRecs] = useState(cache.current.recs);
  const [loadIns, setLoadIns] = useState(false);
  const [loadRec, setLoadRec] = useState(false);
  const [error, setError] = useState("");

  const genInsights = async () => {
    setLoadIns(true); setError("");
    try {
      const r = await analysisApi.getInsights(projectId);
      setInsights(r.insights); cache.current.insights = r.insights;
    } catch (e) { setError(e.message); } finally { setLoadIns(false); }
  };

  const genRecs = async () => {
    setLoadRec(true); setError("");
    try {
      const r = await analysisApi.getRecommendations(projectId);
      setRecs(r.recommendations); cache.current.recs = r.recommendations;
    } catch (e) { setError(e.message); } finally { setLoadRec(false); }
  };

  return (
    <div className="space-y-6">
      <ErrorAlert message={error} />
      {!onlyRecommendations && (
        <Panel title="Business Insight Agent" subtitle="LLM-powered analysis — detailed English insights"
          action={<Button onClick={genInsights} loading={loadIns} icon={<Sparkles size={16} />}>{insights ? "Regenerate" : "Generate Insights"}</Button>}>
          {insights ? (
            <ul className="space-y-3">
              {insights.map((ins, i) => (
                <li key={i} className="flex items-start gap-3 rounded-xl bg-bg-raised px-4 py-3">
                  <Lightbulb size={16} className="mt-0.5 flex-shrink-0 text-accent-amber" />
                  <span className="text-sm leading-relaxed text-slate-200">{ins}</span>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-slate-500">Click "Generate Insights" — the AI will produce 8-10 detailed business insights.</p>}
        </Panel>
      )}
      {!onlyInsights && (
        <Panel title="Recommendation Agent" subtitle="Actionable recommendations based on insights"
          action={
            <Button onClick={genRecs} loading={loadRec} disabled={!insights} variant="success"
              icon={insights ? <Target size={16} /> : <Lock size={16} />}>
              {recs ? "Regenerate" : "Generate Recommendations"}
            </Button>
          }>
          {recs ? (
            <ul className="space-y-3">
              {recs.map((rec, i) => (
                <li key={i} className="flex items-start gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
                  <Target size={16} className="mt-0.5 flex-shrink-0 text-emerald-400" />
                  <span className="text-sm leading-relaxed text-slate-200">{rec}</span>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-slate-500">{insights ? 'Click "Generate Recommendations".' : "Generate Insights first — Recommendations depend on them."}</p>}
        </Panel>
      )}
    </div>
  );
}

// ── Forecast Tab ──────────────────────────────────────────────────────────────
function ForecastTab({ projectId, project, cache }) {
  const cols = project?.columns || [];
  const colTypes = project?.column_types || {};
  const numCols = cols.filter(c => colTypes[c] === "numeric");
  const dateCols = cols.filter(c => /date|time/i.test(c)) || cols;

  const [dateCol, setDateCol] = useState(dateCols[0] || "");
  const [valCol, setValCol] = useState(numCols[0] || "");
  const [periods, setPeriods] = useState(3);
  const [poly, setPoly] = useState(false);
  const [result, setResult] = useState(cache.current.forecast);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError("");
    try {
      const r = await analysisApi.getForecast(projectId, {
        project_id: projectId, date_column: dateCol, value_column: valCol,
        periods_ahead: Number(periods), use_polynomial: poly,
      });
      setResult(r); cache.current.forecast = r;
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const figure = result ? {
    data: [
      { x: result.historical_periods, y: result.historical_values, type: "scatter", mode: "lines+markers", name: "Historical", line: { color: "#38bdf8" } },
      { x: result.forecasted_periods, y: result.forecasted_values, type: "scatter", mode: "lines+markers", name: "Forecasted", line: { color: "#34d399", dash: "dash" } },
    ],
    layout: { title: { text: "" } },
  } : null;

  return (
    <div className="space-y-6">
      <Panel title="Forecasting Agent" subtitle="scikit-learn Linear / Polynomial Regression">
        <div className="grid gap-4 sm:grid-cols-4 mb-5">
          {[
            { label: "Date Column", value: dateCol, set: setDateCol, options: dateCols },
            { label: "Value Column (numeric)", value: valCol, set: setValCol, options: numCols },
          ].map(f => (
            <div key={f.label}>
              <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">{f.label}</label>
              <select value={f.value} onChange={e => f.set(e.target.value)}
                className="w-full rounded-xl border border-border-subtle bg-bg-raised px-3 py-2.5 text-sm text-white focus:border-accent-blue focus:outline-none">
                {f.options.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          ))}
          <div>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">Periods Ahead</label>
            <input type="number" min={1} max={12} value={periods} onChange={e => setPeriods(e.target.value)}
              className="w-full rounded-xl border border-border-subtle bg-bg-raised px-3 py-2.5 text-sm text-white focus:border-accent-blue focus:outline-none" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">Model</label>
            <button onClick={() => setPoly(!poly)}
              className={`w-full rounded-xl border px-3 py-2.5 text-sm text-left transition-colors ${poly ? "border-accent-violet/50 bg-accent-violet/10 text-accent-violet" : "border-border-subtle bg-bg-raised text-slate-300"}`}>
              {poly ? "Polynomial (deg 2)" : "Linear Regression"}
            </button>
          </div>
        </div>
        <ErrorAlert message={error} />
        <Button onClick={run} loading={loading} icon={<TrendingUp size={16} />}>Run Forecast</Button>
      </Panel>
      {result && !result.error && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <StatCard label="R² Score" value={result.r2_score} accent="blue" />
            <StatCard label="Accuracy" value={result.accuracy_percent} suffix="%" accent="green" />
            <StatCard label="MAE" value={result.mae} accent="amber" />
          </div>
          <Panel title={`Forecast — ${result.model_type}`}>
            <PlotlyChart figure={figure} height={350} />
          </Panel>
        </>
      )}
      {result?.error && <ErrorAlert message={result.error} />}
    </div>
  );
}

// ── Chat Tab ──────────────────────────────────────────────────────────────────
function ChatTab({ projectId, project }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [histLoaded, setHistLoaded] = useState(false);
  const scrollRef = useRef(null);
  const cache = useRef({});

  const { isSupported: micOk, isListening, start: startMic, stop: stopMic } =
    useSpeechRecognition({ onResult: (t) => setInput(p => p ? `${p} ${t}` : t) });
  const { isSupported: ttsOk, isSpeaking, speak, stop: stopTTS } = useTextToSpeech();

  useEffect(() => {
    chatApi.getHistory(projectId).then(msgs => {
      setMessages(msgs.map(m => ({ role: m.role, content: m.content, chart: m.chart_data, agent: m.agent_used, follow_ups: [] })));
      setHistLoaded(true);
    }).catch(() => setHistLoaded(true));
  }, [projectId]);

  useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setMessages(p => [...p, { role: "user", content: q }]);
    setInput(""); setLoading(true);
    try {
      const r = await chatApi.send(projectId, q);
      const msg = { role: "assistant", content: r.answer, chart: r.chart_data, agent: r.agent_used, follow_ups: r.follow_ups || [] };
      setMessages(p => [...p, msg]);
      if (ttsEnabled && ttsOk) speak(r.answer);
    } catch (e) {
      setMessages(p => [...p, { role: "assistant", content: `⚠️ ${e.message}`, isError: true }]);
    } finally { setLoading(false); }
  };

  const SUGGESTIONS = ["Which category has the highest revenue?", "Show me the top 5 rows", "What are the key trends?", "Any anomalies detected?", "Summarize this dataset"];
  const AGENT_LABELS = { sql: "SQL Agent 🗄️", pandas: "Pandas Agent 🐼", chart: "Visualization 📊", forecast: "Forecast 🔮", general: "Analysis 💡", insights: "Insights 💡", recommend: "Recommendations 🎯" };

  return (
    <div className="flex h-[calc(100vh-200px)] min-h-[500px] flex-col rounded-2xl border border-border-subtle bg-bg-card overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border-subtle px-6 py-4">
        <div>
          <h3 className="font-display text-lg font-semibold text-white">Chat With Your Dataset</h3>
          <p className="text-xs text-slate-500 mt-0.5">10 agents · Voice input · Auto language detect · Smart routing</p>
        </div>
        <div className="flex items-center gap-2">
          {ttsOk && (
            <button onClick={() => { setTtsEnabled(!ttsEnabled); if (isSpeaking) stopTTS(); }}
              title="Toggle voice output"
              className={`flex h-9 w-9 items-center justify-center rounded-lg border transition-colors ${ttsEnabled ? "border-accent-blue/50 bg-accent-blue/10 text-accent-blue" : "border-border-subtle bg-bg-raised text-slate-500"}`}>
              {ttsEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            </button>
          )}
          <button onClick={() => { chatApi.clearHistory(projectId); setMessages([]); }}
            className="flex items-center gap-1.5 rounded-lg border border-border-subtle bg-bg-raised px-3 py-2 text-xs text-slate-400 hover:text-rose-400 transition-colors">
            Clear
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && histLoaded && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <MessageCircle size={36} className="mb-3 text-slate-600" />
            <p className="text-slate-500 text-sm mb-1">Ask anything about your dataset</p>
            <p className="text-xs text-slate-600 mb-5">Replies in English · Tap mic for voice · Auto-detects Urdu/Hindi</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map(s => (
                <button key={s} onClick={() => setInput(s)}
                  className="rounded-full border border-border-subtle bg-bg-raised px-3 py-1.5 text-xs text-slate-400 hover:border-accent-blue/50 hover:text-accent-blue transition-colors">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-accent-blue/20 to-accent-violet/20 text-accent-blue text-sm">🧠</div>
            )}
            <div className="max-w-[80%] space-y-2">
              {msg.agent && msg.role === "assistant" && (
                <span className="text-xs text-slate-600">{AGENT_LABELS[msg.agent] || msg.agent}</span>
              )}
              <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
                ${msg.role === "user" ? "bg-gradient-to-r from-accent-blue to-accent-violet text-bg-base"
                  : msg.isError ? "border border-rose-500/30 bg-rose-500/10 text-rose-300"
                  : "bg-bg-raised text-slate-200"}`}>
                {msg.content}
              </div>
              {msg.chart && (
                <div className="rounded-xl border border-border-subtle bg-bg-card p-3">
                  <PlotlyChart figure={msg.chart} height={280} />
                </div>
              )}
              {msg.follow_ups?.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {msg.follow_ups.map((q, j) => (
                    <button key={j} onClick={() => setInput(q)}
                      className="rounded-full border border-border-subtle bg-bg-raised px-2.5 py-1 text-xs text-slate-400 hover:border-accent-blue/50 hover:text-accent-blue transition-colors">
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {msg.role === "user" && <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-bg-raised text-slate-400 text-sm">👤</div>}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-blue/20 to-accent-violet/20 text-sm">🧠</div>
            <div className="flex items-center gap-1 rounded-2xl bg-bg-raised px-4 py-3">
              {[0,1,2].map(i => <span key={i} className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500" style={{ animationDelay: `${i*0.15}s` }} />)}
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border-subtle px-6 py-4 flex items-center gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
          placeholder={isListening ? "Listening…" : "Ask anything about your data…"}
          className="flex-1 rounded-xl border border-border-subtle bg-bg-raised px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-accent-blue focus:outline-none" />
        {micOk && (
          <button onClick={isListening ? stopMic : startMic}
            className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border transition-all ${isListening ? "animate-pulse-ring border-rose-500/50 bg-rose-500/20 text-rose-300" : "border-border-subtle bg-bg-raised text-slate-400 hover:text-accent-blue"}`}>
            {isListening ? <MicOff size={16} /> : <Mic size={16} />}
          </button>
        )}
        <button onClick={send} disabled={loading || !input.trim()}
          className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-accent-blue to-accent-violet text-bg-base transition-transform hover:scale-105 disabled:opacity-40">
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}

// ── Report Tab ─────────────────────────────────────────────────────────────────
function ReportTab({ projectId }) {
  const [generating, setGenerating] = useState(null);
  const [reports, setReports] = useState({});
  const [error, setError] = useState("");

  const generate = async (format) => {
    setGenerating(format); setError("");
    try {
      const r = await analysisApi.generateReport(projectId, format);
      setReports(p => ({ ...p, [format]: r.filename }));
    } catch (e) { setError(e.message); } finally { setGenerating(null); }
  };

  const FORMATS = [
    { key: "pdf", label: "PDF Report", icon: "📕", desc: "Print-ready, universal format", color: "rose" },
    { key: "docx", label: "Word Document", icon: "📘", desc: "Editable Microsoft Word file", color: "blue" },
    { key: "pptx", label: "PowerPoint", icon: "📙", desc: "Presentation slides with insights", color: "amber" },
  ];

  return (
    <div className="space-y-6">
      <Panel title="Report Generator Agent" subtitle="If prior steps haven't run, the pipeline auto-executes them">
        <ErrorAlert message={error} />
        <p className="text-sm text-slate-400 mb-6">Generate a professional report with statistics, charts, insights, recommendations, and forecast.</p>
        <div className="grid gap-4 sm:grid-cols-3">
          {FORMATS.map(f => (
            <div key={f.key} className="rounded-2xl border border-border-subtle bg-bg-raised p-6">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h4 className="font-display text-base font-semibold text-white">{f.label}</h4>
              <p className="mt-1 mb-5 text-sm text-slate-500">{f.desc}</p>
              {reports[f.key] ? (
                <a href={analysisApi.downloadReport(reports[f.key])} download>
                  <Button variant="success" icon={<Download size={16} />} className="w-full">Download {f.key.toUpperCase()}</Button>
                </a>
              ) : (
                <Button onClick={() => generate(f.key)} loading={generating === f.key} variant="secondary" className="w-full">
                  Generate {f.key.toUpperCase()}
                </Button>
              )}
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
