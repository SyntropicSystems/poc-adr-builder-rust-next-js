# Platform Architecture: Real-Time AI-Enabled ADR Platform
## Version 4.0 — Production Reference Architecture

---

## Document Control

**Version:** 4.0 (Final for MVP Implementation)  
**Date:** October 2025  
**Status:** Approved for Implementation  
**Audience:** Engineering, Product, Infrastructure, Security  
**Scope:** Architectural decisions, technology choices, boundaries, and success criteria

**Purpose:** This document defines the complete production architecture for our AI-enabled ADR platform. It is the single source of truth for all architectural decisions and provides sufficient detail to derive implementation without prescribing implementation details.

---

## Executive Summary

### The Core Architecture Pattern

We are building a **dual-tier architecture** that separates real-time user interactions from complex background workflows:

**Synchronous Tier (Rust):** Handles all real-time, user-facing operations where latency is critical (<1 second). This includes chat streaming, CRUD operations, simple searches, and direct API interactions.

**Asynchronous Tier (Python):** Handles complex, multi-step workflows that inherently take seconds to minutes. This includes advanced RAG, document ingestion, crawling, agent orchestration, and experimentation.

**Event Bus (Kafka):** Provides the clean architectural boundary between these tiers, enabling independent scaling, clear failure isolation, and natural workflow orchestration.

### Why This Architecture

This is not a "two-language problem" (prototyping in Python, rewriting in Rust). Instead, it's a **two-language solution** where each language is used for what it does best:

- **Rust:** Excels at high-throughput request serving, streaming, concurrency, and operational reliability
- **Python:** Excels at complex ML workflows, rich ecosystem integration, and rapid experimentation
- **Kafka:** Enables clean separation, workflow orchestration, and independent evolution

The boundary is **conceptual** (synchronous vs asynchronous operations), not merely technological (Rust vs Python).

### Key Strategic Decisions

1. **Rust for sync tier:** Provider SDKs are mature, streaming is first-class, observability is excellent
2. **Python for async tier:** Complex RAG/agent frameworks (LangChain, LlamaIndex) are unmatched in maturity
3. **Kafka as boundary:** More elegant than gRPC-based integration; enables workflow orchestration naturally
4. **Connect RPC protocol:** Solves gRPC-Web browser compatibility while maintaining type safety
5. **Postgres + pgvector:** Single database for relational and vector data; migrate to dedicated vector DB only if needed
6. **Managed OIDC:** Don't build auth; use Clerk/Auth0
7. **Row-Level Security (RLS):** Defense-in-depth for multi-tenancy

---

## Core Requirements

### Functional Requirements

#### Content Management
- ADR lifecycle: Create, read, update, delete
- Versioning: Append-only history with rollback capability
- Organization: Tags, categories, relationships
- Search: Lexical (full-text) and semantic (vector similarity)

#### AI Features
- **Real-time chat:** Token-by-token streaming with sub-second first token
- **Content generation:** AI-assisted writing, summarization, expansion
- **Semantic search:** Find related ADRs using natural language
- **Recommendations:** Suggest relevant content based on context

#### Platform
- Web application (desktop and mobile responsive)
- Public pages with SEO optimization
- Future: Native mobile applications (iOS/Android)

### Non-Functional Requirements

#### Performance (Critical Priority)

**Explicit Latency Budget (p95):**

| Component | Target | Impact |
|-----------|--------|--------|
| First token to browser | < 350ms | User perceives "thinking" time |
| Inter-token gap | < 60ms | Smooth streaming experience |
| Interactive UI response | < 100ms | Perceived as instant |
| User cancellation propagation | < 100ms | Stop feels immediate |
| SSR page load (warm) | < 500ms | Acceptable for server render |

**What we control vs what we don't:**
- ✅ **Controllable:** Network hops (minimize), serialization (optimize), proxy overhead (reduce), UI rendering (optimize)
- ❌ **External:** Provider model inference time (~200ms), network physics (~65ms)

**Goal:** Minimize all controllable latency to near-zero.

#### Scalability
- Horizontal scaling for all tiers
- Handle 10,000+ concurrent chat streams
- Support millions of documents/embeddings
- Linear cost scaling with usage

#### Reliability
- 99.9% uptime target
- 99% stream completion rate
- <0.1% application error rate (excluding provider errors)
- Graceful degradation on provider failures

#### Type Safety
- Single source of truth: Protobuf schemas
- Generated code for all languages (Rust, TypeScript, Swift, Kotlin)
- Breaking changes caught at build time by Buf
- Zero runtime type mismatches

#### Security
- TLS 1.3 for external connections
- mTLS for internal service-to-service
- Row-Level Security (RLS) for multi-tenancy isolation
- Secrets in managed secret store (never in code/config)
- Egress allowlist (prevent SSRF/data exfiltration)

#### Cost Management
- Per-user and per-organization quotas
- Real-time spend tracking and alerts
- Automatic kill-switches at spend thresholds
- Free-tier abuse prevention

---

## Architectural Principles

These principles guide all architectural decisions and resolve ambiguity:

### 1. Latency Truthfulness
**If the user is waiting, it's synchronous. If they're not waiting, it's asynchronous.**

This is the fundamental decision criterion. Don't force async operations into the sync tier to maintain architectural "purity." Don't keep sync operations off the sync tier for "consistency."

### 2. Direct Hot Path
**For interactive features, minimize hops and translation layers.**

The path from browser to AI provider should be as direct as possible:
- Browser → Envoy → Rust → Provider (optimal)
- NOT: Browser → Envoy → Rust → Python → Provider (extra hop)

### 3. Single Source of Truth
**Protobuf defines all contracts. Generated code, not hand-written.**

One schema generates:
- Rust server code (tonic)
- TypeScript client code (Connect)
- Future: Swift/Kotlin for mobile

Breaking changes fail at CI, not production.

### 4. Hexagonal Services
**Domain logic is pure. Infrastructure is at the edges.**

Services have three layers:
- **Domain:** Pure business logic, no I/O
- **Application:** Use cases, orchestration
- **Adapters:** Database, HTTP, gRPC, event bus

This allows testing without infrastructure and swapping adapters without touching business logic.

### 5. Observability by Default
**If you can't measure it, you can't optimize it.**

Every request has:
- Distributed trace (traceparent header)
- Per-token latency metrics
- Structured logs with context

Observability is not bolted on; it's built in.

### 6. Least Privilege & Isolation
**Security in layers. Assume breach.**

- Database: RLS enforces tenant isolation even if application logic fails
- Secrets: Never in environment variables or config files
- Egress: Allowlist prevents exfiltration
- Authentication: Bearer tokens, not cookies (avoid CORS complexity)

### 7. Selective Technology Adoption
**Use the right tool for each job. Avoid dogma.**

Not "Rust everywhere" or "Python everywhere." Instead:
- Rust where: Performance critical, high concurrency, user-facing
- Python where: Rich ML ecosystem needed, rapid experimentation
- The boundary is clean and explicit (event bus)

---

## System Architecture

### High-Level Overview

