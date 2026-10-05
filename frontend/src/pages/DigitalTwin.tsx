import { useEffect, useState } from "react";
import { AlertTriangle, ShieldCheck, Zap, Activity, Cpu, Server, Radio, HardDrive } from "lucide-react";
import { gridAPI, faultAPI, recoveryAPI } from "../services/api";
import type { GridComponent, FaultEvent } from "../types";
import { useEventStore } from "../store/eventStore";

interface LineDef { id: string; name: string; aliases: string[]; x1: number; y1: number; x2: number; y2: number; cx: number; cy: number; }

const LINES: LineDef[] = [
  { id: "L1", name: "Transmission Feeder L1", aliases: ["LINE_1", "L1", "LINE_L1", "LINE_0"], x1: 400, y1: 80, x2: 200, y2: 200, cx: 300, cy: 140 },
  { id: "L2", name: "Transmission Feeder L2", aliases: ["LINE_2", "L2", "LINE_L2", "LINE_1"], x1: 400, y1: 80, x2: 600, y2: 200, cx: 500, cy: 140 },
  { id: "L3", name: "Distribution Feeder L3", aliases: ["LINE_3", "L3", "LINE_L3", "LINE_2"], x1: 200, y1: 200, x2: 120, y2: 340, cx: 160, cy: 270 },
  { id: "L4", name: "Distribution Feeder L4", aliases: ["LINE_4", "L4", "LINE_L4", "LINE_3"], x1: 200, y1: 200, x2: 280, y2: 340, cx: 240, cy: 270 },
  { id: "L5", name: "Distribution Feeder L5", aliases: ["LINE_5", "L5", "LINE_L5", "LINE_4"], x1: 600, y1: 200, x2: 520, y2: 340, cx: 560, cy: 270 },
  { id: "L6", name: "Distribution Feeder L6", aliases: ["LINE_6", "L6", "LINE_L6", "LINE_5"], x1: 600, y1: 200, x2: 680, y2: 340, cx: 640, cy: 270 },
  { id: "L7", name: "Intertie Feeder L7", aliases: ["LINE_7", "L7", "LINE_L7", "LINE_6"], x1: 280, y1: 340, x2: 400, y2: 440, cx: 340, cy: 390 },
];

