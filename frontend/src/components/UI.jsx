/**
 * components/UI.jsx — All reusable base UI components
 */

import { Loader2 } from "lucide-react";

// ── Button ────────────────────────────────────────────────────────────────────
const VARIANTS = {
  primary: "bg-gradient-to-r from-accent-blue to-accent-violet text-bg-base hover:brightness-110 glow-blue",
  secondary: "bg-bg-raised border border-border-glow text-slate-200 hover:border-accent-blue/50",
  success: "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:brightness-110 glow-green",
  danger: "bg-gradient-to-r from-rose-500 to-rose-600 text-white hover:brightness-110",
  ghost: "bg-transparent text-slate-400 hover:text-white hover:bg-bg-raised",
};

export function Button({ children, variant = "primary", loading, disabled, icon, className = "", size = "md", ...props }) {
  const sizes = { sm: "px-3 py-1.5 text-xs", md: "px-5 py-2.5 text-sm", lg: "px-6 py-3 text-base" };
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold
                  transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-40
                  ${sizes[size]} ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : icon}
      {children}
    </button>
  );
}

// ── Panel ─────────────────────────────────────────────────────────────────────
export function Panel({ title, subtitle, action, children, className = "" }) {
  return (
    <div className={`flex flex-col rounded-2xl border border-border-subtle bg-bg-card shadow-lg animate-fade-up ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between border-b border-border-subtle px-6 py-4">
          <div>
            {title && <h3 className="font-display text-lg font-semibold text-white">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      <div className="min-h-0 flex-1 p-6">{children}</div>
    </div>
  );
}

// ── StatCard ──────────────────────────────────────────────────────────────────
const ACCENT_COLORS = {
  blue: "text-accent-blue",
  green: "text-accent-green",
  amber: "text-accent-amber",
  rose: "text-rose-400",
  violet: "text-accent-violet",
  pink: "text-accent-pink",
};

export function StatCard({ label, value, suffix = "", accent = "blue", icon, change }) {
  return (
    <div className="rounded-2xl border border-border-subtle bg-bg-card px-5 py-4 animate-fade-up">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</span>
        {icon && <span className="text-slate-600 text-lg">{icon}</span>}
      </div>
      <p className={`font-mono text-3xl font-semibold ${ACCENT_COLORS[accent]}`}>
        {value ?? "—"}
        {suffix && <span className="text-base text-slate-500 ml-1">{suffix}</span>}
      </p>
      {change && (
        <div className={`mt-2 flex items-center gap-1 text-xs ${
          change.direction === "up" ? "text-emerald-400" : change.direction === "down" ? "text-rose-400" : "text-slate-500"
        }`}>
          <span>{change.direction === "up" ? "↑" : change.direction === "down" ? "↓" : "→"}</span>
          <span>{change.percent}% {change.label}</span>
        </div>
      )}
    </div>
  );
}

// ── Badge ─────────────────────────────────────────────────────────────────────
const BADGE_COLORS = {
  blue: "text-sky-300 bg-sky-500/10 border-sky-500/30",
  green: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  amber: "text-amber-300 bg-amber-500/10 border-amber-500/30",
  rose: "text-rose-300 bg-rose-500/10 border-rose-500/30",
  violet: "text-violet-300 bg-violet-500/10 border-violet-500/30",
  pink: "text-pink-300 bg-pink-500/10 border-pink-500/30",
};

export function Badge({ children, color = "blue" }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 font-mono text-xs font-semibold ${BADGE_COLORS[color]}`}>
      {children}
    </span>
  );
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
export function Skeleton({ className = "" }) {
  return <div className={`skeleton rounded-xl ${className}`} />;
}

export function SkeletonGrid({ cols = 4, height = "h-24" }) {
  return (
    <div className={`grid grid-cols-${cols} gap-4`}>
      {[...Array(cols)].map((_, i) => <Skeleton key={i} className={height} />)}
    </div>
  );
}

// ── Error Alert ───────────────────────────────────────────────────────────────
export function ErrorAlert({ message }) {
  if (!message) return null;
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
      {message}
    </div>
  );
}

// ── Empty State ───────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-5xl mb-4">{icon}</div>}
      <h3 className="font-display text-lg font-semibold text-white mb-2">{title}</h3>
      {description && <p className="text-slate-500 text-sm mb-6 max-w-xs">{description}</p>}
      {action}
    </div>
  );
}
