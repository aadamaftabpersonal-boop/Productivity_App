import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Code2, Trophy, Target, LogOut, Award, Cpu } from "lucide-react";
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
    <div className="min-h-screen bg-[#070a12] text-slate-100 font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md shadow-cyan-500/20">
              <Cpu size={20} />
            </div>
            <span className="font-heading text-xl font-bold text-white tracking-tight">
              CP Hub
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/80">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wide transition-all ${
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

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 px-3.5 py-2 rounded-xl border border-transparent hover:border-rose-500/20 transition"
          >
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}