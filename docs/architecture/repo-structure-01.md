Below is a drop‑in llm.context.md you can place at the root of the monorepo.
It is intentionally project‑agnostic in tone, v0‑specific in facts, and designed to be the single entry point for any AI agent (or human) to discover everything it needs—by following links and file paths from here.

⸻

llm.context.md

Purpose: This is the entry point for AI agents (and humans) working in this monorepo.
It tells you what this project is, how it is organized, which contracts are canonical, what invariants you must preserve, and where to look next.
If you only read one file, read this. It will route you to everything else.

⸻

1) Project Identity (v0)
	•	Name: Wishflower Platform v0 (experimentation platform for personalized shopping)
	•	Scope (v0): A working end‑to‑end path for US‑1 Discovery Chat:
	•	User submits a query → hybrid search (keyword + vector) over a fake catalog → assistant reply → product results.
	•	Seven primitives present:
	1.	Event Bus (Kafka API; local: Redpanda)
	2.	Stateful Orchestrator (Temporal; Python worker)
	3.	System of Record (Postgres + pgvector)
	4.	Stateless Services (Rust API Gateway; FastAPI AI Gateway; Python workers)
	5.	Universal Observability (OpenTelemetry → Jaeger/Prom/Loki/Grafana)
	6.	Data Lake & Analytics (MinIO S3 archive; ClickHouse analytics)
	7.	Presentation Layer (Next.js UI with SSE)
	•	Deliberate v0 constraints (do not change unless instructed):
	•	Embeddings are 64‑D (stub/deterministic); DB column vector(64).
	•	SSE (Server‑Sent Events) for UI streaming; not WebSockets in v0.
	•	Conversation history lives in workflow memory; DB is an audit log (append‑only).
	•	No auth in v0; single demo user/session is acceptable.
	•	AI calls are stubbed via AI Gateway; no external provider calls.
	•	Images: placeholder assets only; no licensed third‑party images.

⸻

2) Repository Topography (authoritative map)

/                      # repo root (this file lives here)
├─ platform/           # type: platform (shared, canonical contracts)
│  └─ schemas/         # Protobuf + OpenAPI sources (single source of truth)
│
├─ libraries/          # type: library (shared generated & helpers)
│  ├─ rs-protos/       # generated Rust (prost/tonic) from Protobuf
│  ├─ py-protos/       # generated Python (betterproto)
│  ├─ ts-client/       # generated TypeScript client from OpenAPI
│  ├─ obs-rs/          # (optional) Rust OTEL helpers
│  └─ obs-py/          # (optional) Python OTEL helpers
│
├─ products/           # type: product (leaf, runnable apps)
│  ├─ ui-web/          # Next.js UI (SSE client)
│  ├─ gateway-rust/    # Rust Axum API Gateway (POST + SSE)
│  ├─ ai-gateway-py/   # FastAPI AI Gateway (stubs)
│  ├─ orchestrator-py/ # Temporal worker + HTTP bridge
│  ├─ analytics-consumer-py/ # Kafka → ClickHouse
│  └─ archive-writer-py/     # Kafka → MinIO (S3) archive
│
├─ data/               # type: data (files; not code libs)
│  ├─ db/
│  │  ├─ migrations/   # SQL migrations (pg + pgvector)
│  │  └─ seed/         # products.jsonl, placeholder image configs, etc.
│  └─ infra/
│     ├─ otel/collector.yaml
│     └─ grafana-provisioning/
│
├─ tooling/            # type: tooling (scripts, aspects, generators)
│  ├─ schema_codegen/  # buf/openapi generator scripts/configs
│  └─ boundary_checker/# Bazel boundary aspect (optional)
│
├─ .workspace/         # Bazel workspace metadata & templates
│  ├─ component_types.bzl
│  ├─ boundary_rules.bzl
│  └─ templates/
│
├─ infra/              # container orchestration (compose), local services
│  └─ docker-compose.yml
│
├─ libs/               # (alias path; may mirror libraries/) — if present
│
├─ README.md           # human quickstart (run/build details live here)
├─ DECISIONS.md        # architectural decisions & rationale
└─ ARCHITECTURE.md     # high-level architecture (human-oriented)

Agents: treat paths in this section as canonical. Prefer following links here over ad‑hoc project search.

⸻

3) Canonical Contracts & Interfaces

3.1 Protobuf (internal RPC + events) — Single source of truth
	•	Location: platform/schemas/**/*.proto
	•	Generates:
	•	Rust crate: libraries/rs-protos/
	•	Python package: libraries/py-protos/
	•	Versioning: package.x.v1 style (e.g., ai_gateway.v1, chat.v1).
	•	Rules:
	•	Add fields; never remove. Deprecate, then drop in a later major.
	•	No breaking renames. Add new field; migrate consumers.

