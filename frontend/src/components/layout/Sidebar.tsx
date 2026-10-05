import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Network, Activity, AlertTriangle,
  Brain, Zap, HeartPulse, Lightbulb, FileText, Settings, LogOut
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/digital-twin", label: "Digital Twin", icon: Network },
  { to: "/sensors", label: "Live Sensors", icon: Activity },
  { to: "/faults", label: "Anomalies", icon: AlertTriangle },
  { to: "/ai", label: "AI Insights", icon: Brain },
  { to: "/recovery", label: "Recommendations", icon: Lightbulb },
  { to: "/simulator", label: "Fault Simulator", icon: Zap },
  { to: "/analytics", label: "Asset Health", icon: HeartPulse },
  { to: "/history", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-56 bg-white border-r border-gp-border flex flex-col h-screen shadow-soft">
      <div className="p-5 border-b border-gp-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-violet-500 rounded-lg flex items-center justify-center shadow-sm">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="font-bold text-gp-text text-sm tracking-tight">GridShield AI</div>
            <div className="text-[10px] text-gp-muted font-medium">AIoT Control System</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 py-3 px-2 overflow-y-auto space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-gp-primarySoft text-gp-primary shadow-sm"
                  : "text-gp-muted hover:text-gp-text hover:bg-slate-50"
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gp-border p-3">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-violet-400 flex items-center justify-center text-white text-xs font-bold">
              {(user?.username || "A")[0].toUpperCase()}
            </div>
            <div>
              <div className="text-xs font-semibold text-gp-text">{user?.username}</div>
              <div className="text-[10px] text-gp-muted">{user?.role}</div>
            </div>
          </div>
          <button onClick={logout} className="p-1.5 hover:bg-slate-100 rounded-md text-gp-muted hover:text-gp-danger transition">
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
