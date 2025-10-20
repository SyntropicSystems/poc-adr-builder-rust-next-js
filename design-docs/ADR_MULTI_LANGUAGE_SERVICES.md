# Multi-Language Integration - Architecture Decisions

## Document Structure
Following the same format as our core architecture decisions document. Each problem includes: problem statement, problem stack, why this is a problem, options with research and trade-offs, decision, success criteria, metrics, evidence-based triggers to revisit, risks, and migration costs.

---

## Problem Stack Overview

```
P.ML.1. Multi-Language System Integration (STRATEGIC)
    ├── P.ML.1.1. Client Integration Pattern
    ├── P.ML.1.2. Service Federation Model
    └── P.ML.1.3. Cross-Language Type Safety

P.ML.2. Polyglot Adapter Implementation (ARCHITECTURAL)
    ├── P.ML.2.1. Adapter Bridge vs Native
    ├── P.ML.2.2. Adapter Service Communication
    └── P.ML.2.3. Adapter Lifecycle Management

P.ML.3. SDK Distribution Strategy (TACTICAL)
    ├── P.ML.3.1. SDK Tier Selection
    ├── P.ML.3.2. Logic Duplication Prevention
    └── P.ML.3.3. Offline Capability Requirements

P.ML.4. Operational Complexity (OPERATIONAL)
    ├── P.ML.4.1. Service Deployment Model
    ├── P.ML.4.2. Inter-Service Monitoring
    └── P.ML.4.3. Polyglot Debugging Strategy
```

---

# P.ML.1. Multi-Language System Integration

## P.ML.1.1. Client Integration Pattern

### Problem Statement
How do we enable Python, Go, and Node.js applications to consume the ADR service while maintaining type safety, minimizing complexity, and avoiding architectural changes to our core Rust service?

### Problem Stack
- **Parent**: P.ML.1 (Multi-Language System Integration)
- **Siblings**: P.ML.1.2 (Service Federation), P.ML.1.3 (Type Safety)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Determines ease of integration for external applications
- Affects type safety across language boundaries
- Influences maintenance burden for multi-language support
- Impacts developer experience in different languages
- Determines client library distribution strategy

**Risks of Not Solving:**
- Applications build custom, inconsistent clients
- Type mismatches between languages cause runtime errors
- Maintenance burden multiplies with each language
- No single source of truth for API contracts
- Breaking changes propagate poorly to clients
- Duplication of API client logic across languages

### Options

#### Option A: Language-Specific REST Clients
**Description**: Provide hand-written REST client libraries for each language.

**Pros**:
- Idiomatic to each language
- Can optimize for language-specific patterns
- Full control over client API surface
- Works with existing REST infrastructure

**Cons**:
- Must maintain separate clients for Python, Go, Node
- Manual synchronization with API changes
- Type safety only as good as manual definitions
- High maintenance burden (3+ codebases)
- Breaking changes require updating all clients
- Easy for implementations to drift
- Need to version and distribute separately

**Trade-offs**: Language idioms vs maintenance burden

#### Option B: Auto-Generated REST Clients (OpenAPI)
**Description**: Generate clients from OpenAPI specification for each language.

**Pros**:
- Single source of truth (OpenAPI spec)
- Generated clients for all languages
- Reduces manual maintenance
- Tooling widely available

**Cons**:
- OpenAPI generation quality varies by language
- Generated code often not idiomatic
- REST still has over-fetching/under-fetching issues
- Need to maintain OpenAPI spec separately
- Breaking changes still require client regeneration
- No compile-time safety across boundaries

**Trade-offs**: Automation vs code quality

#### Option C: Direct gRPC Clients from Protobuf ⭐ CHOSEN
**Description**: Clients use protobuf-generated gRPC clients directly.

```python
# Python client
from adr_pb2_grpc import ADRServiceStub
from adr_pb2 import GetADRRequest

channel = grpc.insecure_channel('localhost:50051')
client = ADRServiceStub(channel)
adr = client.GetADR(GetADRRequest(id='P1.1'))
```

**Pros**:
- Zero additional architecture work (we already use gRPC)
- Type-safe clients in all languages (protobuf codegen)
- Single source of truth (existing .proto files)
- Automatic synchronization (regenerate from proto)
- Breaking changes caught at compile time
- Efficient binary protocol
- Clients are thin wrappers (minimal code)
- Supports streaming if needed later

**Cons**:
- Requires protobuf toolchain per language
- Generated code may not be perfectly idiomatic
- Developers need basic gRPC knowledge

**Trade-offs**: Slight tooling complexity for guaranteed type safety

**Research References**:
- gRPC supports Python, Go, Node.js officially
- protoc can generate for 10+ languages
- Companies like Google, Netflix use this pattern

### Decision
**Chosen**: Option C - Direct gRPC Clients from Protobuf

**Rationale**:
- Leverages our existing gRPC/protobuf architecture (P3.1.1 decision)
- No additional infrastructure needed
- Type safety is guaranteed by protobuf compiler
- Breaking changes detected automatically
- Minimal maintenance burden (just regenerate)
- Industry-proven pattern
- Scales to any language with gRPC support

**Implementation Strategy**:
1. Provide protobuf files in repository or package
2. Document code generation process per language
3. Optionally provide pre-generated clients as packages
4. Clients handle only connection/configuration

### Success Criteria
1. ✅ Can generate type-safe client for Python, Go, Node from .proto files
2. ✅ No manual client code required (100% generated)
3. ✅ Breaking API changes cause compile errors in client languages
4. ✅ Client generation documented and reproducible
5. ✅ Clients work against live Rust service
6. ✅ Time to add new language client < 1 hour

