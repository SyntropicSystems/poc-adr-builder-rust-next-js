# ADR Editor System - Architecture Decisions

## Document Structure
Following the same format as our CLI tools decisions document.

---

## Problem Stack Overview

```
P1. System Architecture (STRATEGIC)
    ├── P1.1. Overall Architecture Pattern
    │   ├── P1.1.1. Hexagonal Architecture Design
    │   └── P1.1.2. Service Boundaries
    ├── P1.2. Technology Stack
    │   ├── P1.2.1. Backend Language & Runtime
    │   └── P1.2.2. Frontend Framework
    └── P1.3. Deployment Model
        ├── P1.3.1. Monorepo vs Multi-repo
        └── P1.3.2. Service Deployment Strategy

P2. SDK & Core Domain (ARCHITECTURAL)
    ├── P2.1. SDK Structure & Layers
    │   ├── P2.1.1. Domain Model Location
    │   ├── P2.1.2. SDK Distribution
    │   └── P2.1.3. Versioning Strategy
    ├── P2.2. Storage Abstraction
    │   ├── P2.2.1. Port/Adapter Pattern
    │   ├── P2.2.2. Repository Interface Design
    │   └── P2.2.3. Adapter Implementation Strategy
    └── P2.3. Business Logic Placement
        ├── P2.3.1. Domain Logic in SDK
        └── P2.3.2. Service Logic Separation

P3. API Layer (ARCHITECTURAL)
    ├── P3.1. API Protocol Choice
    │   ├── P3.1.1. REST vs GraphQL vs gRPC
    │   └── P3.1.2. API Versioning
    ├── P3.2. Type Safety Across Boundaries
    │   ├── P3.2.1. Contract Definition
    │   ├── P3.2.2. Code Generation Strategy
    │   └── P3.2.3. Validation Layer
    └── P3.3. API Client Architecture
        ├── P3.3.1. Client SDK Design
        └── P3.3.2. Error Handling Strategy

P4. Frontend Architecture (TACTICAL)
    ├── P4.1. Next.js Architecture
    │   ├── P4.1.1. App Router vs Pages Router
    │   ├── P4.1.2. Rendering Strategy (SSR/SSG/CSR)
    │   └── P4.1.3. API Route Usage
    ├── P4.2. State Management
    │   ├── P4.2.1. Global State (Zustand vs alternatives)
    │   ├── P4.2.2. Server State (React Query vs alternatives)
    │   └── P4.2.3. Form State Management
    └── P4.3. Component Architecture
        ├── P4.3.1. Component Organization
        └── P4.3.2. Reusability Strategy

P5. Storage Implementation (TACTICAL)
    ├── P5.1. Filesystem Backend
    │   ├── P5.1.1. File Format (JSON vs YAML vs Binary)
    │   └── P5.1.2. File Organization
    ├── P5.2. Database Backends
    │   ├── P5.2.1. Schema Design
    │   ├── P5.2.2. Migration Strategy
    │   └── P5.2.3. Multi-tenancy Approach
    └── P5.3. Concurrent Backend Support
        └── P5.3.1. Running Multiple Backends Simultaneously

P6. CLI Tool Architecture (TACTICAL)
    ├── P6.1. CLI Framework Choice
    ├── P6.2. SDK Integration
    └── P6.3. Configuration Management
```

---

# P1. System Architecture

## P1.1. Overall Architecture Pattern

### Problem Statement
How do we structure the system to maximize code reuse between CLI, service, and different storage backends while maintaining clean boundaries and flexibility?

### Problem Stack
- **Parent**: Root (System Design)
- **Children**: P1.1.1 (Hexagonal Design), P1.1.2 (Service Boundaries)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Determines code reusability across CLI, service, and future tools
- Affects maintainability and testing
- Influences how easily we can swap storage backends
- Determines deployment flexibility
- Impacts development velocity

**Risks of Not Solving:**
- Business logic duplicated across CLI and service
- Storage coupling makes backend changes expensive
- Hard to test without real infrastructure
- Difficult to add new interfaces (e.g., TUI, desktop app)
- Tight coupling between layers

### Options

#### Option A: Traditional Layered Architecture
```
Frontend (Next.js)
    ↓
API Layer (REST/GraphQL)
    ↓
Service Layer (Rust)
    ↓
Data Access Layer
    ↓
Database
```

**Pros**:
- Simple, well-understood pattern
- Clear top-to-bottom flow
- Easy to explain to team

**Cons**:
- Layers depend on each other (coupling)
- Hard to swap storage layer
- Business logic mixed with infrastructure
- Testing requires entire stack
- Can't reuse core logic in CLI without service

**Trade-offs**: Simplicity vs flexibility

#### Option B: Hexagonal Architecture (Ports & Adapters) ⭐ CHOSEN
```
         ┌──────────────────────────┐
         │   Domain Core (SDK)      │
         │   - ADR entities         │
         │   - Business rules       │
         │   - Use cases            │
         └────────┬─────────────────┘
                  │
      ┌───────────┴──────────────┐
      │                          │
   Ports                      Ports
   (Interfaces)              (Interfaces)
      │                          │
   Adapters                  Adapters
      │                          │
┌─────┴─────┐           ┌────────┴─────────┐
│ Inbound   │           │ Outbound         │
│ - HTTP    │           │ - Filesystem     │
│ - CLI     │           │ - Postgres       │
│ - gRPC    │           │ - DynamoDB       │
└───────────┘           └──────────────────┘
```