Key messages (v0):
	•	chat.v1.Correlation { trace_id, interaction_id, session_id, user_id, ts_ms }
	•	chat.v1.ChatMessageSubmitted
	•	chat.v1.AiIntentParsed
	•	chat.v1.SearchExecuted
	•	chat.v1.SearchResultsReady
	•	chat.v1.UiResponseSent
	•	ai_gateway.v1.GenerateRequest/Response, EmbedRequest/Response, ListModels*

3.2 OpenAPI (external UI API)
	•	Location: platform/schemas/openapi.yaml
	•	Generates: libraries/ts-client/
	•	Endpoints (v0):
	•	POST /api/chat/message → 202 Accepted
	•	GET /api/stream?sessionId=... → SSE stream

3.3 AI Gateway HTTP Contract (v0)
	•	Endpoints:
	•	POST /v1/chat/generate — supports response_format: "text" | "structured"
	•	POST /v1/embeddings — returns 64‑D vectors
	•	GET /v1/models — model roster + routing rules
	•	GET /v1/health
	•	Preferences: fast | balanced | high_quality | specialized
	•	Structured output: provide JSON Schema in structured_schema (HTTP) / structured_schema_json (gRPC) and Gateway must validate.

⸻

4) Eventing & Telemetry (must follow)

4.1 Kafka Topics (logical names)
	•	chat.interactions
	•	ai.intent
	•	search.executed
	•	search.results_ready
	•	ui.updates (Gateway → UI SSE)
	•	ai.reasoning (AI Gateway reasoning log)
	•	(Optional) ai.cost_exceeded

4.2 Message Headers (propagation)

All produced messages must include headers:

Header	Value
traceparent	W3C trace context
tracestate	W3C trace state
interaction_id	UUID string
session_id	Session identifier
user_id	User identifier

Do not invent new keys for correlation. Use these names.

4.3 SSE Envelope (UI updates)

Payload emitted by ui.updates and forwarded to SSE:

{
  "type": "search.results",
  "interaction_id": "int-...",
  "assistant_message": { "text": "I found 12 options..." },
  "products": [
    { "sku": "JK-BYFALL-0001", "name": "Sierra Trail Shell", "price_cents": 17900, "image": "s3://wishflower-assets/products/JK-BYFALL-0001/image_1.jpg" }
  ]
}

Field names are frozen in v0: type, interaction_id, assistant_message.text, products[*].{sku,name,price_cents,image}.

4.4 AI Reasoning Event (canonical shape)

Emitted by the AI Gateway for every request:

{
  "interaction_id": "int-abc123",
  "timestamp": "2025-10-17T10:35:22Z",
  "endpoint": "/v1/chat/generate",
  "use_case": "intent_extraction",
  "model_preference_requested": "fast",
  "model_used": "gpt-4o-mini-2024-07-18",
  "provider": "openai",
  "request": { "messages": [/* redacted/truncated */], "parameters": {/* … */} },
  "response": { "content": {/* structured or text */}, "finish_reason": "stop" },
  "performance": { "latency_ms": 234, "tokens": { "prompt": 87, "completion": 45, "total": 132 }, "cost_usd": 0.000264 },
  "privacy": { "redacted": true }
}

Redaction policy (v0): mask emails/phones; truncate oversized fields.

⸻

5) Data & Storage Conventions

5.1 Database (Postgres + pgvector)
	•	Migrations: data/db/migrations/
	•	Tables (v0 minimal):
	•	products:
	•	embedding vector(64) (mandatory 64‑D)
	•	tsv tsvector (generated, GIN index)
	•	fields: id, sku, name, brand, category, price_cents, currency, description, …
	•	conversations (append‑only audit log; not read for context in v0)
	•	Indexes:
	•	GIN(tsv); ivfflat(embedding vector_cosine_ops)

If you change the DB schema, you must add a migration and update any typed models and queries in code.

5.2 Object Storage (MinIO S3)
	•	Assets: s3://wishflower-assets/products/{SKU}/image_{1..3}.jpg
	•	Archive: s3://wishflower-events/YYYY/MM/DD/topic=<TOPIC>/part-*.jsonl
	•	Policy: Only local/generated images in v0 (no licensed/external images).

5.3 ClickHouse (Analytics)
	•	Base table: events_raw(ts DateTime, topic String, interaction_id String, payload JSON)
	•	Views: e.g., mv_search_kpis for response counts/latency.

⸻

6) Observability (what to instrument)
	•	Trace every request end‑to‑end; use attributes:
	•	interaction_id, session_id, user_id, component, use_case, model_preference, model_used.
	•	Metrics (examples):
	•	chat_end_to_end_ms (histogram)
	•	pg.hybrid_query_ms
	•	ai_gateway_latency_ms, ai_gateway_cost_usd
	•	Logs: JSON, include correlation fields; avoid dumping large payloads (respect redaction).

Collector config: data/infra/otel/collector.yaml
Dashboards: data/infra/grafana-provisioning/

