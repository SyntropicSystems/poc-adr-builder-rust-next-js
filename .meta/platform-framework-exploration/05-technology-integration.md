# Technology Integration: Rust, Python, TypeScript Together

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Two-language solution philosophy
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - Foundation that spans all languages
- → [04-repository-strategy.md](./04-repository-strategy.md) - How repos handle multiple languages
- → [06-extraction-rules.md](./06-extraction-rules.md) - Extraction rules apply across languages

---

## Context

### The Multi-Language Challenge

When building platforms, we face a choice:

**Single Language Approach**:
- ✅ Consistency and simplicity
- ✅ Shared patterns and tools
- ❌ Forces compromises (async in Rust is hard, ML in Rust is immature)
- ❌ Not using best tool for each job
- ❌ Limits what you can build effectively

**Multiple Languages Without Integration**:
- ✅ Use best tool for each domain
- ❌ Integration complexity
- ❌ Code duplication across languages
- ❌ No shared types or contracts
- ❌ Coordination nightmare

**What We Need**:
- Use each language where it excels
- Shared contracts and types across all languages
- Clean boundaries with clear communication patterns
- Type safety end-to-end (browser to backend to workers)
- Each tier can evolve independently

### Key Constraints

**Technology Stack** (stated explicitly):
- **Rust**: Synchronous tier, user-facing services
- **Python**: Asynchronous tier, ML workflows
- **TypeScript**: Frontend, browser, SSR

**Known Challenges**:
1. Async Rust is complex (tokio, async/await pain points)
2. Python is great for ML but not for real-time services
3. TypeScript is essential for browser but can't run on server efficiently
4. Need type safety across all three languages
5. Need clear boundaries to prevent coupling

**Unknown Factors**:
- Exact performance characteristics under load
- How much code will be in each language (ratio)
- Which AI provider SDK patterns will stabilize
- Whether gRPC-Web or Connect RPC is better for frontend

---

## Key Insights

### Insight 1: Not a Problem, but a Solution

**Mental Model Shift**:

Not: "We have a two-language problem" (need to rewrite Python in Rust)

But: **"We have a two-language solution"** (each language where it excels)

```
┌─────────────────────────────────────────────┐
│  SYNCHRONOUS TIER (Rust)                    │
│  - User-facing services                     │
│  - Real-time operations (<1 second)         │
│  - API Gateway                              │
│  - gRPC services                            │
│  - Database queries                         │
│  Why: Performance, memory safety, type safety
└──────────────┬──────────────────────────────┘
               │ Kafka Event Bus
               │ (clean boundary)
┌──────────────┴──────────────────────────────┐
│  ASYNCHRONOUS TIER (Python)                 │
│  - Background workflows (seconds-minutes)   │
│  - ML model inference                       │
│  - Complex orchestration                    │
│  - Document processing                      │
│  Why: Rich ML ecosystem, rapid development  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  FRONTEND TIER (TypeScript)                 │
│  - Browser execution                        │
│  - Next.js SSR                              │
│  - Type-safe UI components                  │
│  Why: Only option for browser, great DX     │
└─────────────────────────────────────────────┘
```

**Why This Works**:
- Rust doesn't need async complexity (synchronous services are simpler)
- Python doesn't need real-time performance (batch operations are fine)
- TypeScript stays in its domain (browser/SSR)
- Each language uses its strengths

### Insight 2: Protobuf as Universal Glue

**The Contract Foundation**:

```
┌─────────────────────────────────┐
│  PROTOBUF CONTRACTS (.proto)    │
│  - Single source of truth       │
│  - Language-agnostic            │
│  - Versioned schemas            │
└────────┬────────┬───────┬───────┘
         │        │       │
         ↓        ↓       ↓
      Rust      Python  TypeScript
    (prost)    (grpcio) (protobuf-ts)
```

