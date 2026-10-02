import { useEffect, useState } from "react";
import { Circle, Activity } from "lucide-react";
import { wsClient } from "../../services/websocket";

export default function TopBar() {
  const [connected, setConnected] = useState(false);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const unsub = wsClient.subscribe(() => setConnected(true));
    const timer = setInterval(() => setTime(new Date()), 1000);
    const connCheck = setInterval(() => {
      setConnected(wsClient.isConnected());
    }, 2000);
    return () => {
      unsub();
      clearInterval(timer);
      clearInterval(connCheck);
    };
  }, []);

  return (
    <header className="h-14 bg-grid-card border-b border-grid-border flex items-center justify-between px-6 select-none shadow-sm">
      <div className="flex items-center gap-3">
        <Activity className="w-4 h-4 text-grid-accent" />
        <span className="text-xs tracking-wider font-semibold text-grid-text uppercase">
          Autonomous Control Station <span className="text-[10px] text-grid-muted font-mono ml-2 font-normal">v1.0.0 [LINEN THEME]</span>
        </span>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1 rounded bg-[#f7f5f0] border border-grid-border">
          <Circle className={`w-2 h-2 fill-current ${connected ? "text-grid-success" : "text-grid-danger"}`} />
          <span className="text-[10px] font-bold tracking-widest font-mono text-grid-text uppercase">
            {connected ? "TELEMETRY ON" : "CONNECTING"}
          </span>
        </div>
        <div className="text-grid-muted font-mono text-xs hidden sm:block">
          {time.toLocaleTimeString()} UTC
        </div>
      </div>
    </header>
  );
}
