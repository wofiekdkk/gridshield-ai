import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import StatusBadge from "../components/ui/StatusBadge";
import { gridAPI, faultAPI } from "../services/api";
import type { GridComponent } from "../types";
import { useEventStore } from "../store/eventStore";

export default function DigitalTwin() {
  const [components, setComponents] = useState<GridComponent[]>([]);
  const [selected, setSelected] = useState<GridComponent | null>(null);
  const [faultyIds, setFaultyIds] = useState<Set<string>>(new Set());
  const events = useEventStore((s) => s.events);

  const load = async () => {
    try {
      const [comps, faults] = await Promise.all([gridAPI.getComponents(), faultAPI.list(true)]);
      if (Array.isArray(comps)) setComponents(comps);
      if (Array.isArray(faults)) setFaultyIds(new Set(faults.map((f: any) => f.component_id)));
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [events.length]);

  const fillFor = (c: GridComponent) => {
    if (faultyIds.has(c.component_id)) return "fill-[#b55b5b] stroke-[#e49b9b] pulse-fault";
    if (c.is_critical) return "fill-[#4a707a] stroke-[#90b2bd]";
    return "fill-[#5f7d61] stroke-[#b8d1ba]";
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-grid-border">
        <h1 className="text-xl font-bold tracking-tight text-grid-text uppercase">Digital Twin Monitor</h1>
        <p className="text-xs text-grid-muted font-mono mt-1">GRAPH TOPOLOGY PERSISTENCE VISUALIZATION</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <Card title="Schematic Topology Layout">
            <svg viewBox="0 0 800 500" className="w-full h-[500px] bg-[#faf8f5] rounded border border-grid-border">
              {/* Lines - Refined sand-charcoal colors */}
              <line x1="400" y1="60" x2="200" y2="180" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="400" y1="60" x2="600" y2="180" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="200" y1="180" x2="120" y2="320" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="200" y1="180" x2="280" y2="320" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="600" y1="180" x2="520" y2="320" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="600" y1="180" x2="680" y2="320" stroke="#bdafa4" strokeWidth="1.5" />
              <line x1="280" y1="320" x2="400" y2="420" stroke="#bdafa4" strokeWidth="1.5" strokeDasharray="3" />
              <line x1="520" y1="320" x2="400" y2="420" stroke="#bdafa4" strokeWidth="1.5" strokeDasharray="3" />

              {/* Power Plant - Soft Ochre */}
              <g onClick={() => setSelected({ component_id: "GEN_1", component_type: "generator", name: "Main Power Plant", status: "NORMAL" })} className="cursor-pointer">
                <circle cx="400" cy="60" r="20" className="fill-[#c9a054] stroke-[#e8cf9c]" strokeWidth="1.5" />
                <text x="400" y="64" textAnchor="middle" className="text-[10px] font-mono font-bold" fill="#ffffff">GEN</text>
                <text x="400" y="32" textAnchor="middle" className="text-[10px] font-mono tracking-widest uppercase font-bold" fill="#827a73">Main Gen</text>
              </g>

              {/* Substations - Terracotta or Neutral */}
              {["SUB_A", "SUB_B"].map((id, i) => {
                const x = i === 0 ? 200 : 600;
                const comp: GridComponent = { component_id: id, component_type: "substation", name: `Substation ${id}`, status: "NORMAL" };
                return (
                  <g key={id} onClick={() => setSelected(comp)} className="cursor-pointer">
                    <rect x={x - 22} y={162} width={44} height={36} className={fillFor(comp)} strokeWidth="1.5" rx="2" />
                    <text x={x} y={184} textAnchor="middle" className="text-[10px] font-mono font-bold" fill="#ffffff">{id}</text>
                  </g>
                );
              })}

              {/* Buses - Sage or Terracotta */}
              {[
                { id: "BUS_A1", x: 120, y: 320 },
                { id: "BUS_A2", x: 280, y: 320 },
                { id: "BUS_B1", x: 520, y: 320 },
                { id: "BUS_B2", x: 680, y: 320 },
              ].map((b) => {
                const comp = components.find((c) => c.component_id === b.id) || ({ component_id: b.id, component_type: "bus", name: b.id, status: "NORMAL" } as GridComponent);
                return (
                  <g key={b.id} onClick={() => setSelected(comp)} className="cursor-pointer">
                    <circle cx={b.x} cy={b.y} r={12} className={fillFor(comp)} strokeWidth="1.5" />
                    <text x={b.x} y={b.y + 26} textAnchor="middle" className="text-[9px] font-mono font-semibold" fill="#827a73">{b.id}</text>
                  </g>
                );
              })}

              {/* Critical Load - Muted Teal */}
              <g onClick={() => setSelected({ component_id: "LOAD_CRIT", component_type: "load", name: "Hospital (Critical)", is_critical: true, status: "NORMAL" })} className="cursor-pointer">
                <rect x={378} y={405} width={44} height={28} className="fill-[#4a707a] stroke-[#90b2bd]" strokeWidth="1.5" rx="2" />
                <text x="400" y="422" textAnchor="middle" className="text-[9px] font-mono font-bold" fill="#ffffff">CRIT</text>
                <text x="400" y="450" textAnchor="middle" className="text-[9px] font-mono tracking-widest uppercase font-bold" fill="#4a707a">HOSPITAL LOAD</text>
              </g>

              {/* Line Labels */}
              <text x="290" y="115" fill="#827a73" className="text-[10px] font-mono font-bold">L1</text>
              <text x="510" y="115" fill="#827a73" className="text-[10px] font-mono font-bold">L2</text>
              <text x="150" y="255" fill="#827a73" className="text-[10px] font-mono font-bold">L3</text>
              <text x="250" y="255" fill="#827a73" className="text-[10px] font-mono font-bold">L4</text>
              <text x="550" y="255" fill="#827a73" className="text-[10px] font-mono font-bold">L5</text>
              <text x="650" y="255" fill="#827a73" className="text-[10px] font-mono font-bold">L6</text>
              <text x="330" y="380" fill="#827a73" className="text-[10px] font-mono font-bold">L7</text>
            </svg>

            <div className="mt-4 flex flex-wrap gap-4 text-[10px] font-mono uppercase tracking-wider font-semibold">
              <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-grid-success rounded" /> Normal</div>
              <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-grid-warning rounded" /> Gen Plant</div>
              <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-grid-danger rounded pulse-fault" /> Fault Injected</div>
              <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-grid-recovery rounded" /> Critical Bus</div>
            </div>
          </Card>
        </div>

        <Card title="Structural Specifications">
          {selected ? (
            <div className="space-y-4 text-xs font-mono">
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Component Identification</div>
                <div className="font-bold text-grid-text mt-1">{selected.component_id}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Functional Type</div>
                <div className="text-grid-text capitalize mt-1">{selected.component_type}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Station Label</div>
                <div className="text-grid-text mt-1">{selected.name}</div>
              </div>
              <div>
                <div className="text-[10px] text-grid-muted uppercase">Operating Status</div>
                <div className="mt-1">
                  <StatusBadge status={faultyIds.has(selected.component_id) ? "FAULT" : "NORMAL"} />
                </div>
              </div>
              {selected.is_critical && (
                <div className="p-3 bg-grid-recovery/10 border border-grid-recovery/30 rounded text-[10px] text-grid-recovery uppercase font-bold leading-relaxed">
                  ⚠ priority dispatch protection enforced on node
                </div>
              )}
            </div>
          ) : (
            <div className="text-grid-muted text-[10px] font-mono text-center py-12 uppercase">
              Interact with network graph node to map attributes
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
