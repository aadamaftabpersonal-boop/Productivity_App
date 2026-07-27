import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Code2, Trophy, Target, LogOut, Terminal } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/reviewer", label: "Reviewer", icon: Code2 },
  { to: "/contests", label: "Contests", icon: Trophy },
  { to: "/weakness", label: "Weakness", icon: Target },
  { to: "/leaderboard", label: "Leaderboard", icon: Trophy },
];


export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-panel/60 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
          <div className="flex items-center gap-2 font-mono text-sm text-tier-green">
            <Terminal size={16} strokeWidth={2} />
            portal
          </div>
          <nav className="flex gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition ${
                    isActive ? "bg-tier-blue/15 text-tier-blue" : "text-muted hover:text-text hover:bg-border/30"
                  }`
                }
              >
                <Icon size={15} strokeWidth={2} />
                {label}
              </NavLink>
            ))}
          </nav>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-sm text-muted hover:text-tier-red transition font-mono"
          >
            <LogOut size={14} />
            logout
          </button>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}