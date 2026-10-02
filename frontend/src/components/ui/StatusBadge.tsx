interface Props { status: string; }

const colors: Record<string, string> = {
  NORMAL: "bg-grid-success/20 text-grid-success border-grid-success/40",
  WARNING: "bg-grid-warning/20 text-grid-warning border-grid-warning/40",
  FAULT: "bg-grid-danger/20 text-grid-danger border-grid-danger/40",
  DETECTED: "bg-grid-danger/20 text-grid-danger border-grid-danger/40",
  CLASSIFIED: "bg-orange-500/20 text-orange-400 border-orange-500/40",
  LOCALIZED: "bg-orange-500/20 text-orange-400 border-orange-500/40",
  RECOVERING: "bg-grid-recovery/20 text-grid-recovery border-grid-recovery/40",
  RECOVERED: "bg-grid-success/20 text-grid-success border-grid-success/40",
  FAILED: "bg-grid-danger/20 text-grid-danger border-grid-danger/40",
};

export default function StatusBadge({ status }: Props) {
  const cls = colors[status] || "bg-grid-muted/20 text-grid-muted border-grid-muted/40";
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded border ${cls}`}>
      {status}
    </span>
  );
}
