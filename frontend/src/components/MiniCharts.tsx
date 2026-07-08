export type MarketPoint = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma20: number | null;
  ma50: number | null;
  ma120: number | null;
  ma250: number | null;
  rsi: number | null;
};

type MarketChartProps = {
  title: string;
  data?: MarketPoint[];
  currentValue?: string;
};

const lines = [
  { key: "ma20" as const, label: "MA20", color: "#10a37f" },
  { key: "ma50" as const, label: "MA50", color: "#2563eb" },
  { key: "ma120" as const, label: "MA120", color: "#f59e0b" },
  { key: "ma250" as const, label: "MA250", color: "#7c3aed" }
];

export function MarketChart({ title, data = [], currentValue }: MarketChartProps) {
  const points = data.slice(-18);
  if (points.length < 2) {
    return (
      <div className="chart-box chart-box-empty">
        <div className="chart-title">价格 / 均线 / RSI / 成交量</div>
        <div className="chart-empty-state">
          <strong>技术图表数据源待接入</strong>
          <span>配置 Alpha Vantage API 后显示 {title} 的真实 K线、均线、RSI 与成交量。</span>
        </div>
      </div>
    );
  }

  const values = points.flatMap((point) => [
    point.low,
    point.high,
    ...lines.map((line) => point[line.key]).filter((value): value is number => value !== null)
  ]);
  const minPrice = Math.min(...values);
  const maxPrice = Math.max(...values);
  const priceRange = Math.max(maxPrice - minPrice, 1);
  const priceY = (value: number) => 150 - ((value - minPrice) / priceRange) * 120;
  const step = 510 / Math.max(points.length - 1, 1);
  const pointX = (index: number) => 25 + index * step;
  const maxVolume = Math.max(...points.map((point) => point.volume), 1);
  const latest = points[points.length - 1];

  return (
    <div className="chart-box">
      <div className="chart-toolbar">
        <div className="chart-title">价格 / 均线 / RSI / 成交量</div>
        <div className="legend-row">
          {lines.map((line) => <span key={line.key} className={`legend-${line.key}`}>{line.label}</span>)}
        </div>
        {currentValue ? <span className="chart-current">当前：{currentValue}</span> : null}
      </div>
      <div className="price-chart-area">
        <svg className="chart-svg" viewBox="0 0 560 170" role="img" aria-label={title}>
          {[30, 60, 90, 120, 150].map((y) => (
            <line key={y} x1="18" x2="542" y1={y} y2={y} stroke="#e5e7eb" />
          ))}
          {points.map((point, index) => {
            const x = pointX(index);
            const rising = point.close >= point.open;
            const color = rising ? "#10a37f" : "#ef4444";
            const top = priceY(Math.max(point.open, point.close));
            const bottom = priceY(Math.min(point.open, point.close));
            return (
              <g key={point.date}>
                <line x1={x} x2={x} y1={priceY(point.high)} y2={priceY(point.low)} stroke={color} strokeWidth="2" />
                <rect x={x - 5} y={top} width="10" height={Math.max(bottom - top, 2)} rx="1" fill={color} />
              </g>
            );
          })}
          {lines.map((line) => {
            const linePoints = points
              .map((point, index) => point[line.key] === null ? null : `${pointX(index)},${priceY(point[line.key] as number)}`)
              .filter(Boolean)
              .join(" ");
            return linePoints ? <polyline key={line.key} points={linePoints} fill="none" stroke={line.color} strokeWidth="2" /> : null;
          })}
        </svg>
      </div>
      <div className="subcharts">
        <div className="subchart-panel">
          <div className="tiny-title">RSI {latest.rsi === null ? "" : latest.rsi.toFixed(1)}</div>
          <svg viewBox="0 0 250 58" aria-label="RSI">
            <line x1="0" x2="225" y1="14" y2="14" stroke="#fca5a5" strokeDasharray="3 3" />
            <line x1="0" x2="225" y1="44" y2="44" stroke="#86efac" strokeDasharray="3 3" />
            <polyline
              points={points.map((point, index) => point.rsi === null ? null : `${index * (220 / Math.max(points.length - 1, 1))},${52 - point.rsi * 0.48}`).filter(Boolean).join(" ")}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2"
            />
            <text x="230" y="17" fill="#ef4444" fontSize="9">70</text>
            <text x="230" y="47" fill="#10a37f" fontSize="9">30</text>
          </svg>
        </div>
        <div className="subchart-panel">
          <div className="tiny-title">成交量</div>
          <div className="volume-bars">
            {points.map((point) => (
              <span
                key={point.date}
                className={point.close >= point.open ? "up" : "down"}
                style={{ height: `${Math.max((point.volume / maxVolume) * 62, 4)}px` }}
                title={`${point.date}：${point.volume.toLocaleString()}`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
