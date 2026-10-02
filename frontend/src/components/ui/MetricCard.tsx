import type { ReactNode } from "react";

interface Props {
  label: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
  trend?: string;
  color?: "success" | "warning" | "danger" | "default";
}

export default function MetricCard({ label, value, unit, icon, trend, color = "default" }: Props) {
  const colors = {
    success: "text-grid-success",
    warning: "text-grid-warning",
    danger: "text-grid-danger",
    default: "text-grid-text",
  };
  return (
    <div className="bg-grid-card border border-grid-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-grid-muted uppercase tracking-wider">{label}</span>
        {icon && <div className="text-grid-muted">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${colors[color]}`}>{value}</span>
        {unit && <span className="text-sm text-grid-muted">{unit}</span>}
      </div>
      {trend && <div className="text-xs text-grid-muted mt-1">{trend}</div>}
    </div>
  );
}
