# ADR Platform - Final Repository Structure
## Complete Architecture with Phased Implementation

**Version:** 1.0  
**Date:** October 2025  
**Status:** North Star Architecture  
**Implementation:** Phased (Sync Tier → Async Tier → Production)

---

## Document Purpose

This document defines the **complete repository structure** for the ADR Platform PoC, showing:
1. **North Star Architecture** - The full dual-tier system when complete
2. **Phased Implementation** - How to build it incrementally (Rust → Python → Production)
3. **Migration Path** - How to lift into production monorepo with minimal effort

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Complete Directory Structure](#complete-directory-structure)
3. [Phased Implementation](#phased-implementation)
4. [Component Specifications](#component-specifications)
5. [Technology Stack](#technology-stack)
6. [Development Workflow](#development-workflow)
7. [Migration Strategy](#migration-strategy)
8. [Best Practices](#best-practices)

---

## Architecture Overview

### Dual-Tier Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Next.js 14 (App Router)                          │  │
│  │  - Server Components (Node.js runtime, gRPC)      │  │
│  │  - Client Components (Connect Web, streaming)     │  │
│  │  - Zustand (UI state) + React Query (server)     │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────┬────────────────────────────────────────┘
                  │
                  │ Connect RPC (gRPC-Web)
                  ↓
┌──────────────────────────────────────────────────────────┐
│              API GATEWAY (ENVOY)                         │
│  - TLS termination                                       │
│  - JWT validation (jwt_authn filter)                     │
│  - gRPC-Web ↔ gRPC translation                          │
│  - Request routing & load balancing                      │
└─────────────────┬────────────────────────────────────────┘
                  │
                  │ gRPC (HTTP/2)
                  ↓
┌──────────────────────────────────────────────────────────┐
│         SYNCHRONOUS TIER (Rust Services)                 │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  ADR Service                                    │    │
│  │  - CRUD operations (<100ms)                     │    │
│  │  - Version management                           │    │
│  │  - Search coordination                          │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  AI Gateway (Hot Path)                          │    │
│  │  - Token streaming (<350ms first token)         │    │
│  │  - Provider routing (Anthropic/OpenAI/Gemini)   │    │
│  │  - Caching & rate limiting                      │    │
│  │  - Quota enforcement                            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Auth Service (Optional thin layer)             │    │
│  │  - Claims enrichment                            │    │
│  │  - Tenant resolution                            │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────┬────────────────────────────────────────┘
                  │
                  │ SQL + Kafka events
                  ↓
┌──────────────────────────────────────────────────────────┐
│            DATA & EVENT LAYER                            │
│                                                          │
│  ┌──────────────────────┐  ┌─────────────────────────┐  │
│  │  Postgres + pgvector │  │  Kafka / Redpanda       │  │
│  │  - Relational data   │  │  - Event bus            │  │
│  │  - Vector embeddings │  │  - Workflow triggers    │  │
│  │  - Full-text search  │  │  - Job progress         │  │
│  │  - RLS enabled       │  │  - Audit log            │  │
│  └──────────────────────┘  └─────────────────────────┘  │
└─────────────────┬────────────────────────────────────────┘
                  │
                  │ Consume events
                  ↓
┌──────────────────────────────────────────────────────────┐
│         ASYNCHRONOUS TIER (Python Workers)               │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Document Ingestion Worker                      │    │
│  │  - PDF/DOCX/HTML parsing (unstructured.io)     │    │
│  │  - Text chunking & cleaning                     │    │
│  │  - Metadata extraction                          │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Embedding Worker                               │    │
│  │  - Generate embeddings (batch optimization)     │    │
│  │  - Store in pgvector                            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  RAG Worker                                     │    │
│  │  - Query expansion                              │    │
│  │  - Multi-pass retrieval                         │    │
│  │  - Cross-encoder reranking                      │    │
│  │  - Context assembly                             │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Agent Worker                                   │    │
│  │  - Multi-step reasoning (LangChain/AutoGen)     │    │
│  │  - Tool orchestration                           │    │
│  │  - Complex workflows                            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Crawler Worker                                 │    │
│  │  - Web scraping (Scrapy/Playwright)             │    │
│  │  - Anti-bot handling                            │    │
│  │  - Content extraction                           │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Key Architectural Boundaries

| Boundary | Protocol | Latency Target | Use Case |
|----------|----------|----------------|----------|
| **Browser ↔ Rust** | Connect RPC (gRPC-Web) | <100ms | Interactive UI, real-time streaming |
| **Rust ↔ Database** | SQL (connection pool) | <50ms | Transactional operations |
| **Rust → Kafka** | Kafka produce | <10ms | Event publishing (fire-and-forget) |
| **Kafka → Python** | Kafka consume | Async | Background job processing |
| **Python ↔ Database** | SQL | Variable | Result storage, state updates |

---

## Complete Directory Structure

### Overview (North Star)

```
poc-adr-builder-rust-next-js/
├── crates/                    # Rust workspace (all services)
├── workers/                   # Python async workers
├── apps/                      # Frontend applications
├── proto/                     # Protobuf schemas (single source of truth)
├── infra/                     # Infrastructure configs
├── tools/                     # Build & dev automation
├── docs/                      # Documentation
├── .meta/                     # Ephemeral working documents
├── Cargo.toml                 # Rust workspace root
├── pyproject.toml             # Python workspace root
├── package.json               # Node workspace root
├── WORKSPACE                  # Bazel workspace (optional)
└── README.md
```

### Detailed Structure with Phase Annotations

```
poc-adr-builder-rust-next-js/
│
├── crates/                           # Rust workspace
│   │
│   ├── adr-domain/                   # 📦 PHASE 1: Pure domain
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── adr.rs                # ADR entity
│   │   │   ├── version.rs            # Version entity
│   │   │   ├── tag.rs                # Tag entity
│   │   │   └── error.rs              # Domain errors
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   │
│   ├── adr-sdk/                      # 📦 PHASE 1: Ports + use cases
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── ports/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── repository.rs     # Repository trait
│   │   │   │   └── events.rs         # Event publisher trait
│   │   │   └── use_cases/
│   │   │       ├── mod.rs
│   │   │       ├── create_adr.rs
│   │   │       ├── update_adr.rs
│   │   │       ├── search_adrs.rs
│   │   │       └── version_adr.rs
│   │   ├── Cargo.toml                # depends: adr-domain
│   │   └── BUILD.bazel
│   │
│   ├── adr-adapters/                 # 📦 PHASE 1: Storage implementations
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── filesystem.rs         # [feature = "filesystem"]
│   │   │   ├── postgres.rs           # [feature = "postgres"]
│   │   │   └── kafka.rs              # 📦 PHASE 2: Kafka publisher
│   │   ├── Cargo.toml                # depends: adr-sdk
│   │   └── BUILD.bazel
│   │
│   ├── adr-service/                  # 📦 PHASE 1: gRPC service (ADR CRUD)
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── grpc/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── server.rs         # tonic server
│   │   │   │   └── handlers.rs       # RPC handlers
│   │   │   ├── observability/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── tracing.rs        # OpenTelemetry setup
│   │   │   │   └── metrics.rs        # Prometheus metrics
│   │   │   └── config.rs
│   │   ├── Cargo.toml                # depends: adr-sdk, adr-adapters
│   │   └── BUILD.bazel
│   │
│   ├── ai-gateway/                   # 📦 PHASE 1: AI streaming service
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── streaming/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── anthropic.rs      # Anthropic streaming
│   │   │   │   ├── openai.rs         # OpenAI streaming
│   │   │   │   └── gemini.rs         # Gemini streaming
│   │   │   ├── providers/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── router.rs         # Provider selection
│   │   │   │   └── failover.rs       # Failover logic
│   │   │   ├── caching/
│   │   │   │   ├── mod.rs
│   │   │   │   └── redis.rs          # Response cache
│   │   │   ├── quota/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── tracker.rs        # Usage tracking
│   │   │   │   └── enforcer.rs       # Quota enforcement
│   │   │   ├── grpc/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── server.rs
│   │   │   │   └── streaming.rs      # Server streaming handler
│   │   │   ├── observability/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── tracing.rs
│   │   │   │   └── metrics.rs        # Token/latency metrics
│   │   │   └── config.rs
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   │
│   ├── auth-service/                 # 📦 PHASE 3: Auth claims (optional)
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── claims.rs             # Claims enrichment
│   │   │   └── grpc/
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   │
│   └── adr-cli/                      # 📦 PHASE 1: CLI tool
│       ├── src/
│       │   ├── main.rs
│       │   ├── commands/
│       │   │   ├── mod.rs
│       │   │   ├── create.rs
│       │   │   ├── list.rs
│       │   │   ├── update.rs
│       │   │   └── search.rs
│       │   └── config.rs
│       ├── Cargo.toml                # depends: adr-sdk, adr-adapters
│       └── BUILD.bazel
│
├── workers/                          # 📦 PHASE 2: Python async workers
│   │
│   ├── ingestion/                    # Document ingestion worker
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # Kafka consumer loop
│   │   │   ├── parsers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdf.py            # PDF parsing
│   │   │   │   ├── docx.py           # DOCX parsing
│   │   │   │   └── html.py           # HTML parsing
│   │   │   ├── chunker.py            # Text chunking
│   │   │   └── metadata.py           # Metadata extraction
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── embeddings/                   # Embedding generation worker
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── generator.py          # Embedding API calls
│   │   │   ├── batch.py              # Batch optimization
│   │   │   └── storage.py            # Store in pgvector
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── rag/                          # 📦 PHASE 2: RAG search worker
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── retrieval/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vector.py         # Vector search
│   │   │   │   ├── lexical.py        # Full-text search
│   │   │   │   └── hybrid.py         # Hybrid fusion
│   │   │   ├── reranking/
│   │   │   │   ├── __init__.py
│   │   │   │   └── cross_encoder.py  # Cross-encoder reranking
│   │   │   ├── query/
│   │   │   │   ├── __init__.py
│   │   │   │   └── expansion.py      # Query expansion
│   │   │   └── synthesis.py          # Result synthesis
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── agents/                       # 📦 PHASE 3: Agent orchestration
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── orchestrator.py       # LangChain/AutoGen
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── search.py
│   │   │   │   └── web.py
│   │   │   └── workflows/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── crawler/                      # 📦 PHASE 3: Web crawler
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── scraper.py            # Scrapy/Playwright
│   │   │   ├── extractor.py          # Content extraction
│   │   │   └── antibot.py            # Anti-bot handling
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   └── shared/                       # Shared Python utilities
│       ├── src/
│       │   ├── __init__.py
│       │   ├── kafka_client.py       # Kafka utilities
│       │   ├── db_client.py          # Postgres utilities
│       │   ├── observability.py      # OpenTelemetry setup
│       │   └── config.py             # Configuration
│       └── pyproject.toml
│
├── apps/                             # Frontend applications
│   │
│   └── adr-web/                      # 📦 PHASE 1: Next.js frontend
│       ├── app/                      # App Router
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   ├── (auth)/               # Auth routes
│       │   │   ├── login/
│       │   │   └── callback/
│       │   ├── chat/                 # 📦 PHASE 1: Streaming chat
│       │   │   ├── page.tsx
│       │   │   └── layout.tsx
│       │   ├── adrs/                 # 📦 PHASE 1: ADR CRUD
│       │   │   ├── page.tsx          # List view
│       │   │   ├── [id]/
│       │   │   │   ├── page.tsx      # Detail view
│       │   │   │   └── edit/
│       │   │   └── new/
│       │   ├── search/               # 📦 PHASE 2: Advanced search
│       │   │   └── page.tsx
│       │   └── jobs/                 # 📦 PHASE 2: Job monitoring
│       │       └── page.tsx
│       ├── components/
│       │   ├── ui/                   # shadcn/ui components
│       │   ├── chat/
│       │   │   ├── ChatInterface.tsx
│       │   │   ├── StreamingResponse.tsx
│       │   │   └── MessageList.tsx
│       │   ├── adr/
│       │   │   ├── ADREditor.tsx
│       │   │   ├── ADRList.tsx
│       │   │   └── VersionHistory.tsx
│       │   └── search/
│       │       ├── SearchBar.tsx
│       │       └── ResultsList.tsx
│       ├── lib/
│       │   ├── grpc/                 # Generated gRPC clients
│       │   │   ├── adr/              # From proto/adr/v1/
│       │   │   ├── ai/               # From proto/ai/v1/
│       │   │   └── events/           # From proto/events/v1/
│       │   ├── state/                # Zustand stores
│       │   │   ├── chat.ts
│       │   │   ├── adrs.ts
│       │   │   └── user.ts
│       │   ├── hooks/                # React hooks
│       │   │   ├── useChat.ts
│       │   │   └── useADRs.ts
│       │   └── utils/
│       ├── public/
│       ├── styles/
│       ├── package.json
│       ├── tsconfig.json
│       ├── next.config.js
│       └── BUILD.bazel
│
├── proto/                            # 📦 PHASE 1: Protobuf schemas
│   │
│   ├── adr/
│   │   └── v1/
│   │       ├── adr.proto             # ADR entity
│   │       ├── service.proto         # ADR service RPCs
│   │       └── BUILD.bazel
│   │
│   ├── ai/
│   │   └── v1/
│   │       ├── gateway.proto         # AI Gateway RPCs
│   │       ├── streaming.proto       # Streaming messages
│   │       └── BUILD.bazel
│   │
│   ├── events/                       # 📦 PHASE 2: Kafka event schemas
│   │   └── v1/
│   │       ├── document.proto        # Document events
│   │       ├── job.proto             # Job progress events
│   │       ├── search.proto          # Search events
│   │       └── BUILD.bazel
│   │
│   └── auth/                         # 📦 PHASE 3: Auth service
│       └── v1/
│           ├── claims.proto
│           └── BUILD.bazel
│
├── infra/                            # Infrastructure configs
│   │
│   ├── docker-compose.yml            # 📦 PHASE 1: Local dev stack
│   │                                 # (Postgres, Redis, Envoy)
│   │
│   ├── docker-compose.kafka.yml      # 📦 PHASE 2: + Kafka/Redpanda
│   │
│   ├── envoy/                        # 📦 PHASE 1: Envoy configuration
│   │   ├── envoy.yaml                # Main config
│   │   ├── clusters.yaml             # Service clusters
│   │   └── filters.yaml              # JWT validation, etc.
│   │
│   ├── postgres/                     # 📦 PHASE 1: Database setup
│   │   ├── init.sql                  # Schema creation
│   │   ├── migrations/               # SQL migrations
│   │   │   ├── 001_initial_schema.sql
│   │   │   ├── 002_add_vectors.sql
│   │   │   └── 003_enable_rls.sql
│   │   └── seeds/                    # Seed data
│   │
│   ├── kafka/                        # 📦 PHASE 2: Kafka configuration
│   │   ├── topics.yaml               # Topic definitions
│   │   └── schemas/                  # Schema registry configs
│   │
│   ├── observability/                # 📦 PHASE 3: Observability stack
│   │   ├── otel-collector.yaml       # OpenTelemetry collector
│   │   ├── prometheus.yml            # Prometheus config
│   │   ├── grafana/
│   │   │   ├── datasources.yml
│   │   │   └── dashboards/
│   │   │       ├── ai-performance.json
│   │   │       ├── service-health.json
│   │   │       └── cost-tracking.json
│   │   └── jaeger.yml                # Jaeger tracing
│   │
│   └── k8s/                          # 📦 PHASE 3: Kubernetes manifests
│       ├── base/                     # Base configs
│       └── overlays/                 # Environment-specific
│           ├── dev/
│           ├── staging/
│           └── production/
│
├── tools/                            # Build & dev automation
│   │
│   ├── codegen/                      # 📦 PHASE 1: Code generation
│   │   ├── proto-gen.sh              # Generate from protobuf
│   │   ├── buf.yaml                  # Buf configuration
│   │   └── buf.gen.yaml              # Buf code generation
│   │
│   ├── dev/                          # 📦 PHASE 1: Dev utilities
│   │   ├── setup-local.sh            # Local environment setup
│   │   ├── start-services.sh         # Start all services
│   │   └── stop-services.sh          # Stop all services
│   │
│   ├── db/                           # 📦 PHASE 1: Database utilities
│   │   ├── migrate.sh                # Run migrations
│   │   ├── seed.sh                   # Seed data
│   │   └── reset.sh                  # Reset database
│   │
│   ├── testing/                      # 📦 PHASE 1: Testing utilities
│   │   ├── run-integration-tests.sh
│   │   ├── run-load-tests.sh         # 📦 PHASE 3
│   │   └── measure-latency.sh        # 📦 PHASE 3
│   │
│   └── deploy/                       # 📦 PHASE 3: Deployment scripts
│       ├── build-images.sh
│       ├── push-images.sh
│       └── deploy-staging.sh
│
├── docs/                             # Documentation (existing)
│   ├── architecture/
│   ├── adr/
│   ├── api/
│   └── development/
│
├── .meta/                            # Ephemeral working documents
│   └── task-service/
│       ├── design-docs/
│       └── project-management/
│
├── Cargo.toml                        # 📦 PHASE 1: Rust workspace root
├── pyproject.toml                    # 📦 PHASE 2: Python workspace root
├── package.json                      # 📦 PHASE 1: Node workspace root
├── WORKSPACE                         # Bazel workspace (optional)
├── .gitignore
├── .dockerignore
├── LICENSE
└── README.md
```

---

## Phased Implementation

### Phase 1: Rust Sync Tier + Frontend (Weeks 1-4)

**Goal:** Validate critical path: Browser → Rust → AI Provider

#### What to Build

**Foundation:**
- ✅ Cargo workspace with layered crates
- ✅ Proto schemas for ADR + AI Gateway
- ✅ Buf code generation pipeline
- ✅ Next.js with App Router + Connect Web client
- ✅ Docker Compose (Postgres + Redis + Envoy)

**Core Services:**
- ✅ `adr-domain`: Pure entities (ADR, Version, Tag)
- ✅ `adr-sdk`: Repository trait, use cases
- ✅ `adr-adapters`: Filesystem + Postgres adapters
- ✅ `adr-service`: gRPC service (CRUD, search coordination)
- ✅ `ai-gateway`: Streaming service (Anthropic/OpenAI)
- ✅ `adr-cli`: CLI tool (validates SDK reuse)

**Frontend:**
- ✅ ADR CRUD pages (`/adrs`, `/adrs/[id]`, `/adrs/new`)
- ✅ Streaming chat interface (`/chat`)
- ✅ Connect Web integration (gRPC-Web)
- ✅ Zustand for UI state
- ✅ React Query for server state

**Infrastructure:**
- ✅ Envoy with JWT validation
- ✅ Postgres with pgvector
- ✅ Redis for caching
- ✅ OpenTelemetry basics

#### Success Criteria

**Performance:**
- ✅ First token latency: < 350ms (p95)
- ✅ Inter-token latency: < 60ms (p95)
- ✅ UI response time: < 100ms
- ✅ Cancellation propagation: < 100ms

**Architecture:**
- ✅ CLI and Service share SDK (same code)
- ✅ Swapping storage backend: 1 line change
- ✅ Domain crate has zero infrastructure deps
- ✅ gRPC-Web streaming works in all browsers

**Deliverables:**
- ✅ Working chat with token streaming
- ✅ ADR CRUD operations
- ✅ Simple semantic search (pgvector)
- ✅ Hexagonal boundaries validated

#### Time Estimate: 16-24 EU

---

### Phase 2: Python Async Tier (Weeks 5-6)

**Goal:** Add event-driven background processing

#### What to Build

**Event Bus:**
- ✅ Kafka/Redpanda (managed or Docker Compose)
- ✅ Topics: `document.uploaded`, `embeddings.requested`, `rag.search.requested`
- ✅ Proto schemas for events (`proto/events/v1/`)
- ✅ Kafka adapter in `adr-adapters`
- ✅ Event publisher trait in `adr-sdk`

**Python Workers:**
- ✅ `workers/shared`: Kafka client, DB client, observability
- ✅ `workers/ingestion`: Document parsing (PDF/DOCX/HTML)
- ✅ `workers/embeddings`: Embedding generation (batch)
- ✅ `workers/rag`: Multi-pass retrieval, reranking

**Frontend Updates:**
- ✅ Job monitoring UI (`/jobs`)
- ✅ Advanced search UI (`/search`)
- ✅ Progress indicators for async operations

**Infrastructure:**
- ✅ Docker Compose with Kafka
- ✅ Kafka topic definitions
- ✅ Schema registry setup

#### Success Criteria

**Event Processing:**
- ✅ Document uploaded → parsed → chunked → embedded (end-to-end)
- ✅ Job progress events visible in UI
- ✅ Kafka consumer lag < 100 messages
- ✅ Worker horizontal scaling works

**Python Integration:**
- ✅ LangChain/LlamaIndex basics work
- ✅ unstructured.io document parsing works
- ✅ Embeddings stored in pgvector correctly

**Deliverables:**
- ✅ Upload document → searchable (full pipeline)
- ✅ Advanced RAG with reranking
- ✅ Job monitoring dashboard

#### Time Estimate: 8-12 EU

---

### Phase 3: Production Readiness (Weeks 7-8)

**Goal:** Make it production-grade

#### What to Build

**Advanced Features:**
- ✅ Agent orchestration (AutoGen/CrewAI)
- ✅ Web crawler worker
- ✅ Complex multi-step workflows
- ✅ Auth service (claims enrichment)

**Observability:**
- ✅ Full OpenTelemetry tracing
- ✅ Grafana dashboards (AI performance, service health, cost)
- ✅ Prometheus metrics collection
- ✅ Jaeger distributed tracing
- ✅ Alert configuration (PagerDuty/OpsGenie)

**Security:**
- ✅ Clerk/Auth0 integration
- ✅ Envoy JWT validation
- ✅ Row-Level Security (RLS) in Postgres
- ✅ Egress allowlist
- ✅ Secrets management

**Cost Management:**
- ✅ Per-user/org quotas
- ✅ Spend tracking dashboard
- ✅ Automatic kill-switches
- ✅ Budget alerts

**Operations:**
- ✅ Load testing (1000+ concurrent streams)
- ✅ Disaster recovery procedures
- ✅ Deployment runbooks
- ✅ Kubernetes manifests

#### Success Criteria

**Performance Under Load:**
- ✅ Handle 1000 concurrent chat streams
- ✅ Latency targets met under load (p95)
- ✅ Error rate < 0.1%
- ✅ Stream completion rate > 99%

**Security:**
- ✅ Penetration testing passed
- ✅ RLS verified (tenant isolation)
- ✅ Secrets audit clean
- ✅ Auth flow end-to-end

**Observability:**
- ✅ All critical metrics visible
- ✅ Alerts tested and working
- ✅ Dashboards comprehensive
- ✅ Distributed tracing working

**Deliverables:**
- ✅ Production-ready architecture validated
- ✅ All SLOs met
- ✅ Security hardened
- ✅ Observability complete

#### Time Estimate: 12-16 EU

---

## Component Specifications

### Rust Services

#### adr-domain

**Purpose:** Pure domain entities with business logic

**Dependencies:** None (zero infrastructure)

**Key Types:**
```rust
pub struct ADR {
    pub id: Uuid,
    pub title: String,
    pub content: String,
    pub status: ADRStatus,
    pub tags: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

pub enum ADRStatus {
    Draft,
    Proposed,
    Accepted,
    Deprecated,
    Superseded,
}
```

**Rules:**
- No I/O (pure functions only)
- No external crate dependencies (except std, uuid, chrono)
- Business logic lives here

---

#### adr-sdk

**Purpose:** Use cases and port definitions (hexagonal architecture)

**Dependencies:** `adr-domain`

**Key Traits:**
```rust
#[async_trait]
pub trait ADRRepository {
    async fn create(&self, adr: ADR) -> Result<ADR>;
    async fn find_by_id(&self, id: Uuid) -> Result<Option<ADR>>;
    async fn list(&self, filter: ADRFilter) -> Result<Vec<ADR>>;
    async fn update(&self, adr: ADR) -> Result<ADR>;
    async fn delete(&self, id: Uuid) -> Result<()>;
}

#[async_trait]
pub trait EventPublisher {
    async fn publish(&self, event: DomainEvent) -> Result<()>;
}
```

**Use Cases:**
- `CreateADR`: Validates and persists new ADR
- `UpdateADR`: Updates existing ADR
- `SearchADRs`: Semantic + lexical search
- `VersionADR`: Creates new version

---

#### adr-service

**Purpose:** gRPC service for ADR CRUD operations

**Dependencies:** `adr-sdk`, `adr-adapters`, `tonic`, `sqlx`

**Configuration:**
```rust
pub struct Config {
    pub grpc_port: u16,
    pub database_url: String,
    pub kafka_brokers: Vec<String>,
    pub otel_endpoint: String,
}
```

**gRPC Methods:**
```protobuf
service ADRService {
  rpc CreateADR(CreateADRRequest) returns (CreateADRResponse);
  rpc GetADR(GetADRRequest) returns (GetADRResponse);
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc UpdateADR(UpdateADRRequest) returns (UpdateADRResponse);
  rpc DeleteADR(DeleteADRRequest) returns (DeleteADRResponse);
  rpc SearchADRs(SearchADRsRequest) returns (SearchADRsResponse);
}
```

**Latency Targets:**
- Create/Update: < 100ms (p95)
- Read: < 50ms (p95)
- Search: < 200ms (p95)

---

#### ai-gateway

**Purpose:** AI streaming service with provider abstraction

**Dependencies:** `tonic`, `reqwest`, `redis`, `tokio-stream`

**Configuration:**
```rust
pub struct Config {
    pub grpc_port: u16,
    pub anthropic_api_key: String,
    pub openai_api_key: String,
    pub gemini_api_key: String,
    pub redis_url: String,
    pub default_provider: Provider,
}
```

**gRPC Methods:**
```protobuf
service AIGateway {
  rpc StreamChat(ChatRequest) returns (stream ChatChunk);
  rpc GenerateEmbedding(EmbeddingRequest) returns (EmbeddingResponse);
  rpc GetModels(GetModelsRequest) returns (GetModelsResponse);
}
```

**Latency Targets:**
- First token: < 350ms (p95)
- Inter-token: < 60ms (p95)
- Cancellation: < 100ms

**Features:**
- Provider routing (preference-based)
- Failover (automatic)
- Response caching (Redis)
- Quota enforcement (per-user/org)
- Token tracking (real-time)

---

### Python Workers

#### ingestion Worker

**Purpose:** Parse and process uploaded documents

**Dependencies:** `unstructured`, `kafka-python`, `sqlalchemy`, `pgvector`

**Event Input:** `document.uploaded`
```protobuf
message DocumentUploaded {
  string document_id = 1;
  string tenant_id = 2;
  string s3_url = 3;
  string mime_type = 4;
}
```

**Event Output:** `document.processed`
```protobuf
message DocumentProcessed {
  string document_id = 1;
  string tenant_id = 2;
  int32 chunks_created = 3;
  repeated string chunk_ids = 4;
}
```

**Processing Steps:**
1. Download from S3
2. Parse based on MIME type (PDF/DOCX/HTML)
3. Extract text and metadata
4. Chunk semantically
5. Publish `embeddings.requested` for each chunk
6. Store chunks in DB

**SLO:** < 30 seconds for typical document (10 pages)

---

#### rag Worker

**Purpose:** Advanced retrieval and reranking

**Dependencies:** `langchain`, `llama-index`, `sentence-transformers`

**Event Input:** `rag.search.requested`
```protobuf
message RAGSearchRequested {
  string search_id = 1;
  string tenant_id = 2;
  string query = 3;
  int32 top_k = 4;
}
```

**Processing Steps:**
1. Query expansion (generate variations)
2. Vector search (pgvector)
3. Lexical search (full-text)
4. Hybrid fusion (RRF)
5. Cross-encoder reranking
6. Result synthesis
7. Store results

**SLO:** < 15 seconds for complex search

---

### Frontend (Next.js)

#### Architecture

**Server Components:**
- Use Node.js runtime (not Edge)
- Call Rust services via native gRPC
- SSR for initial page load
- No client-side data fetching

**Client Components:**
- Use Connect Web (gRPC-Web)
- Stream tokens in real-time
- Optimistic UI updates
- Handle cancellation

**State Management:**
- **Zustand**: UI state (chat messages, drafts)
- **React Query**: Server state (ADRs, cached searches)
- **URL State**: Filters, pagination

---

## Technology Stack

### Complete Stack Table

| Layer | Component | Technology | Version | Purpose |
|-------|-----------|-----------|---------|---------|
| **Frontend** | Framework | Next.js | 14+ | React with App Router |
| | Language | TypeScript | 5+ | Type safety |
| | RPC Client | @connectrpc/connect-web | latest | gRPC-Web |
| | State (UI) | Zustand | 4+ | UI state |
| | State (Server) | TanStack Query | 5+ | Server state |
| | Styling | Tailwind CSS | 3+ | Utility-first CSS |
| | Components | shadcn/ui | latest | Component library |
| **API Gateway** | Proxy | Envoy | 1.28+ | gRPC-Web translation |
| | TLS | Let's Encrypt | - | Free certificates |
| **Backend (Rust)** | Language | Rust | 1.75+ | Services |
| | Async Runtime | Tokio | 1.35+ | Async/await |
| | gRPC | Tonic | 0.11+ | gRPC server |
| | HTTP Client | reqwest | 0.11+ | Provider APIs |
| | Database | sqlx | 0.7+ | Postgres client |
| | Serialization | serde | 1.0+ | JSON |
| | Protobuf | prost | 0.12+ | Protocol Buffers |
| | Observability | tracing | 0.1+ | Structured logging |
| | OTel | opentelemetry | 0.21+ | Tracing/metrics |
| **Backend (Python)** | Language | Python | 3.11+ | Workers |
| | LLM Framework | LangChain | 0.1+ | Orchestration |
| | RAG Framework | LlamaIndex | 0.9+ | Retrieval |
| | Agent Framework | AutoGen | 0.2+ | Multi-agent |
| | Kafka Client | confluent-kafka | 2.3+ | Event bus |
| | Doc Parsing | unstructured | 0.11+ | PDF/DOCX/HTML |
| | Embeddings | sentence-transformers | 2.2+ | Local embeddings |
| | DB Client | sqlalchemy | 2.0+ | Postgres ORM |
| | Vector Client | pgvector-python | 0.2+ | Vector ops |
| **Data** | Database | Postgres | 15+ | Relational + vector |
| | Vector Ext | pgvector | 0.5+ | Vector similarity |
| | Connection Pool | PgBouncer | 1.21+ | Connection mgmt |
| | Cache | Redis | 7+ | Response cache |
| **Event Bus** | Broker | Redpanda | 23+ | Kafka-compatible |
| | Alt: Managed | AWS MSK | - | Managed Kafka |
| | Schema Registry | Confluent | 7+ | Protobuf schemas |
| **Observability** | Metrics | Prometheus | 2.48+ | Time-series |
| | Dashboards | Grafana | 10+ | Visualization |
| | Tracing | Jaeger | 1.52+ | Distributed traces |
| | Logs | Loki | 2.9+ | Log aggregation |
| | Collector | OTel Collector | 0.91+ | Telemetry pipeline |
| **Infrastructure** | Containers | Docker | 24+ | Development |
| | Orchestration | Docker Compose | 2.23+ | Local dev |
| | Production | ECS/Cloud Run | - | Managed containers |
| | CI/CD | GitHub Actions | - | Automation |
| | Protobuf | Buf | 1.28+ | Schema management |

---

## Development Workflow

### Daily Development

**Start local environment:**
```bash
# Terminal 1: Start infrastructure
docker-compose up -d

# Terminal 2: Start Rust services
cargo run -p adr-service
# or
cargo run -p ai-gateway

# Terminal 3: Start frontend
cd apps/adr-web
pnpm dev

# Terminal 4: (Phase 2) Start Python workers
cd workers/ingestion
poetry run python -m src.main
```

**Run tests:**
```bash
# Rust tests
cargo test

# Python tests
cd workers/rag
pytest

# Frontend tests
cd apps/adr-web
pnpm test

# Integration tests
./tools/testing/run-integration-tests.sh
```

**Generate code from proto:**
```bash
# Regenerate all clients
./tools/codegen/proto-gen.sh

# Or use make
make proto
```

---

### Code Review Checklist

**Before committing:**
- [ ] All tests pass (`cargo test`, `pytest`, `pnpm test`)
- [ ] Proto changes have generated code committed
- [ ] Observability added (traces, metrics, logs)
- [ ] Error handling covers edge cases
- [ ] Documentation updated (if public API changed)
- [ ] No secrets in code or config
- [ ] Latency targets considered

**For Proto changes:**
- [ ] Buf lint passes
- [ ] No breaking changes (or justified)
- [ ] Generated code committed
- [ ] All consumers updated

**For new services:**
- [ ] Dockerfile present
- [ ] Health check endpoint
- [ ] Graceful shutdown
- [ ] Config via environment variables
- [ ] Observability integrated

---

## Migration Strategy

### Lifting to Production Monorepo

**Goal:** < 4 EU migration time, zero refactoring

#### Step 1: Directory Copy (1 EU)

```bash
# From PoC to Monorepo
MONOREPO_PATH="../production-monorepo"

# Copy Rust services
cp -r crates/* $MONOREPO_PATH/services/rust/

# Copy Python workers
cp -r workers/* $MONOREPO_PATH/workers/

# Copy Frontend
cp -r apps/adr-web $MONOREPO_PATH/apps/

# Copy Proto schemas
cp -r proto/* $MONOREPO_PATH/proto/

# Copy Infrastructure configs
cp -r infra/* $MONOREPO_PATH/infra/
```

#### Step 2: Update Workspace Configs (0.5 EU)

**Cargo.toml:**
```toml
# Add to monorepo Cargo.toml
[workspace]
members = [
    # Existing...
    "services/rust/adr-domain",
    "services/rust/adr-sdk",
    "services/rust/adr-adapters",
    "services/rust/adr-service",
    "services/rust/ai-gateway",
]
```

**package.json:**
```json
{
  "workspaces": [
    "apps/adr-web",
    // Existing workspaces...
  ]
}
```

**pyproject.toml:**
```toml
[tool.poetry]
packages = [
    { include = "workers/ingestion" },
    { include = "workers/rag" },
    // ...
]
```

#### Step 3: Update Bazel (1 EU)

```bash
# Verify Bazel builds
bazel build //services/rust/adr-service
bazel build //apps/adr-web
bazel test //...
```

#### Step 4: Integration (1.5 EU)

- Wire into monorepo CI/CD
- Update deployment configs
- Add to service mesh (if applicable)
- Update documentation
- Add to monitoring dashboards

#### Step 5: Cleanup (0.5 EU)

- Archive PoC repo
- Document lessons learned
- Update architecture decisions
- Celebrate! 🎉

**Total: ~4 EU**

---

### Import Path Changes

**Zero changes needed for:**
- Rust: `use adr_sdk::repository` (same path)
- TypeScript: `import { ADRServiceClient } from '@/lib/grpc/adr'` (same path)
- Python: Adjust for monorepo structure if needed

**Proto generation:**
- Update `buf.gen.yaml` with monorepo paths
- Regenerate once
- No source code changes

---

## Best Practices

### Hexagonal Architecture

**Rules:**
1. **Domain** depends on nothing
2. **SDK** depends only on domain
3. **Adapters** depend on SDK
4. **Services** depend on SDK + adapters
5. **Never** import infrastructure in domain

**Testing:**
```rust
// Test domain without infrastructure
#[test]
fn test_adr_validation() {
    let adr = ADR::new("Title", "Content");
    assert!(adr.is_valid());
}

// Test use case with mock repository
#[tokio::test]
async fn test_create_adr_use_case() {
    let mock_repo = MockRepository::new();
    let use_case = CreateADR::new(Box::new(mock_repo));
    let result = use_case.execute(request).await;
    assert!(result.is_ok());
}
```

---

### gRPC Best Practices

**Streaming:**
```rust
// Server streaming (AI Gateway)
async fn stream_chat(
    &self,
    request: Request<ChatRequest>,
) -> Result<Response<Self::StreamChatStream>, Status> {
    let (tx, rx) = mpsc::channel(100);
    
    tokio::spawn(async move {
        // Stream tokens
        for token in provider.stream().await {
            tx.send(Ok(ChatChunk { token })).await?;
        }
    });
    
    Ok(Response::new(ReceiverStream::new(rx)))
}
```

**Error Handling:**
```rust
// Map domain errors to gRPC status codes
impl From<DomainError> for Status {
    fn from(err: DomainError) -> Self {
        match err {
            DomainError::NotFound => Status::not_found(err.to_string()),
            DomainError::Validation => Status::invalid_argument(err.to_string()),
            DomainError::Unauthorized => Status::permission_denied(err.to_string()),
            _ => Status::internal(err.to_string()),
        }
    }
}
```

---

### Observability Best Practices

**Structured Logging:**
```rust
// Always include correlation fields
tracing::info!(
    tenant_id = %tenant_id,
    user_id = %user_id,
    adr_id = %adr_id,
    "ADR created successfully"
);
```

**Tracing:**
```rust
// Instrument functions
#[tracing::instrument(skip(self))]
async fn create_adr(&self, request: CreateADRRequest) -> Result<ADR> {
    // Automatically adds span with function name and args
}
```

**Metrics:**
```rust
// Use histogram for latencies
histogram!("ai_first_token_duration_ms", first_token_ms);

// Use counter for counts
counter!("adrs_created_total", 1, "tenant_id" => tenant_id);

// Use gauge for current state
gauge!("active_chat_streams", active_count as f64);
```

---

### Testing Strategy

**Unit Tests (Fast):**
- Domain logic (pure functions)
- Use cases (with mocks)
- Utilities

**Integration Tests (Medium):**
- Repository implementations (with test DB)
- gRPC handlers (with test server)
- Kafka consumers (with test topics)

**End-to-End Tests (Slow):**
- Full request flow (browser → service → provider)
- Job workflows (upload → process → searchable)
- Failure scenarios

**Performance Tests:**
- Load testing (1000+ concurrent streams)
- Latency measurement (p50/p95/p99)
- Cost tracking

---

## Appendix

### Glossary

- **ADR**: Architecture Decision Record
- **Sync Tier**: Rust services handling real-time operations (<1s)
- **Async Tier**: Python workers handling background jobs (seconds to minutes)
- **Connect RPC**: Modern RPC framework compatible with gRPC
- **Hexagonal Architecture**: Ports & Adapters pattern
- **pgvector**: Postgres extension for vector similarity search
- **RLS**: Row-Level Security (multi-tenancy isolation)
- **OpenTelemetry**: Observability standard (traces, metrics, logs)
- **SLO**: Service Level Objective

### References

- **Architecture Brief**: `docs/architecture/brief.md`
- **Original PoC Analysis**: `docs/architecture/repo-structure-02.md`
- **Monorepo Reference**: `docs/architecture/repo-structure-01.md`
- **Connect RPC**: https://connectrpc.com
- **Buf**: https://buf.build/docs
- **OpenTelemetry**: https://opentelemetry.io

---

## Document Metadata

**Version:** 1.0  
**Created:** October 2025  
**Last Updated:** October 2025  
**Authors:** Engineering Team  
**Status:** North Star - Ready for Implementation  

**Next Steps:**
1. Review and approve this structure
2. Create Phase 1 implementation plan
3. Set up initial Cargo workspace
4. Begin proto schema design

---

**This document represents the complete vision for the ADR Platform PoC. Implementation proceeds in phases, but the structure is designed to support the full architecture from day one.**
