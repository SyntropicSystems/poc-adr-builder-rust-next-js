# Architecture Overview

**ADR Editor PoC** - System Architecture Documentation

---

## 🎯 Purpose

This document describes the high-level architecture of the ADR Editor PoC. It explains:
- Overall system structure
- Component relationships
- Key design patterns
- Integration points

For **why** these decisions were made, see [ADRs](../adr/).

---

## 📐 Architecture Pattern

### Hexagonal Architecture (Ports & Adapters)

We use hexagonal architecture to achieve:
- **Testability**: Business logic tests without infrastructure
- **Flexibility**: Swap storage backends without changing core logic
- **Clarity**: Clear boundaries between domain, application, and infrastructure

```
┌────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                         │
│  (Inbound Adapters - How users interact)                   │
├──────────────────────┬─────────────────────────────────────┤
│                      │                                      │
│   Next.js Frontend   │          CLI Tool                   │
│   (React)            │          (Rust Binary)              │
│                      │                                      │
│   - Server Comp.     │   - clap commands                   │
│   - Client Comp.     │   - Direct SDK use                  │
│   - gRPC client      │                                      │
│                      │                                      │
└──────────┬───────────┴──────────┬──────────────────────────┘
           │ gRPC                 │ In-process
           │                      │
┌──────────▼──────────────────────▼──────────────────────────┐
│              APPLICATION LAYER                              │
│           (Inbound Ports - Service API)                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         adr-service (gRPC Server)                   │   │
│  │  - Implements ADRService (from .proto)              │   │
│  │  - Maps gRPC requests to use cases                  │   │
│  │  - Handles auth, validation, errors                 │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    DOMAIN CORE                              │
│            (The heart of the system)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  adr-domain (Pure Domain)                            │  │
│  │  - ADR entity                                        │  │
│  │  - Value objects (Problem, Decision, Option)        │  │
│  │  - Domain validation rules                          │  │
│  │  - NO infrastructure dependencies                   │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                        │                                    │
│  ┌─────────────────────▼────────────────────────────────┐  │
│  │  adr-sdk (Application Logic)                         │  │
│  │  - Use cases (CreateADR, UpdateADR, QueryADRs)      │  │
│  │  - Outbound ports (ADRRepository trait)             │  │
│  │  - Business rules orchestration                     │  │
│  │  - Depends ONLY on adr-domain                       │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
       ┌─────────────────┴─────────────────┐
       │     Outbound Port                 │
       │  (ADRRepository trait)             │
       └─────────────────┬─────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                           │
│          (Outbound Adapters - External systems)             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  adr-adapters                                        │  │
│  │  - FilesystemAdapter (impl ADRRepository)           │  │
│  │  - PostgresAdapter (future)                         │  │
│  │  - DynamoDBAdapter (future)                         │  │
│  │  Each implements same trait → swappable             │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                 ┌────────▼────────┐
                 │    Storage      │
                 │  (Filesystem,   │
                 │   Database,     │
                 │   etc.)         │
                 └─────────────────┘
```

### Key Insights

**1. SDK is Shared**
```
adr-cli  ──┐
           ├──> adr-sdk (shared code!)
adr-service┘
```
Both CLI and service use the SAME business logic. This validates hexagonal architecture works.

**2. Dependencies Point Inward**
```
Infrastructure → Application → Domain
     (adapters)      (SDK)    (entities)
```
Domain has ZERO dependencies. Infrastructure depends on everything. Clean dependency flow.

**3. Swappable Adapters**
```rust
// Configuration determines adapter
match config.storage {
    Storage::Filesystem => FilesystemAdapter::new(),
    Storage::Postgres => PostgresAdapter::new(),
    // Just swap one line to change storage!
}
```

---

## 🏗️ Component Breakdown

### Crate Structure

```
crates/
├── adr-domain/      # Layer 1: Pure Domain
├── adr-sdk/         # Layer 2: Application Logic
├── adr-adapters/    # Layer 3: Infrastructure
├── adr-service/     # Inbound Adapter (gRPC)
└── adr-cli/         # Inbound Adapter (CLI)
```

### adr-domain (Pure Domain)

**Purpose**: Core business entities and rules

**Contents**:
- `ADR` entity (id, title, status, problem, decision, etc.)
- Value objects (`ProblemStatement`, `Decision`, `Option`)
- Domain validation (title length, status transitions)
- Enums (`ADRStatus`: Proposed, Accepted, Rejected, Superseded)

**Dependencies**: NONE (pure Rust)

**Key Rule**: No infrastructure code allowed here!

```rust
// Example: Pure domain entity
pub struct ADR {
    pub id: String,
    pub title: String,
    pub status: ADRStatus,
    pub problem: ProblemStatement,
    pub options: Vec<Option>,
    pub decision: Decision,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl ADR {
    pub fn validate(&self) -> Result<(), ValidationError> {
        // Domain validation rules
        if self.title.is_empty() || self.title.len() > 200 {
            return Err(ValidationError::InvalidTitle);
        }
        Ok(())
    }
}
```

