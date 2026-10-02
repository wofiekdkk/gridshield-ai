import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Network, Activity, AlertTriangle,
  Brain, Wrench, Zap, BarChart3, History, Settings, LogOut
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/digital-twin", label: "Digital Twin", icon: Network },
  { to: "/sensors", label: "Live Sensors", icon: Activity },
  { to: "/faults", label: "Fault Center", icon: AlertTriangle },
  { to: "/ai", label: "AI Diagnostics", icon: Brain },
  { to: "/recovery", label: "Recovery Center", icon: Wrench },
  { to: "/simulator", label: "Fault Simulator", icon: Zap },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/history", label: "History", icon: History },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-60 bg-grid-panel border-r border-grid-border flex flex-col h-screen">
      <div className="p-6 border-b border-grid-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-grid-accent rounded flex items-center justify-center shadow-sm">
            <Zap className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <div className="font-bold text-grid-text tracking-wide text-sm leading-tight uppercase">GridShield</div>
            <div className="text-[10px] text-grid-muted font-mono tracking-widest leading-none mt-0.5">MEMBER SYSTEM</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 py-4 overflow-y-auto space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-2.5 text-xs tracking-wider uppercase transition-all ${
                isActive
                  ? "bg-grid-card text-grid-accent border-r-2 border-grid-accent font-semibold shadow-sm"
                  : "text-grid-muted hover:text-grid-text hover:bg-grid-card/40"
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-grid-border p-4 bg-grid-panel/50">
        <div className="flex items-center justify-between">
          <div className="pl-2">
            <div className="text-xs font-bold text-grid-text uppercase">{user?.username}</div>
            <div className="text-[10px] text-grid-muted font-mono tracking-wider">{user?.role}</div>
          </div>
          <button
            onClick={logout}
            className="p-2 hover:bg-grid-card rounded text-grid-muted hover:text-grid-danger transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
