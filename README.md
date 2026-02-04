# Algo Trading Bot Manager (AlgoAgentMgr)

## 1) Clarifying questions (≤8) + defaults

**Questions**
1. Do you want SPY-only execution for the SPX proxy in phase 1, or also paper-trade SPX index signals for monitoring? (Default: SPY execution only; SPX used for monitoring/regime.)
2. Preferred base currency for portfolio analytics and risk limits (USD, USDT, or both)? (Default: USD with USDT treated as cash-equivalent.)
3. Target region/regulatory constraints for Robinhood usage (e.g., US-only)? (Default: US-only, with explicit API key/credentials gating.)
4. Preferred data providers for SPY/SPX minute data (e.g., Polygon, IEX Cloud, Nasdaq Data Link)? (Default: pluggable provider; recommend Polygon for intraday + caching.)
5. Risk model preference: simple limits only or include VaR/CVaR and stress tests? (Default: include VaR/CVaR + scenario shocks.)
6. Do you require on-prem/self-hosted deployment first, or is managed cloud acceptable? (Default: self-hosted Docker Compose for MVP; cloud-ready for V1.)
7. Alerting channels to prioritize (email, SMS, Slack, webhook)? (Default: email + webhook.)

**Defaults applied for implementation**
- Portfolio currency: USD, USDT treated as cash-equivalent.
- Execution: SPY via Robinhood adapter (stub if equities API not available), BTC via Hyperliquid.
- Data: pluggable provider layer with Polygon recommended; cache + parquet for OHLCV.
- Deployment: Docker Compose MVP; cloud-ready V1.
- Alerts: email + webhook.

---

## 2) PRD + user journeys + screen layouts

### PRD
**Target user**
- Retail power users and semi-pro traders who want institutional-grade controls without quant dev overhead.

**Jobs-to-be-done (JTBD)**
- “I want to design strategies quickly and know the results are trustworthy.”
- “I want to deploy bots safely with strict risk controls.”
- “I want a clear portfolio-level view of risk, correlation, and regime exposure.”

**Success metrics**
- Time-to-first-backtest < 15 minutes.
- Backtest Trust Score average ≥ 70 for deployed strategies.
- 99.9% data pipeline uptime and < 1% missing-bar rate post-cleaning.
- < 1% live order reject rate (excluding intentional kills/safety rejects).

**Scope boundaries**
- Phase 1: BTC (Hyperliquid) + SPY (Robinhood adapter), SPX for monitoring/regimes only.
- No options/futures execution in phase 1 (design broker adapter to add later).
- No social trading or copy-trading in phase 1.

### Primary journeys
1. **Create strategy → backtest → review → paper → live deploy**
   - Strategy Builder → Backtest Lab → Backtest Report + Trust Score → Paper Deploy → Live Deploy (armed step).
2. **Bot monitoring**
   - Bots → Bot Detail (health, positions, P&L, drawdown, alerts).
3. **Portfolio dashboard**
   - Home Dashboard → Portfolio Analytics (equity curve, exposure, correlation, regime breakdown).
4. **Regime Lab → connect regimes to strategy filters**
   - Regime Lab → choose model → create regime filter → attach to strategy rule set.

### Screen outlines
- **Home Dashboard**: equity curve, daily P&L, regime probabilities, alerts, open risk.
- **Bots**: table of bots with status, venue, P&L, drawdown, last heartbeat.
- **Bot Detail**: trade list, equity curve, positions, exposure, guardrail triggers.
- **Portfolio Analytics**: combined equity, drawdowns, correlation heatmap, regime attribution.
- **Backtest Lab**: run queue, parameter sweeps, walk-forward, Trust Score, export.
- **Strategy Builder**: low-code graph + code SDK panel, validation/errors.
- **Regime Lab (HMM)**: features, #states, model stability, regime probabilities.
- **Deploy Center**: arming checklist, risk limits, broker connection health.
- **Data Manager**: data sources, ingestion status, gaps, quality checks.
- **Alerts/Rules**: alert policy editor and history.
- **Settings**: API keys, role-based access, risk limits, billing.

---

## 3) Architecture diagram (ASCII ok) + stack recommendation

```
[Web App]
   | GraphQL/REST
[API Gateway/FastAPI]
   |----> [Backtest Service + Job Workers] ---[Redis Queue]---[Scheduler]
   |----> [Execution Service] ---> [Hyperliquid Adapter]
   |                             ---> [Robinhood Adapter/Stub]
   |----> [Regime Service (HMM)]
   |----> [Data Service] ---> [Providers] ---> [Cache/Parquet/DB]
   |----> [Portfolio Analytics Service]
   |----> [Observability Stack]

[Postgres] [Timescale/ClickHouse] [Object Storage]
```