```
┌────────────────────────────────────────────────────┐
│                  Client Layer                      │
│                                                    │
│  Next.js (App Router)                             │
│  ├─ Server Components (SSR, Node runtime)         │
│  └─ Client Components (gRPC-Web streaming)        │
│                                                    │
│  Mobile Web (Responsive)                          │
│  Native Mobile (Future: iOS/Android)              │
└────────────────────────────────────────────────────┘
            │
            │ gRPC-Web (binary Protobuf)
            │ via Connect Web client
            ↓
┌────────────────────────────────────────────────────┐
│              API Gateway (Envoy)                   │
│                                                    │
│  ├─ TLS termination                               │
│  ├─ CORS handling                                 │
│  ├─ JWT validation (jwt_authn filter)             │
│  ├─ gRPC-Web → gRPC translation                   │
│  └─ Request routing                               │
└────────────────────────────────────────────────────┘
            │
            │ gRPC (HTTP/2)
            ↓
┌────────────────────────────────────────────────────┐
│            Rust Services (Tonic gRPC)              │
│                                                    │
│  ADR Service                                       │
│  ├─ CRUD operations                               │
│  ├─ Versioning                                    │
│  └─ Search coordination                           │
│                                                    │
│  AI Gateway (Hot Path)                            │
│  ├─ Streaming chat (provider APIs)                │
│  ├─ Simple tool calling                           │
│  ├─ Provider routing & failover                   │
│  ├─ Caching & rate limiting                       │
│  └─ Token budgeting                               │
│                                                    │
│  Auth Service (Thin)                              │
│  └─ Claims augmentation (if needed)               │
└────────────────────────────────────────────────────┘
            │
            │ SQL (via connection pool)
            ↓
┌────────────────────────────────────────────────────┐
│            Postgres (Managed)                      │
│                                                    │
│  ├─ Relational data (ADRs, users, orgs)           │
│  ├─ Vectors (pgvector extension)                  │
│  ├─ Full-text search (tsvector)                   │
│  ├─ Job status tracking                           │
│  └─ Row-Level Security (RLS) enabled              │
└────────────────────────────────────────────────────┘

            ↕ (publish events / poll status)

┌────────────────────────────────────────────────────┐
│         Event Bus (Managed Kafka/Redpanda)         │
│                                                    │
│  Topics:                                          │
│  ├─ document.uploaded                             │
│  ├─ rag.search.requested                          │
│  ├─ embeddings.requested                          │
│  ├─ job.progress                                  │
│  └─ crawl.submitted                               │
└────────────────────────────────────────────────────┘
            │
            │ consume events
            ↓
┌────────────────────────────────────────────────────┐
│          Python Worker Tier (Async)                │
│                                                    │
│  Document Ingestion Worker                        │
│  ├─ PDF/DOCX/HTML parsing                         │
│  ├─ OCR (if needed)                               │
│  ├─ Text chunking                                 │
│  └─ Metadata extraction                           │
│                                                    │
│  Embedding Worker                                  │
│  ├─ Generate embeddings (API or local)            │
│  └─ Batch optimization                            │
│                                                    │
│  RAG Worker                                        │
│  ├─ Query expansion                               │
│  ├─ Multi-pass retrieval                          │
│  ├─ Cross-encoder reranking                       │
│  └─ Result synthesis                              │
│                                                    │
│  Agent Worker                                      │
│  ├─ Multi-step reasoning                          │
│  ├─ Tool orchestration                            │
│  └─ Complex workflows                             │
│                                                    │
│  Crawler Worker                                    │
│  ├─ Web scraping                                  │
│  ├─ Anti-bot handling                             │
│  └─ Content extraction                            │
│                                                    │
│  All workers:                                      │
│  ├─ Consume from Kafka                            │
│  ├─ Publish progress events                       │
│  └─ Write results to Postgres/pgvector            │
└────────────────────────────────────────────────────┘
```

### Tier Characteristics

| Aspect | Synchronous Tier (Rust) | Asynchronous Tier (Python) |
|--------|------------------------|----------------------------|
| **Latency** | <1 second (sub-100ms ideal) | Seconds to minutes (10s-10m typical) |
| **User state** | Actively waiting | Submitted job, doing other things |
| **Concurrency** | Thousands of concurrent operations | Tens to hundreds of workers |
| **Failure mode** | Return error immediately | Retry, DLQ, eventual consistency |
| **Scaling** | Horizontal (stateless services) | Horizontal (add workers per topic) |
| **Language choice** | Rust (performance, reliability) | Python (ecosystem, experimentation) |
| **Communication** | gRPC (request/response, streaming) | Kafka (events, at-least-once) |
| **Observability** | Per-request traces, real-time metrics | Job progress, batch metrics |

---

## Critical Architectural Decisions

### Decision 1: Rust for Synchronous Tier

**Decision:** All real-time, user-facing operations use Rust services with gRPC.

**Rationale:**

1. **Provider SDK Maturity:** Rust SDKs for Anthropic, OpenAI, and Gemini are production-ready with first-class async/streaming support
2. **Not "ML in Rust":** We're building an API gateway, not training models. Rust's web/async ecosystem is world-class.
3. **Performance:** 10x higher throughput than Python for request serving (benchmarked)
4. **Reliability:** No GIL, no garbage collection pauses, compile-time safety
5. **Concurrency:** True parallelism for thousands of concurrent streams

**What we DON'T need from Rust:**
- ❌ ML training frameworks (Burn, Candle)
- ❌ Classical ML algorithms (linfa)
- ❌ Local model inference (initially)
- ❌ DataFrame processing (Polars)

**What we DO need (all mature in Rust):**
- ✅ Async HTTP clients (reqwest, hyper)
- ✅ Streaming support (tokio-stream)
- ✅ gRPC server (tonic)
- ✅ JSON/Protobuf serialization (serde, prost)
- ✅ Database clients (sqlx, tokio-postgres)

**Dependencies:**
- `tokio` - Async runtime
- `tonic` - gRPC server framework
- `reqwest` - HTTP client for provider APIs
- `sqlx` - Async Postgres client
- `serde` - Serialization
- `prost` - Protobuf
- `tracing` - Observability

**Alternative considered:** Python with FastAPI
- **Rejected because:** GIL limits concurrent streams, garbage collection causes latency spikes, 10x lower throughput

### Decision 2: Python for Asynchronous Tier

**Decision:** All complex, multi-step workflows use Python workers communicating via Kafka.

**Rationale:**

1. **Ecosystem Maturity:** LangChain, LlamaIndex, AutoGen, CrewAI are unmatched for complex RAG/agents
2. **Pre-built Components:** 100+ document loaders, dozens of retrievers, many agent frameworks
3. **Iteration Speed:** Python's dynamic typing and REPL enable rapid experimentation
4. **Team Skills:** Data/ML teams already know Python
5. **Battle-tested:** These frameworks are used in production by thousands of companies

**Rust AI/ML ecosystem gaps (for complex workflows):**
- ❌ No equivalent to LangChain's orchestration
- ❌ No equivalent to LlamaIndex's query engines
- ❌ Limited document loaders (PDF/DOCX basic, no unstructured.io equivalent)
- ❌ No multi-agent frameworks comparable to AutoGen/CrewAI
- ❌ Small ecosystem of pre-built components

**Rust AI/ML ecosystem strengths (not our use case):**
- ✅ High-performance local inference (Candle, ONNX)
- ✅ Classical ML algorithms (linfa)
- ✅ Data processing (Polars)
- ✅ GPU-accelerated training (Burn)

**The key insight:** We're not doing local ML. We're orchestrating API calls and complex workflows. Python excels here.

**Alternative considered:** Rust for all async operations
- **Rejected because:** Would require building orchestration frameworks from scratch, slower iteration on AI features, smaller ecosystem

### Decision 3: Kafka as the Architectural Boundary

**Decision:** Use managed Kafka (or Redpanda) as the event bus between sync and async tiers.

**Rationale:**

1. **Clean Separation:** Sync and async tiers evolve independently
2. **Natural Workflows:** Multi-step processes are event chains, not RPC calls
3. **Failure Isolation:** Async tier failure doesn't affect sync tier
4. **Scalability:** Add workers per topic based on queue depth
5. **Auditability:** Event log provides full workflow history
6. **Retry/DLQ:** Built-in replay and dead-letter queues

