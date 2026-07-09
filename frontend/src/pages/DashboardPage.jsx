import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Trash2, FolderOpen, BarChart3, MessageCircle, FileText, Clock } from "lucide-react";
import Navbar from "../components/Navbar";
import UploadZone from "../components/UploadZone";
import { StatCard, Button, ErrorAlert, Skeleton } from "../components/UI";
import { projectApi } from "../lib/api";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(null);

  const loadStats = async () => {
    try {
      const data = await projectApi.dashboardStats();
      setStats(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadStats(); }, []);

  const handleUpload = async (file) => {
    setUploading(true); setProgress(0); setError("");
    try {
      const data = await projectApi.upload(file, setProgress);
      navigate(`/project/${data.project_id}`);
    } catch (e) {
      setError(e.message);
      setUploading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.preventDefault(); e.stopPropagation();
    if (!confirm("Delete this project?")) return;
    setDeleting(id);
    try {
      await projectApi.delete(id);
      await loadStats();
    } catch (e) {
      setError(e.message);
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-white">
            Welcome back, {user?.username}! 👋
          </h1>
          <p className="mt-1 text-slate-400">Upload a dataset to start your AI analysis</p>
        </div>

        <ErrorAlert message={error} />

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-8">
          {loading ? (
            [...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)
          ) : (
            <>
              <StatCard label="Total Projects" value={stats?.total_projects ?? 0} icon={<FolderOpen size={18} />} accent="blue" />
              <StatCard label="Reports Generated" value={stats?.total_reports ?? 0} icon={<FileText size={18} />} accent="violet" />
              <StatCard label="Chat Messages" value={stats?.total_chats ?? 0} icon={<MessageCircle size={18} />} accent="green" />
              <StatCard label="Last Login" value={stats?.last_login ? new Date(stats.last_login).toLocaleDateString() : "Today"} icon={<Clock size={18} />} accent="amber" />
            </>
          )}
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Upload */}
          <div>
            <h2 className="font-display text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Plus size={20} className="text-accent-blue" /> New Analysis
            </h2>
            <UploadZone onFile={handleUpload} uploading={uploading} progress={progress} />
          </div>

          {/* Recent Projects */}
          <div>
            <h2 className="font-display text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 size={20} className="text-accent-violet" /> Recent Projects
            </h2>
            {loading ? (
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-16" />)}
              </div>
            ) : stats?.recent_projects?.length ? (
              <div className="space-y-3">
                {stats.recent_projects.map(p => (
                  <Link
                    key={p.id}
                    to={`/project/${p.id}`}
                    className="flex items-center justify-between rounded-2xl border border-border-subtle bg-bg-card px-5 py-4 hover:border-border-glow transition-all group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-accent-blue/20 to-accent-violet/20 text-lg">
                        📊
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-slate-200 truncate group-hover:text-white">{p.name}</p>
                        <p className="text-xs text-slate-500">
                          {p.total_rows ? `${p.total_rows.toLocaleString()} rows · ` : ""}{new Date(p.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDelete(p.id, e)}
                      disabled={deleting === p.id}
                      className="ml-3 flex-shrink-0 rounded-lg p-2 text-slate-600 hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 size={15} />
                    </button>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-border-subtle bg-bg-card px-6 py-12 text-center">
                <div className="text-4xl mb-3">📂</div>
                <p className="text-slate-400 text-sm">No projects yet — upload a dataset to get started</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        {stats?.recent_activity?.length > 0 && (
          <div className="mt-8">
            <h2 className="font-display text-xl font-semibold text-white mb-4">Recent Activity</h2>
            <div className="rounded-2xl border border-border-subtle bg-bg-card divide-y divide-border-subtle">
              {stats.recent_activity.slice(0, 5).map((log, i) => (
                <div key={i} className="flex items-center justify-between px-5 py-3">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{
                      log.action === "upload" ? "📤" : log.action === "chat" ? "💬" : "📊"
                    }</span>
                    <div>
                      <p className="text-sm font-medium text-slate-300 capitalize">{log.action}</p>
                      <p className="text-xs text-slate-500 truncate max-w-xs">{log.detail}</p>
                    </div>
                  </div>
                  <span className="text-xs text-slate-600">{new Date(log.time).toLocaleTimeString()}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
