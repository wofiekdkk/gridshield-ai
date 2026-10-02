import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import { analyticsAPI } from "../services/api";

export default function History() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => setEvents(await analyticsAPI.recentEvents(100));
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  const sevColor = (s: string) => ({
    INFO: "text-grid-accent", WARNING: "text-grid-warning",
    CRITICAL: "text-grid-danger", RECOVERY: "text-grid-recovery",
  }[s] || "text-grid-muted");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Event History</h1>
        <p className="text-sm text-grid-muted">Full chronological system event timeline</p>
      </div>

      <Card>
        <div className="space-y-1 max-h-[600px] overflow-y-auto font-mono text-xs">
          {events.map((e) => (
            <div key={e.id} className="flex gap-3 py-2 px-2 hover:bg-grid-bg border-b border-grid-border/30">
              <span className="text-grid-muted shrink-0 w-40">{new Date(e.timestamp).toLocaleString()}</span>
              <span className={`font-bold w-24 shrink-0 ${sevColor(e.severity)}`}>{e.severity}</span>
              <span className="text-grid-accent w-40 shrink-0">{e.event_type}</span>
              <span className="text-grid-text">{e.message}</span>
            </div>
          ))}
          {events.length === 0 && <div className="text-grid-muted text-center py-8">No events</div>}
        </div>
      </Card>
    </div>
  );
}
