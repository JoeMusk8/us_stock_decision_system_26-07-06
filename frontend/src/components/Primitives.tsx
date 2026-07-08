import type { ReactNode } from "react";

export function PageHeader({ title, description }: { title: string; description: string }) {
  return (
    <header className="page-header">
      <div className="eyebrow">美股交易决策辅助系统</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </header>
  );
}

export function Panel({ title, caption, children, className = "" }: { title: string; caption?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          {caption ? <p>{caption}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "good" | "warn" | "bad" | "info" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function Button({ children, onClick, variant = "primary", disabled = false }: { children: ReactNode; onClick?: () => void; variant?: "primary" | "secondary"; disabled?: boolean }) {
  return (
    <button className={`button ${variant}`} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

export function Metric({ label, value, hint, tone = "neutral" }: { label: string; value: React.ReactNode; hint?: string; tone?: "neutral" | "good" | "warn" | "bad" | "info" }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value ?? "待验证"}</div>
      {hint ? <div className={`metric-hint ${tone}`}>{hint}</div> : null}
    </div>
  );
}
