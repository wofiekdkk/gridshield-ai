import type { ReactNode } from "react";

interface Props {
  title?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}

export default function Card({ title, children, action, className = "" }: Props) {
  return (
    <div className={`bg-white border border-gp-border rounded-xl shadow-soft ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-gp-border">
          {title && <h3 className="text-sm font-bold text-gp-text">{title}</h3>}
          {action}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}
