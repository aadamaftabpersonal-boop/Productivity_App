import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Lock, Mail, User as UserIcon, ArrowRight, Cpu } from "lucide-react";

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
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden bg-[#070a12]">
      {/* Background Radial Glow Effects */}
      <div className="absolute top-1/4 right-1/3 w-[500px] h-[500px] bg-violet-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Logo & Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-cyan-500 text-white shadow-lg shadow-violet-500/25 mb-4">
            <Cpu size={24} />
          </div>
          <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
            Create Account
          </h1>
          <p className="text-slate-400 text-sm mt-1.5 font-sans">
            Start tracking code mastery and empirical complexity growth
          </p>
        </div>

        {/* Centered Glass Form Card */}
        <form onSubmit={handleSubmit} className="saas-card p-8 space-y-5 border-violet-500/30">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Full Name
            </label>
            <div className="relative">
              <UserIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={18} />
              <input
                type="text"
                placeholder="Alex Mercer"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className="saas-input h-12 pl-11 pr-4"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={18} />
              <input
                type="email"
                required
                placeholder="alex@domain.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="saas-input h-12 pl-11 pr-4"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={18} />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="saas-input h-12 pl-11 pr-4"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center text-sm py-3.5 mt-2 bg-gradient-to-r from-violet-600 to-cyan-500"
          >
            {loading ? "Creating Account..." : (
              <>
                Create CP Hub Account <ArrowRight size={16} />
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