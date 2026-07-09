import { Link, useNavigate } from "react-router-dom";
import { LogOut, LayoutDashboard, ChevronDown } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <header className="sticky top-0 z-30 border-b border-border-subtle bg-bg-base/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent-blue to-accent-violet text-xl">🧠</div>
          <div>
            <p className="font-display text-base font-bold leading-none text-white">AI Data Analyst</p>
            <p className="text-xs text-slate-500">Pro Platform</p>
          </div>
        </Link>
        {user && (
          <div className="relative">
            <button onClick={() => setOpen(!open)} className="flex items-center gap-2.5 rounded-xl border border-border-subtle bg-bg-card px-4 py-2 hover:border-border-glow transition-colors">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-accent-blue/20 to-accent-violet/20 text-sm font-bold text-accent-blue">
                {user.username?.[0]?.toUpperCase() || "U"}
              </div>
              <span className="font-medium text-sm text-slate-300">{user.username}</span>
              <ChevronDown size={14} className="text-slate-500" />
            </button>
            {open && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-border-subtle bg-bg-card shadow-xl z-50">
                <div className="p-2">
                  <p className="px-3 py-1.5 text-xs text-slate-500">{user.email}</p>
                  <Link to="/dashboard" onClick={() => setOpen(false)} className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-bg-raised">
                    <LayoutDashboard size={15} /> Dashboard
                  </Link>
                  <button onClick={handleLogout} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-rose-400 hover:bg-rose-500/10">
                    <LogOut size={15} /> Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
