import { useEffect, useState } from "react";
import { Circle, Calendar } from "lucide-react";
import { wsClient } from "../../services/websocket";

export default function TopBar() {
  const [connected, setConnected] = useState(false);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const unsub = wsClient.subscribe(() => setConnected(true));
    const timer = setInterval(() => setTime(new Date()), 1000);
    const connCheck = setInterval(() => setConnected(wsClient.isConnected()), 2000);
    return () => { unsub(); clearInterval(timer); clearInterval(connCheck); };
  }, []);

  const today = new Date();
  const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1);
  const fmt = (d: Date) => d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

  return (
    <header className="h-14 bg-white border-b border-gp-border flex items-center justify-between px-6 shadow-soft">
      <div>
        <h2 className="text-sm font-bold text-gp-text">AI Insights</h2>
        <p className="text-[11px] text-gp-muted">Forecasting, anomaly detection and actionable recommendations</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 border border-gp-border rounded-lg text-xs text-gp-muted">
          <Calendar className="w-3.5 h-3.5" />
          <span className="font-medium">{fmt(today)} – {fmt(tomorrow)}</span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-50 border border-gp-border">
          <Circle className={`w-2 h-2 fill-current ${connected ? "text-gp-success" : "text-gp-warning"}`} />
          <span className={`text-[10px] font-semibold ${connected ? "text-gp-success" : "text-gp-warning"}`}>
            {connected ? "LIVE" : "..."}
          </span>
        </div>
        <div className="text-xs text-gp-muted font-mono">{time.toLocaleTimeString()}</div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
          GS
        </div>
      </div>
    </header>
  );
}