export default function DigitalTwin() {
  const [components, setComponents] = useState<GridComponent[]>([]);
  const [activeFaults, setActiveFaults] = useState<FaultEvent[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [recovering, setRecovering] = useState(false);
  const events = useEventStore((s) => s.events);

  const loadData = async () => {
    try {
      const [comps, faults] = await Promise.all([gridAPI.getComponents().catch(() => []), faultAPI.list(true).catch(() => [])]);
      if (Array.isArray(comps)) setComponents(comps);
      if (Array.isArray(faults)) setActiveFaults(faults);
    } catch (e) {}
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 2500);
    return () => clearInterval(timer);
  }, [events.length]);

  const getFaultFor = (primaryId: string, aliases: string[] = []): FaultEvent | undefined => {
    const candidates = [primaryId, ...aliases].map((s) => s.toUpperCase());
    return activeFaults.find((f) => {
      const target = (f.component_id || "").toUpperCase();
      return candidates.some((c) => target === c || target.includes(c) || c.includes(target));
    });
  };

  const handleAutoRecover = async (faultId: string) => {
    setRecovering(true);
    try { await recoveryAPI.autoRecover(faultId); await loadData(); } 
    catch (e: any) { alert(e.response?.data?.detail || "Recovery failed"); } 
    finally { setRecovering(false); }
  };

  return (
    <div className="space-y-5 h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-5 rounded-xl border border-gp-border shadow-soft">
        <div>
          <h1 className="text-lg font-bold text-gp-text flex items-center gap-2">
            <Activity className="w-5 h-5 text-gp-primary" /> System Topology &amp; Asset Tracking
          </h1>
          <p className="text-xs text-gp-muted mt-0.5">Real-time kinematic digital twin with AI overlay</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-gp-border rounded-lg text-xs font-medium text-gp-muted">
            <Server className="w-3.5 h-3.5" /> Nodes: <span className="font-bold text-gp-text">{components.length || 7}</span>
          </div>
          {activeFaults.length > 0 ? (
            <div className="px-4 py-1.5 bg-red-50 border border-red-200 text-red-600 rounded-lg text-xs font-bold flex items-center gap-2 animate-pulse shadow-sm">
              <AlertTriangle className="w-4 h-4" /> {activeFaults.length} CRITICAL ALERTS
            </div>
          ) : (
            <div className="px-4 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-600 rounded-lg text-xs font-bold flex items-center gap-2 shadow-sm">
              <ShieldCheck className="w-4 h-4" /> SYSTEM STABLE
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-5 flex-1 min-h-[600px]">
        {/* Main SVG Canvas */}
        <div className="xl:col-span-3 bg-white rounded-xl border border-gp-border shadow-soft overflow-hidden relative flex flex-col">
          
          {/* Overlay Tools */}
          <div className="absolute top-4 left-4 flex gap-2 z-10">
            <div className="bg-white/90 backdrop-blur border border-gp-border p-2 rounded-lg shadow-sm flex items-center gap-3 text-[10px] font-semibold text-gp-muted uppercase tracking-wider">
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-gp-primary animate-pulse" /> Active Flow</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-gp-danger" /> Faulted</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-gp-warning" /> Generator</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-gp-teal" /> Critical</span>
            </div>
          </div>

          {activeFaults.length > 0 && (
             <div className="absolute top-4 right-4 z-10 bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-4 max-w-sm">
               <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center shrink-0">⚡</div>
               <div>
                 <div className="text-xs font-bold">{activeFaults[0].fault_type}</div>
                 <div className="text-[10px] opacity-90">{activeFaults[0].component_id} | Risk: {((activeFaults[0].cascade_risk || 0) * 100).toFixed(0)}%</div>
               </div>
               <button onClick={() => handleAutoRecover(activeFaults[0].fault_id)} disabled={recovering} className="px-3 py-1.5 bg-white text-red-600 text-[10px] font-bold rounded shadow-sm hover:bg-red-50 transition shrink-0 disabled:opacity-50">
                 {recovering ? "HEALING" : "AUTO-HEAL"}
               </button>
             </div>
          )}

          {/* SVG Viewport */}
          <div className="flex-1 w-full bg-[#f8fafc] flex items-center justify-center p-4">
            <svg viewBox="0 0 800 520" className="w-full h-full max-h-[700px] select-none">
              <defs>
                <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0f172a" floodOpacity="0.08" />
                </filter>
                <filter id="glowRed" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="glowBlue" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* ---------------- TRANSMISSION LINES ---------------- */}
              {LINES.map((line) => {
                const fault = getFaultFor(line.id, line.aliases);
                const isFaulted = !!fault;
                const isSelected = selected?.component_id === line.id || selected?.component_id === line.aliases[0];

                return (
                  <g key={line.id} onClick={() => setSelected({ component_id: line.aliases[0], component_type: "transmission_line", name: line.name, status: isFaulted ? "FAULT" : "NORMAL", fault })} className="cursor-pointer group">
                    {/* Background Trace */}
                    <line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="#e2eaf2" strokeWidth="8" strokeLinecap="round" />
                    
                    {/* Normal Conductor */}
                    <line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke={isFaulted ? "#ef4444" : isSelected ? "#3b82f6" : "#cbd5e1"} strokeWidth={isFaulted ? "4" : "2"} strokeDasharray={line.id === "L7" ? "6 4" : undefined} className="group-hover:stroke-blue-400 transition-colors" />
                    
                    {/* Animated Flow */}
                    {!isFaulted ? (
                      <line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="#3b82f6" strokeWidth="3" className={line.id === "L7" ? "animate-flow-reverse" : "animate-flow"} opacity="0.8" filter="url(#glowBlue)" />
                    ) : (
                      <line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="#ef4444" strokeWidth="6" className="animate-flow-fault" filter="url(#glowRed)" />
                    )}

                    {/* Floating UI Label */}
                    <g transform={`translate(${line.cx}, ${line.cy})`}>
                      <rect x="-24" y="-12" width="48" height="24" rx="12" fill={isFaulted ? "#fef2f2" : "#ffffff"} stroke={isFaulted ? "#ef4444" : "#e2eaf2"} strokeWidth="1.5" filter="url(#softShadow)" />
                      <text x="0" y="3" textAnchor="middle" className="text-[10px] font-bold" fill={isFaulted ? "#ef4444" : "#64748b"}>{line.id}</text>
                    </g>
                  </g>
                );
              })}

              {/* ---------------- NODES ---------------- */}
              
              {/* Generator */}
              {(() => {
                const fault = getFaultFor("GEN_1", ["GEN", "MAIN GEN"]);
                return (
                  <g onClick={() => setSelected({ component_id: "GEN_1", component_type: "generator", name: "Main Power Plant (150 MW)", status: fault ? "FAULT" : "NORMAL", fault })} className="cursor-pointer">
                    {fault && <circle cx={400} cy={80} r={40} fill="none" stroke="#ef4444" strokeWidth={3} className="pulse-fault" />}
                    <circle cx={400} cy={80} r={28} fill="#ffffff" stroke={fault ? "#ef4444" : "#f59e0b"} strokeWidth={4} filter="url(#softShadow)" />
                    <circle cx={400} cy={80} r={20} fill={fault ? "#ef4444" : "#fcf3c5"} />
                    <text x={400} y={84} textAnchor="middle" className="text-[12px] font-black" fill={fault ? "#ffffff" : "#d97706"}>GEN</text>
                  </g>
                );
              })()}

              {/* Substations */}
              {["SUB_A", "SUB_B"].map((id, i) => {
                const x = i === 0 ? 200 : 600;
                const fault = getFaultFor(id, [id === "SUB_A" ? "SUBSTATION_A" : "SUBSTATION_B"]);
                return (
                  <g key={id} onClick={() => setSelected({ component_id: id, component_type: "substation", name: `Substation ${id}`, status: fault ? "FAULT" : "NORMAL", fault })} className="cursor-pointer">
                    {fault && <rect x={x - 36} y={184} width={72} height={52} rx={12} fill="none" stroke="#ef4444" strokeWidth={3} className="pulse-fault" />}
                    <rect x={x - 28} y={180} width={56} height={40} rx={8} fill="#ffffff" stroke={fault ? "#ef4444" : "#3b82f6"} strokeWidth={3} filter="url(#softShadow)" />
                    <rect x={x - 22} y={186} width={44} height={28} rx={4} fill={fault ? "#ef4444" : "#eff6ff"} />
                    <text x={x} y={203} textAnchor="middle" className="text-[11px] font-black" fill={fault ? "#ffffff" : "#2563eb"}>{id.replace("SUB_", "")}</text>
                  </g>
                );
              })}

              {/* Buses */}
              {[
                { id: "BUS_A1", aliases: ["BUS_0", "BUS_1"], x: 120, y: 340 },
                { id: "BUS_A2", aliases: ["BUS_2", "BUS_3"], x: 280, y: 340 },
                { id: "BUS_B1", aliases: ["BUS_4", "BUS_5"], x: 520, y: 340 },
                { id: "BUS_B2", aliases: ["BUS_6", "BUS_7"], x: 680, y: 340 },
              ].map((b) => {
                const fault = getFaultFor(b.id, b.aliases);
                return (
                  <g key={b.id} onClick={() => setSelected({ component_id: b.id, component_type: "bus", name: `Distribution Bus ${b.id}`, status: fault ? "FAULT" : "NORMAL", fault })} className="cursor-pointer">
                    {fault && <circle cx={b.x} cy={b.y} r={22} fill="none" stroke="#ef4444" strokeWidth={2} className="pulse-fault" />}
                    <circle cx={b.x} cy={b.y} r={16} fill="#ffffff" stroke={fault ? "#ef4444" : "#cbd5e1"} strokeWidth={3} filter="url(#softShadow)" />
                    <circle cx={b.x} cy={b.y} r={8} fill={fault ? "#ef4444" : "#f1f5f9"} />
                    <text x={b.x} y={b.y + 32} textAnchor="middle" className="text-[10px] font-bold" fill="#64748b">{b.id}</text>
                  </g>
                );
              })}

              {/* Critical Load */}
              {(() => {
                const fault = getFaultFor("LOAD_CRIT", ["LOAD_0", "CRIT"]);
                return (
                  <g onClick={() => setSelected({ component_id: "LOAD_CRIT", component_type: "critical_load", name: "Hospital Emergency Load", is_critical: true, status: fault ? "FAULT" : "NORMAL", fault })} className="cursor-pointer">
                    {fault && <rect x={306} y={426} width={68} height={48} rx={10} fill="none" stroke="#ef4444" strokeWidth={3} className="pulse-fault" />}
                    <rect x={310} y={430} width={60} height={40} rx={8} fill="#ffffff" stroke={fault ? "#ef4444" : "#14b8a6"} strokeWidth={3} filter="url(#softShadow)" />
                    <rect x={316} y={436} width={48} height={28} rx={4} fill={fault ? "#ef4444" : "#f0fdfa"} />
                    <text x={340} y={453} textAnchor="middle" className="text-[11px] font-black" fill={fault ? "#ffffff" : "#0d9488"}>CRIT</text>
                    <text x={340} y={485} textAnchor="middle" className="text-[10px] font-bold text-gp-muted">HOSPITAL</text>
                  </g>
                );
              })()}
            </svg>
          </div>
        </div>

        {/* High-End Inspector Panel */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          <div className="bg-white rounded-xl border border-gp-border shadow-soft p-5 flex-1">
            <h3 className="text-sm font-bold text-gp-text flex items-center gap-2 mb-4 border-b border-gp-border pb-3">
              <Cpu className="w-4 h-4 text-gp-primary" /> Asset Inspector
            </h3>
            
            {selected ? (
              <div className="space-y-5">
                {/* Header Profile */}
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${selected.status === "FAULT" ? "bg-red-100 text-red-600" : "bg-blue-100 text-blue-600"}`}>
                    {selected.component_type.includes("line") ? <Activity className="w-5 h-5" /> : <HardDrive className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gp-text">{selected.component_id}</div>
                    <div className="text-[11px] text-gp-muted capitalize mt-0.5">{selected.component_type.replace('_', ' ')}</div>
                  </div>
                </div>

                {/* Health & Status */}
                <div className="p-3 bg-slate-50 rounded-lg border border-gp-border">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-semibold text-gp-text">Asset Health</span>
                    <span className={`text-xs font-bold ${selected.status === "FAULT" ? "text-red-600" : "text-emerald-600"}`}>{selected.status === "FAULT" ? "24%" : "98%"}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden mb-3">
                    <div className={`h-full rounded-full transition-all ${selected.status === "FAULT" ? "bg-red-500 w-[24%]" : "bg-emerald-500 w-[98%]"}`} />
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-gp-muted">Status Code</span>
                    <span className={`font-bold px-2 py-0.5 rounded ${selected.status === "FAULT" ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"}`}>{selected.status}</span>
                  </div>
                </div>

                {/* Fault Diagnostics Card */}
                {selected.fault && (
                  <div className="p-4 bg-white border-2 border-red-200 shadow-sm rounded-lg relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
                    <h4 className="text-xs font-bold text-red-600 flex items-center gap-1.5 mb-2">
                      <Zap className="w-3.5 h-3.5" /> AI Diagnostics Match
                    </h4>
                    <div className="space-y-2 text-[11px]">
                      <div className="flex justify-between"><span className="text-gp-muted">Classification</span><span className="font-semibold text-gp-text">{selected.fault.fault_type}</span></div>
                      <div className="flex justify-between"><span className="text-gp-muted">Cascade Risk</span><span className="font-bold text-amber-600">{((selected.fault.cascade_risk || 0) * 100).toFixed(0)}%</span></div>
                      <div className="flex justify-between"><span className="text-gp-muted">Confidence</span><span className="font-bold text-blue-600">{((selected.fault.confidence || 0) * 100).toFixed(1)}%</span></div>
                    </div>
                    <button onClick={() => handleAutoRecover(selected.fault.fault_id)} disabled={recovering} className="w-full mt-3 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 py-1.5 rounded-md font-bold text-[10px] uppercase transition disabled:opacity-50">
                      {recovering ? "Processing..." : "Generate Action Plan"}
                    </button>
                  </div>
                )}

                {/* Simulated Live Telemetry */}
                <div>
                  <h4 className="text-[10px] font-bold text-gp-muted uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Radio className="w-3 h-3" /> Live Telemetry
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-slate-50 p-2 rounded border border-gp-border text-center">
                      <div className="text-[9px] text-gp-muted">VOLTAGE</div>
                      <div className={`text-xs font-bold ${selected.status === "FAULT" ? "text-red-600" : "text-gp-text"}`}>{selected.status === "FAULT" ? "184.2 V" : "230.1 V"}</div>
                    </div>
                    <div className="bg-slate-50 p-2 rounded border border-gp-border text-center">
                      <div className="text-[9px] text-gp-muted">CURRENT</div>
                      <div className={`text-xs font-bold ${selected.status === "FAULT" ? "text-red-600" : "text-gp-text"}`}>{selected.status === "FAULT" ? "210.4 A" : "84.2 A"}</div>
                    </div>
                    <div className="bg-slate-50 p-2 rounded border border-gp-border text-center">
                      <div className="text-[9px] text-gp-muted">TEMP</div>
                      <div className={`text-xs font-bold ${selected.status === "FAULT" ? "text-amber-600" : "text-gp-text"}`}>{selected.status === "FAULT" ? "88.4 °C" : "42.1 °C"}</div>
                    </div>
                    <div className="bg-slate-50 p-2 rounded border border-gp-border text-center">
                      <div className="text-[9px] text-gp-muted">FREQ</div>
                      <div className="text-xs font-bold text-gp-text">49.98 Hz</div>
                    </div>
                  </div>
                </div>

              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center px-4 pb-10 opacity-60">
                <HardDrive className="w-10 h-10 text-gp-muted mb-3" />
                <div className="text-xs font-bold text-gp-text">No Asset Selected</div>
                <div className="text-[10px] text-gp-muted mt-1">Select any node or conductor trace on the schematic to view real-time diagnostics.</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
