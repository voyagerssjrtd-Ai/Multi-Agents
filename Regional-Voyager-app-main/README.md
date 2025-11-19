Run this before running any scripts in the powershell terminal

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

npm config set strict-ssl false

npm config set registry http://registry.npmjs.org/

npm install

npm run dev


uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

⚙️ PHASE 1 – DATA & DATABASES

Design schemas (SQLite)

Tables: products, inventory, sales, suppliers, sku_forecasts, audit_log.

Design schemas (DuckDB)

TablesViews: sales_/history, aggregated_sales, sku_features.

Load seed data

Historical sales CSV → DuckDB.

Current inventory & products → SQLite.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📡 PHASE 2 – KAFKA + STREAMING PIPELINE

Bring up infra via Docker Compose

Kafka + Zookeeper

Redis

Prometheus

Grafana

Create Kafka topics

sales_events

inventory_updates

forecast_events

alert_events

Implement Sale Simulator

Simple Python script:

Generates random sales.

Publishes to sales_events.

Implement InventoryUpdateService

Consumes sales_events.

Writes to sales (SQLite).

Updates inventory.qty (SQLite + Redis).

Writes inventory_updates to Kafka.

Updates Prometheus metric: inventory_stock{sku}.

Implement Stream-to-DuckDB

Batch/stream exporter from SQLite → DuckDB (for analytics & model training).
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📈 PHASE 3 – FORECASTING ENGINE (ARIMA/SARIMAX/LSTM)

Offline training (not in real-time yet)

Use DuckDB queries to pull SKU time-series.

Train:

ARIMA / SARIMAX per SKU.

LSTM global model (optional, PyTorch/Keras).

Save models under models/arima/, models/lstm/.

Create models/model_map.yaml mapping sku → model_type.

Online ForecastingEngine service

Consumes sales_events from Kafka.

Maintains rolling data windows per SKU (in memory or Redis).

On schedule or N events:

Loads correct model (from model_map.yaml).

Runs forecast for horizon (e.g., 7–14 days).

Computes:

expected_stockout_date

recommended_reorder_qty.

Writes to:

forecast_events topic.

sku_forecasts table in SQLite or DuckDB.

Prometheus metrics: forecast_demand{sku}, stockout_risk_days{sku}.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📚 PHASE 4 – FAISS + RAG LAYER

Prepare unstructured docs

Supplier notes, PO history, past stockouts, promo plans → text chunks.

Build FAISS index

Use azure/genailab-maas-text-embedding-3-large to create embeddings.

Store vectors + metadata in FAISS index (faiss.index file).

Save meta JSON with mapping id → text, sku, tags.

Create RAG_Agent helper

Function: retrieve_context(query, sku) → top-k docs from FAISS.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🧠 PHASE 5 – LANGGRAPH MULTI-AGENT SYSTEM

Define shared state

session_id, user_id, user_query_text, intent, db_data, forecast_data, rag_context, analysis, final_response, actions.

Implement each agent as a LangGraph node

VoiceIO_Agent → Whisper for audio → text.

Guardrail_Agent → input cleaning, role check, basic filters.

QueryRouter_Agent (gpt-4o-mini) → intent classification + route list.

DB_Query_Agent:

Uses Llama-3.3-70B to choose SQL template + params.

Executes only whitelisted, parameterized SQL.

RAG_Agent:

Calls FAISS retrieval.

Forecasting_Agent:

Reads from Forecast Engine API or sku_forecasts table.

Uses Phi-4 to combine numeric forecast + RAG + DB data → structured recommendation.

Analytics/Report_Agent:

Uses gpt-35-turbo / gpt-4o for summaries, RCA explanations.

ResponseAssembler_Agent:

Uses gpt-4o to merge everything into a final answer.

Adds recommended actions: CREATE_PO, DISCOUNT, TRANSFER_STOCK.

NotificationAgent:

Publishes alert_events to Kafka when needed.

Writes to audit_log.

Define LangGraph edges

Pipeline for typical replenishment query:

VoiceIO → Guardrail → Router → DB → Forecasting → RAG → Analytics → Assembler → Notification.

Expose LangGraph as HTTP API

POST /chat for text queries.

POST /voice for audio queries.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🖥️ PHASE 6 – FRONTEND (UI + Voice)

Build minimal React UI

Text chat box + history.

Mic button to record → send audio to /voice.

Table to show recommended SKUs and reorder qty.

Status indicator for alerts.

Integrate with LangGraph API

Call /chat or /voice.

Render final_response + actions nicely.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📊 PHASE 7 – DASHBOARDS & ALERTS

Prometheus exporters

From:

InventoryUpdateService (stock)

ForecastingEngine (forecast & risk)

LangGraph (latency, error counts)

Create Grafana dashboards

Inventory Overview:

inventory_stock{sku}, OOS count, depot filters.

Forecast & Risk:

forecast_demand{sku}, stockout_risk_days{sku}.

Overstock / Slow Movers:

Use DuckDB queries, maybe via API.

System Health:

Kafka lag, API latencies, errors.

Configure alerts

Stockout risk:

stockout_risk_days{sku} < lead_time + buffer.

Overstock:

High qty + many days without sales.

Show alerts in Grafana + optionally send via webhook/email.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🔐 PHASE 8 – SECURITY, GOVERNANCE & FAILOVER

Auth & RBAC

Issue simple JWTs or integrate Keycloak.

Include user roles in token (manager, picker, auditor).

Guardrail_Agent enforces what each role can ask/see.

Guardrails & Validation

Input filters (no raw SQL, no system prompts).

Output filters (no PII, no cross-department leakage).

Log all requests in audit_log.

Failover mechanisms

If Forecast Engine down:

Forecasting_Agent falls back to:

Moving average from DuckDB.

Simple safety-stock-based reorder.

If Kafka down:

Temporarily write events directly to SQLite and buffer.

If RAG/FAISS down:

Skip context; tell user explanation may be limited.

Slow-moving stock logic

Batch job in DuckDB:

Identify SKUs with high stock + low sales.

Mark them as slow movers.

NotificationAgent triggers actions:

Suggest discounts, bundling, supplier return, or transfers.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🧪 PHASE 9 – TESTING & DEMO SCRIPT

Scenario tests

Simulate fast sales → see stock drop, forecast update, alerts fire.

Ask:

“When will SKU X run out?”

“How much should I order today?”

“Why did we overstock SKU Y?”

“What should I do with 90-day old stock of SKU Z?”

Prepare demo script

Start dashboards on big screen.

Start sale simulator.

Use voice query → show full agent flow + Grafana reaction.

Close with “how we can reuse the same platform for other domains”.
