import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-mono text-tier-green text-sm mb-1">$ auth --register</div>
          <h1 className="font-mono text-2xl font-bold">Create account</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-panel border border-border rounded-lg p-6 space-y-4">
          {error && (
            <div className="text-tier-red text-sm bg-tier-red/10 border border-tier-red/30 rounded px-3 py-2">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm text-muted mb-1.5">Full name</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full bg-base border border-border rounded px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-tier-blue/50"
            />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1.5">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full bg-base border border-border rounded px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-tier-blue/50"
            />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1.5">Password</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full bg-base border border-border rounded px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-tier-blue/50"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-tier-blue text-white font-medium rounded px-4 py-2.5 hover:opacity-90 disabled:opacity-50 transition"
          >
            {loading ? "Creating..." : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-muted mt-4">
          Already have an account? <Link to="/login" className="text-tier-blue hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}