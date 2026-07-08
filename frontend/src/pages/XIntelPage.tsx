import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPost } from "../api/client";
import { Badge, Button, EmptyState, PageHeader, Panel } from "../components/Primitives";

type XAccount = { handle: string; created_at: string; since_id?: string | null };
type XPost = { id: string; handle: string; text: string; created_at: string; source_status?: string };
type XAnalysis = {
  original_text: string;
  published_at: string;
  account: string;
  topics: string[];
  companies: string[];
  tickers: string[];
  truth_level: string;
  impact_direction: string;
  impact_strength: string;
  mapping_level: string;
  evidence_sources: string[];
  verification_items: string[];
};

export default function XIntelPage() {
  const [handle, setHandle] = useState("");
  const [accounts, setAccounts] = useState<XAccount[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [posts, setPosts] = useState<XPost[]>([]);
  const [analysis, setAnalysis] = useState<XAnalysis | null>(null);
  const [selectedPost, setSelectedPost] = useState<XPost | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refreshAccounts() {
    const rows = await apiGet<XAccount[]>("/api/x/accounts");
    setAccounts(rows);
    if (!selected && rows[0]) setSelected(rows[0].handle);
  }

  async function refreshPosts(target = selected) {
    setLoading(true);
    try {
      const query = target ? `?handle=${encodeURIComponent(target)}` : "";
      setPosts(await apiGet<XPost[]>(`/api/x/posts${query}`));
      setError("");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshAccounts().catch((err) => setError(String(err)));
  }, []);

  useEffect(() => {
    refreshPosts(selected).catch((err) => setError(String(err)));
  }, [selected]);

  async function addAccount() {
    if (!handle.trim()) return;
    await apiPost<XAccount>("/api/x/accounts", { handle });
    setHandle("");
    await refreshAccounts();
  }

  async function removeAccount(value: string) {
    await apiDelete(`/api/x/accounts/${value}`);
    setSelected("");
    await refreshAccounts();
  }

  async function analyze(post: XPost) {
    setLoading(true);
    setSelectedPost(post);
    try {
      setAnalysis(await apiPost<XAnalysis>(`/api/x/posts/${post.id}/analyze`));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page page-x-intel">
      <PageHeader title="信息抓取和分析模块" description="持续跟踪指定 X 账号，分析真实性、相关主题、公司映射和待验证事项。" />
      <section className="input-band">
        <label>
          输入 X 账号，最多 15 个
          <input value={handle} onChange={(event) => setHandle(event.target.value)} placeholder="@Semianalysis / @nvidia" />
        </label>
        <Button onClick={addAccount}>添加账号</Button>
        <Button variant="secondary" onClick={() => setHandle("")}>清空输入</Button>
        <Badge tone="info">当前 {accounts.length} / 15</Badge>
      </section>
      {error ? <div className="error-line">{error}</div> : null}
      <div className="grid x-grid">
        <Panel title="跟踪账号" caption="点击账号查看该账号输出内容。">
          <div className="list">
            {accounts.map((account) => (
              <button key={account.handle} className={`list-row ${selected === account.handle ? "selected" : ""}`} onClick={() => setSelected(account.handle)}>
                <span>@{account.handle}</span>
                <Badge tone={selected === account.handle ? "good" : "neutral"}>{selected === account.handle ? "当前" : "输出"}</Badge>
                <span className="row-action" onClick={(event) => { event.stopPropagation(); removeAccount(account.handle); }}>移除</span>
              </button>
            ))}
            {!accounts.length ? <EmptyState text="尚未添加账号。配置 X API 后可开始跟踪真实内容。" /> : null}
          </div>
        </Panel>
        <Panel title="按账号输出内容" caption={selected ? `当前账号：@${selected}` : "等待选择账号"}>
          <div className="stack">
            {posts.map((post) => (
              <article className="feed-card" key={post.id}>
                <div className="feed-meta">
                  <strong>@{post.handle}</strong>
                  <span>{post.created_at || "时间待验证"}</span>
                </div>
                <p>{post.text}</p>
                <div className="row-between">
                  <Badge tone={post.source_status === "数据源待接入" ? "warn" : "neutral"}>{post.source_status ?? "未分析"}</Badge>
                  <Button onClick={() => analyze(post)} disabled={loading}>AI分析</Button>
                </div>
              </article>
            ))}
            {!posts.length ? <EmptyState text={loading ? "正在抓取..." : "暂无输出内容"} /> : null}
          </div>
        </Panel>
        <Panel title="AI 分析输出栏" caption="真实性、映射关系、证据来源和待验证事项。">
          {analysis ? (
            <div className="analysis-block">
              <div className="current-analysis-object">
                <h3>当前分析对象</h3>
                <p>账号：@{selectedPost?.handle || analysis.account}</p>
                <p>内容：{selectedPost?.text || analysis.original_text}</p>
              </div>
              <Badge tone="info">真实性：{analysis.truth_level}</Badge>
              <Badge tone="neutral">映射：{analysis.mapping_level}</Badge>
              <h3>相关主题</h3>
              <p>{analysis.topics.join(" / ") || "待验证"}</p>
              <h3>相关公司</h3>
              <p>{analysis.companies.join(" / ") || "待验证"}</p>
              <h3>相关股票代码</h3>
              <p>{analysis.tickers.join(", ") || "待验证"}</p>
              <h3>影响方向与强度</h3>
              <p>{analysis.impact_direction} · {analysis.impact_strength}</p>
              <h3>证据来源</h3>
              <p>{analysis.evidence_sources.join(" / ") || "待验证"}</p>
              <h3>待验证事项</h3>
              <ul>{analysis.verification_items.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          ) : (
            <EmptyState text="选择某条内容并点击 AI分析 后显示结果。" />
          )}
        </Panel>
      </div>
    </div>
  );
}
