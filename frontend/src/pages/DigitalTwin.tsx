import { useEffect, useState } from "react";
import { AlertTriangle, Wrench, ShieldCheck, Zap } from "lucide-react";
import Card from "../components/ui/Card";
import StatusBadge from "../components/ui/StatusBadge";
import { gridAPI, faultAPI, recoveryAPI } from "../services/api";
import type { GridComponent, FaultEvent } from "../types";
import { useEventStore } from "../store/eventStore";

// Line definitions mapping SVG geometry to possible backend component IDs
interface LineDef {
  id: string;
  name: string;
  aliases: string[];
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  labelX: number;
  labelY: number;
  fromNode: string;
  toNode: string;
}

const LINES: LineDef[] = [
  { id: "L1", name: "Transmission Feeder L1", aliases: ["LINE_1", "L1", "LINE_L1", "LINE_0"], x1: 400, y1: 60, x2: 200, y2: 180, labelX: 285, labelY: 110, fromNode: "GEN_1", toNode: "SUB_A" },
  { id: "L2", name: "Transmission Feeder L2", aliases: ["LINE_2", "L2", "LINE_L2", "LINE_1"], x1: 400, y1: 60, x2: 600, y2: 180, labelX: 515, labelY: 110, fromNode: "GEN_1", toNode: "SUB_B" },
  { id: "L3", name: "Distribution Feeder L3", aliases: ["LINE_3", "L3", "LINE_L3", "LINE_2"], x1: 200, y1: 180, x2: 120, y2: 320, labelX: 145, labelY: 250, fromNode: "SUB_A", toNode: "BUS_A1" },
  { id: "L4", name: "Distribution Feeder L4", aliases: ["LINE_4", "L4", "LINE_L4", "LINE_3"], x1: 200, y1: 180, x2: 280, y2: 320, labelX: 255, labelY: 250, fromNode: "SUB_A", toNode: "BUS_A2" },
  { id: "L5", name: "Distribution Feeder L5", aliases: ["LINE_5", "L5", "LINE_L5", "LINE_4"], x1: 600, y1: 180, x2: 520, y2: 320, labelX: 545, labelY: 250, fromNode: "SUB_B", toNode: "BUS_B1" },
  { id: "L6", name: "Distribution Feeder L6", aliases: ["LINE_6", "L6", "LINE_L6", "LINE_5"], x1: 600, y1: 180, x2: 680, y2: 320, labelX: 655, labelY: 250, fromNode: "SUB_B", toNode: "BUS_B2" },
  { id: "L7", name: "Intertie Feeder L7", aliases: ["LINE_7", "L7", "LINE_L7", "LINE_6"], x1: 280, y1: 320, x2: 400, y2: 420, labelX: 330, labelY: 380, fromNode: "BUS_A2", toNode: "LOAD_CRIT" },
];