**Pros**:
- Domain logic completely independent
- Storage backends easily swappable (just adapters)
- Highly testable (mock ports)
- CLI and service share same core
- Can add new interfaces without changing core
- Infrastructure at the edges

**Cons**:
- More upfront design
- Need to define clear ports
- More abstraction layers
- Requires discipline to maintain boundaries

**Trade-offs**: Upfront complexity for long-term flexibility

#### Option C: Microkernel Architecture
**Description**: Plugin-based system with small core and extensions for each storage backend.

**Pros**:
- Highly extensible
- Small core footprint
- Dynamic plugins possible

**Cons**:
- Overkill for this use case
- Complex plugin system
- Dynamic loading issues in Rust
- Harder to reason about

**Trade-offs**: Maximum flexibility vs unnecessary complexity

**Research References**:
- Hexagonal Architecture (Alistair Cockburn)
- Clean Architecture (Robert Martin)
- Domain-Driven Design (Eric Evans)
- Rust patterns: https://github.com/rust-unofficial/patterns

### Decision
**Chosen**: Option B - Hexagonal Architecture (Ports & Adapters)

**Rationale**:
- Perfect fit for "SDK that can be used by both CLI and service"
- Storage abstraction requirement maps directly to adapter pattern
- Domain logic stays pure, testable, and reusable
- Can start with filesystem, add databases incrementally
- CLI and service are just different inbound adapters using same core
- Industry-proven pattern for these exact requirements

**Architecture Layers**:
```rust
// 1. Domain Core (SDK - adr-sdk crate)
//    - Pure business logic, no infrastructure
//    - Defines ports (traits)
pub trait ADRRepository { ... }
pub trait ADRValidator { ... }

// 2. Adapters (adr-adapters crate)
//    - Implement ports
//    - Storage: filesystem, postgres, dynamodb
//    - Each adapter is independent
pub struct FilesystemAdapter;
impl ADRRepository for FilesystemAdapter { ... }

// 3. Applications (use SDK + wire adapters)
//    - CLI tool (adr-cli)
//    - Service (adr-service)
//    - Each picks which adapters to use
```

### Success Criteria
1. ✅ Domain core has zero infrastructure dependencies
2. ✅ Can swap storage backend by changing one line (adapter)
3. ✅ CLI and service share same domain logic (import same SDK)
4. ✅ Can test business rules without any storage
5. ✅ Adding new storage backend doesn't touch core
6. ✅ Adding new interface (e.g., TUI) doesn't touch core

### Metrics
**Quantitative**:
- Core domain dependencies: 0 infrastructure crates
- Code reuse between CLI and service: > 80%
- Time to add new storage backend: < 1 day
- Test coverage of domain core: > 90% (easy with pure logic)

**Qualitative**:
- "Adding X backend was just implementing the trait"
- "Business logic changes don't require infrastructure changes"
- "Tests run fast without database"

### Triggers to Revisit

1. **Coupling Detected**
   - Domain core imports infrastructure crates
   - Storage logic leaking into use cases
   - Tests require real infrastructure

2. **Abstraction Burden**
   - More time spent on ports/adapters than features
   - Abstractions feel forced or unnatural
   - Team struggling to understand boundaries

3. **Performance Issues**
   - Abstraction layers causing measurable overhead
   - Can't optimize without breaking abstractions
   - Need to bypass ports for critical paths

4. **Complexity Feedback**
   - Onboarding time > 1 day due to architecture
   - Developers avoiding changes due to layers
   - Bug fixes require touching multiple layers

### Risks of Decision

1. **Over-Abstraction Risk**
   - Risk: Too many layers, unnecessary complexity
   - Mitigation: Keep ports simple, add only as needed
   - Severity: Medium

2. **Learning Curve**
   - Risk: Team unfamiliar with hexagonal architecture
   - Mitigation: Documentation, examples, pair programming
   - Severity: Low

