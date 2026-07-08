---
title: US Stock Decision System
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 美股交易决策辅助系统 MVP

Python FastAPI + React/TypeScript 全栈应用，包含 4 个互相独立的模块：

- 信息抓取和分析模块
- 行业分析模块
- 个股分析模块
- 市场仪表盘模块

系统只提供交易决策辅助，不接券商、不下单、不输出确定性买卖指令。

## 本地运行

后端：

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。前端默认请求 `http://localhost:8000`。

## 线上部署

仓库已包含一体化 `Dockerfile` 和 `render.yaml`。Render 会构建 React 前端，并由 FastAPI 同域托管静态文件。

部署步骤：

1. 推送代码到 GitHub 仓库。
2. 在 Render 新建 Blueprint，选择该 GitHub 仓库。
3. Render 会读取 `render.yaml` 创建 `market-decision-assistant` 服务。
4. 在 Render 环境变量中填入 `X_BEARER_TOKEN`、`FMP_API_KEY`、`ALPHA_VANTAGE_API_KEY`、`AI_API_KEY`。

部署后访问 Render 分配的服务 URL 即可查看系统。

## 环境变量

复制 `.env.example` 为 `.env`，填入真实密钥。缺少密钥时，后端会返回 `数据源待接入` 或 `待验证`，不会伪造市场数据。

## 合规约束

个股模块只允许输出：

- 辅助观察区间
- 风险区间
- 辅助决策等级：不参与、观察、等待确认、可重点关注、高风险，谨慎

禁止输出“立即买入”“立即卖出”“最佳买入价格”“最佳卖出价格”“保证盈利”“一定上涨”。