**Stack**
- Frontend: Next.js + TypeScript + Tailwind.
- Backend API: FastAPI + Pydantic + SQLAlchemy.
- Backtest/Research: Python workers, Ray/Celery.
- Regime: hmmlearn or pomegranate + MLflow-style registry.
- Data: Polars + Parquet, TimescaleDB or ClickHouse for time-series.
- Queue/Orchestration: Redis + RQ/Celery + APScheduler.
- Observability: OpenTelemetry, Prometheus, Grafana, Loki.
- Secrets: Vault or AWS Secrets Manager; in MVP use local encrypted env.

---

## 4) Data model + API outline + job queue plan

### Core data model (high level)
- **User**: id, role, auth, settings
- **Bot**: id, name, strategy_id, venue, status, risk_profile
- **Strategy**: id, definition (DSL/SDK), version, params
- **BacktestRun**: id, strategy_id, datasets, config, trust_score, artifacts
- **Order/Fill**: order intent → fills, latency, slippage
- **PortfolioSnapshot**: equity, exposures, correlations, regime attribution
- **RegimeModel**: config, features, states, metrics, version hash
- **DataSet**: symbol, timeframe, provider, quality metrics

### API outline (REST)
- `GET /bots` `POST /bots` `PATCH /bots/{id}`
- `GET /bots/{id}/metrics`
- `POST /backtests` `GET /backtests/{id}`
- `GET /portfolio/summary` `GET /portfolio/analytics`
- `POST /regimes/train` `GET /regimes/models`
- `POST /deploy/paper` `POST /deploy/live`
- `POST /data/ingest` `GET /data/quality`

### Job queue plan
- **Queues**: `ingestion`, `backtest`, `regime-train`, `reporting`, `execution-monitor`
- **Workers**: stateless workers auto-scaling, idempotent job handlers
- **Schedulers**: periodic regime inference, data refresh, health checks

---

## 5) Backtest engine spec + bias guards + test plan

**Engine spec**
- Multi-timeframe event loop with deterministic seed and ordered bars.
- Execution model supports fees, spread, slippage, latency, partial fills, order types.
- Strategy interface consumes data bundles (per timeframe) and emits intents.

**Bias guards**
- Strict timestamp alignment and no future data in feature set.
- Train/validation/test splits with walk-forward option.
- Warnings for too many parameters, too small sample size, regime instability.
- Fill model includes realistic spread/impact, preventing optimistic fills.

**Backtest Trust Score**
- Penalize: no OOS, huge sweeps, unrealistic fills, tiny samples.
- Reward: walk-forward, conservative fills, stable regime alignment.

**Test plan**
- Unit tests for alignment, candle resampling, execution model.
- Integration tests for full backtest run with synthetic data.
- Regression tests for Trust Score thresholds.

---

## 6) Regime Lab/HMM pipeline + model registry spec

**Pipeline**
1. Feature generation (returns, vol, trend, drawdown, correlations, volume proxy).
2. Data normalization and missing-data handling.
3. HMM fit with selectable #states, AIC/BIC evaluation.
4. Stability checks across windows and perturbations.
5. Posterior regime probabilities and labels.

**Registry**
- Versioning includes training window, features, #states, seed, hash.
- Store metrics: AIC/BIC, stability score, predictive accuracy.
- Promote/demote model versions with audit trail.

---

## 7) Execution/deploy spec + safety checks

**Lifecycle**
- Draft → Backtested → Paper → Live → Paused/Stopped

**Safety checks**
- Pre-trade: max position, max daily loss, leverage, stale data, regime filter.
- Arming step: explicit human confirmation to go live.
- Monitoring: heartbeat, order rejects, slippage drift, feed health.
- Kill switch: manual + automated triggers.

---

## 8) Milestone build plan

**MVP (4–6 weeks)**
- Backtest engine, strategy builder MVP, data ingestion, bot lifecycle UI.
- Hyperliquid adapter (BTC), Robinhood stub (SPY).
- Regime Lab MVP with HMM + model registry.

**V1 (8–12 weeks)**
- Portfolio analytics with regime attribution.
- Advanced risk: VaR/CVaR + stress tests.
- Improved execution monitoring + alerting.

---

## 9) Initial repo scaffold (folders/modules) + key interface stubs

```
apps/web/               # Next.js frontend
services/api/           # FastAPI gateway
services/backtest/      # Backtest engine & workers
services/execution/     # Broker adapters
services/regime/        # HMM training/inference
services/data/          # Ingestion + quality checks
packages/shared/        # Shared domain models
infra/                  # Docker, infra scripts
jobs/                   # Job definitions
scripts/                # CLI helpers
```

Key interface stubs are included in:
- `services/api/main.py`
- `services/api/routers/*.py`
- `services/backtest/engine.py`
- `services/execution/adapters.py`
- `services/regime/hmm_pipeline.py`
- `services/data/ingestion.py`
- `packages/shared/models.py`