**Compared to alternatives:**

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Python via gRPC** | Synchronous RPC familiar | Python must speak gRPC, Envoy routing complex, GIL bottleneck, tighter coupling | ❌ Rejected |
| **Kafka/Redpanda** | Clean boundary, natural workflows, independent scaling | Operational complexity (managed mitigates) | ✅ **Chosen** |
| **NATS JetStream** | Simpler ops than Kafka | Less mature tooling, smaller ecosystem | 🟡 Possible future pivot |
| **SQS + Step Functions** | Fully managed, serverless | AWS lock-in, less flexibility | 🟡 Possible future pivot |

**Why not gRPC for async tier:**
- Requires Python services to implement gRPC servers (more complexity)
- Envoy must route to Python services (configuration overhead)
- GIL becomes bottleneck under concurrent requests
- Synchronous model doesn't fit async workflows naturally
- No built-in retry/DLQ/replay

**Why Kafka wins:**
- Python workers consume events (simple pattern)
- No Envoy configuration needed
- No GIL concerns (workers are independent processes)
- Multi-step workflows are event chains (natural model)
- Built-in durability, replay, and monitoring

**Operational strategy:**
- Use managed Kafka (AWS MSK, Confluent Cloud) or managed Redpanda
- Partition by `tenant_id` for ordering and isolation
- One topic per workflow type (granular scaling)
- DLQ per topic for poison pill handling

### Decision 4: Connect RPC Protocol

**Decision:** Use Connect RPC (from Buf) instead of raw gRPC-Web.

**Rationale:**

**gRPC-Web problems:**
- Safari/iOS quirks and compatibility issues
- CDN/proxy buffering can break streams
- No graceful fallback when HTTP/2 unavailable
- Manual CORS header management
- Binary-only (hard to debug)

**Connect RPC solutions:**
- ✅ Auto-negotiates best protocol (gRPC-Web, Connect, or JSON)
- ✅ Graceful fallback for browser compatibility
- ✅ Can enable JSON mode for debugging
- ✅ Better TypeScript ergonomics
- ✅ Same Protobuf schemas (no lock-in)
- ✅ Supports streaming (server-streaming for tokens)

**Implementation:**
- **Frontend:** `@connectrpc/connect-web` generates TypeScript clients
- **Backend:** Tonic serves native gRPC; Envoy translates Connect → gRPC
- **Dev:** Can use `tonic-web` for direct browser → Rust (bypass Envoy)

**Alternative considered:** Raw gRPC-Web
- **Rejected because:** Browser compatibility issues, no fallback, harder to debug

### Decision 5: Postgres + pgvector (Start Simple)

**Decision:** Use Postgres with pgvector extension for all data, including vectors. Migrate to dedicated vector DB only if needed.

**Rationale:**

1. **Single Database:** Relational data + vectors + full-text search in one place
2. **Operational Simplicity:** One database to manage, backup, secure
3. **pgvector is Sufficient:** Handles 100k-1M vectors well with HNSW/IVFFLAT
4. **Postgres Expertise:** Team already knows Postgres
5. **Hybrid Search:** Easy to combine vector similarity + full-text + filters

**When to migrate to dedicated vector DB:**
- > 1M vectors with strict latency requirements
- Complex vector operations (filtering, metadata, faceting)
- Multi-vector queries (cross-collection search)

**Likely candidates:** Qdrant (Rust-native), Weaviate, Pinecone

**Schema strategy:**
```sql
-- ADRs table with vector column
CREATE TABLE adrs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI/Anthropic embeddings
    content_tsv tsvector,    -- Full-text search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX ON adrs USING hnsw (embedding vector_cosine_ops);

-- Full-text search index
CREATE INDEX ON adrs USING gin(content_tsv);

-- Tenant isolation (RLS)
ALTER TABLE adrs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON adrs
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

**Alternative considered:** Qdrant from day one
- **Rejected because:** Adds operational complexity, premature optimization

### Decision 6: Next.js with Node Runtime for SSR

**Decision:** Server Components use Node.js runtime (not Edge) and call services via native gRPC.

**Rationale:**

**The constraint:**
- Edge runtimes (Vercel Edge, Cloudflare Workers) don't support native gRPC
- Native gRPC requires Node.js APIs (HTTP/2 client, native modules)

**Options:**

| Approach | SSR Runtime | Works? | Trade-offs |
|----------|-------------|--------|------------|
| **Node + native gRPC** | Node.js | ✅ Yes | Simple, no extra layer |
| **Edge + Connect JSON** | Edge | ✅ Yes | Extra translation (gRPC↔JSON) |
| **Edge + REST endpoints** | Edge | ✅ Yes | Need separate REST API |

**Decision:** Node runtime by default
- Mark SSR routes: `export const runtime = 'nodejs'`
- Use native gRPC from Server Components
- Simple, no translation layer

**If Edge SSR needed later:**
- Add Connect JSON bridge (Envoy `google.api.http` annotations)
- Or add tiny Connect gateway for SSR-only traffic
- But only if Edge runtime benefits (global distribution, cost) outweigh complexity

**Key insight:** SSR latency (500ms) is less critical than interactive latency (100ms). Adding 5-10ms for JSON translation doesn't hurt UX.

**Alternative considered:** Edge runtime everywhere
- **Rejected because:** Requires JSON bridge, more complex, no clear benefit for MVP

### Decision 7: Managed Authentication (Clerk/Auth0)

**Decision:** Use managed OIDC provider (Clerk recommended), not build custom auth.

**Rationale:**

1. **Not Core Competency:** Authentication is complex and security-critical
2. **Time to Market:** Building auth delays AI features (our differentiation)
3. **Maintenance Burden:** Password resets, MFA, social login, session management
4. **Security:** Managed providers have dedicated security teams
5. **Compliance:** GDPR, SOC2 compliance included

**Integration pattern:**
- Frontend gets JWT from Clerk/Auth0
- Browser sends `Authorization: Bearer <jwt>` header
- Envoy validates JWT signature (jwt_authn filter)
- Envoy extracts user_id, email, adds to gRPC metadata
- Rust services read user context from metadata

**Why Bearer tokens (not cookies):**
- Simpler CORS (no `withCredentials` complexity)
- Works cross-domain without SameSite issues
- Safari Intelligent Tracking Prevention (ITP) doesn't block
- Mobile apps can use same pattern

**Alternative considered:** Build custom auth
- **Rejected because:** 3-6 months of work, security risk, not differentiating

### Decision 8: Row-Level Security (RLS) for Multi-Tenancy

**Decision:** Enable RLS on all tenant-scoped tables. Set `app.tenant_id` at transaction start.

**Rationale:**

**Defense in depth:**
- Even if application logic has bug, database enforces isolation
- SQL injection can't cross tenant boundaries
- Reduces blast radius of security vulnerabilities

**Implementation:**
```sql
-- Enable RLS
ALTER TABLE adrs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON adrs
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

```rust
// Rust service sets tenant context
let tenant_id = extract_tenant_from_metadata(request)?;
sqlx::query("SET LOCAL app.tenant_id = $1")
    .bind(tenant_id)
    .execute(&mut tx)
    .await?;

// All subsequent queries automatically filtered by RLS
let adrs = sqlx::query_as("SELECT * FROM adrs WHERE ...")
    .fetch_all(&mut tx)
    .await?;
```

**Performance consideration:**
- RLS adds predicate to every query
- Minimal overhead (<1ms typically)
- Indexes on `tenant_id` ensure it's efficient

**Alternative considered:** Application-level filtering only
- **Rejected because:** Single point of failure, higher risk

---

## Technology Stack

### Frontend

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Framework** | Next.js 14+ (App Router) | React Server Components, streaming, built-in optimization |
| **Language** | TypeScript | Type safety, IDE support, catches errors at build time |
| **RPC Client** | `@connectrpc/connect-web` | gRPC-Web streaming, auto-generated from Protobuf |
| **State** | Zustand | Simple, minimal, fast |
| **Data Fetching** | TanStack Query | Caching, invalidation, optimistic updates |
| **Styling** | Tailwind CSS | Utility-first, fast iteration, small bundle |
| **Forms** | React Hook Form | Performance, validation, low re-renders |