**Generated Types**:
```proto
// shared/contracts/proto/adr/v1/adr.proto
message ADR {
  string id = 1;
  string title = 2;
  string context = 3;
  string decision = 4;
  ADRStatus status = 5;
}

enum ADRStatus {
  PROPOSED = 0;
  ACCEPTED = 1;
  DEPRECATED = 2;
}
```

**Rust**:
```rust
// Generated from .proto
use contracts::adr::v1::{Adr, AdrStatus};

fn create_adr() -> Adr {
    Adr {
        id: uuid::Uuid::new_v4().to_string(),
        title: "Use Protobuf".to_string(),
        status: AdrStatus::Proposed as i32,
        ..Default::default()
    }
}
```

**Python**:
```python
# Generated from .proto
from contracts.adr.v1 import adr_pb2

def create_adr() -> adr_pb2.ADR:
    return adr_pb2.ADR(
        id=str(uuid.uuid4()),
        title="Use Protobuf",
        status=adr_pb2.PROPOSED
    )
```

**TypeScript**:
```typescript
// Generated from .proto
import { ADR, ADRStatus } from '@contracts/adr/v1/adr';

function createADR(): ADR {
  return {
    id: crypto.randomUUID(),
    title: 'Use Protobuf',
    status: ADRStatus.PROPOSED,
    context: '',
    decision: '',
  };
}
```

**Benefits**:
- Same types in all languages (enforced by protobuf compiler)
- Change schema once, regenerate for all languages
- Type safety across service boundaries
- Clear versioning (v1, v2, etc.)
- No manual type synchronization

### Insight 3: Three Communication Patterns

```
┌──────────────────────────────────────┐
│  Pattern 1: Browser ↔ Rust           │
│  Protocol: gRPC-Web or Connect RPC   │
│  Use: User interactions, real-time   │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Pattern 2: Rust ↔ Python            │
│  Protocol: Kafka (event-driven)      │
│  Use: Background jobs, async work    │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Pattern 3: Service ↔ Service        │
│  Protocol: gRPC (native)             │
│  Use: Microservice communication     │
└──────────────────────────────────────┘
```

**Pattern 1: Browser ↔ Rust (gRPC-Web/Connect)**

```proto
// API definition
service ADRService {
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc CreateADR(CreateADRRequest) returns (CreateADRResponse);
}
```

**Rust Server (using tonic)**:
```rust
#[tonic::async_trait]
impl AdrService for AdrServiceImpl {
    async fn list_adrs(
        &self,
        request: Request<ListADRsRequest>,
    ) -> Result<Response<ListADRsResponse>, Status> {
        // ... implementation
    }
}
```

**TypeScript Client (using Connect)**:
```typescript
import { createPromiseClient } from '@connectrpc/connect';
import { ADRService } from '@contracts/adr/v1/adr_connect';

const client = createPromiseClient(ADRService, transport);
const response = await client.listADRs({});
```

**Why gRPC-Web or Connect**:
- gRPC-Web: Standard, wide support, HTTP/1.1 and HTTP/2
- Connect: Simpler, better browser support, JSON fallback
- Both: Type-safe, streaming support, request/response model

**Pattern 2: Rust → Python (Kafka)**

```rust
// Rust service publishes event
let event = AdrCreatedEvent {
    adr_id: adr.id.clone(),
    title: adr.title.clone(),
};

kafka_producer
    .send("adr.created", event)
    .await?;
```

```python
# Python worker consumes event
@kafka_consumer.subscribe("adr.created")
async def handle_adr_created(event: adr_pb2.ADRCreatedEvent):
    # Process asynchronously (e.g., generate embeddings)
    embeddings = await generate_embeddings(event.title)
    await store_embeddings(event.adr_id, embeddings)
```

**Why Kafka**:
- Decouples sync and async tiers
- Rust doesn't block waiting for Python
- Python can take seconds/minutes per event
- Easy to scale workers independently
- Built-in retry and dead letter queues

**Pattern 3: Service ↔ Service (gRPC native)**

