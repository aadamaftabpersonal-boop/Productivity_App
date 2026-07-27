import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Code2, Trophy, Target, LogOut, Terminal, Award, Cpu, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/reviewer", label: "AST Reviewer", icon: Code2 },
  { to: "/contests", label: "Contests", icon: Trophy },
  { to: "/weakness", label: "Weakness Signal", icon: Target },
  { to: "/leaderboard", label: "Hall of Fame", icon: Award },
];

export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#070913] text-slate-100 font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-[#0b0f1d]/90 backdrop-blur-2xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          {/* Logo & Status Badge */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5 font-heading text-xl font-bold text-white tracking-tight cursor-pointer" onClick={() => navigate('/dashboard')}>
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/25">
                <Cpu size={20} />
              </div>
              CP Hub <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono">v2.0 PRO</span>
            </div>

            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Engine Online
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800/80">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                    isActive
                      ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/60"
                  }`
                }
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* User Profile & Logout */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
              <ShieldCheck size={14} className="text-cyan-400" />
              <span className="font-mono">AST Verified</span>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 px-3.5 py-2 rounded-xl border border-transparent hover:border-rose-500/20 transition"
            >
              <LogOut size={15} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}