### Metrics
**Quantitative**:
- Client generation time: < 5 minutes per language
- Lines of hand-written client code: 0 (all generated)
- Type safety coverage: 100% (compile-time checked)
- Time to add new language: < 1 hour (setup toolchain)

**Qualitative**:
- "Adding new language is just running protoc"
- "Never worry about API drift between languages"
- "Breaking changes caught before runtime"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Code Generation Failure Indicator**
   - Protobuf generation fails for target languages
   - Generated code doesn't compile
   - Breaking changes in protoc affect clients
   - More than 20% of generation attempts fail

2. **Usability Indicator**
   - Developers consistently complain about generated code quality
   - Need significant wrapper code around generated clients
   - Generated clients missing critical features
   - Multiple requests to hand-write clients instead

3. **Ecosystem Gap Indicator**
   - Target language lacks protobuf/gRPC support
   - Toolchain too complex for developers
   - Generated code incompatible with language idioms
   - Need to support languages without gRPC

4. **Performance Indicator**
   - gRPC overhead unacceptable for clients
   - Binary protocol causing issues
   - REST would be significantly faster
   - Network constraints make gRPC impractical

5. **Type Safety Limitation**
   - Protobuf can't express necessary type constraints
   - Need richer type systems than protobuf supports
   - Runtime validation still needed despite types
   - False sense of security from generated types

### Risks of Decision

1. **Toolchain Complexity**
   - Risk: Each language needs protoc + plugins setup
   - Mitigation: Provide setup scripts, Docker images, documentation
   - Severity: Low (one-time setup per developer)

2. **Generated Code Quality**
   - Risk: Generated code not idiomatic to language
   - Mitigation: Can wrap generated clients with idiomatic APIs
   - Severity: Low (generated code is functional)

3. **Breaking Changes**
   - Risk: Protobuf changes break all clients
   - Mitigation: Semantic versioning, deprecation warnings
   - Severity: Medium (expected for breaking changes)

4. **gRPC Learning Curve**
   - Risk: Developers unfamiliar with gRPC
   - Mitigation: Documentation, examples, common pattern
   - Severity: Low (gRPC widely adopted)

### Migration Cost

**To REST Clients (Option A/B)**:
- Cost: 5-8 EU per language (write clients, maintain)
- Steps: Build OpenAPI spec, generate or write clients
- Time: Ongoing maintenance overhead
- Risk: Lose type safety, increase maintenance

**Rollback Cost**: Low (just use REST API that service already exposes)

---

## P.ML.1.2. Service Federation Model

### Problem Statement
How do we integrate specialized services in Python (ML/analytics), Go (high-performance), or Node.js (integrations) that extend ADR functionality without compromising our Rust core's role as source of truth?

### Problem Stack
- **Parent**: P.ML.1 (Multi-Language System Integration)
- **Siblings**: P.ML.1.1 (Client Integration), P.ML.1.3 (Type Safety)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Determines how we leverage language-specific strengths (Python for ML, Go for performance)
- Affects system complexity and operational burden
- Influences service boundaries and responsibilities
- Impacts data consistency and source of truth
- Determines inter-service communication patterns

**Risks of Not Solving:**
- Rust service forced to do everything (wrong tool for some jobs)
- Can't leverage Python ML ecosystem or Go performance
- Team expertise in other languages wasted
- Monolithic service grows too complex
- Hard to scale specialized workloads independently

### Options

#### Option A: Monolithic Rust Service (No Federation)
**Description**: Implement all functionality in Rust, including ML, analytics, etc.

**Pros**:
- Single service to deploy and maintain
- No inter-service complexity
- Consistent language and patterns
- Simple operational model
- No network hops between components

**Cons**:
- Rust not optimal for ML/analytics (Python ecosystem better)
- Can't leverage specialized libraries (e.g., scikit-learn, TensorFlow)
- Team expertise in other languages unused
- Service becomes bloated with diverse responsibilities
- Hard to scale different workloads independently
- Slower development for non-core features

**Trade-offs**: Simplicity vs language-appropriate tools

#### Option B: Fully Distributed Microservices
**Description**: Many small services in different languages, all equal peers.

**Pros**:
- Maximum language flexibility
- Fine-grained scaling
- Team autonomy per service
- Language-optimal implementations

**Cons**:
- High operational complexity
- No clear source of truth
- Distributed data consistency problems
- Network latency between all services
- Hard to reason about system behavior
- Overkill for current scale

**Trade-offs**: Flexibility vs operational burden

#### Option C: Federated Services with Rust Core ⭐ CHOSEN
**Description**: Rust ADR service as core/source of truth, auxiliary services in appropriate languages extend functionality.

```
                    gRPC Service Mesh
                            │
        ┌──────────────┬────┴────┬──────────────┐
        │              │         │              │
   Rust ADR       Python ML   Go          Node Notify
   Service        Service   Compliance    Service
   (CORE)         (extend)  (extend)      (extend)
   - CRUD         - Analyze - Validate    - Alerts
   - Storage      - Suggest - Policy      - Webhooks
   - Truth        - Report  - Audit       - Integration
```

