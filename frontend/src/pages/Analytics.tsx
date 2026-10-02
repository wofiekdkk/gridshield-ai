import { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import Card from "../components/ui/Card";
import MetricCard from "../components/ui/MetricCard";
import { analyticsAPI } from "../services/api";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6"];

export default function Analytics() {
  const [summary, setSummary] = useState<any>({});
  const [dist, setDist] = useState<any[]>([]);
  const [vuln, setVuln] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      setSummary(await analyticsAPI.summary());
      setDist(await analyticsAPI.faultDistribution());
      setVuln(await analyticsAPI.vulnerable());
    };
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Analytics</h1>
        <p className="text-sm text-grid-muted">System performance and historical insights</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Total Faults" value={summary.total_faults || 0} />
        <MetricCard label="Recovered" value={summary.recovered_faults || 0} color="success" />
        <MetricCard label="Recovery Rate" value={(summary.recovery_success_rate || 0).toFixed(1)} unit="%" color="success" />
        <MetricCard label="Avg Cascade Risk" value={((summary.average_cascade_risk || 0) * 100).toFixed(1)} unit="%" color="warning" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Fault Distribution">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={dist} dataKey="count" nameKey="fault_type" cx="50%" cy="50%" outerRadius={100} label>
                {dist.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#1a2234", border: "1px solid #2a3447" }} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Most Vulnerable Components">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={vuln} layout="vertical" margin={{ left: 80 }}>
              <CartesianGrid stroke="#2a3447" />
              <XAxis type="number" stroke="#9ca3af" />
              <YAxis type="category" dataKey="component_id" stroke="#9ca3af" width={80} fontSize={10} />
              <Tooltip contentStyle={{ background: "#1a2234", border: "1px solid #2a3447" }} />
              <Bar dataKey="fault_count" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