### API Gateway

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Proxy** | Envoy | gRPC-Web translation, JWT validation, observability |
| **TLS** | Let's Encrypt | Free, automated, widely trusted |
| **CDN** | CloudFlare/CloudFront | Global distribution, DDoS protection |

### Backend Services

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Rust (stable) | Performance, safety, concurrency |
| **RPC Framework** | Tonic | gRPC server, async/streaming, code generation |
| **Async Runtime** | Tokio | Battle-tested, rich ecosystem |
| **HTTP Client** | reqwest | Async, connection pooling, TLS |
| **Database** | sqlx | Compile-time SQL verification, async |
| **Serialization** | serde + prost | JSON and Protobuf support |
| **Observability** | tracing + opentelemetry | Structured logging, distributed tracing |

### Async Workers

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Python 3.11+ | Rich ML/AI ecosystem |
| **LLM Framework** | LangChain | Comprehensive orchestration, many integrations |
| **RAG Framework** | LlamaIndex | Advanced retrieval strategies |
| **Agent Framework** | AutoGen/CrewAI | Multi-agent orchestration |
| **Event Consumer** | kafka-python / confluent-kafka | Mature Kafka clients |
| **Document Parsing** | PyPDF2, python-docx, unstructured.io | Wide format support |
| **Embedding** | sentence-transformers (if local) | High-quality embeddings |

### Data Layer

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Database** | Managed Postgres (AWS RDS/Azure) | Reliability, automatic backups, read replicas |
| **Vector Extension** | pgvector | Vector similarity search in Postgres |
| **Connection Pool** | PgBouncer | Connection management, reduces overhead |
| **Backup** | Automated daily snapshots | Point-in-time recovery |
| **Monitoring** | CloudWatch/Azure Monitor | Database metrics, slow query logs |

### Event Bus

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Message Broker** | Managed Kafka (AWS MSK) or Redpanda Cloud | Durability, replay, throughput |
| **Schema Registry** | Confluent Schema Registry | Protobuf schema evolution |
| **Monitoring** | Kafka metrics → Prometheus | Queue depth, consumer lag |

### Infrastructure

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Container Platform** | AWS ECS/Cloud Run/Azure Container Apps | Managed containers, auto-scaling |
| **Container Registry** | AWS ECR/GCR/ACR | Private, integrated with platform |
| **Object Storage** | S3/GCS/Azure Blob | Document/attachment storage |
| **Secrets** | AWS Secrets Manager/Vault | Encrypted, rotated credentials |
| **DNS** | CloudFlare/Route53 | Global DNS, low latency |

### Observability

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Metrics** | Prometheus + Grafana | Time-series metrics, rich visualization |
| **Tracing** | OpenTelemetry → Jaeger/Tempo | Distributed tracing |
| **Logs** | Structured logs → Loki/CloudWatch | Centralized, searchable |
| **Dashboards** | Grafana | Custom dashboards, alerting |
| **Alerting** | PagerDuty/OpsGenie | On-call rotation, escalation |

### CI/CD

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Version Control** | GitHub | Industry standard, Actions integration |
| **CI** | GitHub Actions | Integrated, free for open source |
| **Protobuf** | Buf | Schema linting, breaking change detection |
| **Testing** | cargo test (Rust), pytest (Python) | Native testing frameworks |
| **Container Builds** | Docker BuildKit | Layer caching, multi-stage builds |
| **Deployment** | Terraform/Pulumi | Infrastructure as code |

---

## Service Boundaries and Responsibilities

### Synchronous Tier (Rust Services)

#### ADR Service

**Responsibilities:**
- CRUD operations for ADRs
- Version management (create, list, diff, rollback)
- Tag and category management
- Search coordination (delegates to vector search)
- Access control (checks user permissions)

**Does NOT:**
- Parse uploaded documents (async worker)
- Generate embeddings (async worker)
- Heavy text processing (async worker)

**Key characteristics:**
- Stateless (scales horizontally)
- <100ms response time for mutations
- <50ms for reads (with caching)

#### AI Gateway Service

**Responsibilities:**
- Stream chat completions from providers (Anthropic, OpenAI, Gemini)
- Simple tool/function calling (synchronous tools only)
- Provider routing and failover
- Response caching (prompt → completion)
- Rate limiting and quota enforcement
- Token budget tracking
- Request/response logging (metadata only, not content)

**Does NOT:**
- Complex multi-step reasoning (async worker)
- Multi-pass retrieval (async worker)
- Training or fine-tuning (async worker)
- Local model inference (initially)

**Key characteristics:**
- High concurrency (1000+ concurrent streams)
- <350ms first token (p95)
- <60ms inter-token gap (p95)
- <100ms cancellation propagation

#### Auth Service (Optional Thin Layer)

**Responsibilities:**
- Claims enrichment (add custom claims to JWT)
- Tenant context resolution (user → tenant mapping)

**Does NOT:**
- Authentication (handled by Clerk/Auth0)
- Token signing/verification (handled by Envoy jwt_authn)

**Key characteristics:**
- Extremely lightweight (or omit entirely if no custom claims needed)
- Envoy + OIDC may be sufficient

### Asynchronous Tier (Python Workers)

#### Document Ingestion Worker

**Responsibilities:**
- Parse uploaded documents (PDF, DOCX, HTML, Markdown)
- OCR for scanned documents (if needed)
- Text extraction and cleaning
- Chunk text into semantic units
- Generate embeddings (call API or use local model)
- Store chunks and embeddings in pgvector
- Publish progress events

**Input event:** `document.uploaded`
**Output events:** `document.processed`, `job.progress`
**SLO:** <30 seconds for typical document (10 pages)

#### Embedding Worker

**Responsibilities:**
- Generate embeddings for text chunks
- Batch optimization (combine multiple requests)
- Retry on rate limits
- Store embeddings with metadata

**Input event:** `embeddings.requested`
**Output events:** `embeddings.generated`, `job.progress`
**SLO:** <10 seconds per batch (100 chunks)

#### RAG Worker

**Responsibilities:**
- Query expansion (generate variations)
- Multi-pass retrieval (search, rerank, search again)
- Cross-encoder reranking
- Hybrid search (vector + full-text + filters)
- Result synthesis
- Context assembly for LLM

**Input event:** `rag.search.requested`
**Output events:** `rag.search.completed`, `job.progress`
**SLO:** <15 seconds for complex search

#### Agent Worker

**Responsibilities:**
- Multi-step reasoning workflows
- Tool selection and invocation
- State management across steps
- Error handling and retries
- Final result assembly

**Input event:** `agent.task.submitted`
**Output events:** `agent.task.completed`, `job.progress`
**SLO:** <60 seconds typical, <10 minutes maximum

#### Crawler Worker

**Responsibilities:**
- Web scraping with anti-bot handling
- Content extraction
- Link following (with depth limits)
- Rate limiting per domain
- Store scraped content

**Input event:** `crawl.submitted`
**Output events:** `crawl.completed`, `job.progress`
**SLO:** <5 minutes per site (depth 2)

### Event Bus Topics

| Topic | Producer | Consumer | Retention | Partitions |
|-------|----------|----------|-----------|------------|
| `document.uploaded` | ADR Service | Ingestion Worker | 7 days | 8 (by tenant_id) |
| `embeddings.requested` | Ingestion Worker | Embedding Worker | 7 days | 8 (by tenant_id) |
| `rag.search.requested` | ADR Service | RAG Worker | 7 days | 8 (by tenant_id) |
| `agent.task.submitted` | AI Gateway | Agent Worker | 7 days | 8 (by tenant_id) |
| `crawl.submitted` | ADR Service | Crawler Worker | 7 days | 4 (by tenant_id) |
| `job.progress` | All Workers | ADR Service (updates DB) | 1 day | 8 (by tenant_id) |