**Pros**:
- Clear separation: Rust = source of truth, others = extensions
- Language-appropriate implementations (Python for ML, etc.)
- Can add/remove auxiliary services without touching core
- Independent scaling of specialized workloads
- Team can use best language for each problem
- Failure isolation (ML service crash doesn't affect core)
- Gradual adoption (start with Rust only, add services as needed)

**Cons**:
- More services to deploy (2-5 services vs 1)
- Inter-service communication overhead
- Need service discovery/coordination
- More complex monitoring
- Distributed tracing needed

**Trade-offs**: Some operational complexity for language flexibility

**Research References**:
- Microservices pattern: Martin Fowler
- Service mesh: Istio, Linkerd patterns
- gRPC federation: Google's internal patterns

### Decision
**Chosen**: Option C - Federated Services with Rust Core

**Rationale**:
- Rust service already designed as core (hexagonal architecture)
- Enables leveraging Python ML ecosystem without Rust ML struggle
- Go for high-performance auxiliary tasks (e.g., compliance checks)
- Node.js for webhook integrations (huge npm ecosystem)
- Operational complexity manageable at 2-5 services
- Can start with just Rust, add services only when needed (YAGNI)
- gRPC already chosen, perfect for service federation

**Architectural Principles**:
1. **Rust ADR Service is the single source of truth** for ADR data
2. **Auxiliary services extend, never replace** core functionality
3. **All inter-service communication via gRPC** (type-safe)
4. **Services are independent** (can deploy, scale, fail separately)
5. **Shared protobuf schemas** enforce contracts

**Service Types**:

**Core Service (Rust)**:
- ADR CRUD operations
- Storage management
- Business rules
- API gateway for clients

**Extension Services (Any Language)**:
- Python ML: similarity analysis, decision prediction, analytics
- Go Compliance: policy validation, audit logs, performance-critical checks
- Node.js Notify: webhooks, Slack/email alerts, external integrations

### Success Criteria
1. ✅ Rust service operates independently without auxiliary services
2. ✅ Auxiliary services can be added without modifying Rust core
3. ✅ Auxiliary services can fail without affecting core CRUD operations
4. ✅ All inter-service communication type-safe via protobuf
5. ✅ Clear documentation of which service owns what functionality
6. ✅ Can deploy services independently

### Metrics
**Quantitative**:
- Core service uptime: > 99.9% (independent of auxiliary services)
- Time to add new auxiliary service: < 4 EU
- Inter-service latency: < 50ms (p95)
- Service count: < 10 total (avoid microservice explosion)

**Qualitative**:
- "Easy to add specialized services in appropriate languages"
- "Core service never affected by auxiliary service issues"
- "Clear service boundaries and responsibilities"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Operational Complexity Indicator**
   - More than 10 services deployed
   - Significant time spent on service coordination
   - Deployments frequently break due to service dependencies
   - On-call burden too high from managing multiple services

2. **Performance Indicator**
   - Inter-service latency exceeds 100ms (p95)
   - Network hops causing user-visible delays
   - More than 20% overhead from service federation
   - Monolithic service would be faster

3. **Coupling Indicator**
   - Auxiliary services frequently need Rust core changes
   - Changes require coordinated deploys across services
   - Service boundaries unclear or frequently violated
   - Distributed transactions becoming common

4. **Scale Mismatch**
   - Services too small (overheads outweigh benefits)
   - Or services too large (should be split)
   - Can't scale services independently despite design
   - All services need to scale together anyway

5. **Team Friction**
   - Multiple services causing communication overhead
   - Unclear ownership of functionality
   - Difficult to onboard new developers (too many services)
   - Debugging across services too complex

### Risks of Decision

1. **Operational Complexity**
   - Risk: Managing 3-5 services harder than 1
   - Mitigation: Start with Rust only, add services incrementally
   - Severity: Medium

2. **Network Latency**
   - Risk: gRPC calls between services add latency
   - Mitigation: Monitor latency, async where possible, caching
   - Severity: Low-Medium

3. **Distributed Debugging**
   - Risk: Issues spanning multiple services hard to debug
   - Mitigation: Distributed tracing (OpenTelemetry), correlation IDs
   - Severity: Medium

4. **Deployment Coordination**
   - Risk: Breaking changes require coordinated deploys
   - Mitigation: API versioning, backward compatibility
   - Severity: Medium

### Migration Cost

**To Monolithic (Option A)**:
- Cost: 10-15 EU (merge services, lose language flexibility)
- Steps: Port auxiliary logic to Rust, consolidate
- Risk: Lose language-appropriate implementations

**To Full Microservices (Option B)**:
- Cost: 15-20 EU (split core, add coordination)
- Steps: Extract services from core, add orchestration
- Risk: Over-engineering, high operational burden

**Rollback Cost**: Low-Medium (can always merge services back to Rust)

---

## P.ML.2. Polyglot Adapter Implementation

## P.ML.2.1. Adapter Bridge vs Native Implementation

### Problem Statement
When we need to implement a storage adapter, should we write it natively in Rust or allow implementation in Python/Go/Node via a bridge pattern?

### Problem Stack
- **Parent**: P.ML.2 (Polyglot Adapter Implementation)
- **Siblings**: P.ML.2.2 (Adapter Communication), P.ML.2.3 (Lifecycle)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Determines which storage backends we can easily support
- Affects performance (in-process vs network call)
- Influences operational complexity
- Impacts language-specific SDK utilization
- Determines adapter development velocity

**Risks of Not Solving:**
- Force all adapters in Rust (miss language-optimal SDKs)
- Or allow any language (lose performance, increase complexity)
- Can't leverage existing libraries in other languages
- Slower development for complex storage systems

### Options

#### Option A: Rust-Only Adapters
**Description**: All storage adapters must be implemented in Rust.

**Pros**:
- No network overhead (in-process)
- Consistent language and patterns
- Simple deployment (single binary)
- No inter-service complexity
- Easy to debug (one language)

**Cons**:
- Rust libraries may not exist for some storage systems
- Can't leverage mature Python/Go/Node storage clients
- Slower development (if SDK only exists in other language)
- May require writing Rust bindings to C libraries
- Team expertise in other languages unused for adapters

**Trade-offs**: Performance vs language flexibility

#### Option B: Foreign Function Interface (FFI)
**Description**: Rust calls Python/Go/Node code via FFI boundaries.

```rust
// Rust adapter calls Python via PyO3
pub struct PythonAdapter {
    py_module: PyObject,
}

impl ADRRepository for PythonAdapter {
    fn save(&self, adr: &ADR) -> Result<()> {
        Python::with_gil(|py| {
            self.py_module.call_method1(py, "save", (adr,))
        })
    }
}
```

**Pros**:
- In-process (no network calls)
- Can use any language's libraries
- Single binary deployment

**Cons**:
- Complex FFI boundaries (unsafe, error-prone)
- Memory management across boundaries
- Limited to languages with good Rust FFI (Python, C)
- Debugging is painful (crossing language boundaries)
- Deployment complexity (bundle interpreters/runtimes)
- Version conflicts (Rust + Python in same process)
- Crash in foreign code crashes entire service

**Trade-offs**: In-process vs safety/complexity

**Research**: PyO3 (Rust-Python), cgo (Go-C), napi-rs (Rust-Node)

#### Option C: Adapter Bridge Pattern ⭐ CHOSEN
**Description**: Rust implements bridge adapter that delegates to external gRPC service.

```
Rust Service
    ↓
SDK (Rust)
    ↓
PostgresAdapter (Rust) ← native
MongoAdapter (Bridge) ← gRPC → Node.js MongoDB Service
ArangoAdapter (Bridge) ← gRPC → Go ArangoDB Service
```

```protobuf
// storage_adapter.proto
service StorageAdapter {
  rpc Save(ADR) returns (Empty);
  rpc FindById(FindByIdRequest) returns (ADR);
  rpc FindByStatus(FindByStatusRequest) returns (stream ADR);
}
```

```rust
// Rust bridge adapter (thin gRPC client)
pub struct GrpcAdapterBridge {
    client: StorageAdapterClient,
}

#[async_trait]
impl ADRRepository for GrpcAdapterBridge {
    async fn save(&self, adr: &ADR) -> Result<()> {
        self.client.save(adr).await?;
        Ok(())
    }
}
```

**Pros**:
- Rust service stays pure (no FFI complexity)
- Adapter in optimal language (Python for Elasticsearch, Go for Arango)
- Fault isolation (adapter crash doesn't kill core service)
- Can use language-native storage clients
- Type-safe via protobuf
- Easy to test (mock gRPC service)
- Can deploy adapter separately (scaling, upgrades)

**Cons**:
- Network hop overhead (latency)
- More services to deploy (operational burden)
- Not suitable for hot path (performance-critical)

**Trade-offs**: Network overhead vs safety and language flexibility

### Decision
**Chosen**: Option C - Adapter Bridge Pattern (with Option A as default)

**Rationale**:
- **Default to Rust adapters** for performance and simplicity
- **Use bridge only when compelling reason**:
  - Storage system has much better SDK in another language
  - Complex storage logic easier in higher-level language
  - Want fault isolation for experimental storage
  - Team expertise concentrated in other language
- Maintains clean hexagonal architecture
- Type-safe via protobuf (same as service federation)
- Already using gRPC, no new patterns

**Decision Tree**:
```
Need new storage adapter?
    ↓
Does good Rust library exist?
    ├─ Yes → Rust adapter (Option A)
    └─ No → 
        ↓
        Is storage in hot path?
        ├─ Yes → Write Rust bindings or native Rust
        └─ No → Bridge adapter (Option C)
```

**Implemented Adapters**:
- Filesystem: Rust (simple, no dependencies)
- PostgreSQL: Rust (sqlx is excellent)
- DynamoDB: Rust (aws-sdk-rust is good)
- MongoDB: Bridge to Node.js (if needed, better Node driver)
- ArangoDB: Bridge to Go (if needed, better Go driver)

### Success Criteria
1. ✅ Can implement adapter in Rust (default path)
2. ✅ Can implement adapter in Python/Go/Node via bridge (escape hatch)
3. ✅ Bridge adapters implement same ADRRepository trait
4. ✅ No FFI complexity in Rust core
5. ✅ Type safety maintained via protobuf
6. ✅ Bridge adapters isolated (failures don't affect core)

### Metrics
**Quantitative**:
- Rust adapters: > 80% (default path)
- Bridge adapters: < 20% (only when needed)
- Network overhead for bridge: < 5ms (p95)
- Time to implement native Rust adapter: 3-5 EU
- Time to implement bridge adapter: 4-6 EU (includes service)

**Qualitative**:
- "Most adapters are Rust, some use bridge when it makes sense"
- "Bridge pattern simple to understand and implement"
- "No FFI complexity or crashes"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Performance Indicator**
   - Bridge adapter latency exceeds 10ms (p95)
   - Network overhead causing user-visible delays
   - More than 20% of requests hit bridge adapters
   - Storage operations too slow via bridge

2. **Complexity Indicator**
   - More than 50% of adapters are bridges (should be exception)
   - Bridge adapter services hard to maintain
   - Deployment complexity too high
   - Debugging across bridge frequently needed

3. **Rust Library Maturity**
   - Rust libraries now available for all storage systems
   - Bridge adapters no longer needed
   - Or: Rust libraries still lacking, FFI becoming necessary

4. **Operational Burden**
   - Too many adapter services to manage
   - Bridge adapters failing frequently
   - Coordination overhead too high
   - Want in-process adapters only

### Risks of Decision

1. **Network Latency**
   - Risk: Bridge adds 1-10ms per storage operation
   - Mitigation: Use for cold path only, monitor latency
   - Severity: Low-Medium

2. **Operational Complexity**
   - Risk: More services to deploy and monitor
   - Mitigation: Only use bridge when compelling, document why
   - Severity: Medium

3. **Debugging Difficulty**
   - Risk: Issues spanning Rust + adapter service
   - Mitigation: Distributed tracing, correlation IDs
   - Severity: Low-Medium

4. **Over-Use of Bridges**
   - Risk: Team defaults to bridge instead of Rust
   - Mitigation: Strong preference for Rust, require justification
   - Severity: Medium

### Migration Cost

**To Rust-Only (Option A)**:
- Cost: 3-5 EU per bridge adapter (rewrite in Rust)
- Steps: Implement Rust adapter, remove bridge service
- Risk: Lose language-optimal implementation

**To FFI (Option B)**:
- Cost: 10-15 EU per adapter (complex FFI)
- Steps: Implement FFI bindings, handle memory safety
- Risk: High complexity, safety issues

**Rollback Cost**: Medium (need to rewrite adapters)

---

## P.ML.3. SDK Distribution Strategy

## P.ML.3.1. SDK Tier Selection

### Problem Statement
When Python/Go/Node applications need to work with ADR data structures and logic, what level of SDK should we provide: just data types, remote wrappers, or full local logic?

### Problem Stack
- **Parent**: P.ML.3 (SDK Distribution Strategy)
- **Siblings**: P.ML.3.2 (Logic Duplication), P.ML.3.3 (Offline Capability)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Determines maintenance burden across languages
- Affects logic duplication and consistency
- Influences offline capability for CLIs
- Impacts API surface area to maintain
- Determines single source of truth

**Risks of Not Solving:**
- Duplicate business logic in each language (maintenance nightmare)
- Logic drift between languages (inconsistency)
- Or: no SDK at all (every app implements from scratch)
- Breaking changes hard to coordinate
- No clear pattern for new languages

### Options

#### Option A: No SDK (Clients Do Everything)
**Description**: Only provide protobuf files, clients implement everything.

**Pros**:
- Zero maintenance burden
- Complete flexibility for clients
- No version coordination needed

**Cons**:
- Every client reimplements logic (duplication)
- Inconsistency across clients
- Errors repeated in each implementation
- No guidance for new users
- Poor developer experience

**Trade-offs**: Zero maintenance vs terrible DX

#### Option B: Full-Featured SDKs with Local Logic
**Description**: Rich SDKs in each language with all validation, business rules, etc.

```python
# Python SDK with full local logic
from adr_sdk import ADRManager, ValidationError

manager = ADRManager(remote_url='localhost:50051')

# Local validation before network call
adr = manager.create_adr(
    title='My ADR',
    problem='Problem statement...'
)  # validates locally, then saves remotely
```

**Pros**:
- Rich developer experience
- Offline validation possible
- Fewer network calls
- Can work partially offline

**Cons**:
- MUST duplicate business logic in each language
- Logic will drift over time (guaranteed)
- High maintenance: change in Rust requires 3+ language updates
- Testing multiplies (test each language SDK)
- Breaking changes require coordinated updates
- Single source of truth violated

**Trade-offs**: Rich DX vs unsustainable maintenance

#### Option C: Tiered SDK Strategy ⭐ CHOSEN
**Description**: Provide multiple tiers, choose based on needs.

**Tier 1: Data Structures Only** (Default)
```python
# Just protobuf-generated types
from adr_pb2 import ADR, ProblemStatement, Decision

adr = ADR(
    id='P1.1',
    title='...',
    problem=ProblemStatement(statement='...')
)
```
- Effort: 0.5 EU (just protoc codegen)
- Use when: Just need to work with ADR data

**Tier 2: Remote SDK Wrapper** (When Needed)
```python
# Convenient wrapper around gRPC
from adr_sdk import ADRClient

client = ADRClient('localhost:50051')
adr = client.create_adr(title='...', problem='...')
adrs = client.list_adrs(status='ACTIVE')
```
- Effort: 2-3 EU per language
- Use when: Want idiomatic API, OK with network calls

**Tier 3: Hybrid with Local Validation** (Rarely)
```python
# Local validation + remote persistence
from adr_sdk import ADRManager

manager = ADRManager(remote_url='localhost:50051')
adr = manager.create_adr(...)  # validates locally, saves remotely
```
- Effort: 8-12 EU per language (duplicate validation)
- Use when: Offline operation critical, willing to maintain

**Pros**:
- Start simple (Tier 1), upgrade only when needed
- Most apps use Tier 1 or 2 (low maintenance)
- Tier 3 exists but discouraged (high cost visible)
- Can choose appropriate tier per use case
- Clear escalation path

**Cons**:
- Need to document tier selection
- Tier 3 still has duplication problems (but explicit)

**Trade-offs**: Flexibility vs need for clear guidance

### Decision
**Chosen**: Option C - Tiered SDK Strategy

**Rationale**:
- Start simple (Tier 1), meet most needs
- Tier 2 for better DX without duplication
- Tier 3 exists but requires justification (offline CLI, etc.)
- Can make different choices per language (Python Tier 2, Go Tier 1)
- Maintenance burden grows only if Tier 3 adopted
- Rust remains single source of truth

**Default Recommendations**:
- **Python**: Tier 2 (nice wrapper for scripts/notebooks)
- **Go**: Tier 1 (Go developers comfortable with protobuf)
- **Node.js**: Tier 2 (idiomatic Promise-based API)
- **Offline CLI**: Consider Tier 3 only if truly needed

**Maintenance Strategy**:
- Tier 1: Auto-generated, zero maintenance
- Tier 2: Thin wrapper, updates with protobuf changes
- Tier 3: Flag as "high maintenance" in docs, require strong justification

### Success Criteria
1. ✅ Tier 1 available for all languages (just protoc)
2. ✅ Tier 2 implemented for Python, Node.js
3. ✅ Tier 3 only implemented when justified (not default)
4. ✅ Clear documentation on tier selection
5. ✅ Rust service remains single source of truth for business logic
6. ✅ Time to add Tier 1 for new language: < 1 hour

### Metrics
**Quantitative**:
- Percentage using Tier 1: 40-50%
- Percentage using Tier 2: 40-50%
- Percentage using Tier 3: < 10% (only when necessary)
- Lines of duplicated logic: 0 for Tier 1/2, growing for Tier 3
- Maintenance time per SDK tier: Tier 1 < 1 EU, Tier 2 < 3 EU, Tier 3 > 8 EU

**Qualitative**:
- "Easy to get started with Tier 1"
- "Tier 2 makes common operations convenient"
- "Tier 3 clearly marked as high maintenance"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Maintenance Burden Indicator**
   - Tier 3 SDKs taking significant time to maintain
   - Logic drift detected between Tier 3 and Rust
   - Updates to business rules require 3+ SDK changes
   - More than 20% of development time on SDK maintenance

2. **Adoption Pattern Indicator**
   - Everyone wants Tier 3 (suggests architecture problem)
   - Or: Everyone stuck on Tier 1 (Tier 2 not useful enough)
   - Clear pattern that one tier is wrong choice
   - Frequent requests for features not in current tier

3. **Network Performance Indicator**
   - Tier 2 network calls causing performance issues
   - Need local validation to reduce roundtrips
   - Latency makes Tier 2 unusable
   - Offline operation becoming common requirement

4. **Complexity Indicator**
   - Tier selection confusing for developers
   - Wrong tier chosen frequently
   - Need simpler model (just one tier)
   - Documentation not helping with decisions

### Risks of Decision

1. **Tier 3 Adoption**
   - Risk: Teams adopt Tier 3 without understanding cost
   - Mitigation: Require justification, document maintenance burden
   - Severity: Medium-High

2. **Tier 1 Too Basic**
   - Risk: Developers frustrated with raw protobuf
   - Mitigation: Provide Tier 2 for common languages quickly
   - Severity: Low

3. **Inconsistent Tier Choices**
   - Risk: Each team picks different tier, hard to support
   - Mitigation: Clear guidelines, default recommendations
   - Severity: Low-Medium

4. **Logic Drift in Tier 3**
   - Risk: Validation logic diverges from Rust
   - Mitigation: Flag Tier 3 as experimental, test against Rust service
   - Severity: High (for Tier 3 only)

### Migration Cost

**From Tier 1 to Tier 2**: Low (2-3 EU, add wrapper)
**From Tier 2 to Tier 3**: High (8-12 EU, duplicate logic)
**From Tier 3 to Tier 2**: Low (remove local logic, use remote)
**Rollback**: Very Low (stay at Tier 1)

---

## P.ML.3.2. Logic Duplication Prevention

### Problem Statement
How do we prevent business logic from being duplicated across Rust, Python, Go, and Node.js implementations?

### Problem Stack
- **Parent**: P.ML.3 (SDK Distribution Strategy)
- **Siblings**: P.ML.3.1 (SDK Tiers), P.ML.3.3 (Offline Capability)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Duplicated logic creates maintenance burden
- Logic will drift over time (guaranteed)
- Bugs must be fixed in multiple places
- Testing multiplies across languages
- Single source of truth violated

**Risks of Not Solving:**
- Business rules inconsistent across languages
- Security vulnerabilities duplicated or missed
- Behavior differs between CLI and service
- Breaking changes require coordinated updates
- Impossible to maintain long-term

### Options

#### Option A: Accept Duplication (Manual Sync)
**Description**: Implement logic in each language, keep in sync manually.

**Pros**:
- Language-idiomatic implementations
- No architectural complexity
- Full control per language

**Cons**:
- WILL drift (history proves this)
- High maintenance burden
- Bugs duplicated or inconsistent fixes
- Testing multiplies
- No single source of truth

**Trade-offs**: Flexibility vs maintainability

#### Option B: Schema-Driven Code Generation
**Description**: Define validation rules in schema (JSON Schema, DSL), generate code for each language.

```yaml
# validation_schema.yaml
rules:
  - field: title
    required: true
    min_length: 5
    max_length: 200
  - field: problem.statement
    required: true
    min_length: 10
```

**Pros**:
- Single source of truth (schema)
- Generated validators in all languages
- Can't drift (regenerated from schema)
- Validation logic not hand-written

**Cons**:
- Complex code generation needed
- Schema may not express all rules
- Generated code may not be optimal
- Tooling maintenance burden
- Not all logic is validation (business rules)

**Trade-offs**: Guaranteed consistency vs tooling complexity

#### Option C: Remote Validation (Network Calls) ⭐ CHOSEN
**Description**: Keep ALL business logic in Rust, clients call service for validation and operations.

```python
# Python client - no local validation
from adr_sdk import ADRClient

client = ADRClient('localhost:50051')

# Validation happens in Rust service
try:
    adr = client.create_adr(title='X', problem='...')
except ValidationError as e:
    print(f"Invalid: {e}")
```

**Pros**:
- Zero duplication (Rust is single source of truth)
- Can't drift (there's only one implementation)
- Updates require changing only Rust
- Testing happens in one place
- All clients get fixes immediately
- Simplest to maintain

**Cons**:
- Requires network call for validation
- Can't validate offline
- Slower than local validation

**Trade-offs**: Network dependency vs zero duplication

#### Option D: Hybrid (Critical Logic Only Remote)
**Description**: Simple validation local (length, format), business rules remote.

```python
# Python client
def create_adr(title, problem):
    # Local: basic checks (fast, no network)
    if len(title) < 5:
        raise ValueError("Title too short")
    
    # Remote: business rules (authoritative)
    return client.create_adr(title, problem)
```

**Pros**:
- Fast feedback for simple errors
- Complex logic stays in Rust
- Reduced network calls

**Cons**:
- Still some duplication (local checks)
- Client and service validation can disagree
- Maintenance burden for local checks

**Trade-offs**: Performance vs partial duplication

### Decision
**Chosen**: Option C - Remote Validation (with Option D for Tier 3 SDKs only)

**Rationale**:
- **Default (Tier 1/2)**: All validation in Rust service (Option C)
  - Zero duplication
  - Single source of truth
  - Simple to maintain
- **Tier 3 SDKs (if needed)**: Can add local validation (Option D)
  - Clearly marked as higher maintenance
  - Local validation tested against Rust
  - Used only for offline scenarios

**Implementation**:
- Rust service exposes validation endpoints if needed
- Clients send data, get validation errors back
- Rich error messages help client display issues
- Tier 3 SDKs duplicate ONLY if offline critical

**Validation Strategy**:
```rust
// Rust service - single place for validation
pub fn validate_adr(adr: &ADR) -> Result<(), ValidationError> {
    // All rules here
    if adr.title.len() < 5 { return Err(...) }
    if !adr.problem.statement.is_empty() { return Err(...) }
    // Complex business rules
    validate_status_transition(&adr.status, &adr.old_status)?;
    Ok(())
}
```

### Success Criteria
1. ✅ Business logic exists in exactly ONE place (Rust SDK)
2. ✅ Tier 1/2 clients make zero local business decisions
3. ✅ Tier 3 clients (if any) explicitly document duplicated logic
4. ✅ Updates to business rules require changing only Rust
5. ✅ All clients get rule changes immediately (next API call)
6. ✅ No drift detection needed (impossible to drift)

### Metrics
**Quantitative**:
- Lines of duplicated business logic: 0 (Tier 1/2), documented (Tier 3)
- Time to update business rule: < 1 hour (change Rust only)
- Drift incidents: 0 (architectural guarantee for Tier 1/2)

**Qualitative**:
- "Never worry about logic drift"
- "Update once, all clients benefit"
- "Testing in one place"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Performance Indicator**
   - Validation network calls causing user-visible delays
   - More than 30% of API calls are validation only
   - Latency unacceptable for interactive use
   - Need local validation for UX

2. **Offline Requirement Indicator**
   - Multiple requests for offline validation
   - CLIs can't work without network
   - Mobile apps need offline mode
   - Field usage requires no connectivity

3. **Complexity Indicator**
   - Business rules too complex for remote-only
   - Need local decision-making
   - Chatty API due to validation calls
   - Round-trips becoming bottleneck

4. **Schema Generation Maturity**
   - Tooling exists to generate validators reliably
   - Schema languages expressive enough
   - Code generation high quality
   - Maintenance burden acceptable

### Risks of Decision

1. **Network Dependency**
   - Risk: Can't validate without network
   - Mitigation: Tier 3 SDKs for offline scenarios
   - Severity: Low (most use cases online)

2. **Latency**
   - Risk: Validation slower than local
   - Mitigation: Batch validation, caching, monitor latency
   - Severity: Low-Medium

3. **Tier 3 Drift**
   - Risk: Tier 3 SDKs still duplicate logic
   - Mitigation: Test against Rust, document maintenance cost
   - Severity: Medium (only affects Tier 3)

### Migration Cost

**To Schema-Driven (Option B)**: High (10-15 EU, build tooling)
**To Accept Duplication (Option A)**: Low (just implement, high ongoing cost)
**Rollback**: Very Low (clients already calling service)

---

## P.ML.4. Operational Complexity

## P.ML.4.1. Service Deployment Model

### Problem Statement
When we have Rust core service plus auxiliary services (Python ML, Go compliance, Node notify) plus potential adapter services, how do we deploy and manage them operationally?

### Problem Stack
- **Parent**: P.ML.4 (Operational Complexity)
- **Siblings**: P.ML.4.2 (Monitoring), P.ML.4.3 (Debugging)
- **Level**: Operational

### Why This Is A Problem
**Impact:**
- Determines operational burden and on-call complexity
- Affects deployment velocity and rollback capability
- Influences scaling strategies
- Impacts cost (infrastructure and team time)
- Determines reliability and uptime

**Risks of Not Solving:**
- Deployment chaos (no clear process)
- Services step on each other
- Difficult rollbacks
- Can't scale services independently
- High operational burden kills productivity

### Options

#### Option A: Single Deployment Unit (Container with All Services)
**Description**: Package all services (Rust, Python, Go, Node) in one container.

**Pros**:
- Simple deployment (one unit)
- No service discovery needed
- Atomic updates (all or nothing)
- Easy to version

**Cons**:
- Can't scale services independently
- One service crash kills all
- Large container image
- Deployment of one service requires deploying all
- Language runtime conflicts in one container

**Trade-offs**: Simplicity vs flexibility

#### Option B: Fully Independent Deployments
**Description**: Each service deployed completely independently, different repos, CI/CD, etc.

**Pros**:
- Maximum independence
- Can scale each service
- Deploy independently
- Different teams can own services

**Cons**:
- High coordination overhead
- Service discovery complexity
- Version compatibility matrix
- Breaking changes coordination difficult
- High operational burden

**Trade-offs**: Independence vs coordination overhead

#### Option C: Monorepo with Independent Deployments ⭐ CHOSEN
**Description**: All services in one repo, deployed independently but with coordination.

```
repo/
├── services/
│   ├── adr-service/        (Rust core)
│   ├── ml-service/         (Python)
│   ├── compliance-service/ (Go)
│   └── notify-service/     (Node)
├── adapters/
│   └── mongo-adapter/      (Node bridge)
├── proto/                  (shared schemas)
└── deploy/
    ├── docker-compose.yml  (local dev)
    └── k8s/                (production)
```

**Pros**:
- Coordinated changes easy (same repo)
- Shared protobuf schemas
- Atomic cross-service updates possible
- But: can deploy services independently when needed
- Single CI/CD pipeline
- Version coordination simpler

**Cons**:
- Larger repository
- Need clear module boundaries
- Build system must support multiple languages

**Trade-offs**: Coordination vs repo size

**Research References**:
- Google monorepo pattern
- Bazel for multi-language builds
- Kubernetes service mesh patterns

### Decision
**Chosen**: Option C - Monorepo with Independent Deployments

**Rationale**:
- Coordinated changes common (protobuf updates affect all)
- Can still deploy services independently
- Simpler version coordination (all in sync)
- Easier local development (one checkout)
- Supports both atomic and independent deploys
- Industry-proven at scale (Google, many others)

**Deployment Strategy**:

**Local Development**:
```yaml
# docker-compose.yml
services:
  adr-service:
    build: ./services/adr-service
    ports: ["50051:50051"]
  
  ml-service:
    build: ./services/ml-service
    depends_on: [adr-service]
  
  # ... other services
```

**Production (Kubernetes)**:
- Each service = separate deployment
- Can scale independently
- Shared service mesh for discovery
- Rolling updates per service
- Rollback per service

**Versioning**:
- Shared version for coordinated releases
- Independent versions for service-specific updates
- Protobuf versioning ensures compatibility

### Success Criteria
1. ✅ All services in one repository
2. ✅ Can deploy any service independently
3. ✅ Local development with one command (docker-compose up)
4. ✅ Protobuf changes automatically propagate to all services
5. ✅ Can scale services independently in production
6. ✅ Clear deployment documentation

### Metrics
**Quantitative**:
- Time to deploy all services: < 10 minutes
- Time to deploy one service: < 3 minutes
- Deployment success rate: > 95%
- Rollback time: < 5 minutes

**Qualitative**:
- "Easy to develop locally"
- "Clear deployment process"
- "Can deploy confidently"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Repository Scale Indicator**
   - Repository too large (> 10GB)
   - Clone time > 5 minutes
   - CI builds taking > 30 minutes
   - Difficult to navigate codebase

2. **Deployment Coupling Indicator**
   - Services can't be deployed independently despite design
   - Always need coordinated deploys
   - Or: Never need coordinated deploys (split repo?)
   - Version conflicts frequent

3. **Team Friction Indicator**
   - Multiple teams stepping on each other
   - Merge conflicts common
   - Want separate repos per service
   - Ownership unclear

4. **Operational Burden Indicator**
   - Deployment process too complex
   - Frequent deployment failures
   - Rollbacks difficult
   - On-call burden too high

### Risks of Decision

1. **Repository Growth**
   - Risk: Repo becomes too large
   - Mitigation: Use git LFS for large files, modular structure
   - Severity: Low (monitor size)

2. **Build Complexity**
   - Risk: Multi-language builds complex
   - Mitigation: Docker per service, clear build docs
   - Severity: Low-Medium

3. **Deployment Coordination**
   - Risk: Still need to coordinate some deploys
   - Mitigation: Clear versioning, breaking change process
   - Severity: Medium

### Migration Cost

**To Separate Repos (Option B)**: Medium (5-8 EU, split repo, setup CI/CD per repo)
**To Monolithic (Option A)**: Low (merge services, lose independence)
**Rollback**: N/A (starting state)

---

## Summary: Multi-Language Integration Decisions

| ID | Problem | Decision | Effort | Status |
|---|---|---|---|---|
| P.ML.1.1 | Client Integration | gRPC clients from protobuf | 0.5 EU per language | ✅ Recommended |
| P.ML.1.2 | Service Federation | Rust core + auxiliary services | 2-4 EU per service | ✅ When needed |
| P.ML.2.1 | Adapter Implementation | Rust default, bridge when compelling | 3-5 EU per bridge | ✅ Recommended |
| P.ML.3.1 | SDK Tiers | Tier 1/2 default, Tier 3 rare | 0.5-3 EU | ✅ Recommended |
| P.ML.3.2 | Logic Duplication | Remote validation (Rust only) | 0 EU | ✅ Recommended |
| P.ML.4.1 | Deployment Model | Monorepo, independent deploys | Baseline | ✅ Recommended |

## Key Principles for Multi-Language Integration

### ✅ DO:
1. **Rust is source of truth** - All core logic stays in Rust
2. **gRPC + Protobuf for all inter-language communication** - Type-safe, generated
3. **Default to Rust implementations** - Use other languages only when compelling
4. **Start simple** - Tier 1 SDK, add features only when needed
5. **Measure first** - Only add language/service when evidence supports it

### ❌ DON'T:
1. **Duplicate business logic** across languages
2. **Use FFI** unless absolutely critical
3. **Default to bridge adapters** (Rust adapters preferred)
4. **Build Tier 3 SDKs** without strong justification
5. **Add services prematurely** (YAGNI)

## Integration Effort Summary

| Scenario | Pattern | Effort (EU) |
|----------|---------|-------------|
| Python app needs to read ADRs | gRPC client (Tier 1) | 0.5 |
| Python CLI needs nice API | Remote SDK (Tier 2) | 2-3 |
| Python ML service for analysis | Federated service | 3-5 |
| Go adapter for ArangoDB | Adapter bridge | 4-6 |
| Node adapter for MongoDB | Adapter bridge | 4-6 |
| Offline Python CLI | Hybrid SDK (Tier 3) | 8-12 |

---

*This architecture enables polyglot integration while maintaining Rust as the single source of truth and minimizing maintenance burden.*