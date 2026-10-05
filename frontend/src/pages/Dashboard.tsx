import { useEffect, useState } from "react";
import {
  Activity, Zap, AlertTriangle, TrendingUp, Shield, Gauge,
  Cpu, ArrowUpRight, ArrowRight, Wrench, BatteryCharging
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, ReferenceLine
} from "recharts";
import KPICard from "../components/ui/MetricCard";
import { gridAPI, faultAPI, analyticsAPI, recoveryAPI } from "../services/api";
import { useEventStore } from "../store/eventStore";
import { useNavigate } from "react-router-dom";

const forecastData = [
  { t: "00:00", actual: 3200, forecast: 3100, lo: 2900, hi: 3400 },
  { t: "04:00", actual: 2800, forecast: 2750, lo: 2500, hi: 3000 },
  { t: "08:00", actual: 4100, forecast: 4000, lo: 3700, hi: 4300 },
  { t: "12:00", actual: 4800, forecast: 4700, lo: 4400, hi: 5000 },
  { t: "16:00", actual: 4500, forecast: 4600, lo: 4300, hi: 4900 },
  { t: "18:00", actual: null, forecast: 4850, lo: 4500, hi: 5200 },
  { t: "20:00", actual: null, forecast: 4200, lo: 3900, hi: 4500 },
  { t: "22:00", actual: null, forecast: 3600, lo: 3300, hi: 3900 },
];

