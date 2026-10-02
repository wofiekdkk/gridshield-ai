import { useEffect, useState } from "react";
import { CheckCircle, XCircle } from "lucide-react";
import Card from "../components/ui/Card";
import { recoveryAPI } from "../services/api";
import { useEventStore } from "../store/eventStore";
import type { RecoveryPlan } from "../types";

export default function RecoveryCenter() {
  const [plans, setPlans] = useState<RecoveryPlan[]>([]);
  const events = useEventStore((s) => s.events);

  const load = async () => {
    try {
      const res = await recoveryAPI.listPlans();
      if (Array.isArray(res)) setPlans(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [events.length]);

  const execute = async (planId: string) => {
    try {
      await recoveryAPI.execute(planId);
      load();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Execution failed");
    }
  };

  const grouped = plans.reduce((acc: Record<string, RecoveryPlan[]>, p) => {
    (acc[p.fault_id] = acc[p.fault_id] || []).push(p);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Recovery Center</h1>
        <p className="text-sm text-grid-muted">Candidate recovery plans with constraint validation</p>
      </div>

      {Object.keys(grouped).length === 0 && (
        <Card><div className="text-grid-muted text-center py-8">No recovery plans available</div></Card>
      )}

      {Object.entries(grouped).map(([faultId, planList]) => (
        <Card key={faultId} title={`Plans for ${faultId}`}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {planList.map((p) => (
              <div
                key={p.plan_id}
                className={`p-4 border rounded ${
                  p.selected ? "border-grid-success bg-grid-success/5" :
                  p.feasible ? "border-grid-border bg-grid-bg" :
                  "border-grid-danger/50 bg-grid-danger/5"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-sm text-grid-text">{p.plan_id.split("-").pop()}</span>
                  {p.feasible ? (
                    <span className="flex items-center gap-1 text-xs text-grid-success">
                      <CheckCircle className="w-3 h-3" /> FEASIBLE
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-xs text-grid-danger">
                      <XCircle className="w-3 h-3" /> REJECTED
                    </span>
                  )}
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-grid-muted">Restored Load</span>
                    <span className="text-grid-text font-semibold">{(p.restored_load || 0).toFixed(1)} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-grid-muted">Cascade Risk</span>
                    <span className={`font-semibold ${(p.cascade_risk || 0) > 0.5 ? "text-grid-danger" : "text-grid-success"}`}>
                      {((p.cascade_risk || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-grid-muted">Max Loading</span>
                    <span className={`font-semibold ${(p.max_line_loading || 0) > 1 ? "text-grid-danger" : "text-grid-success"}`}>
                      {((p.max_line_loading || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-grid-muted">Score</span>
                    <span className="text-grid-accent font-semibold">{(p.objective_score || 0).toFixed(2)}</span>
                  </div>
                  <div>
                    <div className="text-xs text-grid-muted mb-1">Actions ({p.actions?.length || 0})</div>
                    <div className="text-xs font-mono text-grid-text max-h-20 overflow-y-auto">
                      {p.actions?.map((a: any, i: number) => (
                        <div key={i}>• {a.action} {a.component}</div>
                      ))}
                    </div>
                  </div>
                </div>

                {p.feasible && !p.selected && (
                  <button
                    onClick={() => execute(p.plan_id)}
                    className="w-full mt-3 bg-grid-accent hover:bg-blue-600 text-white py-1.5 rounded text-sm font-semibold"
                  >
                    Execute Plan
                  </button>
                )}
                {p.selected && <div className="mt-3 text-center text-xs text-grid-success">✓ EXECUTED</div>}
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
