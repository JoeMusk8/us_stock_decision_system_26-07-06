import { useEffect, useState } from "react";
import { apiGet } from "../api/client";
import { MarketChart, type MarketPoint } from "../components/MiniCharts";
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
  const [reminders, setReminders] = useState<string[]>(Array(15).fill(""));

  useEffect(() => {
    apiGet<Dashboard>("/api/dashboard")
      .then((payload) => {
        setData(payload);
        setReminders((current) => current.map((item, index) => {
          const event = payload.events[index];
          return item || (event ? `${event.name} / ${event.date}` : "");
        }));
      })
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <div className="page page-dashboard">
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
              <MarketChart title="纳斯达克技术状态" data={asChartData(data.nasdaq.chart_data)} currentValue={formatNumber(data.nasdaq.price)} />
            </Panel>
            <Panel title="比特币技术状态图" caption="图形化展示 BTC：实时价格和风险偏好信号。">
              <MarketChart title="比特币技术状态" data={asChartData(data.bitcoin.chart_data)} currentValue={formatCurrency(data.bitcoin.price)} />
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
            <Panel title="自定义时间提醒跟踪输入" caption="具体提醒内容由用户输入，支持 15 个跟踪窗口。">
              <div className="reminder-head"><Badge tone="info">15个输入窗口</Badge></div>
              <div className="reminder-grid">
                {reminders.map((reminder, index) => (
                  <input
                    key={index}
                    value={reminder}
                    onChange={(event) => setReminders((current) => current.map((item, itemIndex) => itemIndex === index ? event.target.value : item))}
                    placeholder={`提醒${index + 1}：输入事件/日期`}
                    aria-label={`提醒${index + 1}`}
                  />
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

function asChartData(value: unknown): MarketPoint[] {
  return Array.isArray(value) ? value as MarketPoint[] : [];
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
