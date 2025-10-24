# Foundational Infrastructure: The 7 Core Pieces

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Why these are foundational
- → [05-technology-integration.md](./05-technology-integration.md) - How they work together
- → [07-implementation-roadmap.md](./07-implementation-roadmap.md) - How to build them

---

## Context

### What Makes Something "Foundational"

**Criteria for foundational infrastructure**:
1. ✅ **100% certainty** all projects will need it
2. ✅ **High cost** to retrofit if done wrong
3. ✅ **Technology/architecture** decision (not domain logic)
4. ✅ **Platform-wide capability** (not project-specific)

**Examples**:
- Foundational: API Gateway (all services need it, Envoy config hard to change later)
- NOT Foundational: ADR Domain (domain logic, only some projects need it)

**Rule**: Foundational infrastructure gets extracted IMMEDIATELY (no rule of two/three)

---

## Key Insights

### The 7 Foundational Pieces

All 7 pieces will be built in **Week 1-2** of implementation:

```
1. Contracts (Proto Schemas)       ← Type safety foundation
2. API Gateway Core               ← Gateway patterns
3. AI Gateway SDK                 ← AI provider abstraction  
4. Frontend Foundation            ← Next.js + Connect patterns
5. Observability SDK              ← Tracing/metrics/logs
6. CLI Framework                  ← CLI tool patterns
7. Storage Patterns               ← Database/RLS/repository
```

**Why these 7**:
- Stated requirement: "Next.js, API gateway, AI, CLI tools needed"
- Technology decisions: Rust/Python/TypeScript integration
- High retrofit cost: Auth, observability, gateway config
- Platform-wide: Every service needs these patterns

---

## 1. Contracts (Proto Schemas)

### Purpose
Single source of truth for all types and service interfaces. Generates code for Rust, TypeScript, and Python.

### Structure
```
shared/contracts/
├── proto/
│   ├── common/v1/
│   │   ├── user.proto          # User, auth claims
│   │   ├── org.proto           # Organization, tenant
│   │   ├── metadata.proto      # Request metadata, headers
│   │   ├── pagination.proto    # Standard pagination
│   │   ├── error.proto         # Error types
│   │   └── events.proto        # Event envelope
│   │
│   ├── api-gateway/v1/
│   │   └── gateway.proto       # Gateway config, routes
│   │
│   └── ai/v1/
│       ├── chat.proto          # Chat types (streaming)
│       ├── completion.proto    # Completion types
│       └── models.proto        # Model metadata
│
├── buf.yaml                    # Buf configuration
├── buf.gen.yaml                # Code generation
└── README.md                   # Contract evolution rules
```

### Why Foundational
- Zero downside (just types, no implementation)
- High value (type safety across all languages)
- Breaking changes affect everything
- Enables rapid development (generate code)

### Usage Pattern
```bash
# In any project
cd project-a
ln -s ../../shared/contracts/proto proto
buf generate
# Types generated for Rust, TS, Python
```