### adr-sdk (Application Logic)

**Purpose**: Use cases and repository port

**Contents**:
- **Outbound Port**: `ADRRepository` trait (defines what storage must provide)
- **Use Cases**: Business logic orchestration
  - `CreateADR`: Validates input, generates ID, saves
  - `UpdateADR`: Loads, validates changes, saves
  - `QueryADRs`: Searches and filters
  - `DeleteADR`: Marks as archived
- Error types (`ADRError`)

**Dependencies**: `adr-domain` only

**Key Insight**: This is the SHARED code between CLI and service!

```rust
// Example: Repository port (trait)
#[async_trait]
pub trait ADRRepository: Send + Sync {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError>;
    async fn find_by_status(&self, status: ADRStatus) -> Result<Vec<ADR>, ADRError>;
    async fn list_all(&self) -> Result<Vec<ADR>, ADRError>;
    async fn delete(&self, id: &str) -> Result<(), ADRError>;
}

// Example: Use case
pub struct CreateADRUseCase<R: ADRRepository> {
    repository: Arc<R>,
}

impl<R: ADRRepository> CreateADRUseCase<R> {
    pub async fn execute(&self, input: CreateADRInput) -> Result<ADR, ADRError> {
        // 1. Validate input (domain rule)
        let adr = ADR::new(input.title, input.description)?;
        
        // 2. Save via repository (port)
        self.repository.save(&adr).await?;
        
        // 3. Return created ADR
        Ok(adr)
    }
}
```

### adr-adapters (Infrastructure)

**Purpose**: Storage implementations

**Contents**:
- `FilesystemAdapter`: Saves ADRs as JSON files
- `PostgresAdapter`: (Future) Saves to PostgreSQL
- `DynamoDBAdapter`: (Future) Saves to AWS DynamoDB
- Each implements `ADRRepository` trait

**Dependencies**: `adr-sdk`, `adr-domain`, infrastructure crates

**Feature Flags**: Each adapter behind feature flag
```toml
[features]
filesystem = []
postgres = ["sqlx", "tokio-postgres"]
dynamodb = ["aws-sdk-dynamodb"]
```

```rust
// Example: Filesystem adapter implementation
pub struct FilesystemAdapter {
    base_path: PathBuf,
}

#[async_trait]
impl ADRRepository for FilesystemAdapter {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError> {
        let path = self.base_path.join(format!("{}.json", adr.id));
        let json = serde_json::to_string_pretty(adr)?;
        tokio::fs::write(path, json).await?;
        Ok(())
    }
    
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError> {
        let path = self.base_path.join(format!("{}.json", id));
        match tokio::fs::read_to_string(path).await {
            Ok(json) => Ok(Some(serde_json::from_str(&json)?)),
            Err(_) => Ok(None),
        }
    }
    
    // ... other methods
}
```

### adr-service (gRPC Service)

**Purpose**: Web service exposing gRPC API

**Contents**:
- gRPC server (tonic)
- Service implementation (maps gRPC → SDK)
- Configuration (adapter selection)
- Middleware (auth, logging, errors)

**Dependencies**: `adr-sdk`, `adr-adapters`, `tonic`, `prost`

**Key Insight**: Uses same SDK as CLI!

```rust
// Example: gRPC service implementation
pub struct ADRServiceImpl {
    repository: Arc<dyn ADRRepository>,
}

#[tonic::async_trait]
impl adr_service_server::AdrService for ADRServiceImpl {
    async fn create_adr(
        &self,
        request: Request<CreateAdrRequest>,
    ) -> Result<Response<Adr>, Status> {
        let req = request.into_inner();
        
        // Use SDK use case (same as CLI!)
        let use_case = CreateADRUseCase::new(self.repository.clone());
        let adr = use_case
            .execute(CreateADRInput {
                title: req.title,
                description: req.description,
            })
            .await
            .map_err(|e| Status::internal(e.to_string()))?;
        
        Ok(Response::new(adr.into()))
    }
}
```

### adr-cli (CLI Tool)

**Purpose**: Command-line interface

**Contents**:
- CLI parsing (clap)
- Commands (create, list, get, update, delete)
- Direct SDK usage (in-process)

**Dependencies**: `adr-sdk`, `adr-adapters`, `clap`

**Key Insight**: Uses same SDK as service!

```rust
// Example: CLI command
#[derive(Parser)]
enum Commands {
    Create {
        #[arg(short, long)]
        title: String,
        
        #[arg(short, long)]
        description: String,
    },
    // ... other commands
}

async fn handle_create(title: String, description: String) -> Result<()> {
    // Use same adapter as service
    let repository = Arc::new(FilesystemAdapter::new("./adrs")?);
    
    // Use same use case as service!
    let use_case = CreateADRUseCase::new(repository);
    let adr = use_case
        .execute(CreateADRInput { title, description })
        .await?;
    
    println!("Created ADR: {}", adr.id);
    Ok(())
}
```