**Partitioning strategy:**
- Partition by `tenant_id` to ensure ordering per tenant
- Number of partitions = 2x number of consumer instances (for growth)
- Each worker consumes from one partition (single-threaded per partition)

---

## Rust AI/ML Maturity Assessment

### Purpose
This section defines WHERE to use Rust vs Python for AI/ML operations based on ecosystem maturity and our specific needs.

### Maturity Zones

#### 🟢 GREEN ZONE: Use Rust Now

**What we need AND Rust is mature:**

1. **Real-time API Gateway**
   - Provider SDKs (Anthropic, OpenAI, Gemini): ✅ Production-ready
   - Async HTTP clients: ✅ Excellent (reqwest, hyper)
   - Streaming: ✅ First-class (tokio-stream)
   - Rate limiting: ✅ Available (governor crate)
   - Caching: ✅ Available (moka, redis-rs)

2. **Vector Operations**
   - pgvector client: ✅ Mature (native Postgres clients)
   - Qdrant client: ✅ Official, first-class
   - Vector similarity: ✅ Built into databases

3. **Structured Outputs**
   - Validation: ✅ serde-based, excellent
   - JSON Schema: ✅ schemars crate
   - Type safety: ✅ Core language feature

4. **Observability**
   - OpenTelemetry: ✅ Excellent integration
   - Metrics: ✅ prometheus crate
   - Tracing: ✅ tracing crate (best-in-class)

**Decision:** Use Rust for all these. Ecosystem is world-class.

#### 🟡 YELLOW ZONE: Evaluate Case-by-Case

**Rust has tools but may lack polish or ecosystem breadth:**

1. **Simple RAG**
   - If: Single-pass retrieval, basic prompt assembly, <2 second target
   - Then: Rust CAN handle this
   - But: Python has more pre-built components (LangChain loaders, chains)

2. **Local Model Inference**
   - If: Small-to-medium models, CPU/GPU inference, well-defined formats (ONNX, GGUF)
   - Then: Rust is viable (Candle, ONNX Runtime bindings)
   - But: Python has better model zoo and tooling

3. **Document Parsing**
   - If: Simple PDF/DOCX text extraction
   - Then: Rust crates exist (pdf-extract, docx-parser)
   - But: Python has richer ecosystem (unstructured.io)

**Decision:** Evaluate per use case. Start with Python (safer), migrate to Rust if performance becomes critical and workflow is stable.

#### 🔴 RED ZONE: Use Python Async Workers

**What we need but Rust ecosystem is immature or we need rapid iteration:**

1. **Advanced RAG**
   - Multi-pass retrieval
   - Cross-encoder reranking
   - Query expansion/decomposition
   - Hybrid search with complex filters
   - **Why Python:** LangChain/LlamaIndex have these patterns built-in

2. **Multi-Agent Orchestration**
   - Multi-step reasoning
   - Agent collaboration
   - Complex tool selection
   - **Why Python:** AutoGen, CrewAI, LangGraph are battle-tested

3. **Document Processing**
   - OCR (Tesseract integration)
   - Table extraction
   - Complex layout parsing
   - **Why Python:** unstructured.io, doctr, many specialized libraries

4. **Web Crawling**
   - Anti-bot handling (Playwright, Selenium)
   - JavaScript rendering
   - Session management
   - **Why Python:** Scrapy, Beautiful Soup, rich ecosystem

5. **Training/Fine-tuning**
   - Model training
   - Fine-tuning workflows
   - Hyperparameter tuning
   - **Why Python:** PyTorch, Transformers library, decades of tooling

6. **Experimentation**
   - Jupyter notebooks
   - Interactive EDA
   - Rapid prototyping
   - **Why Python:** REPL, dynamic typing, visualization libraries

**Decision:** Use Python async workers for ALL of these. Don't fight the ecosystem.

### Decision Framework (Fast Decisioning)

```
┌─────────────────────────────────────┐
│ Is the user actively waiting?      │
│ (< 1 second expected)               │
└─────────────┬───────────────────────┘
              │
         Yes  │  No
              │
    ┌─────────▼──────────┐
    │  SYNCHRONOUS TIER  │
    │     (Rust)         │
    └────────────────────┘
              │
              │ No
              │
    ┌─────────▼──────────────────────┐
    │ Is it a simple API call +      │
    │ basic data transformation?     │
    └─────────┬──────────────────────┘
              │
         Yes  │  No
              │
    ┌─────────▼──────────┐  ┌────────▼──────────────┐
    │   Rust sync tier   │  │ ASYNCHRONOUS TIER     │
    │   (if <100ms)      │  │ (Python workers)      │
    └────────────────────┘  └───────────────────────┘
```

**Quick reference table:**

| Operation | Tier | Language | Reason |
|-----------|------|----------|--------|
| Chat streaming | Sync | Rust | User waiting, API call + stream |
| CRUD operations | Sync | Rust | User waiting, database ops |
| Simple semantic search | Sync | Rust | User waiting, single vector query |
| Document upload & parse | Async | Python | Multi-step, rich ecosystem |
| Generate embeddings | Async | Python | Batch optimization, not urgent |
| Advanced RAG | Async | Python | Multi-pass, reranking, complex |
| Agent workflows | Async | Python | Multi-step reasoning, tools |
| Web crawling | Async | Python | Anti-bot, rich ecosystem |

---

## Security Architecture

### Authentication & Authorization

#### Authentication Flow

```
1. User logs in via Clerk/Auth0 (browser redirect)
2. Clerk returns JWT with claims:
   {
     "sub": "user_123",
     "email": "user@example.com",
     "org_id": "org_456",
     "roles": ["user"]
   }
3. Browser stores JWT (memory or secure localStorage)
4. Browser includes JWT in every request:
   Authorization: Bearer <jwt>
5. Envoy validates JWT:
   - Check signature against JWKS
   - Check expiration
   - Check audience/issuer
6. Envoy extracts claims, forwards to service:
   x-user-id: user_123
   x-user-email: user@example.com
   x-tenant-id: org_456
7. Service reads claims from metadata
8. Service sets RLS context:
   SET LOCAL app.tenant_id = 'org_456'
9. All queries automatically filtered by RLS
```

#### Authorization Patterns

**In Services (Domain Layer):**
```rust
// Extract user context from gRPC metadata
let user = extract_user_from_metadata(request)?;

// Check permissions (domain logic)
if !user.can_edit_adr(&adr) {
    return Err(Status::permission_denied("Cannot edit this ADR"));
}

// Perform operation
// RLS ensures tenant isolation even if logic has bug
```

**In Database (RLS):**
```sql
-- Automatically filter all queries by tenant
CREATE POLICY tenant_isolation ON adrs
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Users can only see published ADRs (unless author)
CREATE POLICY published_or_author ON adrs
    USING (
        status = 'published'
        OR author_id = current_setting('app.user_id')::uuid
    );
```

### Multi-Tenancy Isolation

**Layers of defense:**

1. **Application:** Service validates tenant_id from JWT
2. **Database:** RLS enforces isolation even if app fails
3. **Network:** Services can't reach other tenants' data at network level (future: separate VPCs per tenant tier)

### Secrets Management

**Rules:**
- ❌ Never in code
- ❌ Never in config files
- ❌ Never in environment variables (for long-lived secrets)
- ✅ Always in secret manager (AWS Secrets Manager, Vault)
- ✅ Rotate regularly (automatic rotation where possible)
- ✅ Principle of least privilege (each service gets only its secrets)

**Implementation:**
```rust
// Services fetch secrets at startup
let secrets = SecretManager::new()
    .fetch_secret("anthropic_api_key")
    .await?;

// Refresh secrets periodically (24 hours)
tokio::spawn(async move {
    loop {
        tokio::time::sleep(Duration::from_hours(24)).await;
        secrets.refresh().await?;
    }
});
```

