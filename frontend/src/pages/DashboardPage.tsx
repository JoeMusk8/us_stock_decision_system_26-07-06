import { useEffect, useState } from "react";
import { apiGet } from "../api/client";
import { MarketChart } from "../components/MiniCharts";
import { Badge, EmptyState, Metric, PageHeader, Panel } from "../components/Primitives";

type Dashboard = {
  market_status: string;
  nasdaq: Record<string, number | string | null>;
  bitcoin: Record<string, number | string | null>;
  sentiment: Record<string, number | string | null>;
  events: Array<{ name: string; date: string; source: string; status: string }>;
  ai_market_reading: string;
  market_level: string;
  data_quality: string[];
};

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet<Dashboard>("/api/dashboard").then(setData).catch((err) => setError(String(err)));
  }, []);

  return (
    <div>
      <PageHeader title="仪表盘模块" description="只展示关键市场状态：纳斯达克、BTC、情绪、事件日历和市场辅助等级。" />
      {error ? <div className="error-line">{error}</div> : null}
      {data ? (
        <>
          <div className="dashboard-metrics">
            <Metric label="纳斯达克指数" value={formatNumber(data.nasdaq.price)} hint={formatPercent(data.nasdaq.change_percent)} tone="info" />
            <Metric label="纳斯达克资金流向" value={data.nasdaq.money_flow ?? "待验证"} hint="资金状态" />
            <Metric label="纳斯达克 RSI" value={formatNumber(data.nasdaq.rsi)} hint="技术状态" />
            <Metric label="比特币实时价格" value={formatCurrency(data.bitcoin.price)} hint={String(data.bitcoin.risk_signal ?? "风险偏好待验证")} />
            <Metric label="市场情绪状态" value={String(data.sentiment.label ?? "数据源待接入")} hint="恐惧 / 贪婪指数" tone="warn" />
          </div>
          <div className="grid dashboard-grid">
            <Panel title="纳斯达克技术状态图" caption="图形化展示 QQQ / 纳指：K线、MA20、MA50、MA120、MA250、RSI 和成交量。">
              <div className="chip-row">
                <Badge>MA20 {formatNumber(data.nasdaq.ma20)}</Badge>
                <Badge>MA50 {formatNumber(data.nasdaq.ma50)}</Badge>
                <Badge>MA120 {formatNumber(data.nasdaq.ma120)}</Badge>
                <Badge>MA250 {formatNumber(data.nasdaq.ma250)}</Badge>
              </div>
              <MarketChart title="纳斯达克技术状态" />
            </Panel>
            <Panel title="比特币技术状态图" caption="图形化展示 BTC：实时价格和风险偏好信号。">
              <MarketChart title="BTC 风险偏好辅助图" />
            </Panel>
          </div>
          <div className="grid dashboard-bottom">
            <Panel title="每日AI综合分析输出窗口" caption="由 AI 根据纳斯达克、资金流向、RSI、均线结构、成交量与事件日历辅助解读。">
              <div className="chip-row">
                <Badge tone={data.market_level.includes("高风险") ? "bad" : "info"}>市场辅助等级：{data.market_level}</Badge>
                <Badge tone="warn">市场状态：{data.market_status}</Badge>
              </div>
              <p className="reading">{data.ai_market_reading}</p>
              <ul>{data.data_quality.map((item) => <li key={item}>{item}</li>)}</ul>
            </Panel>
            <Panel title="重要事件日历" caption="大非农、美联储议息会议、几家大型科技公司的财报日期。">
              <div className="event-list">
                {data.events.map((event) => (
                  <div className="event-row" key={`${event.name}-${event.date}`}>
                    <strong>{event.name}</strong>
                    <span>{event.date}</span>
                    <Badge tone={event.status.includes("待") || event.status.includes("需") ? "warn" : "good"}>{event.status}</Badge>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </>
      ) : (
        <EmptyState text="正在加载仪表盘..." />
      )}
    </div>
  );
}

function formatNumber(value: unknown) {
  return typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "待验证";
}

function formatCurrency(value: unknown) {
  return typeof value === "number" ? `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : "待验证";
}

function formatPercent(value: unknown) {
  return typeof value === "number" ? `${value > 0 ? "+" : ""}${value.toFixed(2)}%` : "待验证";
}