```rust
// Rust service calls another Rust service
let mut client = UserServiceClient::connect("http://user-service:50051").await?;
let response = client.get_user(GetUserRequest {
    user_id: "123".to_string(),
}).await?;
```

**Why gRPC Native**:
- Lowest latency (binary protocol, HTTP/2)
- Service mesh ready (Envoy, Linkerd)
- Best for synchronous service-to-service calls
- Not accessible from browser (use gRPC-Web there)

### Insight 4: Language Usage Matrix

| Use Case | Language | Why | Alternative Considered |
|----------|----------|-----|------------------------|
| API Gateway | Rust | Performance, safety, simple sync | Go (less type safety) |
| User-facing API | Rust | <1s latency required | Node.js (worse performance) |
| Database queries | Rust | Connection pooling, transactions | Python (too slow) |
| CLI tools | Rust | Single binary, fast startup | Python (needs runtime) |
| ML inference | Python | Torch, transformers ecosystem | Rust (immature) |
| Document processing | Python | Libraries (PyPDF2, etc.) | Rust (wheel reinvention) |
| Workflow orchestration | Python | Temporal, Celery, asyncio | Rust (complex async) |
| Vector embeddings | Python | OpenAI SDK, sentence-transformers | Rust (no libraries) |
| Browser UI | TypeScript | Only option | JavaScript (less safe) |
| Next.js SSR | TypeScript | Best SSR framework | Remix (less mature) |
| Form validation | TypeScript | Shared with server via proto | Duplicate logic |

**Pattern Recognition**:

**Rust When**:
- User is waiting (real-time, <1 second)
- Performance critical
- Memory safety critical
- Want single binary deployment
- Synchronous operations are sufficient

**Python When**:
- User is NOT waiting (background, >1 second)
- ML/AI libraries needed
- Rich ecosystem for domain (docs, data processing)
- Rapid iteration on algorithms
- Async operations are complex

**TypeScript When**:
- Browser execution required
- Server-side rendering needed
- UI component logic
- Type safety in frontend

**Never Use**:
- Python for real-time user-facing APIs (too slow)
- Rust for ML inference (too immature)
- TypeScript for compute-intensive backend (not performant)

### Insight 5: Shared Code Patterns

**Can Share via Protobuf**:
- ✅ Request/response types
- ✅ Domain entities (ADR, User, etc.)
- ✅ Enums and status codes
- ✅ Error types

**Cannot Share** (language-specific):
- ❌ Business logic (implement per language)
- ❌ Framework code (Rust ≠ Python ≠ TypeScript)
- ❌ Infrastructure adapters (database, kafka)
- ❌ Testing utilities

**Example: Validation Logic**

**Don't**: Try to share business logic
```rust
// Can't share this with Python
pub fn validate_adr_title(title: &str) -> Result<(), ValidationError> {
    if title.len() > 200 {
        return Err(ValidationError::TitleTooLong);
    }
    Ok(())
}
```

**Do**: Share validation rules via proto annotations
```proto
message CreateADRRequest {
  // Use proto validation (works in all languages)
  string title = 1 [(buf.validate.field).string = {
    min_len: 1,
    max_len: 200,
  }];
}
```

**Or**: Accept duplication of business logic
```rust
// Rust implementation
fn validate_title(title: &str) -> Result<()> { ... }
```
```python
# Python implementation (duplicated, but that's OK)
def validate_title(title: str) -> None: ...
```

**Why Duplication is OK**:
- Business logic is rarely shared between sync/async tiers
- Each language can optimize for its patterns
- Reduces coupling between tiers
- Proto validation catches most cases

### Insight 6: Development Workflow

**Contracts-First Development**:

```
1. Define .proto schema
   ↓
2. Generate code for all languages
   ↓
3. Implement in each language
   ↓
4. Integration tests verify compatibility
```

**Example Workflow**:

