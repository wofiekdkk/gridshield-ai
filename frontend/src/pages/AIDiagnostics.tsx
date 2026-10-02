import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import Card from "../components/ui/Card";
import { aiAPI } from "../services/api";
import { useEventStore } from "../store/eventStore";

export default function AIDiagnostics() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [localizations, setLocalizations] = useState<any[]>([]);
  const events = useEventStore((s) => s.events);

  useEffect(() => {
    const load = async () => {
      setPredictions(await aiAPI.getPredictions());
      setLocalizations(await aiAPI.getLocalizations());
    };
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [events.length]);

  const latest = predictions[0];
  const probData = latest?.probabilities
    ? Object.entries(latest.probabilities).map(([name, value]) => ({ name, value: (value as number) * 100 }))
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">AI Diagnostics</h1>
        <p className="text-sm text-grid-muted">Model predictions, classifications, localizations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Latest Classification">
          {latest ? (
            <>
              <div className="mb-4">
                <div className="text-xs text-grid-muted">Predicted Class</div>
                <div className="text-xl font-bold text-grid-accent">{latest.predicted_class}</div>
                <div className="text-sm text-grid-muted">Confidence: {(latest.confidence * 100).toFixed(1)}%</div>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={probData} layout="vertical" margin={{ left: 100 }}>
                  <CartesianGrid stroke="#2a3447" />
                  <XAxis type="number" stroke="#9ca3af" domain={[0, 100]} />
                  <YAxis type="category" dataKey="name" stroke="#9ca3af" width={100} fontSize={10} />
                  <Tooltip contentStyle={{ background: "#1a2234", border: "1px solid #2a3447" }} />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </>
          ) : <div className="text-grid-muted text-center py-8">No predictions yet</div>}
        </Card>

        <Card title="Localizations">
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {localizations.map((l) => (
              <div key={l.id} className="p-3 bg-grid-bg border border-grid-border rounded">
                <div className="flex justify-between">
                  <span className="font-mono text-sm text-grid-text">{l.predicted_component}</span>
                  <span className="text-xs text-grid-accent">{(l.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="text-xs text-grid-muted">Fault: {l.fault_id}</div>
              </div>
            ))}
            {localizations.length === 0 && <div className="text-grid-muted text-center py-6">No localizations</div>}
          </div>
        </Card>
      </div>

      <Card title="Prediction History">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-grid-muted text-xs uppercase border-b border-grid-border">
              <tr>
                <th className="text-left py-2 px-2">Time</th>
                <th className="text-left py-2 px-2">Fault ID</th>
                <th className="text-left py-2 px-2">Model</th>
                <th className="text-left py-2 px-2">Predicted</th>
                <th className="text-right py-2 px-2">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {predictions.slice(0, 20).map((p) => (
                <tr key={p.id} className="border-b border-grid-border/50">
                  <td className="py-2 px-2 text-grid-muted text-xs">{new Date(p.timestamp).toLocaleTimeString()}</td>
                  <td className="py-2 px-2 font-mono text-xs text-grid-text">{p.fault_id}</td>
                  <td className="py-2 px-2 text-grid-text">{p.model_type}</td>
                  <td className="py-2 px-2 text-grid-accent">{p.predicted_class}</td>
                  <td className="py-2 px-2 text-right text-grid-text">{(p.confidence * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
