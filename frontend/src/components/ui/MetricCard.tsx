import type { ReactNode } from "react";

interface Props {
  label: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon?: ReactNode;
  iconBg?: string;
  sparkColor?: string;
  sparkData?: number[];
  donut?: number;
  color?: "success" | "warning" | "danger" | "default";
}

export default function KPICard({
  label,
  value,
  unit,
  subtitle,
  icon,
  iconBg,
  sparkColor,
  sparkData,
  donut,
  color,
}: Props) {
  const pts = (sparkData || [4, 6, 5, 8, 7, 9, 8, 10, 9, 11]).map((v, i) => `${i * 10},${20 - v}`).join(" ");

  // Map 'color' prop if passed (from Analytics or other pages)
  let resolvedBg = iconBg || "bg-blue-50 text-blue-500";
  let resolvedSpark = sparkColor || "#8b5cf6";

  if (color === "success") {
    resolvedBg = "bg-emerald-50 text-emerald-600";
    resolvedSpark = "#10b981";
  } else if (color === "warning") {
    resolvedBg = "bg-amber-50 text-amber-600";
    resolvedSpark = "#f59e0b";
  } else if (color === "danger") {
    resolvedBg = "bg-red-50 text-red-600";
    resolvedSpark = "#ef4444";
  }

  return (
    <div className="bg-white rounded-xl border border-gp-border p-4 shadow-soft hover:shadow-card transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-9 h-9 rounded-lg ${resolvedBg} flex items-center justify-center`}>{icon}</div>
        {donut !== undefined ? (
          <div className="relative w-10 h-10">
            <svg viewBox="0 0 36 36" className="w-10 h-10 -rotate-90">
              <circle cx="18" cy="18" r="14" fill="none" stroke="#e2eaf2" strokeWidth="4" />
              <circle
                cx="18"
                cy="18"
                r="14"
                fill="none"
                stroke="#10b981"
                strokeWidth="4"
                strokeDasharray={`${donut * 0.88} 88`}
                strokeLinecap="round"
              />
            </svg>
          </div>
        ) : (
          <svg width="70" height="28" viewBox="0 0 100 24" className="opacity-80">
            <polyline points={pts} fill="none" stroke={resolvedSpark} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points={pts} fill={`${resolvedSpark}15`} stroke="none" />
          </svg>
        )}
      </div>
      <div className="text-[11px] font-medium text-gp-muted mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-gp-text tracking-tight">{value}</span>
        {unit && <span className="text-xs font-semibold text-gp-muted">{unit}</span>}
      </div>
      {subtitle && <div className="text-[11px] text-gp-muted mt-1">{subtitle}</div>}
    </div>
  );
}