### Related Docs
- Implementation: [07-implementation-roadmap.md](./07-implementation-roadmap.md#week-1-contracts)
- Integration: [05-technology-integration.md](./05-technology-integration.md#protobuf-as-glue)

---

## 2. API Gateway Core

### Purpose
Envoy configuration patterns and gateway utilities shared by all services.

### Structure
```
shared/api-gateway-core/
├── envoy-base/
│   ├── envoy.yaml.template     # Base Envoy config
│   ├── filters/
│   │   ├── jwt_authn.yaml      # OIDC JWT validation
│   │   ├── cors.yaml           # CORS config
│   │   ├── grpc_web.yaml       # gRPC-Web translation
│   │   └── rate_limit.yaml     # Rate limiting
│   └── clusters/
│       └── backend.yaml.template
│
├── rust/                       # Rust gateway utilities
│   ├── src/
│   │   ├── auth.rs             # Auth helpers
│   │   ├── metadata.rs         # Request metadata extraction
│   │   ├── observability.rs    # Tracing/metrics
│   │   └── middleware.rs       # Common middleware
│   └── Cargo.toml
│
├── typescript/                 # TS client utilities
│   └── src/
│       ├── client.ts           # Connect client factory
│       └── interceptors.ts     # Auth interceptors
│
└── docs/
    ├── SETUP.md                # How to use
    └── PATTERNS.md             # Common patterns
```

### Why Foundational
- All services need API gateway
- Envoy config is complex and hard to change
- Auth/CORS patterns must be consistent
- High cost if every project does differently

### Usage Pattern
```rust
// In Rust service
use api_gateway_core::{
    auth::extract_user_context,
    metadata::RequestMetadata,
};

async fn handle_request(req: Request) -> Result<Response> {
    let user = extract_user_context(&req)?;
    let meta = RequestMetadata::from_request(&req)?;
    // ... business logic
}
```

### Related Docs
- Details: [05-technology-integration.md](./05-technology-integration.md#api-gateway)
- Reference: [10-reference-projects.md](./10-reference-projects.md#adr-platform-architecture)

---

## 3. AI Gateway SDK

### Purpose
AI provider abstraction with streaming, rate limiting, cost tracking, and failover.

### Structure
```
shared/ai-gateway-sdk/
├── rust/
│   ├── src/
│   │   ├── providers/
│   │   │   ├── anthropic.rs    # Anthropic provider
│   │   │   ├── openai.rs       # OpenAI provider
│   │   │   ├── gemini.rs       # Google Gemini
│   │   │   └── mod.rs          # Provider trait
│   │   ├── streaming/
│   │   │   ├── chat.rs         # Chat streaming
│   │   │   ├── buffering.rs    # Smart buffering
│   │   │   └── cancellation.rs # Cancellation handling
│   │   ├── quota.rs            # Quota/rate limiting
│   │   ├── cost.rs             # Cost tracking
│   │   ├── cache.rs            # Response caching
│   │   └── lib.rs
│   └── Cargo.toml
│
├── typescript/
│   └── src/
│       ├── client.ts           # Streaming client
│       └── hooks.ts            # React hooks
│
└── proto/
    └── ai/v1/
        └── gateway.proto       # AI gateway API
```

### Why Foundational
- Multiple projects need AI (stated requirement)
- Provider switching expensive to refactor
- Streaming is tricky (get right once)
- Cost tracking must be consistent

### Provider Trait Pattern
```rust
#[async_trait]
pub trait AIProvider: Send + Sync {
    async fn chat_stream(
        &self,
        request: ChatRequest,
    ) -> Result<impl Stream<Item = ChatToken>>;
    
    fn model_info(&self) -> ModelInfo;
    fn cost_per_token(&self) -> CostInfo;
}

pub struct ProviderRouter {
    providers: HashMap<ProviderId, Box<dyn AIProvider>>,
    fallback_chain: Vec<ProviderId>,
}
```

### Related Docs
- Architecture: [10-reference-projects.md](./10-reference-projects.md#adr-platform-ai-gateway)
- Integration: [05-technology-integration.md](./05-technology-integration.md#ai-streaming)

---

## 4. Frontend Foundation

### Purpose
Next.js + Connect patterns, React hooks, and auth integration.

### Structure
```
shared/frontend-foundation/
├── packages/
│   ├── connect-client/         # gRPC-Web client factory
│   │   ├── src/
│   │   │   ├── client.ts       # Connect client setup
│   │   │   ├── auth.ts         # Auth interceptors
│   │   │   ├── errors.ts       # Error handling
│   │   │   └── streaming.ts    # Streaming helpers
│   │   └── package.json
│   │
│   ├── react-hooks/            # Common React patterns
│   │   ├── src/
│   │   │   ├── useAuth.ts      # Auth hook
│   │   │   ├── useGrpcQuery.ts # gRPC + React Query
│   │   │   ├── useGrpcStream.ts# Streaming hook
│   │   │   └── useGrpcMutation.ts
│   │   └── package.json
│   │
│   └── ui-primitives/          # Base components (optional)
│       ├── src/
│       │   ├── Button.tsx
│       │   ├── Input.tsx
│       │   └── Layout.tsx
│       └── package.json
│
├── templates/
│   └── nextjs-app/             # Template Next.js app
│       ├── app/
│       │   ├── layout.tsx      # Base layout
│       │   └── providers.tsx   # QueryClient, Auth
│       ├── lib/
│       │   └── grpc.ts         # Client setup
│       └── next.config.js
│
└── docs/
    ├── SETUP.md
    └── PATTERNS.md
```

### Why Foundational
- Every project has Next.js frontend (stated)
- gRPC-Web setup same everywhere
- Auth integration patterns reusable
- React Query + Zustand patterns proven

### Usage Pattern
```typescript
// app/lib/grpc.ts
import { createGrpcClient } from '@platform/connect-client';

export const grpcClient = createGrpcClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL,
  auth: {
    provider: 'clerk',
    getToken: () => auth().getToken(),
  },
});

// app/hooks/useADRs.ts
import { useGrpcQuery } from '@platform/react-hooks';

export function useADRs() {
  return useGrpcQuery(
    ['adrs'],
    () => grpcClient.adr.listADRs({}),
  );
}
```

### Related Docs
- Integration: [05-technology-integration.md](./05-technology-integration.md#frontend-tier)
- Reference: [10-reference-projects.md](./10-reference-projects.md#adr-platform-frontend)

---

## 5. Observability SDK

### Purpose
Consistent tracing, metrics, and logging across all services.

### Structure
```
shared/observability-sdk/
├── rust/
│   ├── src/
│   │   ├── tracing.rs          # OpenTelemetry setup
│   │   ├── metrics.rs          # Prometheus metrics
│   │   ├── logging.rs          # Structured logging
│   │   ├── middleware.rs       # gRPC/Axum middleware
│   │   └── lib.rs
│   └── Cargo.toml
│
├── python/
│   └── observability/
│       ├── tracing.py
│       ├── metrics.py
│       └── logging.py
│
├── typescript/
│   └── src/
│       ├── browser.ts          # Browser tracing
│       └── node.ts             # Node.js tracing
│
└── docs/
    ├── SETUP.md
    └── CONVENTIONS.md          # Naming conventions
```

### Why Foundational
- Distributed tracing requires consistency
- Metrics naming must align
- Logging patterns must be uniform
- High cost of inconsistency (can't trace across services)

### Standard Conventions
```rust
// Consistent span names
pub const SPAN_GRPC_HANDLER: &str = "grpc.handler";
pub const SPAN_DB_QUERY: &str = "db.query";
pub const SPAN_HTTP_REQUEST: &str = "http.request";

// Consistent metric names
pub const METRIC_REQUEST_DURATION: &str = "request_duration_seconds";
pub const METRIC_ERROR_COUNT: &str = "error_total";

// Pre-configured middleware
pub fn grpc_tracing_layer() -> TraceLayer { ... }
```

### Related Docs
- Architecture: [10-reference-projects.md](./10-reference-projects.md#observability)
- Patterns: [05-technology-integration.md](./05-technology-integration.md#observability)

---

## 6. CLI Framework

### Purpose
CLI tool patterns for consistent UX, testing, and documentation.

### Structure
```
shared/cli-framework/
├── src/
│   ├── command.rs              # CliTool trait
│   ├── output.rs               # Output formatting
│   ├── config.rs               # Config loading
│   ├── testing.rs              # Test utilities
│   ├── docs.rs                 # Doc generation
│   ├── examples.rs             # Example struct
│   └── lib.rs
│
├── templates/
│   └── tool-template/          # New tool template
│       ├── src/
│       │   ├── commands/
│       │   │   └── mod.rs
│       │   └── main.rs
│       └── Cargo.toml
│
└── docs/
    └── TOOL_GUIDE.md
```

### Why Foundational
- Build tools/CLI tools needed (stated)
- Consistent UX across all tools
- Testing/doc generation patterns reusable
- Command patterns proven in CLI Tools doc

### CliTool Trait
```rust
pub trait CliTool: Send + Sync {
    fn name(&self) -> &'static str;
    fn version(&self) -> &'static str;
    fn build_cli(&self) -> Command;
    fn examples(&self) -> Vec<Example>;
    
    async fn execute(&self, matches: &ArgMatches) -> Result<()>;
}

pub struct Example {
    pub name: &'static str,
    pub description: &'static str,
    pub command: &'static str,
    pub expected_output: Option<&'static str>,
    pub tags: &'static [&'static str],
}
```

### Related Docs
- Full spec: CLI Tools Architecture document (provided earlier)
- Patterns: [10-reference-projects.md](./10-reference-projects.md#cli-tools)

---

## 7. Storage Patterns

### Purpose
Database access patterns with RLS, connection pooling, and repository traits.

### Structure
```
shared/storage-patterns/
├── rust/
│   ├── src/
│   │   ├── pool.rs             # Connection pooling
│   │   ├── rls.rs              # RLS helpers
│   │   ├── migrations.rs       # Migration helpers
│   │   ├── repository.rs       # Repository trait pattern
│   │   └── lib.rs
│   └── Cargo.toml
│
├── migrations/
│   └── common/                 # Common migrations (users, orgs)
│       ├── 001_users.sql
│       └── 002_orgs.sql
│
└── docs/
    └── PATTERNS.md
```

### Why Foundational
- Every service needs database access
- RLS patterns critical for multi-tenancy
- Connection pooling must be correct
- Repository pattern enables testing

### RLS Pattern
```rust
pub struct TenantContext {
    pub tenant_id: Uuid,
    pub user_id: Uuid,
}

pub async fn set_rls_context(
    tx: &mut Transaction<'_, Postgres>,
    ctx: &TenantContext,
) -> Result<()> {
    sqlx::query("SET LOCAL app.tenant_id = $1")
        .bind(ctx.tenant_id)
        .execute(&mut **tx)
        .await?;
    Ok(())
}

// Repository trait
#[async_trait]
pub trait Repository<T>: Send + Sync {
    async fn create(&self, ctx: &TenantContext, entity: T) -> Result<T>;
    async fn get(&self, ctx: &TenantContext, id: Uuid) -> Result<Option<T>>;
    async fn list(&self, ctx: &TenantContext) -> Result<Vec<T>>;
    async fn update(&self, ctx: &TenantContext, entity: T) -> Result<T>;
    async fn delete(&self, ctx: &TenantContext, id: Uuid) -> Result<()>;
}
```

### Related Docs
- Architecture: [10-reference-projects.md](./10-reference-projects.md#hexagonal-architecture)
- Security: [10-reference-projects.md](./10-reference-projects.md#rls-patterns)

---

## Open Questions

### Infrastructure Choices

**API Gateway**:
- [ ] Envoy vs custom gateway?
- [ ] Managed Envoy (e.g., AWS App Mesh) vs self-hosted?
- [ ] gRPC-Web vs Connect protocol details?

**AI Gateway**:
- [ ] Which provider SDKs exactly? (rust crates)
- [ ] Local model inference support?
- [ ] Caching strategy (Redis vs in-memory)?

**Frontend**:
- [ ] Tailwind CSS vs other styling?
- [ ] Component library (shadcn/ui vs build from scratch)?
- [ ] State management details (Zustand patterns)?

**Observability**:
- [ ] OpenTelemetry collector setup?
- [ ] Jaeger vs Tempo vs commercial (Datadog)?
- [ ] Log aggregation (Loki vs CloudWatch)?

**Storage**:
- [ ] Postgres managed service (AWS RDS vs Azure vs other)?
- [ ] Connection pooler (PgBouncer vs pgpool)?
- [ ] Migration tool (sqlx vs diesel)?

### Design Decisions

**Contracts**:
- [ ] Protobuf package naming convention?
- [ ] How to version domains (v1 → v2)?
- [ ] Breaking change policy?

**Code Organization**:
- [ ] Directory naming conventions?
- [ ] Rust workspace structure?
- [ ] TypeScript monorepo tool (turborepo vs pnpm workspaces)?

**Testing**:
- [ ] Integration test patterns?
- [ ] Contract testing approach?
- [ ] E2E test infrastructure?

---

## Related Concepts

### Foundational vs Emergent

**This document**: What to build now (foundational)
**Related**: [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What to build later

**Key difference**:
- Foundational: Known infrastructure, high retrofit cost → Extract now
- Emergent: Domain capabilities, low retrofit cost → Extract at 3rd use

### Implementation Sequence

**Week 1-2**: Build all 7 foundational pieces
- See [07-implementation-roadmap.md](./07-implementation-roadmap.md) for detailed timeline
- Each piece gets basic implementation + docs + examples
- Projects can start using them immediately in Week 3

### Technology Integration

**How pieces work together**:
- See [05-technology-integration.md](./05-technology-integration.md)
- Contracts generate types for all pieces
- API Gateway routes to backend services
- Observability spans all layers
- Storage patterns used by domain logic

### Repository Organization

**Where these live**:
- All in `shared/` directory (not `capabilities/`)
- Versioned independently
- Projects depend on them
- See [04-repository-strategy.md](./04-repository-strategy.md)

---

## Next Steps

### For This Document

- [ ] Validate 7 pieces are comprehensive (nothing missing?)
- [ ] Detail out each piece (expand structures)
- [ ] Answer open questions (move to design docs)
- [ ] Create example code for each piece

### For Implementation

1. **Week 1**: Design each piece in detail
   - Create detailed structure for each
   - Define core interfaces/traits
   - Document usage patterns

2. **Week 2**: Implement basic version of each
   - Contracts with common types
   - Gateway with basic Envoy config
   - AI SDK with one provider
   - Frontend with Connect client
   - Observability with OpenTelemetry
   - CLI with CliTool trait
   - Storage with Repository trait

3. **Week 3**: Projects start using
   - Test in real project context
   - Refine based on usage
   - Document learnings

---

## Success Criteria

This foundation is successful when:

**Completeness**:
- ✅ All 7 pieces exist and have basic implementation
- ✅ Each piece has docs and examples
- ✅ Projects can use all 7 pieces

**Quality**:
- ✅ Contracts generate code for Rust, TS, Python
- ✅ Gateway patterns work with real services
- ✅ AI streaming works smoothly
- ✅ Frontend can call backend via Connect
- ✅ Traces flow across services
- ✅ CLI tools follow consistent patterns
- ✅ Repository pattern enables testing

**Usability**:
- ✅ New project can use foundation in < 2 days
- ✅ Foundation patterns are self-service (no platform team bottleneck)
- ✅ Examples demonstrate usage clearly
- ✅ Breaking changes are rare (< 2 per year)

**Evolution**:
- ✅ Can add new pieces if needed
- ✅ Can refine existing pieces based on usage
- ✅ Learnings feed back into foundation
- ✅ Foundation enables (not constrains) projects

---

**Status Notes**:
- **EXPLORING**: All 7 pieces identified, structures outlined
- **Next**: Detail each piece, answer open questions
- **After**: Implement in Week 1-2 of roadmap