```bash
# 1. Edit proto
vim shared/contracts/proto/adr/v1/adr.proto

# 2. Generate for all languages
buf generate

# Generated files:
# - rust: crates/contracts/src/adr/v1/adr.rs
# - python: py/contracts/adr/v1/adr_pb2.py
# - typescript: packages/contracts/src/adr/v1/adr_pb.ts

# 3. Implement Rust service
cd crates/api-service
cargo build

# 4. Implement Python worker
cd workers/adr-embeddings
poetry install

# 5. Implement TypeScript frontend
cd frontend
npm install

# 6. Run integration tests
cargo test --workspace
pytest
npm test
```

**Type Safety Chain**:
```
.proto file (source of truth)
    ↓
Rust types (compile-time checked)
    ↓
gRPC-Web (serialized protobuf)
    ↓
TypeScript types (compile-time checked)
    ↓
Kafka (serialized protobuf)
    ↓
Python types (runtime checked via protobuf)
```

---

## Open Questions

### Questions for Next Stage

**Protocol Choices**:
- [ ] gRPC-Web vs Connect RPC for browser? (both valid)
- [ ] Kafka vs NATS JetStream vs Redpanda? (event bus)
- [ ] HTTP/2 vs HTTP/3 for gRPC? (performance)
- [ ] JSON encoding option for debugging? (Connect supports this)

**AI Integration**:
- [ ] Which Python AI SDK? (Anthropic SDK, OpenAI SDK, LangChain)
- [ ] Streaming responses from Python to Rust? (need bidirectional channel)
- [ ] How to handle long-running AI generation? (>30 seconds)
- [ ] Caching strategy for embeddings? (Redis, Postgres, Vector DB)

**Code Generation**:
- [ ] Buf vs protoc for code generation?
- [ ] Where to store generated code? (commit vs generate on build)
- [ ] How to handle breaking changes in proto?
- [ ] Version compatibility testing?

**Performance**:
- [ ] Protobuf serialization overhead acceptable?
- [ ] Kafka latency acceptable for async tier?
- [ ] gRPC-Web overhead vs native gRPC?
- [ ] Should we measure before committing?

### Deferred Questions (Not Now)

- gRPC streaming for real-time updates (future enhancement)
- Multi-region Kafka setup (premature)
- Load balancing and service mesh (infrastructure concern)
- Observability across languages (use OpenTelemetry later)

---

## Related Concepts

### Connection to Other Documents

**Foundational Infrastructure** ([02-foundational-infrastructure.md](./02-foundational-infrastructure.md)):
- Contracts (Proto Schemas) - Foundation for all language integration
- AI Gateway SDK - Abstracts Python AI provider details from Rust
- API Gateway Core - Handles gRPC-Web/Connect for browser
- Observability SDK - Spans all languages with OpenTelemetry

**Repository Strategy** ([04-repository-strategy.md](./04-repository-strategy.md)):
- Shared repos can contain multiple languages
- Example: `shared/contracts` has proto (generates all languages)
- Projects can mix languages (Rust services + Python workers + TS frontend)
- Each language follows its own package manager in its directory

**Extraction Rules** ([06-extraction-rules.md](./06-extraction-rules.md)):
- Extract contracts immediately (foundational)
- Language-specific helpers follow rule of two/three
- Don't extract language bridges (too project-specific)

### Technology-Specific Patterns

**Rust Patterns**:
- Use `tonic` for gRPC server
- Use `prost` for protobuf
- Use `tokio` for async (only in API layer, not business logic)
- Use `rdkafka` for Kafka producer

**Python Patterns**:
- Use `grpcio` for protobuf
- Use `aiokafka` for Kafka consumer
- Use `asyncio` for concurrency
- Use provider SDKs directly (anthropic, openai)

**TypeScript Patterns**:
- Use `@connectrpc/connect` for API calls
- Use `protobuf-ts` or `@bufbuild/protobuf` for types
- Use React Query for data fetching
- Use Next.js App Router for SSR

### Integration Boundaries

