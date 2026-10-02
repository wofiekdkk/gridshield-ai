import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import StatusBadge from "../components/ui/StatusBadge";
import { faultAPI, recoveryAPI } from "../services/api";
import type { FaultEvent } from "../types";
import { useEventStore } from "../store/eventStore";

export default function FaultCenter() {
  const [faults, setFaults] = useState<FaultEvent[]>([]);
  const [selected, setSelected] = useState<FaultEvent | null>(null);
  const events = useEventStore((s) => s.events);

  const load = async () => {
    try {
      const data = await faultAPI.list();
      if (Array.isArray(data)) setFaults(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [events.length]);

  const autoRecover = async (faultId: string) => {
    try {
      await recoveryAPI.autoRecover(faultId);
      load();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Recovery failed");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Fault Center</h1>
        <p className="text-sm text-grid-muted">All detected faults and their status</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title={`Faults (${faults.length})`}>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {faults.map((f) => (
                <div
                  key={f.fault_id}
                  onClick={() => setSelected(f)}
                  className={`p-3 border rounded cursor-pointer transition ${
                    selected?.fault_id === f.fault_id
                      ? "border-grid-accent bg-grid-accent/10"
                      : "border-grid-border hover:border-grid-accent/50 bg-grid-bg"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-sm text-grid-text">{f.fault_id}</span>
                    <StatusBadge status={f.status} />
                  </div>
                  <div className="text-xs text-grid-muted">
                    {f.fault_type} • {f.component_id} • {new Date(f.start_time).toLocaleString()}
                  </div>
                  <div className="flex gap-4 mt-1 text-xs">
                    <span className="text-grid-muted">Confidence: <span className="text-grid-text">{((f.confidence || 0) * 100).toFixed(1)}%</span></span>
                    <span className="text-grid-muted">Cascade: <span className="text-grid-text">{((f.cascade_risk || 0) * 100).toFixed(1)}%</span></span>
                    <span className="text-grid-muted">Severity: <span className="text-grid-text">{((f.severity || 0) * 100).toFixed(0)}%</span></span>
                  </div>
                </div>
              ))}
              {faults.length === 0 && (
                <div className="text-grid-muted text-sm text-center py-8">No faults recorded</div>
              )}
            </div>
          </Card>
        </div>

        <Card title="Fault Detail">
          {selected ? (
            <div className="space-y-4">
              <div>
                <div className="text-xs text-grid-muted">Fault ID</div>
                <div className="font-mono text-grid-text">{selected.fault_id}</div>
              </div>
              <div>
                <div className="text-xs text-grid-muted">Type</div>
                <div className="text-grid-text">{selected.fault_type}</div>
              </div>
              <div>
                <div className="text-xs text-grid-muted">Component</div>
                <div className="text-grid-text">{selected.component_id}</div>
              </div>
              <div>
                <div className="text-xs text-grid-muted">Status</div>
                <StatusBadge status={selected.status} />
              </div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-grid-bg p-2 rounded">
                  <div className="text-xs text-grid-muted">Confidence</div>
                  <div className="text-lg font-bold text-grid-accent">{((selected.confidence || 0) * 100).toFixed(0)}%</div>
                </div>
                <div className="bg-grid-bg p-2 rounded">
                  <div className="text-xs text-grid-muted">Cascade</div>
                  <div className="text-lg font-bold text-grid-warning">{((selected.cascade_risk || 0) * 100).toFixed(0)}%</div>
                </div>
                <div className="bg-grid-bg p-2 rounded">
                  <div className="text-xs text-grid-muted">Severity</div>
                  <div className="text-lg font-bold text-grid-danger">{((selected.severity || 0) * 100).toFixed(0)}%</div>
                </div>
              </div>
              {selected.status !== "RECOVERED" && (
                <button
                  onClick={() => autoRecover(selected.fault_id)}
                  className="w-full bg-grid-accent hover:bg-blue-600 text-white font-semibold py-2 rounded text-sm"
                >
                  Auto-Recover
                </button>
              )}
            </div>
          ) : (
            <div className="text-grid-muted text-sm text-center py-6">Select a fault</div>
          )}
        </Card>
      </div>
    </div>
  );
}