---

## 🔌 Integration Points

### gRPC API

**Protocol**: Protocol Buffers (`.proto` files)
**Transport**: HTTP/2
**Location**: `proto/adr/v1/adr.proto`

**Why gRPC**:
- Type-safe across languages (Rust ↔ TypeScript)
- Efficient binary protocol
- Streaming support (future)
- Code generation (single source of truth)

**Service Definition**:
```protobuf
service ADRService {
  rpc CreateADR(CreateADRRequest) returns (ADR);
  rpc GetADR(GetADRRequest) returns (ADR);
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc UpdateADR(UpdateADRRequest) returns (ADR);
  rpc DeleteADR(DeleteADRRequest) returns (google.protobuf.Empty);
}
```

### Next.js Frontend

**Stack**:
- Next.js 14+ (App Router)
- Server Components (SSR from gRPC)
- Client Components (interactive, mutations)
- Zustand (global UI state)
- React Query (server state + caching)

**Data Flow**:
```
User Action
    ↓
React Component (Client)
    ↓
React Query mutation
    ↓
gRPC client (grpc-web)
    ↓
Rust Service (gRPC)
    ↓
SDK Use Case
    ↓
Repository (Storage)
    ↓
Response ← ← ← ← ←
    ↓
React Query cache update
    ↓
UI re-renders
```

---

## 🚀 Deployment View

### Development
```
┌─────────────────┐   ┌──────────────────┐
│  Next.js Dev    │   │  Rust Service    │
│  localhost:3000 │──▶│  localhost:50051 │
└─────────────────┘   └──────────┬───────┘
                                 │
                      ┌──────────▼────────┐
                      │  Filesystem       │
                      │  ./adrs/*.json    │
                      └───────────────────┘
```

### PoC Deployment (Simple)
```
┌──────────────┐
│   Docker     │
│  Container   │
│              │
│ ┌──────────┐ │
│ │ Next.js  │ │
│ │ (static) │ │
│ └────┬─────┘ │
│      │       │
│ ┌────▼─────┐ │
│ │  Service │ │
│ │  (Rust)  │ │
│ └────┬─────┘ │
│      │       │
│ ┌────▼─────┐ │
│ │   Data   │ │
│ │ (volume) │ │
│ └──────────┘ │
└──────────────┘
```

---

## 📊 Data Flow Examples

### Example 1: Create ADR via Web UI

```
1. User fills form in Next.js
   Component: <CreateADRForm /> (client component)
   ↓
2. Form submits → React Query mutation
   useMutation({ mutationFn: createADR })
   ↓
3. gRPC request (grpc-web)
   CreateADRRequest { title, description }
   ↓
4. Rust Service receives request
   ADRServiceImpl::create_adr()
   ↓
5. Service → SDK Use Case
   CreateADRUseCase::execute()
   ↓
6. Use Case → Repository
   repository.save(&adr)
   ↓
7. Adapter saves to storage
   FilesystemAdapter writes JSON
   ↓
8. Response bubbles back ← ← ← ←
   ADR returned with ID
   ↓
9. React Query updates cache
   queryClient.setQueryData(['adrs'])
   ↓
10. UI updates (shows new ADR)
```

### Example 2: Create ADR via CLI

```
1. User runs command
   $ adr-cli create --title "Use GraphQL"
   ↓
2. CLI parses arguments
   clap → Commands::Create { title }
   ↓
3. CLI → SDK Use Case (DIRECT)
   CreateADRUseCase::execute()
   ↓
4. Use Case → Repository
   repository.save(&adr)
   ↓
5. Adapter saves to storage
   FilesystemAdapter writes JSON
   ↓
6. Response ← ← ←
   ADR returned
   ↓
7. CLI prints success
   "Created ADR-001: Use GraphQL"
```

**Key**: Steps 3-6 are IDENTICAL for CLI and service!

---

## 🎯 Validation Goals

This architecture validates:

✅ **SDK Reusability**: CLI and service share 80%+ code
✅ **Storage Abstraction**: Can swap backends by changing config
✅ **Clean Boundaries**: Compiler enforces layer separation
✅ **Testability**: Can test use cases without infrastructure
✅ **gRPC Integration**: Rust ↔ Next.js communication works
✅ **Type Safety**: Protobuf ensures type consistency

---

## 🔗 Related Documentation

- **Why Hexagonal**: [ADR 0001](../adr/0001-use-hexagonal-architecture.md)
- **Technology Choices**: [Technology Stack](./TECHNOLOGY_STACK.md)
- **Migration Strategy**: [Migration Guide](./MIGRATION.md)
- **API Details**: [gRPC API](../api/GRPC.md)

---

**Next**: See [Technology Stack](./TECHNOLOGY_STACK.md) for specific technology choices and rationale.