export default function DigitalTwin() {
  const [components, setComponents] = useState<GridComponent[]>([]);
  const [activeFaults, setActiveFaults] = useState<FaultEvent[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [recovering, setRecovering] = useState(false);
  const events = useEventStore((s) => s.events);

  const loadData = async () => {
    try {
      const [comps, faults] = await Promise.all([
        gridAPI.getComponents().catch(() => []),
        faultAPI.list(true).catch(() => []),
      ]);
      if (Array.isArray(comps)) setComponents(comps);
      if (Array.isArray(faults)) setActiveFaults(faults);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 2500);
    return () => clearInterval(timer);
  }, [events.length]);

  // Helper to check if a component or line is currently faulted
  const getFaultFor = (primaryId: string, aliases: string[] = []): FaultEvent | undefined => {
    const candidates = [primaryId, ...aliases].map((s) => s.toUpperCase());
    return activeFaults.find((f) => {
      const target = (f.component_id || "").toUpperCase();
      return candidates.some((c) => target === c || target.includes(c) || c.includes(target));
    });
  };

  const handleAutoRecover = async (faultId: string) => {
    setRecovering(true);
    try {
      await recoveryAPI.autoRecover(faultId);
      await loadData();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Recovery execution failed");
    } finally {
      setRecovering(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-grid-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-grid-text uppercase">Digital Twin Schematic</h1>
          <p className="text-xs text-grid-muted font-mono mt-1">
            LIVE INTERACTIVE TOPOLOGY &amp; FAULT HEATMAP ({components.length} NODES DISCOVERED)
          </p>
        </div>
        <div className="flex items-center gap-2">
          {activeFaults.length > 0 ? (
            <span className="px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-600 rounded text-xs font-mono font-bold flex items-center gap-1.5 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5" /> {activeFaults.length} ANOMALY DETECTED
            </span>
          ) : (
            <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 rounded text-xs font-mono font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> GRID FULLY BALANCED
            </span>
          )}
        </div>
      </div>

      {/* Active Fault Alert Banner with Auto-Recover Action */}
      {activeFaults.length > 0 && (
        <div className="p-4 bg-red-500/10 border border-red-500/40 rounded-lg flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-red-500 text-white rounded-lg flex items-center justify-center font-bold text-lg animate-bounce">
              ⚡
            </div>
            <div>
              <div className="text-xs font-bold text-red-600 font-mono uppercase">
                CRITICAL ANOMALY: {activeFaults[0].fault_type} ON {activeFaults[0].component_id}
              </div>
              <div className="text-[11px] text-grid-muted mt-0.5 font-mono">
                Fault ID: {activeFaults[0].fault_id} | Cascade Risk: {((activeFaults[0].cascade_risk || 0) * 100).toFixed(0)}% | Confidence: {((activeFaults[0].confidence || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
          <button
            onClick={() => handleAutoRecover(activeFaults[0].fault_id)}
            disabled={recovering}
            className="px-4 py-2 bg-grid-accent hover:bg-amber-700 text-white rounded font-mono text-xs font-bold flex items-center gap-2 shadow transition disabled:opacity-50"
          >
            <Wrench className="w-4 h-4" />
            {recovering ? "HEALING GRID..." : "TRIGGER AUTO-SELF HEALING"}
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <Card title="Schematic Network Graphic">
            <svg viewBox="0 0 800 500" className="w-full h-[500px] bg-[#faf8f5] rounded border border-grid-border select-none">

              {/* ---------------- DRAW TRANSMISSION LINES (L1 - L7) ---------------- */}
              {LINES.map((line) => {
                const fault = getFaultFor(line.id, line.aliases);
                const isFaulted = !!fault;
                const isSelected = selected?.component_id === line.id || selected?.component_id === line.aliases[0];

                return (
                  <g
                    key={line.id}
                    onClick={() => setSelected({
                      component_id: line.aliases[0],
                      component_type: "transmission_line",
                      name: line.name,
                      status: isFaulted ? "FAULT" : "NORMAL",
                      fault,
                    })}
                    className="cursor-pointer group"
                  >
                    {/* Outer fault glow line */}
                    {isFaulted && (
                      <line
                        x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2}
                        stroke="#b55b5b" strokeWidth="8" opacity="0.4"
                        className="pulse-fault"
                      />
                    )}

                    {/* Main Line */}
                    <line
                      x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2}
                      stroke={isFaulted ? "#b55b5b" : isSelected ? "#b57c5b" : "#bdafa4"}
                      strokeWidth={isFaulted ? "3.5" : isSelected ? "3" : "2"}
                      strokeDasharray={line.id === "L7" ? "4" : undefined}
                      className={isFaulted ? "pulse-fault" : "group-hover:stroke-[#b57c5b] transition-all"}
                    />

                    {/* Line Label Badge */}
                    <rect
                      x={line.labelX - 14} y={line.labelY - 10} width="28" height="18" rx="3"
                      fill={isFaulted ? "#b55b5b" : "#ffffff"}
                      stroke={isFaulted ? "#802020" : "#bdafa4"}
                      strokeWidth="1"
                    />
                    <text
                      x={line.labelX} y={line.labelY + 3}
                      textAnchor="middle"
                      className="text-[10px] font-mono font-bold"
                      fill={isFaulted ? "#ffffff" : "#2b2927"}
                    >
                      {line.id}
                    </text>

                    {/* FAULT BADGE ON LINE */}
                    {isFaulted && (
                      <g transform={`translate(${line.labelX}, ${line.labelY - 22})`}>
                        <rect x="-24" y="-10" width="48" height="16" rx="2" fill="#b55b5b" stroke="#ffffff" strokeWidth="1" />
                        <text x="0" y="1" textAnchor="middle" fill="#ffffff" className="text-[9px] font-mono font-bold">
                          ⚡ FAULT
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* ---------------- DRAW NODES ---------------- */}

              {/* 1. Generator */}
              {(() => {
                const fault = getFaultFor("GEN_1", ["GEN", "GENERATOR", "MAIN GEN"]);
                const isFaulted = !!fault;
                return (
                  <g
                    onClick={() => setSelected({ component_id: "GEN_1", component_type: "generator", name: "Main Power Plant (150 MW)", status: isFaulted ? "FAULT" : "NORMAL", fault })}
                    className="cursor-pointer"
                  >
                    {isFaulted && <circle cx="400" cy="60" r="28" fill="none" stroke="#b55b5b" strokeWidth="2" className="pulse-halo" />}
                    <circle cx="400" cy="60" r="22" fill={isFaulted ? "#b55b5b" : "#c9a054"} stroke={isFaulted ? "#802020" : "#e8cf9c"} strokeWidth="2" />
                    <text x="400" y="64" textAnchor="middle" className="text-[10px] font-mono font-bold" fill="#ffffff">GEN</text>
                    <text x="400" y="30" textAnchor="middle" className="text-[10px] font-mono tracking-widest uppercase font-bold" fill="#827a73">Main Gen</text>
                  </g>
                );
              })()}

              {/* 2. Substations A & B */}
              {["SUB_A", "SUB_B"].map((id, i) => {
                const x = i === 0 ? 200 : 600;
                const fault = getFaultFor(id, [id === "SUB_A" ? "SUBSTATION_A" : "SUBSTATION_B"]);
                const isFaulted = !!fault;
                return (
                  <g
                    key={id}
                    onClick={() => setSelected({ component_id: id, component_type: "substation", name: `Substation ${id}`, status: isFaulted ? "FAULT" : "NORMAL", fault })}
                    className="cursor-pointer"
                  >
                    {isFaulted && <rect x={x - 28} y={155} width={56} height={50} rx="4" fill="none" stroke="#b55b5b" strokeWidth="2" className="pulse-halo" />}
                    <rect x={x - 22} y={162} width={44} height={36} rx="3" fill={isFaulted ? "#b55b5b" : "#5f7d61"} stroke={isFaulted ? "#ffffff" : "#b8d1ba"} strokeWidth="1.5" />
                    <text x={x} y={184} textAnchor="middle" className="text-[10px] font-mono font-bold" fill="#ffffff">{id}</text>
                    {isFaulted && (
                      <text x={x} y={152} textAnchor="middle" fill="#b55b5b" className="text-[10px] font-mono font-bold">⚡ FAULT</text>
                    )}
                  </g>
                );
              })}

              {/* 3. Buses A1, A2, B1, B2 */}
              {[
                { id: "BUS_A1", aliases: ["BUS_0", "BUS_1"], x: 120, y: 320 },
                { id: "BUS_A2", aliases: ["BUS_2", "BUS_3"], x: 280, y: 320 },
                { id: "BUS_B1", aliases: ["BUS_4", "BUS_5"], x: 520, y: 320 },
                { id: "BUS_B2", aliases: ["BUS_6", "BUS_7"], x: 680, y: 320 },
              ].map((b) => {
                const fault = getFaultFor(b.id, b.aliases);
                const isFaulted = !!fault;
                return (
                  <g
                    key={b.id}
                    onClick={() => setSelected({ component_id: b.id, component_type: "bus", name: `Distribution Bus ${b.id}`, status: isFaulted ? "FAULT" : "NORMAL", fault })}
                    className="cursor-pointer"
                  >
                    {isFaulted && <circle cx={b.x} cy={b.y} r="18" fill="none" stroke="#b55b5b" strokeWidth="2" className="pulse-halo" />}
                    <circle cx={b.x} cy={b.y} r={13} fill={isFaulted ? "#b55b5b" : "#5f7d61"} stroke={isFaulted ? "#ffffff" : "#b8d1ba"} strokeWidth="1.5" />
                    <text x={b.x} y={b.y + 26} textAnchor="middle" className="text-[9px] font-mono font-semibold" fill={isFaulted ? "#b55b5b" : "#827a73"}>{b.id}</text>
                  </g>
                );
              })}

              {/* 4. Critical Load */}
              {(() => {
                const fault = getFaultFor("LOAD_CRIT", ["LOAD_0", "HOSPITAL", "CRIT"]);
                const isFaulted = !!fault;
                return (
                  <g
                    onClick={() => setSelected({ component_id: "LOAD_CRIT", component_type: "critical_load", name: "Hospital Emergency Load (30 MW)", is_critical: true, status: isFaulted ? "FAULT" : "NORMAL", fault })}
                    className="cursor-pointer"
                  >
                    {isFaulted && <rect x={372} y={398} width={56} height={42} rx="4" fill="none" stroke="#b55b5b" strokeWidth="2" className="pulse-halo" />}
                    <rect x={378} y={405} width={44} height={28} rx="3" fill={isFaulted ? "#b55b5b" : "#4a707a"} stroke={isFaulted ? "#ffffff" : "#90b2bd"} strokeWidth="1.5" />
                    <text x="400" y="422" textAnchor="middle" className="text-[9px] font-mono font-bold" fill="#ffffff">CRIT</text>
                    <text x="400" y="450" textAnchor="middle" className="text-[9px] font-mono tracking-widest uppercase font-bold" fill={isFaulted ? "#b55b5b" : "#4a707a"}>HOSPITAL LOAD</text>
                  </g>
                );
              })()}

            </svg>

            {/* Legend */}
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4 text-[10px] font-mono uppercase tracking-wider font-semibold border-t border-grid-border pt-3">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#5f7d61] rounded" /> Normal Feeder</div>
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#c9a054] rounded" /> Power Plant</div>
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#4a707a] rounded" /> Critical Load</div>
                <div className="flex items-center gap-1.5"><span className="w-3 h-3 bg-[#b55b5b] rounded text-white text-[8px] flex items-center justify-center font-bold">⚡</span> Fault Injected</div>
              </div>
              <div className="text-grid-muted">Click any feeder line or bus node to inspect</div>
            </div>
          </Card>
        </div>

        <Card title="Inspector Panel">
          {selected ? (
            <div className="space-y-4 text-xs font-mono">
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Selected Element</div>
                <div className="font-bold text-grid-text mt-0.5">{selected.component_id}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Functional Type</div>
                <div className="text-grid-text capitalize mt-0.5">{selected.component_type}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Component Description</div>
                <div className="text-grid-text mt-0.5">{selected.name}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Current Operating Status</div>
                <div className="mt-1">
                  <StatusBadge status={selected.status} />
                </div>
              </div>

              {selected.fault && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-[11px] space-y-1.5">
                  <div className="font-bold text-red-600 flex items-center gap-1">
                    <Zap className="w-3.5 h-3.5" /> ACTIVE ANOMALY
                  </div>
                  <div>Type: <span className="text-grid-text font-bold">{selected.fault.fault_type}</span></div>
                  <div>Cascade Risk: <span className="text-amber-600 font-bold">{((selected.fault.cascade_risk || 0) * 100).toFixed(0)}%</span></div>
                  <div>AI Confidence: <span className="text-blue-600 font-bold">{((selected.fault.confidence || 0) * 100).toFixed(1)}%</span></div>
                  <button
                    onClick={() => handleAutoRecover(selected.fault.fault_id)}
                    disabled={recovering}
                    className="w-full mt-2 bg-grid-accent hover:bg-amber-700 text-white py-1.5 rounded font-bold text-[10px] uppercase"
                  >
                    {recovering ? "Healing..." : "Heal Component"}
                  </button>
                </div>
              )}

              {selected.is_critical && (
                <div className="p-3 bg-grid-recovery/10 border border-grid-recovery/30 rounded text-[10px] text-grid-recovery uppercase font-bold leading-relaxed">
                  ⚠ Priority dispatch protection enforced on node
                </div>
              )}
            </div>
          ) : (
            <div className="text-grid-muted text-[10px] font-mono text-center py-12 uppercase">
              Interact with network graph node or transmission line to inspect attributes
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