3. **Performance Overhead**
   - Risk: Trait dispatch and abstraction layers add overhead
   - Mitigation: Rust zero-cost abstractions, benchmark critical paths
   - Severity: Low (Rust's trait system is designed for this)

### Migration Cost
**To Layered (Option A)**: Low-Medium (flatten structure, lose benefits)
**To Microkernel (Option C)**: High (major redesign)
**Rollback**: Medium (would lose storage flexibility)

---

## P2.1. SDK Structure & Layers

### Problem Statement
How do we organize the SDK (core domain) to maximize reusability while maintaining clear boundaries between domain logic, ports, and infrastructure concerns?

### Problem Stack
- **Parent**: P2 (SDK & Core Domain)
- **Siblings**: P2.2 (Storage Abstraction), P2.3 (Business Logic)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Determines what's reusable vs what's application-specific
- Affects dependency graph and compile times
- Influences testability
- Impacts versioning and release strategy
- Determines API surface for consumers

**Risks of Not Solving:**
- Unclear what belongs in SDK vs adapters vs applications
- Circular dependencies between crates
- CLI and service diverge in implementation
- Hard to version and release independently

### Options

#### Option A: Single SDK Crate (Monolithic)
```
adr-sdk/
├── src/
│   ├── domain/      # Entities, value objects
│   ├── ports/       # Repository traits
│   ├── use_cases/   # Business logic
│   └── adapters/    # All adapters included
```

**Pros**:
- Simple, one dependency
- No coordination between crates
- Fast to get started

**Cons**:
- Brings all adapter dependencies even if unused
- Can't version adapters independently
- Compile time includes all backends
- Tight coupling between core and adapters

**Trade-offs**: Simplicity vs flexibility

#### Option B: Layered SDK Crates ⭐ CHOSEN
```
adr-domain/          # Pure domain (entities, value objects)
    └── no dependencies
    
adr-sdk/             # Ports + Use cases
    └── depends on: adr-domain
    
adr-adapters/        # Adapter implementations
    ├── depends on: adr-sdk
    └── features: filesystem, postgres, dynamodb
    
adr-cli/             # CLI application
    └── depends on: adr-sdk, adr-adapters (feature flags)
    
adr-service/         # Web service
    └── depends on: adr-sdk, adr-adapters (feature flags)
```

**Pros**:
- Clear dependency graph (domain ← sdk ← adapters ← apps)
- Core has no infrastructure dependencies
- Adapters opt-in via feature flags
- Can version layers independently
- Small core, fast compilation
- CLI only pulls in adapters it needs

**Cons**:
- More crates to manage
- Need to coordinate versions
- Slightly more complex setup

**Trade-offs**: More crates vs better separation

#### Option C: Workspace with Separate Repos
**Description**: Each crate in its own repository, published separately.

**Pros**:
- True independence
- Can be used by external projects
- Clear release cadence per crate

**Cons**:
- High coordination overhead
- Version management nightmare
- Harder to make cross-crate changes
- Over-engineering for private use

**Trade-offs**: Maximum independence vs practical overhead

### Decision
**Chosen**: Option B - Layered SDK Crates in Monorepo

**Rationale**:
- Clear separation of concerns (domain, ports, adapters, apps)
- Core domain is dependency-free (pure logic)
- Adapters are opt-in via features (CLI only pulls filesystem)
- Service pulls multiple adapters
- Monorepo makes cross-crate changes easy
- Can still publish crates independently if needed later

**Crate Structure**:
```rust
// adr-domain (pure domain)
pub struct ADR { ... }
pub struct ProblemStatement { ... }
// No traits, no I/O, pure data + domain logic

// adr-sdk (ports + use cases)
pub trait ADRRepository { ... }
pub struct CreateADRUseCase { ... }
// Uses domain types, defines ports, no implementations

// adr-adapters (implementations)
#[cfg(feature = "filesystem")]
pub struct FilesystemAdapter { ... }

#[cfg(feature = "postgres")]
pub struct PostgresAdapter { ... }
```

### Success Criteria
1. ✅ Domain crate has zero dependencies
2. ✅ SDK crate only depends on domain (no infrastructure)
3. ✅ Adapters crate feature flags work (only compile what's needed)
4. ✅ CLI can build with only filesystem adapter
5. ✅ Service can build with multiple adapters
6. ✅ Dependency graph is acyclic

### Metrics
**Quantitative**:
- Domain crate dependencies: 0
- SDK crate infrastructure dependencies: 0
- CLI build time with one adapter: < 30s
- SDK compilation time: < 10s

**Qualitative**:
- "Easy to add new adapter without touching core"
- "CLI doesn't pull in database dependencies"

### Triggers to Revisit

1. **Dependency Creep**
   - Domain crate gains dependencies
   - SDK crate imports infrastructure
   - Circular dependencies appear

2. **Coordination Overhead**
   - Changes require updating 3+ crates
   - Version mismatches cause issues
   - Release process becomes painful

3. **Compilation Issues**
   - Build times increase significantly
   - Feature flags become complex web
   - Adapter features conflict

### Risks of Decision

1. **Multiple Crate Management**
   - Risk: Coordination between crates
   - Mitigation: Workspace dependencies, shared versions
   - Severity: Low

2. **Feature Flag Complexity**
   - Risk: Complex feature combinations
   - Mitigation: Test common combinations in CI
   - Severity: Low

### Migration Cost
**To Monolithic**: Low (merge crates)
**To Separate Repos**: Medium (split monorepo, versioning)
**Rollback**: Very Low

---

## P2.2.1. Port/Adapter Pattern Details

### Problem Statement
How do we design the port (trait) interfaces to support multiple storage backends (filesystem, Postgres, DynamoDB, etc.) without leaking storage-specific concerns into the domain?

### Problem Stack
- **Parent**: P2.2 (Storage Abstraction)
- **Siblings**: P2.2.2 (Repository Interface), P2.2.3 (Adapters)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Determines ease of adding new storage backends
- Affects testability (can we mock storage?)
- Influences performance (abstraction overhead)
- Impacts error handling across backends
- Determines what operations are supported

**Risks of Not Solving:**
- Traits designed for one backend, hard to implement others
- Domain logic coupled to storage specifics
- Can't test without real storage
- Each backend requires domain changes

### Options

#### Option A: Generic CRUD Repository
```rust
pub trait Repository<T> {
    fn create(&self, item: T) -> Result<T>;
    fn read(&self, id: String) -> Result<Option<T>>;
    fn update(&self, item: T) -> Result<T>;
    fn delete(&self, id: String) -> Result<()>;
    fn list(&self) -> Result<Vec<T>>;
}
```

**Pros**:
- Simple, standard pattern
- Works for most CRUD operations
- Easy to understand

**Cons**:
- Too generic (one-size-fits-all)
- Doesn't express domain operations
- Query operations awkward (how to filter?)
- Forces all backends to support same operations
- Lost domain semantics

**Trade-offs**: Simplicity vs domain expressiveness

#### Option B: Domain-Specific Repository ⭐ CHOSEN
```rust
pub trait ADRRepository: Send + Sync {
    // Domain operations, not CRUD
    async fn save(&self, adr: &ADR) -> Result<(), ADRError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError>;
    async fn find_by_status(&self, status: ADRStatus) -> Result<Vec<ADR>, ADRError>;
    async fn find_by_tag(&self, tag: &str) -> Result<Vec<ADR>, ADRError>;
    async fn find_superseding(&self, id: &str) -> Result<Vec<ADR>, ADRError>;
    async fn list_all(&self) -> Result<Vec<ADR>, ADRError>;
    async fn delete(&self, id: &str) -> Result<(), ADRError>;
}
```

**Pros**:
- Speaks domain language
- Expresses actual use cases
- Each method has clear purpose
- Easy to add domain-specific queries
- Hides storage implementation details

**Cons**:
- More methods to implement per adapter
- Might not map 1:1 to storage operations
- Could grow large with many queries

**Trade-offs**: Domain clarity vs implementation burden

#### Option C: Query Object Pattern
```rust
pub trait ADRRepository {
    async fn save(&self, adr: &ADR) -> Result<()>;
    async fn find(&self, query: ADRQuery) -> Result<Vec<ADR>>;
}

pub enum ADRQuery {
    ById(String),
    ByStatus(ADRStatus),
    ByTag(String),
    All,
}
```

**Pros**:
- Fewer trait methods
- Extensible queries
- Backend can optimize query execution

**Cons**:
- Less type-safe (enum of queries)
- Harder to discover what queries exist
- Backend must handle all query types
- Query complexity in enum instead of methods

**Trade-offs**: Extensibility vs type safety

### Decision
**Chosen**: Option B - Domain-Specific Repository

**Rationale**:
- ADR domain has clear, bounded query needs
- Type-safe, discoverable API
- Each method maps to a use case
- Easy to implement (each adapter knows what to do)
- Doesn't grow unbounded (ADR domain is stable)
- Clear intent: `find_by_status` vs generic `find`

**Additional Design**:
```rust
// Error type that works across backends
#[derive(Debug, thiserror::Error)]
pub enum ADRError {
    #[error("ADR not found: {0}")]
    NotFound(String),
    
    #[error("ADR already exists: {0}")]
    AlreadyExists(String),
    
    #[error("Invalid ADR: {0}")]
    ValidationError(String),
    
    #[error("Storage error: {0}")]
    StorageError(String),  // Backend-agnostic
}

// Result type alias
pub type ADRResult<T> = Result<T, ADRError>;
```

### Success Criteria
1. ✅ All methods express domain operations
2. ✅ Filesystem, Postgres, DynamoDB can all implement trait
3. ✅ No storage-specific types in trait (e.g., no SQL queries)
4. ✅ Easy to create mock implementation for testing
5. ✅ Error types work for all backends

### Metrics
**Quantitative**:
- Number of repository methods: < 15
- Time to implement new adapter: < 1 day
- Test coverage with mocks: 100% of use cases

**Qualitative**:
- "Clear what each method does"
- "Easy to implement for new backend"
- "Errors are helpful"

### Triggers to Revisit

1. **Trait Explosion**
   - More than 20 methods in trait
   - Many methods rarely used
   - Complexity in implementing adapters

2. **Backend Mismatch**
   - Can't implement trait for a target backend
   - Need to add backend-specific methods
   - Hacks or workarounds in adapters

3. **Query Complexity**
   - Need complex filtering/sorting
   - Query combinations not expressible
   - Performance issues from generic queries

### Risks of Decision

1. **Method Growth**
   - Risk: Trait grows as features added
   - Mitigation: Group related operations, use builder pattern
   - Severity: Medium

2. **Adapter Implementation Burden**
   - Risk: Each adapter must implement all methods
   - Mitigation: Provide default implementations where possible
   - Severity: Low

### Migration Cost
**To Generic (Option A)**: Low (simplify trait)
**To Query Object (Option C)**: Medium (refactor to enum)
**Rollback**: Low

---

## P3.1.1. API Protocol Choice (REST vs GraphQL vs gRPC)

### Problem Statement
What API protocol should the Rust service expose for the Next.js frontend, CLI tool, and future clients?

### Problem Stack
- **Parent**: P3.1 (API Protocol Choice)
- **Siblings**: P3.1.2 (API Versioning)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Determines frontend development experience
- Affects type safety across boundaries
- Influences performance and efficiency
- Impacts tooling and code generation
- Determines API evolution strategy

**Risks of Not Solving:**
- Type mismatches between frontend and backend
- Manual API client maintenance
- Performance issues (over-fetching/under-fetching)
- Hard to version and evolve API

### Options

#### Option A: REST with OpenAPI
```
POST   /api/adrs
GET    /api/adrs
GET    /api/adrs/:id
PUT    /api/adrs/:id
DELETE /api/adrs/:id
GET    /api/adrs?status=active
```

**Pros**:
- Simple, well-understood
- Great tooling (Swagger, Postman)
- Works everywhere (browsers, curl)
- Easy to cache
- TypeScript client generation from OpenAPI

**Cons**:
- Multiple roundtrips (N+1 problem)
- Over-fetching or under-fetching
- Versioning can be awkward
- No built-in subscriptions
- Manual schema maintenance

**Trade-offs**: Simplicity vs flexibility

**Rust Libraries**: `axum`, `actix-web`, `utoipa` (OpenAPI generation)

#### Option B: GraphQL
```graphql
query {
  adr(id: "P1.1") {
    title
    problem { statement }
    decision { rationale }
  }
}
```

**Pros**:
- Flexible queries (get exactly what you need)
- Single endpoint
- Strong typing
- Introspection
- No over-fetching
- Great frontend DX

**Cons**:
- More complex to implement
- Caching harder
- Query complexity management needed
- Rust GraphQL ecosystem smaller
- Overkill for simple CRUD?

**Trade-offs**: Flexibility vs complexity

**Rust Libraries**: `async-graphql`, `juniper`

#### Option C: gRPC with Protocol Buffers ⭐ CHOSEN
```protobuf
service ADRService {
  rpc CreateADR(CreateADRRequest) returns (ADR);
  rpc GetADR(GetADRRequest) returns (ADR);
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc UpdateADR(UpdateADRRequest) returns (ADR);
  rpc DeleteADR(DeleteADRRequest) returns (Empty);
}
```

**Pros**:
- We ALREADY have protobuf schema (adr.proto)!
- Type safety across Rust, TypeScript, CLI
- Code generation for all languages
- Efficient binary protocol
- Streaming support built-in
- Versioning via protobuf
- Works great with Rust
- Can expose REST gateway (grpc-gateway)

**Cons**:
- Not browser-native (needs gRPC-web)
- Less tooling than REST
- Binary format harder to debug
- Slightly more setup

**Trade-offs**: Type safety + efficiency vs ecosystem maturity

**Rust Libraries**: `tonic` (excellent gRPC + prost)

#### Option D: Hybrid (gRPC + REST Gateway)
**Description**: Core API is gRPC, but expose REST/JSON gateway for browsers.

**Pros**:
- Best of both worlds
- gRPC for CLI and service-to-service
- REST for browser compatibility
- Single source of truth (protobuf)

**Cons**:
- Two API surfaces to maintain
- More complexity
- Gateway adds latency

### Decision
**Chosen**: Option C - gRPC with Protocol Buffers (with REST gateway for browsers)

**Rationale**:
- **We already defined protobuf schemas for ADR!** Perfect alignment.
- Type safety end-to-end (Rust, TypeScript, CLI)
- Code generation eliminates manual API clients
- Efficient for CLI tool (binary protocol)
- Can add REST gateway for Next.js if needed (grpc-web)
- Versioning built into protobuf
- Streaming support for future features (watch ADR changes)
- Rust has excellent gRPC support (tonic)

**Implementation Strategy**:
```protobuf
// adr.proto (we already have this!)
service ADRService {
  rpc CreateADR(CreateADRRequest) returns (ADR);
  rpc GetADR(GetADRRequest) returns (ADR);
  rpc ListADRs(ListADRsRequest) returns (stream ADR);  // Streaming!
  rpc UpdateADR(UpdateADRRequest) returns (ADR);
  rpc DeleteADR(DeleteADRRequest) returns (Empty);
  rpc WatchADR(WatchADRRequest) returns (stream ADREvent);  // Live updates!
}
```

**For Next.js**: Use `grpc-web` or REST gateway (`tonic-web`, `grpc-gateway-rs`)

### Success Criteria
1. ✅ Single protobuf schema defines API
2. ✅ TypeScript types auto-generated from protobuf
3. ✅ Rust service and CLI share same types
4. ✅ No manual type definitions
5. ✅ API versioning via protobuf
6. ✅ Next.js can call API (via grpc-web or gateway)

### Metrics
**Quantitative**:
- Type errors between frontend/backend: 0 (compile-time checks)
- API client code: 100% generated
- API documentation: Auto-generated from protobuf

**Qualitative**:
- "Adding API method updates all clients automatically"
- "Type safety across all languages"
- "Never write API client code manually"

### Triggers to Revisit

1. **Browser Compatibility Issues**
   - grpc-web too complex
   - Next.js integration problematic
   - Debugging too difficult

2. **Ecosystem Maturity**
   - Rust gRPC libraries lack features
   - TypeScript generation broken
   - Tooling gaps causing friction

3. **Simplicity Needed**
   - Team struggles with gRPC
   - Setup complexity too high
   - Want simpler REST API

4. **Performance Issues**
   - gRPC overhead too high
   - Binary protocol issues
   - REST would be faster

### Risks of Decision

1. **Browser Integration Complexity**
   - Risk: grpc-web adds complexity for Next.js
   - Mitigation: Can use REST gateway, or `tonic-web`
   - Severity: Medium

2. **Learning Curve**
   - Risk: Team unfamiliar with gRPC
   - Mitigation: Documentation, examples, excellent Rust libraries
   - Severity: Low-Medium

3. **Debugging Difficulty**
   - Risk: Binary protocol harder to inspect
   - Mitigation: Use grpcurl, Postman, built-in reflection
   - Severity: Low

### Migration Cost
**To REST (Option A)**: Medium (generate OpenAPI from protobuf)
**To GraphQL (Option B)**: High (redesign API)
**Rollback**: Medium (rewrite API layer)

---

## P4.1.1. Next.js App Router vs Pages Router

### Problem Statement
Should we use Next.js App Router (new, React Server Components) or Pages Router (traditional, proven) for the frontend?

### Problem Stack
- **Parent**: P4.1 (Next.js Architecture)
- **Siblings**: P4.1.2 (Rendering Strategy)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Determines component architecture
- Affects data fetching patterns
- Influences state management needs
- Impacts performance characteristics
- Determines future compatibility

**Risks of Not Solving:**
- Chose legacy pattern (Pages Router) that will be deprecated
- Chose bleeding edge (App Router) with immature ecosystem
- State management mismatch
- Performance issues

### Options

#### Option A: Pages Router (Traditional)
```
pages/
├── index.tsx
├── adrs/
│   ├── index.tsx
│   ├── [id].tsx
│   └── new.tsx
└── api/           # API routes (proxies to Rust)
```

**Pros**:
- Mature, stable, proven
- Huge ecosystem of examples
- Works with all libraries (Zustand, React Query)
- Familiar to most developers
- Simpler mental model

**Cons**:
- Being superseded by App Router
- No React Server Components
- Client-side heavy
- Will be "legacy" in future

**Trade-offs**: Stability vs future-proofing

#### Option B: App Router (New) ⭐ CHOSEN
```
app/
├── page.tsx                    # Homepage
├── adrs/
│   ├── page.tsx               # List ADRs
│   ├── [id]/
│   │   └── page.tsx           # View ADR
│   └── new/
│       └── page.tsx           # Create ADR
├── layout.tsx                  # Root layout
└── api/                        # Route handlers
```

**Pros**:
- Future of Next.js
- React Server Components (better performance)
- Built-in data fetching
- Better SEO (SSR by default)
- Streaming and suspense
- Better loading states

**Cons**:
- Still evolving (though stable now)
- Some libraries not fully compatible yet
- Different patterns from Pages
- Smaller ecosystem of examples

**Trade-offs**: Cutting edge vs battle-tested

#### Option C: Hybrid (Both)
**Description**: Use App Router for new pages, keep Pages Router for API routes or compatibility.

**Pros**:
- Gradual migration path
- Use best of both

**Cons**:
- Confusing (two patterns)
- More complexity
- Doesn't make sense for new project

### Decision
**Chosen**: Option B - App Router

**Rationale**:
- New project, no legacy code
- App Router is stable as of Next.js 13.4+
- Better performance (React Server Components)
- Future-proof (this is where Next.js is going)
- Better DX for data fetching
- SSR by default (good for ADR viewer)
- Zustand works fine with App Router

**Strategy**:
- Use Server Components for static/SSR content
- Use Client Components ("use client") for interactivity
- Leverage React 19 features (useOptimistic, etc.)
- Use Next.js route handlers for API proxy to Rust

### Success Criteria
1. ✅ All pages use App Router pattern
2. ✅ Server Components for static content
3. ✅ Client Components for forms/interactivity
4. ✅ Zustand state management works
5. ✅ gRPC client works from both server and client components

### Metrics
**Quantitative**:
- Time to first byte: < 200ms (SSR)
- Client bundle size: < 200KB (Server Components reduce)
- Build time: < 60s

**Qualitative**:
- Developer feedback: "Easy to work with"
- Good loading states and streaming

### Triggers to Revisit

1. **Compatibility Issues**
   - Libraries don't work with App Router
   - Zustand issues
   - gRPC client incompatible

2. **Complexity Overhead**
   - Server vs Client Components confusing
   - Team struggling with pattern
   - More bugs than Pages Router

3. **Performance Issues**
   - SSR too slow
   - Hydration errors
   - Client bundle larger than Pages

### Risks of Decision

1. **Ecosystem Maturity**
   - Risk: Some libraries not App Router ready
   - Mitigation: Check compatibility, use alternatives
   - Severity: Low (most major libraries support it now)

2. **Learning Curve**
   - Risk: Different patterns than Pages Router
   - Mitigation: Documentation, examples, gradual adoption
   - Severity: Medium

### Migration Cost
**To Pages Router**: Low-Medium (refactor file structure)
**Rollback**: Medium (lose React Server Components benefits)

---

## P4.2.1. Global State Management (Zustand vs Alternatives)

### Problem Statement
What state management solution should we use for global client state (user preferences, UI state, form drafts)?

### Problem Stack
- **Parent**: P4.2 (State Management)
- **Siblings**: P4.2.2 (Server State)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Affects code organization
- Determines learning curve
- Influences bundle size
- Impacts performance
- Determines debugging experience

**Risks of Not Solving:**
- Prop drilling everywhere
- Inconsistent state patterns
- Hard to share state between components
- Performance issues with re-renders

### Options

#### Option A: React Context + useReducer
**Pros**:
- Built-in, no dependencies
- Simple for small apps
- Works with App Router

**Cons**:
- Verbose
- Performance issues (entire context re-renders)
- No DevTools
- Boilerplate heavy

#### Option B: Redux Toolkit
**Pros**:
- Industry standard
- Excellent DevTools
- Time-travel debugging
- Middleware ecosystem

**Cons**:
- Heavy (bundle size)
- Boilerplate (even with toolkit)
- Overkill for small apps
- Learning curve

#### Option C: Zustand ⭐ CHOSEN
```typescript
// Simple, lightweight state
import create from 'zustand'

const useADRStore = create((set) => ({
  filter: 'all',
  setFilter: (filter) => set({ filter }),
  
  drafts: {},
  saveDraft: (id, adr) => set((state) => ({
    drafts: { ...state.drafts, [id]: adr }
  })),
}))
```

**Pros**:
- Tiny bundle size (~1KB)
- Simple API
- No providers needed
- Works great with React 18+
- TypeScript support
- DevTools available
- Works with Server Components

**Cons**:
- Less ecosystem than Redux
- No official middleware (but easy to add)
- Smaller community

**Trade-offs**: Simplicity vs ecosystem

#### Option D: Jotai (Atomic State)
**Pros**:
- Atomic, fine-grained
- Very small
- Modern approach

**Cons**:
- Different mental model
- Less familiar to most devs

### Decision
**Chosen**: Option C - Zustand

**Rationale**:
- You mentioned Zustand specifically
- Perfect for this use case (UI state, preferences, drafts)
- Tiny bundle size
- Simple API (low learning curve)
- Works perfectly with App Router
- TypeScript friendly
- Growing adoption in community

**What goes in Zustand**:
- UI state (sidebar open/closed, theme)
- User preferences (default view, filters)
- Form drafts (unsaved ADR edits)
- Navigation state

**What doesn't**:
- Server data (use React Query for that)
- URL state (use Next.js router)
- Form state during editing (use React Hook Form)

### Success Criteria
1. ✅ Global UI state accessible from any component
2. ✅ No prop drilling
3. ✅ Bundle size impact < 2KB
4. ✅ Works with Server and Client Components
5. ✅ Easy to debug

### Metrics
**Quantitative**:
- Bundle size for state management: < 2KB
- Re-renders: Only components using specific state slice

**Qualitative**:
- "Easy to add new state"
- "No prop drilling"

### Triggers to Revisit

1. **Complexity Growth**
   - Need middleware not available
   - State patterns becoming complex
   - Performance issues

2. **Bundle Size**
   - Total bundle too large
   - Need even smaller solution

3. **Team Feedback**
   - Developers want Redux
   - Confusion about patterns

### Risks of Decision

1. **Limited Ecosystem**
   - Risk: Need features not in Zustand
   - Mitigation: Easy to add or switch later
   - Severity: Low

### Migration Cost
**To Context**: Very Low (remove library)
**To Redux**: Low-Medium (similar patterns)
**Rollback**: Very Low

---

## P4.2.2. Server State Management (React Query vs Alternatives)

### Problem Statement
How do we manage server state (ADRs from API) including caching, loading states, optimistic updates, and synchronization?

### Problem Stack
- **Parent**: P4.2 (State Management)
- **Siblings**: P4.2.1 (Global State)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Determines data fetching patterns
- Affects caching strategy
- Influences loading/error states
- Impacts optimistic updates
- Determines stale data handling

**Risks of Not Solving:**
- Manual cache management
- Inconsistent loading states
- No automatic refetching
- Complex error handling
- Stale data shown to users

### Options

#### Option A: SWR
```typescript
const { data, error, mutate } = useSWR('/api/adrs', fetcher)
```

**Pros**:
- Simple API
- Built by Vercel (Next.js team)
- Good Next.js integration
- Small bundle
- Focus on "stale-while-revalidate"

**Cons**:
- Less features than React Query
- Simpler (which can be limiting)
- Smaller ecosystem

#### Option B: React Query (TanStack Query) ⭐ CHOSEN
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['adr', id],
  queryFn: () => adrClient.getADR({ id }),
})