### Network Security

#### Egress Control

**Problem:** Prevent SSRF (Server-Side Request Forgery) and data exfiltration.

**Solution:** Allowlist permitted domains.

```rust
// Allowed domains for tool/agent calls
const ALLOWED_DOMAINS: &[&str] = &[
    "api.anthropic.com",
    "api.openai.com",
    "api.google.com",
    // Explicitly allowed tools
    "api.github.com",
    "api.notion.com",
];

// Validate before making request
fn validate_url(url: &Url) -> Result<(), Error> {
    let host = url.host_str().ok_or(Error::InvalidUrl)?;
    if !ALLOWED_DOMAINS.iter().any(|d| host.ends_with(d)) {
        return Err(Error::ForbiddenDomain(host.to_string()));
    }
    Ok(())
}
```

#### TLS Everywhere

- **External:** TLS 1.3 (Let's Encrypt)
- **Internal:** mTLS between services (future, if needed)
- **Database:** TLS connections to Postgres

### Data Privacy

#### PII Handling

**Rules:**
- ❌ Never log full prompts or completions
- ❌ Never send PII to analytics
- ✅ Scrub PII before logging
- ✅ Allow users to opt out of provider data retention

**Implementation:**
```rust
// Log only metadata
tracing::info!(
    user_id = %user.id,
    prompt_length = prompt.len(),
    model = %model,
    "Chat completion started"
);
// Do NOT log: prompt, completion, user content

// Provider settings
let request = CompletionRequest {
    model: "claude-sonnet-4",
    // Opt out of training
    metadata: json!({
        "user_id": "anonymous",  // Don't send real user_id
    }),
};
```

#### GDPR Compliance

**User rights:**
- Right to access: API endpoint to export all user data
- Right to deletion: Hard delete user data (including embeddings)
- Right to portability: Export in JSON format

---

## Cost Management & Abuse Prevention

### Per-User/Org Quotas

**Implemented at multiple layers:**

1. **Application Layer (Rust Service):**
   ```rust
   // Check quota before processing
   let quota = quotas.check(tenant_id, QuotaType::ChatCompletions).await?;
   if quota.is_exceeded() {
       return Err(Status::resource_exhausted("Quota exceeded"));
   }

   // Process request...

   // Update quota
   quotas.increment(tenant_id, QuotaType::ChatCompletions, tokens_used).await?;
   ```

2. **Rate Limiting (Per-User):**
   - Requests per minute: 100
   - Concurrent streams: 5
   - Tokens per day: 100,000

3. **Cost Tracking (Per-Org):**
   - Track token usage and convert to cost
   - Alert at 70%, 85%, 95% of budget
   - Hard stop at 110% (with manual override)

### Provider Backpressure

**Problem:** Don't overwhelm providers or accumulate huge costs.

**Solution:**
- Concurrency limit per model: 50 (adjustable)
- Queue depth limit: 1000
- Exponential backoff on 429 (rate limit)
- Circuit breaker on repeated 5xx

**Implementation:**
```rust
// Semaphore for concurrency control
static ANTHROPIC_SEMAPHORE: Lazy<Semaphore> = 
    Lazy::new(|| Semaphore::new(50));

async fn call_anthropic(request: CompletionRequest) -> Result<Stream> {
    // Acquire permit (blocks if at limit)
    let _permit = ANTHROPIC_SEMAPHORE.acquire().await?;

    // Make request
    let response = client.post()...await?;

    // Permit automatically released when _permit drops
    Ok(response)
}
```

### Spend Tracking & Alerts

**Dashboard metrics:**
- Cost per day/week/month
- Cost per org
- Cost per model
- Projected monthly cost

**Alerts:**
- 70% of budget: Info (Slack notification)
- 85% of budget: Warning (Email to admin)
- 95% of budget: Critical (PagerDuty)
- 110% of budget: Auto kill-switch (stop all requests, require manual override)

### Free Tier Defenses

**Problem:** Abuse via free tier sign-ups.

**Mitigations:**
1. Captcha on signup
2. Email verification required
3. First 24 hours: Very strict quotas (10 requests/day)
4. Manual review triggers:
   - Unusual patterns (rapid API calls)
   - High token usage
   - Multiple accounts from same IP

---

## Observability Requirements

### Metrics (Prometheus)

**Application metrics:**
- `ai_first_token_duration_ms` (histogram, p50/p95/p99)
- `ai_inter_token_duration_ms` (histogram, p50/p95/p99)
- `ai_tokens_per_second` (histogram)
- `ai_tokens_total` (counter, by model, tenant)
- `ai_cost_total` (counter, by model, tenant, currency)
- `grpc_request_duration_seconds` (histogram, by service, method)
- `grpc_request_total` (counter, by service, method, status)
- `grpc_active_streams` (gauge)

**Infrastructure metrics:**
- `envoy_cluster_upstream_cx_active` (active connections)
- `envoy_cluster_upstream_rq_time` (request duration)
- `kafka_consumer_lag` (by topic, consumer group)
- `kafka_topic_messages_per_sec` (by topic)
- `postgres_connections_active`
- `postgres_query_duration_seconds` (by query type)

**Business metrics:**
- `users_active_daily` (gauge)
- `adrs_created_total` (counter)
- `searches_total` (counter, by type: lexical/semantic)
- `chat_sessions_total` (counter)

### Tracing (OpenTelemetry → Jaeger/Tempo)

**Trace every request end-to-end:**

```
Browser (generate trace ID)
  ↓ traceparent header
Envoy (propagate)
  ↓ grpc-trace-bin metadata
Rust Service (span: handle_request)
  ↓ traceparent to provider
Anthropic API
```

**Key spans:**
- `handle_chat_request` (entire request lifecycle)
- `validate_quota` (quota check)
- `call_anthropic_api` (provider call)
- `first_token_received` (mark when streaming starts)
- `stream_token` (each token sent to client)
- `db_query` (database calls)

**Example trace:**
```
handle_chat_request (total: 420ms)
├─ validate_quota (5ms)
├─ db_fetch_context (20ms)
├─ call_anthropic_api (380ms)
│  ├─ http_connect (50ms)
│  ├─ wait_for_first_token (280ms)  ← Key metric
│  └─ stream_tokens (50ms, avg 25ms/token)  ← Key metric
└─ db_save_usage (15ms)
```

### Logs (Structured, JSON)

**Log levels:**
- ERROR: System failures, unhandled exceptions
- WARN: Degraded performance, quota exceeded, provider errors
- INFO: Request started/completed, business events
- DEBUG: Internal state (development only)

**Log fields (always include):**
- `timestamp`
- `level`
- `message`
- `trace_id`
- `span_id`
- `service_name`
- `user_id` (if authenticated)
- `tenant_id`
- `request_id`

**Example log:**
```json
{
  "timestamp": "2025-10-22T10:30:45.123Z",
  "level": "INFO",
  "message": "Chat completion started",
  "trace_id": "abc123",
  "span_id": "def456",
  "service": "ai-gateway",
  "user_id": "user_789",
  "tenant_id": "org_012",
  "model": "claude-sonnet-4",
  "prompt_length": 245,
  "max_tokens": 1000
}
```

### Dashboards (Grafana)

**Required dashboards:**

1. **AI Performance:**
   - First token latency (p50, p95, p99) over time
   - Inter-token latency (p50, p95, p99) over time
   - Tokens per second (by model)
   - Stream completion rate
   - Provider errors (by provider, error type)

2. **Service Health:**
   - Request rate (by service, method)
   - Error rate (by service, method, status code)
   - Request duration (p50, p95, p99)
   - Active connections (to Envoy, to services)

3. **Infrastructure:**
   - CPU usage (by service)
   - Memory usage (by service)
   - Kafka consumer lag (by topic)
   - Database connections (active, idle)
   - Database query duration (slow queries)

4. **Business:**
   - Daily active users
   - Chat sessions per day
   - ADRs created per day
   - Cost per day (by provider, by org)

5. **Cost & Quotas:**
   - Cost over time (total, by org, by model)
   - Quota usage (by org, by quota type)
   - Spend alerts

### Alerts

**Critical (PagerDuty):**
- Error rate > 1% for 5 minutes
- p95 latency > 1 second for 5 minutes
- Any service down
- Database connection pool exhausted
- Spend > 110% of budget

**Warning (Email):**
- Error rate > 0.5% for 5 minutes
- p95 latency > 500ms for 5 minutes
- Kafka consumer lag > 1000 messages
- Spend > 85% of budget

**Info (Slack):**
- New deployment
- Spend > 70% of budget
- Unusual traffic patterns

---

## Deployment & Operations

### Environments

| Environment | Purpose | Infrastructure | Data |
|-------------|---------|----------------|------|
| **Local** | Development | Docker Compose | Seed data |
| **Staging** | Pre-production testing | Managed (smaller instances) | Anonymized prod data |
| **Production** | Live users | Managed (full scale) | Real user data |

### Deployment Strategy

**Blue-Green Deployment:**
1. Deploy new version (green)
2. Run smoke tests
3. Route 10% of traffic to green
4. Monitor metrics for 10 minutes
5. If healthy: Route 50%, then 100%
6. If unhealthy: Route 0%, rollback
7. Keep blue alive for 24 hours (fast rollback)

**Database Migrations:**
- Backward-compatible migrations only
- Run migration before deploying code
- Never drop columns/tables without multi-step migration

### Rollback Plan

**Service rollback:**
1. Route traffic back to blue (instant)
2. Investigate issue
3. Fix and redeploy green

**Database rollback:**
- Cannot rollback destructive migrations
- Forward-only philosophy
- Test migrations in staging first

### Disaster Recovery

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Backup strategy:**
- Database: Automated daily snapshots + point-in-time recovery
- Object storage: Versioning enabled
- Event bus: Retain events for 7 days (replay if needed)

**Disaster scenarios:**
1. **Database failure:** Failover to read replica, promote to primary
2. **Region failure:** DNS failover to backup region (4 hour RTO)
3. **Data corruption:** Restore from snapshot (1 hour RPO)

---

## What We Are NOT Doing (And Why)

These are conscious decisions to avoid scope creep and premature optimization.

### 1. NOT Building Custom Auth
**Why:** Authentication is complex, security-critical, and not our differentiation. Use Clerk/Auth0.

### 2. NOT Using Kubernetes (Initially)
**Why:** Managed container platforms (ECS, Cloud Run) are simpler for MVP. Can migrate to K8s later if needed.

### 3. NOT Building Custom Vector Database
**Why:** pgvector is sufficient for MVP. Premature optimization.

### 4. NOT Supporting Real-Time Collaboration (Yet)
**Why:** gRPC-Web doesn't support bidirectional streaming. Would need WebSocket layer. Not MVP.

### 5. NOT Running Models Locally (Initially)
**Why:** Provider APIs are simpler and more reliable. Can add local inference later for cost optimization.

### 6. NOT Building Mobile Apps (Yet)
**Why:** Web-first strategy. Mobile apps use same gRPC APIs later.

### 7. NOT Implementing Multi-Region (Initially)
**Why:** Single region with CDN is sufficient. Add multi-region for latency/compliance later.

### 8. NOT Building Admin Dashboard (Initially)
**Why:** Direct database queries sufficient for MVP. Build admin UI in Phase 2.

### 9. NOT Implementing Fine-Tuning (Initially)
**Why:** Prompt engineering first. Fine-tuning only if provider models insufficient.

### 10. NOT Building Custom ML Models (Initially)
**Why:** Use provider embeddings and models. Build custom only if differentiation requires it.

---

## Success Criteria

### Performance Targets (p95)

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| First token latency | < 350ms | OpenTelemetry histogram |
| Inter-token latency | < 60ms | OpenTelemetry histogram |
| UI perceived response | < 100ms | Click → optimistic update |
| Cancel propagation | < 100ms | Abort → provider stop |
| SSR page load (warm) | < 500ms | Lighthouse, synthetic monitoring |

### Reliability Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Service uptime | ≥ 99.9% | Uptime monitoring (Pingdom) |
| Stream completion rate | ≥ 99% | (completed / started) streams |
| Error rate | < 0.1% | (5xx responses / total) excluding provider |

### Type Safety Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Runtime type errors | 0 | Sentry error tracking |
| Buf breaking changes | 0 in CI | Buf lint in GitHub Actions |

### Developer Velocity Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| New RPC endpoint | < 2 hours | Proto → server → client → deployed |
| Staging deployment | < 15 minutes | Commit → staging live |
| Test coverage | > 80% | cargo tarpaulin (Rust), coverage.py (Python) |

### Cost Efficiency Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Alert latency | < 5 minutes | Alert fires → notification received |
| Quota enforcement | 100% | No requests over quota |
| Kill-switch test | Quarterly | Simulate cost spike, verify auto-stop |

---

## Implementation Phases

### Phase 1: Validation (Weeks 1-2)

**Goal:** Prove critical architecture decisions work in practice.

**Deliverables:**

1. **Transport Matrix Validation**
   - Deploy minimal Rust service with server-streaming
   - Deploy Envoy in front
   - Test gRPC-Web streaming across:
     - Chrome (WiFi, 3G)
     - Safari (WiFi, 3G)
     - iOS Safari (4G)
     - Android Chrome (4G)
   - Test with CDN (CloudFlare) enabled
   - Validate first-token time and smooth streaming
   - Confirm cancellation works (< 100ms)

2. **SSR Runtime Validation**
   - Test Node SSR calling native gRPC ✅
   - Test Edge SSR (expect failure) ✅
   - Test Edge SSR with Connect JSON bridge ✅
   - Document decision

3. **Auth Flow Validation**
   - OIDC login (Clerk trial)
   - JWT → Envoy jwt_authn → service metadata
   - Verify in Chrome, Safari, iOS
   - Verify clock skew handling
   - Verify token refresh

4. **Cancellation Validation**
   - Client abort() → service detects → provider cancels
   - Measure end-to-end time
   - Target: < 100ms

5. **Provider Baselines**
   - Measure first-token time (Anthropic, OpenAI)
   - Measure tokens/sec (Anthropic, OpenAI)
   - Test from different regions
   - Choose optimal region

6. **Proto Workflow**
   - Buf configuration
   - Generate Rust (prost/tonic)
   - Generate TypeScript (Connect)
   - Make breaking change → verify CI fails
   - Fix → verify CI passes

**Success Criteria:**
- ✅ Streaming works smoothly in all tested browsers
- ✅ Cancel propagates < 100ms
- ✅ SSR strategy decided
- ✅ Auth flow end-to-end
- ✅ Provider baselines documented
- ✅ Proto workflow automated

### Phase 2: Foundations (Weeks 3-4)

**Goal:** Build infrastructure and tooling.

**Deliverables:**

1. **Monorepo Setup**
   - `/proto` - Protobuf schemas
   - `/services` - Rust workspace
     - `/adr-service`
     - `/ai-gateway`
     - `/auth-service`
   - `/web` - Next.js app
   - `/workers` - Python workers (future)

2. **Buf & Codegen**
   - `buf.yaml` configuration
   - `buf.gen.yaml` for Rust + TypeScript
   - `make proto` command
   - CI integration (lint, breaking change detection)

3. **Envoy Deployment**
   - Envoy configuration (filters, routes, clusters)
   - TLS certificate (Let's Encrypt)
   - CORS configuration
   - JWT validation setup

4. **Postgres + pgvector + RLS**
   - Managed Postgres instance
   - Install pgvector extension
   - Create schema with RLS policies
   - Connection pooling (PgBouncer)

5. **OIDC Integration**
   - Clerk/Auth0 setup
   - Configure Envoy jwt_authn
   - Test login flow

6. **OpenTelemetry**
   - Rust services export traces
   - Envoy exports traces
   - Collector configuration
   - Jaeger/Tempo setup

7. **Kafka/Redpanda**
   - Managed instance
   - Create topics
   - Test produce/consume

8. **CI/CD Pipeline**
   - GitHub Actions workflow
   - Buf lint
   - Rust tests
   - Build Docker images
   - Deploy to staging

**Success Criteria:**
- ✅ One command regenerates all code from proto
- ✅ CI catches breaking changes
- ✅ Can deploy to staging
- ✅ Observability working (traces visible)

### Phase 3: MVP Features (Weeks 5-8)

**Goal:** Build minimum viable product.

**Features:**

1. **ADR CRUD**
   - Create ADR
   - Read ADR (with syntax highlighting)
   - Update ADR
   - List ADRs (with filters)
   - Soft delete

2. **ADR Versioning**
   - Create new version
   - View version history
   - View diff between versions
   - Rollback to previous version

3. **AI Chat**
   - Streaming chat interface
   - Token-by-token display
   - Cancel generation
   - Quota enforcement
   - Cost tracking

4. **Search**
   - Lexical search (full-text)
   - Semantic search (vector similarity)
   - Hybrid search (combine both)
   - Filters (status, tags, author)

5. **Document Ingestion (Minimal)**
   - Upload document (PDF only for MVP)
   - Publish to Kafka
   - Python worker: parse → chunk → embed → store
   - Job progress UI (queued → processing → complete)

6. **Responsive UI**
   - Desktop layout
   - Mobile layout
   - Dark mode

**Success Criteria:**
- ✅ Can create, read, update ADRs
- ✅ Can chat with streaming tokens
- ✅ Can search ADRs (lexical + semantic)
- ✅ Can upload and process document
- ✅ UI works on mobile

### Phase 4: Production Readiness (Weeks 9-10)

**Goal:** Make it production-ready.

**Tasks:**

1. **Load Testing**
   - Simulate 1000 concurrent chat streams
   - Measure latency under load
   - Identify bottlenecks
   - Optimize

2. **Security Review**
   - Penetration testing
   - RLS verification
   - Secrets audit
   - Egress allowlist verification

3. **Dashboards & Alerts**
   - Grafana dashboards (all required)
   - Alerts configured (critical, warning, info)
   - PagerDuty integration
   - Test alerts (trigger manually)

4. **Runbooks**
   - Deployment runbook
   - Rollback runbook
   - Incident response runbook
   - Disaster recovery runbook

5. **Cost Guardrails**
   - Quotas configured
   - Spend tracking working
   - Alerts tested
   - Kill-switch tested

6. **Disaster Recovery Rehearsal**
   - Simulate database failure → failover
   - Simulate region failure → DNS switch
   - Simulate data corruption → restore from backup
   - Document actual times (compare to RTO/RPO)

**Go-Live Criteria:**
- ✅ All SLOs met in load testing
- ✅ Security review passed
- ✅ All critical alerts tested
- ✅ Runbooks complete and reviewed
- ✅ DR rehearsal successful
- ✅ Cost guardrails verified

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **CDN/proxy buffering breaks streaming** | Medium | High | Bypass CDN for streaming, or configure no-buffering; test with CDN early |
| **Python worker overload** | Medium | Medium | Per-topic quotas, horizontal scaling, DLQ, alerting on lag |
| **Eventual consistency surprises** | Low | Medium | Clear UX copy ("Processing..."), job snapshots, revision IDs |
| **Provider regional variance** | Medium | Low | Baseline tests, co-locate services to provider region, failover routing |
| **pgvector performance degradation** | Low | Medium | Monitor query times and recall, move to Qdrant when limits reached |
| **Kafka operational complexity** | Low | Low | Use managed service (MSK/Redpanda Cloud), not self-hosted |
| **Rust learning curve** | Medium | Low | Allocate training time, pair programming, start with simple services |
| **Cost overruns** | Medium | High | Quotas, spend alerts, kill-switches, budget approvals |

---

## Appendices

### Appendix A: Glossary

- **ADR:** Architecture Decision Record
- **gRPC:** Google Remote Procedure Call
- **gRPC-Web:** gRPC protocol adapted for browsers (HTTP/1.1 compatible)
- **Connect RPC:** Modern RPC framework by Buf, compatible with gRPC
- **RLS:** Row-Level Security (Postgres feature for multi-tenancy)
- **pgvector:** Postgres extension for vector similarity search
- **Envoy:** Cloud-native API gateway
- **Tonic:** Rust gRPC framework
- **Tokio:** Rust async runtime
- **OpenTelemetry (OTel):** Observability standard for traces/metrics
- **Kafka:** Distributed event streaming platform
- **SSR:** Server-Side Rendering
- **CSR:** Client-Side Rendering
- **OIDC:** OpenID Connect (authentication standard)
- **JWT:** JSON Web Token
- **RTO:** Recovery Time Objective
- **RPO:** Recovery Point Objective

### Appendix B: Decision Log

| Date | Decision | Rationale | Status |
|------|----------|-----------|--------|
| 2025-10 | Rust for sync tier | Performance, concurrency, reliability | ✅ Approved |
| 2025-10 | Python for async tier | Ecosystem maturity (LangChain, LlamaIndex) | ✅ Approved |
| 2025-10 | Kafka as boundary | Clean separation, workflow orchestration | ✅ Approved |
| 2025-10 | Connect RPC | Browser compatibility, debugging | ✅ Approved |
| 2025-10 | Postgres + pgvector | Single database, start simple | ✅ Approved |
| 2025-10 | Managed OIDC (Clerk) | Don't build auth | ✅ Approved |
| 2025-10 | Node SSR default | Native gRPC support | ✅ Approved |

### Appendix C: References

**Rust AI/ML Ecosystem:**
- Report 1: ML Training & Classical ML (moderate relevance)
- Report 2: AI Application Layer (high relevance)

**Key takeaways:**
- Rust is mature for API gateway, streaming, observability
- Rust is immature for complex RAG/agent workflows
- Hybrid architecture (Rust + Python) is industry best practice

**gRPC/Connect:**
- Connect RPC docs: https://connectrpc.com
- Buf docs: https://buf.build/docs

**Observability:**
- OpenTelemetry docs: https://opentelemetry.io
- Grafana docs: https://grafana.com/docs

**Database:**
- pgvector docs: https://github.com/pgvector/pgvector

---

## Document Metadata

**Version:** 4.0  
**Status:** Final for MVP Implementation  
**Last Updated:** October 2025  
**Authors:** Engineering Team  
**Reviewers:** CTO, Security Lead, Infrastructure Lead  
**Next Review:** After Phase 2 completion

**Change Log:**
- v4.0: Final comprehensive document integrating all decisions and report analyses
- v3.0: Added RLS, cost guardrails, observability requirements
- v2.1: Added SSR strategy, Rust maturity map
- v2.0: De-risked architecture with spike plan
- v1.0: Initial architecture document

---

## Final Statement

**This architecture uses Rust where it excels (real-time serving, concurrency, reliability) and Python where it excels (complex ML workflows, rich ecosystem, experimentation). The boundary is clean (Kafka event bus), the technologies are mature, and the path to production is clear.**

**All real-time UX and operational governance live in Rust. Advanced RAG, agents, and crawling run as Python workflows behind a durable event bus—with clear progress reporting, strict isolation, and tight cost & latency SLOs.**

**This is not a "two-language problem." This is a two-language solution.**