export default function Dashboard() {
  const [gridState, setGridState] = useState<any>({ total_generation: 150, total_load: 142.5, max_line_loading: 72.3 });
  const [activeFaults, setActiveFaults] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const events = useEventStore((s) => s.events || []);
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const [state, faults, , pl] = await Promise.all([
        gridAPI.getState().catch(() => ({ total_generation: 150, total_load: 142.5, max_line_loading: 72.3 })),
        faultAPI.list(true).catch(() => []),
        analyticsAPI.summary().catch(() => ({ recovery_success_rate: 100, average_restored_load: 87, total_faults: 0 })),
        recoveryAPI.listPlans().catch(() => []),
      ]);
      if (state) setGridState(state);
      if (Array.isArray(faults)) setActiveFaults(faults);
      if (Array.isArray(pl)) setPlans(pl.filter((p: any) => p.feasible && !p.selected).slice(0, 3));
    } catch {}
  };

  useEffect(() => {
    loadData();
    const t = setInterval(loadData, 3000);
    return () => clearInterval(t);
  }, [events.length]);

  const gen = Number(gridState?.total_generation || 150);
  const load = Number(gridState?.total_load || 142.5);
  const renewable = 32;
  const losses = 2.8;

  const assets = [
    { name: "Transformer T-1", score: 92, type: "transformer" },
    { name: "Transformer T-2", score: activeFaults.length > 0 ? 64 : 76, type: "transformer" },
    { name: "Line L-1102", score: activeFaults.length > 0 ? 55 : 88, type: "line" },
  ];

  const insights = [
    { color: "bg-amber-400", text: activeFaults.length > 0
        ? `High cascade risk (${((activeFaults[0]?.cascade_risk || 0.8) * 100).toFixed(0)}%) on ${activeFaults[0]?.component_id}. Consider alternate routing.`
        : "High demand expected at 18:00 (4,850 MW). Consider additional reserves." },
    { color: "bg-blue-400", text: activeFaults.length > 0
        ? `Unusual load pattern detected near ${activeFaults[0]?.component_id}. Similar to past cascade events.`
        : "Unusual load pattern detected in West Grid. Similar to past 3 events." },
    { color: "bg-emerald-400", text: "Renewable generation likely to increase by 15% due to favorable weather." },
  ];

  const applyPlan = async (planId: string) => {
    try { await recoveryAPI.execute(planId); loadData(); }
    catch (e: any) { alert(e.response?.data?.detail || "Failed"); }
  };

  return (
    <div className="space-y-5">
      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Total Demand"
          value={load.toFixed(0)}
          unit="MW"
          subtitle={`${((load / gen) * 100).toFixed(0)}% of generation`}
          icon={<Activity className="w-4 h-4" />}
          iconBg="bg-violet-50 text-violet-500"
          sparkColor="#8b5cf6"
          sparkData={[3, 5, 4, 7, 6, 8, 7, 9, 8, 10]}
        />
        <KPICard
          label="Predicted Peak"
          value="4,850"
          unit="MW"
          subtitle="at 18:00"
          icon={<TrendingUp className="w-4 h-4" />}
          iconBg="bg-blue-50 text-blue-500"
          sparkColor="#3b82f6"
          sparkData={[5, 4, 6, 5, 8, 7, 9, 10, 11, 12]}
        />
        <KPICard
          label="Renewable Share"
          value={renewable}
          unit="%"
          subtitle="+5% vs last week"
          icon={<BatteryCharging className="w-4 h-4" />}
          iconBg="bg-emerald-50 text-emerald-500"
          donut={renewable}
        />
        <KPICard
          label="Grid Losses"
          value={losses}
          unit="%"
          subtitle="-0.4% improved"
          icon={<Gauge className="w-4 h-4" />}
          iconBg="bg-cyan-50 text-cyan-500"
          sparkColor="#06b6d4"
          sparkData={[10, 9, 8, 9, 7, 6, 7, 5, 4, 3]}
        />
      </div>

      {/* Forecasting + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Load Forecasting Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gp-border p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gp-text">Load Forecasting (Next 24 Hours)</h3>
              <div className="flex items-center gap-4 mt-1.5 text-[10px] text-gp-muted">
                <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-blue-500 inline-block rounded" /> Actual</span>
                <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-emerald-400 inline-block rounded border-dashed" /> Forecast</span>
                <span className="flex items-center gap-1"><span className="w-3 h-2 bg-blue-100 inline-block rounded" /> Confidence Range</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-gp-muted">Predicted Peak</div>
              <div className="text-sm font-bold text-gp-primary">4,850 MW</div>
              <div className="text-[10px] text-gp-muted">18:00</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={forecastData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2eaf2" vertical={false} />
              <XAxis dataKey="t" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} domain={[2000, 6000]} />
              <Tooltip contentStyle={{ background: "#fff", border: "1px solid #e2eaf2", borderRadius: 8, fontSize: 11 }} />
              <Area type="monotone" dataKey="hi" stroke="none" fill="url(#confGrad)" />
              <Area type="monotone" dataKey="lo" stroke="none" fill="#fff" />
              <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2.5} dot={false} connectNulls={false} />
              <Line type="monotone" dataKey="forecast" stroke="#34d399" strokeWidth={2} strokeDasharray="6 3" dot={false} />
              <ReferenceLine x="18:00" stroke="#f59e0b" strokeDasharray="4 2" label={{ value: "Peak", fill: "#f59e0b", fontSize: 10 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Insights Panel */}
        <div className="bg-white rounded-xl border border-gp-border p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-gp-text">Insights</h3>
            <ArrowRight className="w-4 h-4 text-gp-muted" />
          </div>
          <div className="space-y-4">
            {insights.map((ins, i) => (
              <div key={i} className="flex gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${ins.color} mt-1.5 shrink-0`} />
                <div>
                  <div className="text-[11px] font-bold text-gp-text mb-0.5">
                    {i === 0 ? "High demand expected" : i === 1 ? "Unusual load pattern" : "Renewable generation"}
                  </div>
                  <div className="text-[11px] text-gp-muted leading-relaxed">{ins.text}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Anomalies + Asset Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Anomaly Detection */}
        <div className="bg-white rounded-xl border border-gp-border p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-gp-danger" />
              <h3 className="text-sm font-bold text-gp-text">Anomaly Detection</h3>
            </div>
            <button onClick={() => navigate("/faults")} className="text-[11px] text-gp-primary font-semibold hover:underline">View All</button>
          </div>
          {activeFaults.length === 0 ? (
            <div className="text-center py-8">
              <Shield className="w-8 h-8 mx-auto text-gp-success mb-2 opacity-70" />
              <div className="text-xs font-semibold text-gp-text">No anomalies detected</div>
              <div className="text-[10px] text-gp-muted mt-1">All feeders operating within normal parameters</div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-[11px] text-gp-danger font-semibold mb-2">{activeFaults.length} anomalies detected</div>
              {activeFaults.slice(0, 3).map((f, i) => {
                const sev = (f.severity || 0) > 0.7 ? "High" : (f.severity || 0) > 0.4 ? "Medium" : "Low";
                const sevColor = sev === "High" ? "bg-red-50 text-red-600 border-red-200" : sev === "Medium" ? "bg-amber-50 text-amber-600 border-amber-200" : "bg-blue-50 text-blue-600 border-blue-200";
                return (
                  <div key={f.fault_id || i} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-gp-border hover:border-gp-primary/30 transition cursor-pointer" onClick={() => navigate("/faults")}>
                    <div className="flex items-center gap-3">
                      <div className="w-1 h-10 rounded-full bg-gp-danger" />
                      <div>
                        <div className="text-xs font-semibold text-gp-text">{f.fault_type?.replace(/_/g, " ") || "Unknown Anomaly"}</div>
                        <div className="text-[10px] text-gp-muted mt-0.5">{f.component_id} · {new Date(f.start_time).toLocaleTimeString()}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <svg width="50" height="20" viewBox="0 0 50 20">
                        <polyline points="0,15 10,12 20,8 30,5 40,3 50,2" fill="none" stroke="#ef4444" strokeWidth="1.5" />
                      </svg>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${sevColor}`}>{sev}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Asset Health */}
        <div className="bg-white rounded-xl border border-gp-border p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-gp-primary" />
              <h3 className="text-sm font-bold text-gp-text">Asset Health</h3>
            </div>
            <button onClick={() => navigate("/analytics")} className="text-[11px] text-gp-primary font-semibold hover:underline">View All</button>
          </div>
          <div className="space-y-4">
            {assets.map((a) => {
              const barColor = a.score >= 85 ? "bg-gp-success" : a.score >= 70 ? "bg-gp-warning" : "bg-gp-danger";
              return (
                <div key={a.name}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center">
                        {a.type === "transformer" ? <Zap className="w-3.5 h-3.5 text-gp-muted" /> : <Activity className="w-3.5 h-3.5 text-gp-muted" />}
                      </div>
                      <span className="text-xs font-semibold text-gp-text">{a.name}</span>
                    </div>
                    <span className="text-xs font-bold text-gp-text">{a.score}/100</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${barColor} transition-all duration-700`} style={{ width: `${a.score}%` }} />
                  </div>
                  <div className="text-[10px] text-gp-muted mt-1">Health Score</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white rounded-xl border border-gp-border p-5 shadow-soft">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded bg-amber-100 flex items-center justify-center">
              <span className="text-amber-600 text-xs">💡</span>
            </div>
            <h3 className="text-sm font-bold text-gp-text">AI Recommendations</h3>
            <span className="text-[10px] text-gp-muted ml-1">{Math.max(plans.length, 3)} actionable recommendations</span>
          </div>
          <button onClick={() => navigate("/recovery")} className="text-[11px] text-gp-primary font-semibold hover:underline">View All</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Recommendation 1 */}
          <div className="p-4 rounded-xl border border-gp-border bg-slate-50/50 hover:border-gp-primary/30 transition">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
                <ArrowUpRight className="w-3.5 h-3.5 text-blue-500" />
              </div>
              <span className="text-xs font-bold text-gp-text">Redistribute Load</span>
            </div>
            <p className="text-[11px] text-gp-muted leading-relaxed mb-3">
              {activeFaults.length > 0
                ? `Shift load away from ${activeFaults[0]?.component_id} to alternate feeders to reduce cascade risk.`
                : "Shift 120 MW from West Grid to South Substation to reduce overload risk."}
            </p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gp-muted">Confidence <span className="font-bold text-gp-text">92%</span></span>
              <button
                onClick={() => (plans[0] ? applyPlan(plans[0].plan_id) : navigate("/recovery"))}
                className="px-3 py-1 bg-gp-primary hover:bg-blue-600 text-white text-[11px] font-semibold rounded-lg transition"
              >
                Apply
              </button>
            </div>
          </div>

          {/* Recommendation 2 */}
          <div className="p-4 rounded-xl border border-gp-border bg-slate-50/50 hover:border-gp-primary/30 transition">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-lg bg-amber-50 flex items-center justify-center">
                <Wrench className="w-3.5 h-3.5 text-amber-500" />
              </div>
              <span className="text-xs font-bold text-gp-text">Schedule Maintenance</span>
            </div>
            <p className="text-[11px] text-gp-muted leading-relaxed mb-3">
              Plan maintenance for Transformer T-2 within 2 weeks. Health score declining.
            </p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gp-muted">Confidence <span className="font-bold text-gp-text">87%</span></span>
              <button onClick={() => navigate("/analytics")} className="px-3 py-1 bg-white border border-gp-border hover:border-gp-primary text-gp-text text-[11px] font-semibold rounded-lg transition">
                View Plan
              </button>
            </div>
          </div>

          {/* Recommendation 3 */}
          <div className="p-4 rounded-xl border border-gp-border bg-slate-50/50 hover:border-gp-primary/30 transition">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-50 flex items-center justify-center">
                <Shield className="w-3.5 h-3.5 text-emerald-500" />
              </div>
              <span className="text-xs font-bold text-gp-text">Increase Reserve Margin</span>
            </div>
            <p className="text-[11px] text-gp-muted leading-relaxed mb-3">
              Maintain additional 300 MW reserve between 17:00–20:00 for peak demand.
            </p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gp-muted">Confidence <span className="font-bold text-gp-text">78%</span></span>
              <button onClick={() => navigate("/simulator")} className="px-3 py-1 bg-white border border-gp-border hover:border-gp-primary text-gp-text text-[11px] font-semibold rounded-lg transition">
                Simulate
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