const mutation = useMutation({
  mutationFn: (adr) => adrClient.createADR(adr),
  onSuccess: () => {
    queryClient.invalidateQueries(['adrs'])
  },
})
```

**Pros**:
- Industry standard for server state
- Excellent DevTools
- Powerful caching strategies
- Optimistic updates built-in
- Automatic refetching
- Request deduplication
- Pagination and infinite queries
- Works great with gRPC

**Cons**:
- Larger bundle than SWR
- More concepts to learn
- Can be overkill for simple apps

**Trade-offs**: Features vs simplicity

#### Option C: Next.js Server Components + fetch
**Description**: Use React Server Components with built-in fetch caching.

**Pros**:
- Built-in to Next.js
- No client-side library
- SSR by default
- Automatic request deduplication

**Cons**:
- Server Components only (no client state)
- Can't do optimistic updates easily
- Less control over caching
- No DevTools

#### Option D: Combination (RSC + React Query) ⭐ BEST APPROACH
**Description**: Use Server Components for initial data, React Query for client-side interactions.

**Pros**:
- SSR benefits (fast initial load)
- Client interactivity (mutations, optimistic updates)
- Best of both worlds

**Cons**:
- Need to understand both patterns
- Slightly more complexity

### Decision
**Chosen**: Option D - Combination (Server Components + React Query)

**Rationale**:
- Leverage Server Components for initial SSR
- Use React Query for client-side mutations and real-time updates
- React Query excellent for gRPC (handles streaming, etc.)
- DevTools help with debugging
- Optimistic updates important for editor UX
- Industry-proven pattern

**Usage Pattern**:
```typescript
// Server Component - initial data (SSR)
// app/adrs/[id]/page.tsx
async function ADRPage({ params }) {
  const adr = await adrClient.getADR({ id: params.id });
  return <ADRView initialData={adr} />;
}

