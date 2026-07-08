import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

const links = [
  { to: "/x-intel", label: "信息抓取" },
  { to: "/industry", label: "行业分析" },
  { to: "/stocks", label: "个股分析" },
  { to: "/dashboard", label: "仪表盘" }
];

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <div className="brand">美股交易决策辅助系统</div>
          <div className="subtle">四个模块独立运行</div>
        </div>
        <nav className="nav">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="risk-note">仅作研究和辅助观察，不构成投资建议。</div>
      </aside>
      <main className="workspace">{children}</main>
    </div>
  );
}
