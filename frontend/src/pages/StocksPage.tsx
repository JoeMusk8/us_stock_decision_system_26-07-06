import { useState } from "react";
import { apiPost } from "../api/client";
import { MarketChart, type MarketPoint } from "../components/MiniCharts";
import { Badge, Button, EmptyState, Metric, PageHeader, Panel } from "../components/Primitives";

type StockAnalysis = {
  symbol: string;
  company_name: string;
  company_background: string;
  main_business: string;
  industry_position: string;
  current_price: number | null;
  change_percent: number | null;
  volume: number | null;
  average_volume: number | null;
  rsi: number | null;
  ma20: number | null;
  ma50: number | null;
  ma120: number | null;
  ma250: number | null;
  money_flow: string;
  financial_summary: string;
  related_x_summary: string;
  ai_conclusion: string;
  observation_range: string;
  risk_range: string;
  decision_level: string;
  data_quality: string[];
  chart_data: MarketPoint[];
};

export default function StocksPage() {
  const [symbolsText, setSymbolsText] = useState("NVDA, TSLA, LITE, COHR, MU");
  const [stocks, setStocks] = useState<StockAnalysis[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const symbols = normalizeSymbols(symbolsText);
  const current = stocks.find((stock) => stock.symbol === selected) ?? stocks[0];

  async function analyze() {
    setLoading(true);
    try {
      const rows = await apiPost<StockAnalysis[]>("/api/stocks/analyze", { symbols });
      setStocks(rows);
      setSelected(rows[0]?.symbol ?? "");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page page-stocks">
      <PageHeader title="个股分析模块" description="最多输入 15 只股票，展示财务、资金流向、RSI、均线、成交量和辅助观察区间。" />
      <section className="input-band">
        <label>
          股票代码或公司名称，最多15只
          <input value={symbolsText} onChange={(event) => setSymbolsText(event.target.value)} placeholder="NVDA, TSLA, LITE, COHR, MU" />
        </label>
        <Button onClick={analyze} disabled={loading || symbols.length === 0 || symbols.length > 15}>添加股票</Button>
        <Button variant="secondary" onClick={() => { setSymbolsText(""); setStocks([]); }}>清空股票</Button>
        <Badge tone={symbols.length > 15 ? "bad" : "info"}>当前 {symbols.length} / 15</Badge>
        <div className="chip-row">{symbols.slice(0, 15).map((symbol) => <Badge key={symbol}>{symbol}</Badge>)}</div>
      </section>
      <div className="grid stocks-grid">
        <Panel title="股票列表" caption="每只股票都有独立 AI分析 按钮。">
          <div className="list">
            {stocks.map((stock) => (
              <div key={stock.symbol} className={`stock-row ${current?.symbol === stock.symbol ? "selected" : ""}`}>
                <strong>{stock.symbol}</strong>
                <span>{formatCurrency(stock.current_price)}</span>
                <span>{formatPercent(stock.change_percent)}</span>
                <Button onClick={() => setSelected(stock.symbol)}>AI分析</Button>
              </div>
            ))}
            {!stocks.length ? <EmptyState text={loading ? "正在分析..." : "输入股票后开始分析。"} /> : null}
          </div>
        </Panel>
        <Panel title={`图像化技术指标${current ? `：${current.symbol}` : ""}`} caption="展示K线、MA20、MA50、MA120、MA250、RSI 和成交量。">
          {current ? (
            <>
              <div className="metric-grid">
                <Metric label="当前价格" value={formatCurrency(current.current_price)} hint={`涨跌幅 ${formatPercent(current.change_percent)}`} tone="info" />
                <Metric label="RSI" value={current.rsi?.toFixed(1) ?? "待验证"} hint={current.rsi && current.rsi >= 70 ? "偏热" : "未极端"} tone={current.rsi && current.rsi >= 70 ? "warn" : "good"} />
                <Metric label="成交量" value={current.volume?.toLocaleString() ?? "待验证"} hint={current.average_volume ? `均量 ${current.average_volume.toLocaleString()}` : "均量待验证"} />
              </div>
              <MarketChart title={`${current.symbol} 技术状态`} data={current.chart_data} currentValue={formatCurrency(current.current_price)} />
            </>
          ) : (
            <EmptyState text="等待选择股票。" />
          )}
        </Panel>
        <Panel title="AI 深入调研输出" caption="基本面、技术面、风险、证据来源与限制。">
          {current ? (
            <div className="analysis-block">
              <Badge tone="info">当前：{current.symbol}</Badge>
              <div className="decision-box">
                <Metric label="辅助观察区间" value={current.observation_range} />
                <Metric label="风险区间" value={current.risk_range} tone="warn" />
              </div>
              <div className="tab-row">
                <Badge>基本面</Badge>
                <Badge>技术面</Badge>
                <Badge>风险</Badge>
                <Badge>证据</Badge>
              </div>
              <div className="research-grid">
                <ResearchCard tone="blue" title="公司背景" text={current.company_background} />
                <ResearchCard tone="green" title="主营业务" text={current.main_business} />
                <ResearchCard tone="amber" title="行业地位" text={current.industry_position} />
                <ResearchCard tone="purple" title="财务兑现" text={current.financial_summary} />
              </div>
              <h3>综合调研结论</h3>
              <p>{current.ai_conclusion}</p>
              <h3>数据质量</h3>
              <ul>{current.data_quality.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          ) : (
            <EmptyState text="点击股票分析后显示辅助区间和风险状态。" />
          )}
        </Panel>
      </div>
    </div>
  );
}

function ResearchCard({ title, text, tone }: { title: string; text: string; tone: "blue" | "green" | "amber" | "purple" }) {
  return (
    <div className={`research-card ${tone}`}>
      <h3>{title}</h3>
      <p>{text || "待验证"}</p>
    </div>
  );
}

function normalizeSymbols(value: string) {
  return Array.from(new Set(value.split(/[,\s，]+/).map((item) => item.trim().toUpperCase()).filter(Boolean)));
}

function formatCurrency(value: number | null) {
  return value === null || value === undefined ? "待验证" : `$${value.toFixed(2)}`;
}

function formatPercent(value: number | null) {
  return value === null || value === undefined ? "待验证" : `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}