// Client Component - mutations and real-time updates
// components/ADRView.tsx
'use client';
function ADRView({ initialData }) {
  const { data } = useQuery({
    queryKey: ['adr', initialData.id],
    queryFn: () => adrClient.getADR({ id: initialData.id }),
    initialData,  // Use SSR data initially
  });
  
  const mutation = useMutation({
    mutationFn: adrClient.updateADR,
    // Optimistic updates for snappy UX
  });
}
```

### Success Criteria
1. ✅ Server Components provide fast initial load (SSR)
2. ✅ React Query handles mutations and optimistic updates
3. ✅ Proper loading and error states
4. ✅ Cache invalidation works correctly
5. ✅ DevTools help debugging

### Metrics
**Quantitative**:
- Time to first byte: < 200ms (SSR)
- Time to interactive: < 1s
- Cache hit rate: > 80%

**Qualitative**:
- "Data fetching is seamless"
- "Optimistic updates feel snappy"
- "Error states are clear"

### Triggers to Revisit

1. **Complexity Overhead**
   - Two patterns confusing
   - Cache invalidation issues
   - SSR and client state out of sync

2. **Bundle Size**
   - React Query too large
   - Need simpler solution

3. **Performance Issues**
   - SSR too slow
   - Client-side fetching better
   - Cache causing issues

### Risks of Decision

1. **Learning Two Patterns**
   - Risk: Team struggles with Server Components + React Query
   - Mitigation: Clear patterns, documentation, examples
   - Severity: Medium

2. **Cache Coordination**
   - Risk: SSR cache and React Query cache out of sync
   - Mitigation: Use initialData pattern, proper invalidation
   - Severity: Low-Medium

### Migration Cost
**To SWR**: Low-Medium (similar API)
**To Server Components Only**: Low (remove React Query)
**Rollback**: Low

---

## Summary: Key Architectural Decisions

| Area | Decision | Rationale | Risk Level |
|------|----------|-----------|----------|
| **Overall Architecture** | Hexagonal (Ports & Adapters) | SDK reusable by CLI and service, storage abstraction | Low |
| **SDK Structure** | Layered crates (domain/sdk/adapters/apps) | Clear separation, opt-in adapters | Low |
| **Repository Pattern** | Domain-specific trait methods | Expressive, type-safe, testable | Low |
| **API Protocol** | gRPC + protobuf | Type safety, already have schema, efficient | Medium |
| **Frontend Framework** | Next.js App Router | Future-proof, Server Components, SSR | Low-Medium |
| **Global State** | Zustand | Lightweight, simple, works with App Router | Low |
| **Server State** | Server Components + React Query | SSR + client mutations, best of both | Medium |

## Next Steps

Before implementing:
1. ✅ Validate gRPC works well between Rust and Next.js (prototype)
2. ✅ Confirm grpc-web or REST gateway approach
3. ✅ Verify Zustand + React Query + App Router compatibility
4. ✅ Test protobuf code generation for TypeScript
5. ✅ Plan storage adapter implementation order (filesystem first)

---

*This architecture supports: CLI tool, web service, Next.js frontend, multiple storage backends, future extensibility.*
