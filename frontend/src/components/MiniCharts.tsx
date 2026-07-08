const candles = [34, 42, 50, 38, 54, 60, 70, 52, 66, 82, 62, 90, 72, 98];
const volumes = [24, 36, 20, 48, 34, 58, 42, 54, 36, 64, 46, 68];

export function MarketChart({ title }: { title: string }) {
  return (
    <div className="chart-box">
      <div className="chart-title">{title}</div>
      <div className="legend-row">
        <span>MA20</span>
        <span>MA50</span>
        <span>MA120</span>
        <span>MA250</span>
      </div>
      <svg className="chart-svg" viewBox="0 0 560 220" role="img" aria-label={title}>
        {[40, 80, 120, 160].map((y) => (
          <line key={y} x1="20" x2="540" y1={y} y2={y} stroke="#e5e7eb" />
        ))}
        {candles.map((height, idx) => {
          const x = 36 + idx * 34;
          const y = 170 - height;
          return (
            <g key={idx}>
              <line x1={x + 5} x2={x + 5} y1={y - 10} y2={175 - idx * 2} stroke={idx % 3 === 0 ? "#b91c1c" : "#047857"} strokeWidth="2" />
              <rect x={x} y={y} width="10" height={height * 0.55} rx="1" fill={idx % 3 === 0 ? "#ef4444" : "#10b981"} />
            </g>
          );
        })}
        <polyline points="30,124 80,116 130,108 180,98 230,92 280,84 330,76 380,72 430,64" fill="none" stroke="#2563eb" strokeWidth="2" />
        <polyline points="30,138 80,132 130,126 180,116 230,108 280,102 330,94 380,88 430,84" fill="none" stroke="#ca8a04" strokeWidth="2" />
        <polyline points="30,154 80,150 130,146 180,138 230,132 280,126 330,120 380,114 430,108" fill="none" stroke="#7c3aed" strokeWidth="2" />
        <polyline points="30,174 80,170 130,166 180,160 230,154 280,148 330,142 380,136 430,130" fill="none" stroke="#334155" strokeWidth="2" />
      </svg>
      <div className="subcharts">
        <div>
          <div className="tiny-title">RSI</div>
          <svg viewBox="0 0 180 54">
            <line x1="0" x2="180" y1="14" y2="14" stroke="#fca5a5" />
            <line x1="0" x2="180" y1="40" y2="40" stroke="#93c5fd" />
            <polyline points="0,38 28,32 54,34 82,24 108,20 136,16 170,22" fill="none" stroke="#0f766e" strokeWidth="2" />
          </svg>
        </div>
        <div>
          <div className="tiny-title">成交量</div>
          <div className="volume-bars">
            {volumes.map((height, idx) => (
              <span key={idx} style={{ height }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

