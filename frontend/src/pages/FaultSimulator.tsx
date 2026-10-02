import { useState, useEffect } from "react";
import { Zap, RotateCcw, AlertTriangle } from "lucide-react";
import Card from "../components/ui/Card";
import { faultAPI, gridAPI } from "../services/api";

const faultTypes = [
  "TRANSMISSION_LINE_FAILURE", "LINE_OVERLOAD", "TRANSFORMER_OVERLOAD",
  "TRANSFORMER_FAILURE", "VOLTAGE_DROP", "OVERVOLTAGE",
  "FREQUENCY_DISTURBANCE", "GENERATOR_FAILURE", "BREAKER_FAILURE",
  "SWITCH_FAILURE", "SENSOR_FAILURE", "COMMUNICATION_FAILURE",
  "SUDDEN_LOAD_INCREASE", "RENEWABLE_GENERATION_DROP",
];

export default function FaultSimulator() {
  const [components, setComponents] = useState<any[]>([]);
  const [componentId, setComponentId] = useState("LINE_7");
  const [faultType, setFaultType] = useState("TRANSMISSION_LINE_FAILURE");
  const [severity, setSeverity] = useState(0.85);
  const [duration, setDuration] = useState(60);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    gridAPI.getComponents().then(setComponents).catch(() => {});
  }, []);

  const inject = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await faultAPI.inject({
        component_id: componentId, fault_type: faultType, severity, duration,
      });
      setResult({ success: true, data: res });
    } catch (e: any) {
      setResult({ success: false, error: e.response?.data?.detail || "Injection failed" });
    } finally { setLoading(false); }
  };

  const reset = async () => {
    try {
      await faultAPI.reset();
      setResult({ success: true, message: "All faults reset" });
    } catch (e: any) {
      setResult({ success: false, error: "Reset failed" });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Fault Simulator</h1>
        <p className="text-sm text-grid-muted">Inject faults into the virtual grid</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Inject Fault">
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-grid-muted mb-1">Component</label>
              <select
                value={componentId}
                onChange={(e) => setComponentId(e.target.value)}
                className="w-full bg-grid-bg border border-grid-border rounded px-3 py-2 text-grid-text"
              >
                {components.map((c) => (
                  <option key={c.component_id} value={c.component_id}>
                    {c.component_id} ({c.component_type})
                  </option>
                ))}
                {components.length === 0 && <option>LINE_7</option>}
              </select>
            </div>

            <div>
              <label className="block text-xs text-grid-muted mb-1">Fault Type</label>
              <select
                value={faultType}
                onChange={(e) => setFaultType(e.target.value)}
                className="w-full bg-grid-bg border border-grid-border rounded px-3 py-2 text-grid-text"
              >
                {faultTypes.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-grid-muted mb-1">
                Severity: <span className="text-grid-text font-bold">{(severity * 100).toFixed(0)}%</span>
              </label>
              <input
                type="range" min={0.1} max={1} step={0.05}
                value={severity}
                onChange={(e) => setSeverity(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-xs text-grid-muted mb-1">Duration (seconds)</label>
              <input
                type="number" value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full bg-grid-bg border border-grid-border rounded px-3 py-2 text-grid-text"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={inject}
                disabled={loading}
                className="flex-1 bg-grid-danger hover:bg-red-600 text-white font-semibold py-2 rounded flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                {loading ? "Injecting..." : "INJECT FAULT"}
              </button>
              <button
                onClick={reset}
                className="bg-grid-card border border-grid-border hover:border-grid-accent text-grid-text px-4 py-2 rounded flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" /> Reset
              </button>
            </div>
          </div>
        </Card>

        <Card title="Result">
          {result ? (
            result.success ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-grid-success">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-semibold">Fault Injected Successfully</span>
                </div>
                {result.data && (
                  <>
                    <div className="text-sm text-grid-muted">Fault ID: <span className="font-mono text-grid-text">{result.data.fault_id}</span></div>
                    <div className="text-sm text-grid-muted">Status: <span className="text-grid-text">{result.data.status}</span></div>
                    <div className="text-sm text-grid-muted">Confidence: <span className="text-grid-text">{((result.data.confidence || 0) * 100).toFixed(1)}%</span></div>
                    <div className="text-sm text-grid-muted">Cascade Risk: <span className="text-grid-text">{((result.data.cascade_risk || 0) * 100).toFixed(1)}%</span></div>
                    <div className="mt-3 p-2 bg-grid-accent/10 text-grid-accent text-xs rounded">
                      AI pipeline executed. Check Recovery Center for plans.
                    </div>
                  </>
                )}
                {result.message && <div className="text-grid-text text-sm">{result.message}</div>}
              </div>
            ) : (
              <div className="text-grid-danger text-sm">{result.error}</div>
            )
          ) : (
            <div className="text-grid-muted text-sm text-center py-8">
              Configure parameters and inject a fault to see results
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
