import { useState } from "react";
import { apiPost } from "../api/client";
import { Badge, Button, EmptyState, PageHeader, Panel } from "../components/Primitives";

type IndustryAnalysis = {
  industry_name: string;
  summary: string;
  upstream_companies: string[];
  midstream_companies: string[];
  downstream_companies: string[];
  core_companies: string[];
  related_tickers: string[];
  logic_summary: string;
  ai_conclusion: string;
  verification_items: string[];
};

export default function IndustryPage() {
  const [industry, setIndustry] = useState("AI基础设施");
  const [analysis, setAnalysis] = useState<IndustryAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);
    try {
      setAnalysis(await apiPost<IndustryAnalysis>("/api/industry/analyze", { industry_name: industry }));
    } finally {
      setLoading(false);
    }
  }

  const upstream = analysis?.upstream_companies ?? [];
  const midstream = analysis?.midstream_companies ?? [];
  const downstream = analysis?.downstream_companies ?? [];

  return (
    <div className="page page-industry">
      <PageHeader title="行业分析模块" description="手动输入行业，拆解上游、中游、下游、核心公司和待验证关系。" />
      <section className="input-band">
        <label>
          输入行业名称
          <input value={industry} onChange={(event) => setIndustry(event.target.value)} placeholder="AI基础设施 / CPO / 半导体 / 数据中心电力" />
        </label>
        <Button onClick={analyze} disabled={loading}>开始分析</Button>
        <Button variant="secondary" onClick={() => setIndustry("")}>清空</Button>
      </section>
      <div className="grid industry-grid">
        <Panel title="产业链全景图谱" caption="上游 / 中游 / 下游拆解，并标注核心受益公司与待验证关系。">
          <div className="supply-chain">
            <ChainColumn title="上游：资源 / 设备 / 零部件" items={upstream} />
            <ChainColumn title="中游：制造 / 集成 / 平台" items={midstream} />
            <ChainColumn title="下游：客户 / 应用 / 需求" items={downstream} />
          </div>
        </Panel>
        <Panel title="核心公司雷达" caption="无法验证的公司关系必须标注待验证。">
          <div className="list">
            {(analysis?.core_companies ?? []).map((company, index) => (
              <div className="company-row" key={company}>
                <strong>{company}</strong>
                <span>AI 输出核心公司</span>
                <Badge tone={index < 2 ? "good" : "warn"}>{index < 2 ? "直接相关" : "待验证"}</Badge>
              </div>
            ))}
            {!analysis?.core_companies.length ? <EmptyState text="开始分析后显示核心公司与相关等级。" /> : null}
          </div>
        </Panel>
      </div>
      <Panel title="AI行业逻辑摘要" className="wide-panel">
        {analysis ? (
          <div className="analysis-block horizontal">
            <div>
              <h3>{analysis.industry_name}</h3>
              <p>{analysis.summary}</p>
            </div>
            <div>
              <h3>相关美股代码</h3>
              <p>{analysis.related_tickers.join(", ") || "待验证"}</p>
            </div>
            <div>
              <h3>AI分析结论</h3>
              <p>{analysis.ai_conclusion}</p>
            </div>
            <div>
              <h3>待验证事项</h3>
              <ul>{analysis.verification_items.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          </div>
        ) : (
          <EmptyState text="输入行业并开始分析。若数据不足，系统会明确标注待验证。" />
        )}
      </Panel>
    </div>
  );
}

function ChainColumn({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="chain-column">
      <h3>{title}</h3>
      {items.map((item) => <div className="chain-node" key={item}>{item}</div>)}
      {!items.length ? <div className="chain-empty">等待 AI 分析结果</div> : null}
    </div>
  );
}
