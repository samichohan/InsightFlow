import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Mail, Lock, User, UserPlus } from "lucide-react";
import { authApi } from "../lib/api";
import { Button, ErrorAlert } from "../components/UI";

export default function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", full_name: "", password: "", confirm: "" });
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) return setError("Passwords do not match");
    if (form.password.length < 8) return setError("Password must be at least 8 characters");
    setLoading(true); setError("");
    try {
      const data = await authApi.signup({
        email: form.email, username: form.username,
        full_name: form.full_name, password: form.password,
      });
      setSuccess("Account created! Check your email to verify, or use the token below for dev mode.");
      setTimeout(() => navigate("/login"), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-blue to-accent-violet text-3xl">🧠</div>
          <h1 className="font-display text-2xl font-bold text-white">Create Your Account</h1>
          <p className="mt-1 text-sm text-slate-400">Join AI Data Analyst Pro — 100% Free</p>
        </div>

        <div className="rounded-2xl border border-border-subtle bg-bg-card p-8">
          {success ? (
            <div className="text-center">
              <div className="text-5xl mb-4">✅</div>
              <h3 className="font-display text-lg font-semibold text-white mb-2">Account Created!</h3>
              <p className="text-sm text-slate-400">{success}</p>
              <p className="text-xs text-slate-500 mt-2">Redirecting to login…</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <ErrorAlert message={error} />

              {[
                { key: "full_name", label: "Full Name", placeholder: "John Doe", icon: <User size={16} />, type: "text", required: false },
                { key: "username", label: "Username", placeholder: "johndoe", icon: <User size={16} />, type: "text", required: true },
                { key: "email", label: "Email", placeholder: "you@example.com", icon: <Mail size={16} />, type: "email", required: true },
              ].map(f => (
                <div key={f.key}>
                  <label className="mb-1.5 block text-sm font-medium text-slate-300">{f.label}</label>
                  <div className="relative">
                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">{f.icon}</span>
                    <input
                      type={f.type} required={f.required}
                      value={form[f.key]} onChange={set(f.key)}
                      placeholder={f.placeholder}
                      className="w-full rounded-xl border border-border-subtle bg-bg-raised pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-accent-blue focus:outline-none"
                    />
                  </div>
                </div>
              ))}

              {["password", "confirm"].map(k => (
                <div key={k}>
                  <label className="mb-1.5 block text-sm font-medium text-slate-300">
                    {k === "password" ? "Password" : "Confirm Password"}
                  </label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={show ? "text" : "password"} required
                      value={form[k]} onChange={set(k)}
                      placeholder="••••••••"
                      className="w-full rounded-xl border border-border-subtle bg-bg-raised pl-10 pr-10 py-2.5 text-sm text-white placeholder-slate-500 focus:border-accent-blue focus:outline-none"
                    />
                    {k === "confirm" && (
                      <button type="button" onClick={() => setShow(!show)} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500">
                        {show ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <Button type="submit" loading={loading} icon={<UserPlus size={16} />} className="w-full">
                Create Account
              </Button>
            </form>
          )}

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link to="/login" className="text-accent-blue hover:underline font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
