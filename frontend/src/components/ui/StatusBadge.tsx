interface Props { status: string; }

const colors: Record<string, string> = {
  NORMAL: "bg-emerald-50 text-emerald-600 border-emerald-200",
  WARNING: "bg-amber-50 text-amber-600 border-amber-200",
  FAULT: "bg-red-50 text-red-600 border-red-200",
  DETECTED: "bg-red-50 text-red-600 border-red-200",
  CLASSIFIED: "bg-orange-50 text-orange-600 border-orange-200",
  LOCALIZED: "bg-orange-50 text-orange-600 border-orange-200",
  RECOVERING: "bg-blue-50 text-blue-600 border-blue-200",
  RECOVERED: "bg-emerald-50 text-emerald-600 border-emerald-200",
  FAILED: "bg-red-50 text-red-600 border-red-200",
  High: "bg-red-50 text-red-600 border-red-200",
  Medium: "bg-amber-50 text-amber-600 border-amber-200",
  Low: "bg-blue-50 text-blue-600 border-blue-200",
};

export default function StatusBadge({ status }: Props) {
  const cls = colors[status] || "bg-slate-50 text-slate-500 border-slate-200";
  return (
    <span className={`inline-block px-2 py-0.5 text-[10px] font-bold rounded-md border ${cls}`}>
      {status}
    </span>
  );
}
