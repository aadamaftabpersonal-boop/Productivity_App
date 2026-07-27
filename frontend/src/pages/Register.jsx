import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Terminal, Lock, Mail, User as UserIcon, ArrowRight } from "lucide-react";

export default function Register() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form.email, form.password, form.full_name);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background Glowing Orbs */}
      <div className="absolute top-1/4 right-1/3 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-mono mb-3">
            <Terminal size={14} /> Join CP Hub Diagnostic Platform
          </div>
          <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
            Create Account
          </h1>
          <p className="text-slate-400 text-sm mt-1 font-sans">
            Start tracking your code mastery & empirical complexity growth
          </p>
        </div>

        {/* Form Card */}
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5 border-violet-500/20 shadow-2xl">
          {error && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Full Name
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Alex Mercer"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className="code-editor h-12 text-sm pl-10"
              />
              <UserIcon className="absolute left-3.5 top-3.5 text-slate-500" size={18} />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <input
                type="email"
                required
                placeholder="alex@domain.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="code-editor h-12 text-sm pl-10"
              />
              <Mail className="absolute left-3.5 top-3.5 text-slate-500" size={18} />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="code-editor h-12 text-sm pl-10"
              />
              <Lock className="absolute left-3.5 top-3.5 text-slate-500" size={18} />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center text-base py-3 mt-2 bg-gradient-to-r from-violet-600 to-cyan-500"
          >
            {loading ? "Creating Profile..." : (
              <>
                Create CP Hub Account <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6 font-sans">
          Already registered?{" "}
          <Link to="/login" className="text-violet-400 font-semibold hover:underline">
            Sign in here
          </Link>
        </p>
      </div>
    </div>
  );
}