```
┌─────────────────────────────────────────────┐
│  BOUNDARY 1: Browser ↔ API Gateway          │
│  Protocol: gRPC-Web or Connect (HTTPS)      │
│  Auth: Session cookie or JWT                │
│  Encoding: Protobuf binary or JSON          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  BOUNDARY 2: API Gateway ↔ Services         │
│  Protocol: gRPC native                      │
│  Auth: Service mesh mTLS (future)           │
│  Encoding: Protobuf binary                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  BOUNDARY 3: Services ↔ Kafka ↔ Workers     │
│  Protocol: Kafka                            │
│  Auth: Kafka SASL (production)              │
│  Encoding: Protobuf binary                  │
└─────────────────────────────────────────────┘
```

---

## Next Steps

### For This Document

- [ ] Validate language choices with team
- [ ] Answer protocol choice questions (gRPC-Web vs Connect)
- [ ] Decide on AI SDK strategy
- [ ] Document code generation approach (buf vs protoc)
- [ ] Mark as STABLE when patterns are validated

### For Implementation

**Week 1** (Protobuf Setup):
1. Set up `shared/contracts` repo
2. Create initial proto schemas
3. Configure buf or protoc
4. Generate code for all three languages
5. Validate generated types compile

**Week 2** (Communication Patterns):
1. Set up Rust gRPC server (tonic)
2. Set up TypeScript client (Connect)
3. Set up Kafka producer (Rust)
4. Set up Kafka consumer (Python)
5. End-to-end integration test

**Week 3-4** (First Feature):
1. Implement ADR list in Rust
2. Call from TypeScript frontend
3. Publish event to Kafka
4. Consume in Python worker
5. Verify full flow works

---

## Success Criteria

This technology integration is successful when:

**Type Safety**:
- ✅ Same types in Rust, Python, TypeScript
- ✅ Compiler catches type mismatches
- ✅ Proto changes automatically propagate
- ✅ No manual type synchronization needed

**Communication**:
- ✅ Browser can call Rust services
- ✅ Rust can publish to Kafka
- ✅ Python can consume from Kafka
- ✅ Services can call each other

**Developer Experience**:
- ✅ Edit proto, regenerate code, get updated types
- ✅ Each language feels natural (not fighting the integration)
- ✅ Can develop in each language independently
- ✅ Integration tests catch incompatibilities

**Performance**:
- ✅ Rust services respond <100ms (p95)
- ✅ Python workers process events (no time limit)
- ✅ Frontend loads fast (<2s to interactive)
- ✅ No bottlenecks from language boundaries

**Maintainability**:
- ✅ Can evolve each language independently
- ✅ Can add new languages if needed (Go, Java, etc.)
- ✅ Proto versioning handles breaking changes
- ✅ Clear where code lives (Rust vs Python vs TypeScript)

---

## References

**Internal**:
- ADR PoC: [../../README.md](../../README.md) - Current Rust implementation
- Platform Architecture Doc: Reference architecture with full stack

**Protobuf/gRPC**:
- Protocol Buffers: https://protobuf.dev/
- gRPC: https://grpc.io/
- Connect RPC: https://connectrpc.com/
- Buf: https://buf.build/

**Rust**:
- Tonic (gRPC): https://github.com/hyperium/tonic
- Prost (Protobuf): https://github.com/tokio-rs/prost
- rdkafka: https://github.com/fede1024/rust-rdkafka

**Python**:
- grpcio: https://grpc.io/docs/languages/python/
- aiokafka: https://aiokafka.readthedocs.io/

**TypeScript**:
- Connect Web: https://connectrpc.com/docs/web/getting-started
- protobuf-ts: https://github.com/timostamm/protobuf-ts
- Next.js: https://nextjs.org/

**Philosophy**:
- Use the right tool for the job
- Embrace multiple languages, don't fight them
- Contracts-first development
- Type safety across boundaries

---

**Status Notes**:
- **EXPLORING**: Patterns documented, need validation with real implementation
- **Next**: Implement first end-to-end feature to validate patterns
- **After**: Document learnings, adjust patterns if needed