⸻

7) Bazel Boundaries (validation only in v0)

Bazel is used to validate structure & dependencies, not to build/run services in v0.
	•	Types: platform, library, product, tooling, data, test
	•	Rules:
	•	Products must not depend on products.
	•	Code must not import data/ as code; use data = [...] file inputs.
	•	Default visibility = private. Open only what you must.
	•	Where:
	•	Types: .workspace/component_types.bzl
	•	Aspect: .workspace/boundary_rules.bzl
	•	Templates: .workspace/templates/

If you add a new component, include a COMPONENT.yaml and LLM-CONTEXT.md in that component’s root. Use the templates.

⸻

8) AI Gateway Contracts (essentials to use)
	•	Prefer preferences over model IDs: fast | balanced | high_quality | specialized.
	•	Structured outputs must conform to the provided JSON Schema; the Gateway retries on schema mismatch and fails with invalid_schema if persistent.
	•	Embeddings: enforce dimensions = 64 in v0. Return 400 for mismatches.
	•	Models roster & routing exposed via /v1/models (backed by routing.yml).

⸻

9) Hybrid Search Conventions
	•	Keyword: plainto_tsquery('simple', …) over tsv.
	•	Vector: ORDER BY embedding <-> $vector::vector LIMIT N.
	•	Fusion: Reciprocal Rank Fusion (RRF) or simple score sum; keep deterministic.
	•	Filters: Prefer SQL filters over post‑filtering when possible (but v0 can filter in code if simpler).

⸻

10) Contribution Rules (agents & humans)

When you add/modify a cross‑service interface:
	1.	Edit Protobuf / OpenAPI under platform/schemas/.
	2.	Regenerate code (see tooling/schema_codegen/).
	3.	Update all callers and servers that use the contract.
	4.	Add/update migrations if the change affects persisted state.
	5.	Add/verify telemetry (trace + metrics + logs).
	6.	Emit/consume the right Kafka events with correct headers.
	7.	Update this file only if top‑level invariants or paths change.
	8.	Update DECISIONS.md if you’re changing a deliberate v0 constraint.

Never do in v0:
	•	Introduce non‑64‑D embeddings or change the products.embedding type.
	•	Switch from SSE to WS without consensus.
	•	Read from conversations for context (v0 keeps history in workflow memory).
	•	Add new correlation header names.
	•	Include licensed third‑party images.

PR Checklist (short):
	•	Contracts updated (if applicable) and generated code committed.
	•	Migrations present & idempotent.
	•	Trace propagation verified (headers present).
	•	Events validated against canonical shapes.
	•	Logs redact sensitive tokens/PII.
	•	Dashboards/metrics still populate.

⸻

11) Glossary (canonical terms)
	•	Interaction: One user request + its system processing chain; identified by interaction_id.
	•	Session: UI session; identified by session_id.
	•	Workflow: Temporal durable sequence handling a chat turn (ChatSessionWorkflow).
	•	AI Gateway: Single abstraction for model calls; returns structured results when asked.
	•	Archive: Raw event copies in S3‑compatible storage (MinIO locally).
	•	Analytics: Aggregations in ClickHouse; UI via Grafana.

⸻

12) Where to look next (routing table)
	•	Contracts (Protobuf/OpenAPI) → platform/schemas/
	•	Generated clients/structs → libraries/rs-protos/, libraries/py-protos/, libraries/ts-client/
	•	DB schema & seeds → data/db/migrations/, data/db/seed/
	•	Observability config → data/infra/otel/collector.yaml, data/infra/grafana-provisioning/
	•	Kafka topics → defined by producers/consumers in products/* (event names in §4.1)
	•	AI Gateway config → products/ai-gateway-py/ (e.g., routing.yml, providers config)
	•	App services → products/gateway-rust/, products/orchestrator-py/, products/ui-web/, products/analytics-consumer-py/, products/archive-writer-py/
	•	Boundary rules → .workspace/
	•	Human run/build details → README.md
	•	Rationale and locked decisions → DECISIONS.md
	•	High‑level architecture → ARCHITECTURE.md

⸻

13) Agent Operating Notes (read carefully)
	•	Be conservative: Prefer editing contracts and generated code over ad‑hoc DTOs.
	•	Respect boundaries: If a change requires a forbidden dependency, propose a library in libraries/ instead.
	•	Prefer determinism: Seeded/deterministic stubs beat randomness (keeps tests stable).
	•	Keep payload names stable: If you must add fields, do so additively; do not rename existing fields.
	•	Minimize context: Start with files listed in §12; fetch more as needed; avoid repo‑wide sweeps.
	•	Safety: Never add secrets to code or events. Redact before emit.
	•	If ambiguous: Propose the contract change first (schema PR), then implementation.

⸻

End of llm.context.md

This file is the source of truth for how to find and understand things here. When in doubt, update this file first so future agents know where to look.