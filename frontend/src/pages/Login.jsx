import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Lock, Mail, ArrowRight, Cpu } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your email and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden bg-[#070a12]">
      {/* Background Radial Glow Effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-violet-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Logo & Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25 mb-4">
            <Cpu size={24} />
          </div>
          <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
            Welcome Back
          </h1>
          <p className="text-slate-400 text-sm mt-1.5 font-sans">
            Sign in to track code weaknesses and AST analysis
          </p>
        </div>

        {/* Centered Glass Form Card */}
        <form onSubmit={handleSubmit} className="saas-card p-8 space-y-5 border-cyan-500/30">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={18} />
              <input
                type="email"
                required
                placeholder="me@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="saas-input h-12 pl-11 pr-4"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center text-sm py-3.5 mt-2"
          >
            {loading ? "Authenticating..." : (
              <>
                Sign In to Engine <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6 font-sans">
          Don't have an account?{" "}
          <Link to="/register" className="text-cyan-400 font-semibold hover:underline">
            Create free account
          </Link>
        </p>
      </div>
    </div>
  );
}