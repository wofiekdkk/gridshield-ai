import type { ReactNode } from "react";

interface Props {
  title?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}

export default function Card({ title, children, action, className = "" }: Props) {
  return (
    <div className={`bg-grid-card border border-grid-border rounded-lg ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-grid-border">
          {title && <h3 className="text-sm font-semibold text-grid-text uppercase tracking-wide">{title}</h3>}
          {action}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
