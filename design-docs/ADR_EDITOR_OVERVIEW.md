# ADR Editor - Architecture Overview

## 🎯 Quick Summary

**Goal**: Build an ADR editor with Next.js frontend, Rust backend, supporting multiple storage backends (filesystem, Postgres, DynamoDB), with shared SDK for CLI and service.

**Core Architecture**: Hexagonal (Ports & Adapters) with SDK at center

---

## 📐 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
├─────────────────────────┬───────────────────────────────────────┤
│                         │                                       │
│  Next.js Frontend       │         CLI Tool                      │
│  (React + Zustand)      │         (Rust Binary)                 │
│                         │                                       │
│  ┌──────────────────┐   │   ┌──────────────────┐               │
│  │ Server Components│   │   │  clap Commands   │               │
│  │ (SSR)            │   │   │                  │               │
│  └────────┬─────────┘   │   └────────┬─────────┘               │
│           │             │            │                          │
│  ┌────────┴─────────┐   │   ┌────────┴─────────┐               │
│  │ Client Components│   │   │  SDK Integration │               │
│  │ + React Query    │   │   │                  │               │
│  └────────┬─────────┘   │   └────────┬─────────┘               │
│           │             │            │                          │
└───────────┼─────────────┴────────────┼──────────────────────────┘
            │                          │
            │ gRPC                     │ Direct
            │ (grpc-web)               │ (in-process)
            ▼                          │
┌───────────────────────────────────────┼──────────────────────────┐
│              RUST SERVICE             │                          │
│         ┌─────────────────────────────┘                          │
│         │                                                        │
│    ┌────┴────────────────────┐                                  │
│    │   API Layer (Inbound)   │                                  │
│    │   - gRPC Server (tonic) │                                  │
│    │   - REST Gateway (opt)  │                                  │
│    └────┬────────────────────┘                                  │
│         │                                                        │
│         ▼                                                        │
│    ┌────────────────────────────────────────┐                   │
│    │         DOMAIN CORE (SDK)              │                   │
│    │  ┌──────────────────────────────────┐  │                   │
│    │  │      adr-domain (pure)           │  │                   │
│    │  │  - ADR entities                  │  │                   │
│    │  │  - Value objects                 │  │                   │
│    │  │  - Domain logic                  │  │                   │
│    │  └──────────────┬───────────────────┘  │                   │
│    │                 │                       │                   │
│    │  ┌──────────────┴───────────────────┐  │                   │
│    │  │      adr-sdk (ports)             │  │                   │
│    │  │  - Repository trait              │  │                   │
│    │  │  - Use cases                     │  │                   │
│    │  │  - Business rules                │  │                   │
│    │  └──────────────┬───────────────────┘  │                   │
│    │                 │                       │                   │
│    └─────────────────┼───────────────────────┘                   │
│                      │                                           │
│         ┌────────────┴──────────────┐                            │
│         │  Outbound Ports           │                            │
│         │  (Repository Interface)   │                            │
│         └────────────┬──────────────┘                            │
│                      │                                           │
│         ┌────────────┴──────────────┐                            │
│         │   Adapter Selection       │                            │
│         │   (Dependency Injection)  │                            │
│         └────┬──────────────────────┘                            │
│              │                                                   │
└──────────────┼───────────────────────────────────────────────────┘
               │
    ┌──────────┼──────────────────────────────┐
    │          │     ADAPTERS (Outbound)      │
    │          │                               │
    │  ┌───────┴────────┐  ┌──────────────┐   │
    │  │  Filesystem    │  │  PostgreSQL  │   │
    │  │  Adapter       │  │  Adapter     │   │
    │  └───────┬────────┘  └──────┬───────┘   │
    │          │                  │            │
    │  ┌───────┴────────┐  ┌──────┴───────┐   │
    │  │  DynamoDB      │  │  Firebase    │   │
    │  │  Adapter       │  │  Adapter     │   │
    │  └───────┬────────┘  └──────┬───────┘   │
    │          │                  │            │
    └──────────┼──────────────────┼────────────┘
               │                  │
         ┌─────▼──────┐    ┌──────▼─────┐
         │ Filesystem │    │ Databases  │
         └────────────┘    └────────────┘
```

---

## 🏗️ Crate Structure

```
workspace/
├── adr-domain/              # Pure domain (no dependencies)
│   ├── src/
│   │   ├── lib.rs
│   │   ├── adr.rs          # ADR entity
│   │   ├── problem.rs      # ProblemStatement
│   │   ├── decision.rs     # Decision
│   │   └── validation.rs   # Domain validation
│   └── Cargo.toml
│
├── adr-sdk/                 # Ports + Use Cases
│   ├── src/
│   │   ├── lib.rs
│   │   ├── repository.rs   # trait ADRRepository
│   │   ├── use_cases/      # Business logic
│   │   │   ├── create_adr.rs
│   │   │   ├── update_adr.rs
│   │   │   └── query_adrs.rs
│   │   └── errors.rs       # Domain errors
│   └── Cargo.toml          # depends: adr-domain
│
├── adr-adapters/            # Adapter implementations
│   ├── src/
│   │   ├── lib.rs
│   │   ├── filesystem.rs   # [feature = "filesystem"]
│   │   ├── postgres.rs     # [feature = "postgres"]
│   │   ├── dynamodb.rs     # [feature = "dynamodb"]
│   │   └── firebase.rs     # [feature = "firebase"]
│   └── Cargo.toml          # depends: adr-sdk
│                           # features: filesystem, postgres, etc.
│
├── adr-cli/                 # CLI application
│   ├── src/
│   │   ├── main.rs
│   │   └── commands/       # CLI commands
│   └── Cargo.toml          # depends: adr-sdk, adr-adapters
│                           # features: filesystem (default)
│
├── adr-service/             # Web service
│   ├── src/
│   │   ├── main.rs
│   │   ├── grpc.rs         # gRPC server
│   │   └── rest.rs         # Optional REST gateway
│   └── Cargo.toml          # depends: adr-sdk, adr-adapters
│                           # features: filesystem, postgres
│
└── frontend/                # Next.js app
    ├── app/                 # App Router
    ├── components/          # React components
    ├── lib/
    │   ├── grpc/           # Generated gRPC client
    │   └── state/          # Zustand stores
    └── package.json
```

---

## 🔄 Data Flow Examples

### Example 1: Create ADR via Web UI

```
1. User fills form in Next.js
   ↓
2. React Component calls mutation
   (React Query + gRPC client)
   ↓
3. gRPC request → Rust Service
   ↓
4. Service → Use Case (adr-sdk)
   ↓
5. Use Case → Repository Port (trait)
   ↓
6. Adapter implements port (e.g., PostgresAdapter)
   ↓
7. Save to Postgres
   ↓
8. Return ADR ← ← ← ← ←
   ↓
9. React Query updates cache
   ↓
10. UI updates (optimistic or on success)
```

### Example 2: Create ADR via CLI

```
1. User runs: adr-cli create --title "..."
   ↓
2. CLI command → Use Case (adr-sdk)
   ↓
3. Use Case → Repository Port
   ↓
4. FilesystemAdapter (selected at compile time)
   ↓
5. Save to ./adrs/adr-001.json
   ↓
6. Return ADR ← ← ←
   ↓
7. CLI prints success message
```

**Key**: CLI and Service use SAME core logic, different adapters!

---

## 🎨 Technology Stack

### Backend (Rust)
- **Framework**: `axum` or `actix-web` (HTTP server)
- **gRPC**: `tonic` + `prost` (Protocol Buffers)
- **Async Runtime**: `tokio`
- **Database**:
  - Postgres: `sqlx` or `diesel`
  - DynamoDB: `aws-sdk-dynamodb`
  - Filesystem: `tokio::fs`
- **Serialization**: `serde`, `serde_json`, `prost`

### Frontend (Next.js)
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+
- **State Management**:
  - Global: `zustand` (~1KB)
  - Server: `@tanstack/react-query` (formerly React Query)
- **gRPC Client**: `@grpc/grpc-js` + `grpc-web` OR REST gateway
- **Forms**: `react-hook-form` + `zod`
- **UI Components**: `shadcn/ui` (optional) or custom

### API
- **Protocol**: gRPC (primary)
- **Schema**: Protocol Buffers (`.proto` files)
- **Gateway**: `tonic-web` or REST gateway for browser
- **Code Gen**:
  - Rust: `tonic-build`
  - TypeScript: `protoc-gen-ts` or similar

---

## 🔌 Adapter Pattern Details

### Repository Trait (Port)

```rust
// adr-sdk/src/repository.rs
#[async_trait]
pub trait ADRRepository: Send + Sync {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError>;
    async fn find_by_status(&self, status: ADRStatus) -> Result<Vec<ADR>, ADRError>;
    async fn list_all(&self) -> Result<Vec<ADR>, ADRError>;
    async fn delete(&self, id: &str) -> Result<(), ADRError>;
}
```

### Filesystem Adapter

```rust
// adr-adapters/src/filesystem.rs
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
    
    // ... other methods
}
```

### Postgres Adapter

```rust
// adr-adapters/src/postgres.rs
pub struct PostgresAdapter {
    pool: PgPool,
}

#[async_trait]
impl ADRRepository for PostgresAdapter {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError> {
        sqlx::query!(
            "INSERT INTO adrs (id, title, status, data) 
             VALUES ($1, $2, $3, $4)
             ON CONFLICT (id) DO UPDATE 
             SET title = $2, status = $3, data = $4",
            adr.id,
            adr.title,
            adr.status.to_string(),
            serde_json::to_value(adr)?
        )
        .execute(&self.pool)
        .await?;
        Ok(())
    }
    
    // ... other methods
}
```

**Key**: Both implement same trait, use case doesn't know which!

---

## 📡 API Protocol (gRPC)

### Protobuf Definition

```protobuf
// proto/adr.proto
syntax = "proto3";
package adr.v1;

service ADRService {
  rpc CreateADR(CreateADRRequest) returns (ADR);
  rpc GetADR(GetADRRequest) returns (ADR);
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc UpdateADR(UpdateADRRequest) returns (ADR);
  rpc DeleteADR(DeleteADRRequest) returns (google.protobuf.Empty);
  
  // Bonus: Streaming for real-time updates
  rpc WatchADRs(WatchADRsRequest) returns (stream ADREvent);
}

message ADR {
  string id = 1;
  string title = 2;
  string status = 3;
  ProblemStatement problem = 4;
  repeated Option options = 5;
  Decision decision = 6;
  // ... rest of fields
}
```

### Rust Server (tonic)

```rust
// adr-service/src/grpc.rs
#[tonic::async_trait]
impl adr_service_server::AdrService for ADRServiceImpl {
    async fn create_adr(
        &self,
        request: Request<CreateAdrRequest>,
    ) -> Result<Response<Adr>, Status> {
        let req = request.into_inner();
        
        // Use SDK (same code as CLI!)
        let use_case = CreateADRUseCase::new(self.repository.clone());
        let adr = use_case.execute(req.into()).await
            .map_err(|e| Status::internal(e.to_string()))?;
        
        Ok(Response::new(adr.into()))
    }
}
```

### TypeScript Client (Next.js)

```typescript
// Generated from protobuf
import { ADRServiceClient } from './generated/adr_grpc_web_pb';

const client = new ADRServiceClient('http://localhost:50051');

// Use in React Query
const { data } = useQuery({
  queryKey: ['adr', id],
  queryFn: async () => {
    const request = new GetADRRequest();
    request.setId(id);
    return client.getADR(request, {});
  },
});
```

**Benefits**:
- ✅ Types generated for Rust AND TypeScript
- ✅ Single source of truth (`.proto` files)
- ✅ No manual API client code
- ✅ Type safety across languages

---

## 🎯 Configuration & Dependency Injection

### Service Startup

```rust
// adr-service/src/main.rs
#[tokio::main]
async fn main() -> Result<()> {
    // Read config
    let config = Config::from_env()?;
    
    // Choose adapter based on config
    let repository: Arc<dyn ADRRepository> = match config.storage_backend {
        StorageBackend::Filesystem => {
            Arc::new(FilesystemAdapter::new(&config.filesystem_path)?)
        }
        StorageBackend::Postgres => {
            let pool = PgPool::connect(&config.database_url).await?;
            Arc::new(PostgresAdapter::new(pool))
        }
        StorageBackend::DynamoDB => {
            let client = aws_sdk_dynamodb::Client::new(&aws_config::load_from_env().await);
            Arc::new(DynamoDBAdapter::new(client, &config.dynamodb_table))
        }
    };
    
    // Start gRPC server
    let service = ADRServiceImpl::new(repository);
    Server::builder()
        .add_service(AdrServiceServer::new(service))
        .serve(addr)
        .await?;
    
    Ok(())
}
```

### CLI Configuration

```rust
// adr-cli/src/main.rs
fn main() -> Result<()> {
    // CLI always uses filesystem (for simplicity)
    let repository = FilesystemAdapter::new("./adrs")?;
    
    // Parse commands
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Create { title } => {
            let use_case = CreateADRUseCase::new(Arc::new(repository));
            let adr = use_case.execute(CreateADRInput { title, ... })?;
            println!("Created ADR: {}", adr.id);
        }
        // ... other commands
    }
    
    Ok(())
}
```

**Key**: Same use cases, different adapters wired at startup!

---

## 🎨 Frontend Architecture

### Server Component (SSR)

```tsx
// app/adrs/[id]/page.tsx
import { getADRClient } from '@/lib/grpc/client';

// Server Component - runs on server
export default async function ADRPage({ params }) {
  const client = getADRClient();
  const adr = await client.getADR({ id: params.id });
  
  return <ADRView initialData={adr} />;
}
```

### Client Component (Interactive)

```tsx
// components/ADRView.tsx
'use client';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useADRStore } from '@/lib/state/adr-store';

export function ADRView({ initialData }) {
  // Server state (React Query)
  const { data: adr } = useQuery({
    queryKey: ['adr', initialData.id],
    queryFn: () => adrClient.getADR({ id: initialData.id }),
    initialData, // Use SSR data
  });
  
  // Global UI state (Zustand)
  const { editMode, setEditMode } = useADRStore();
  
  // Mutations
  const updateMutation = useMutation({
    mutationFn: (updates) => adrClient.updateADR(updates),
    onSuccess: () => {
      queryClient.invalidateQueries(['adr', adr.id]);
    },
  });
  
  return (
    <div>
      {editMode ? (
        <ADREditor adr={adr} onSave={updateMutation.mutate} />
      ) : (
        <ADRDisplay adr={adr} />
      )}
    </div>
  );
}
```

### State Management Pattern

```typescript
// lib/state/adr-store.ts (Zustand)
import create from 'zustand';

export const useADRStore = create((set) => ({
  // UI state
  editMode: false,
  setEditMode: (mode) => set({ editMode: mode }),
  
  // User preferences
  theme: 'light',
  setTheme: (theme) => set({ theme }),
  
  // Draft storage (localStorage persistence)
  drafts: {},
  saveDraft: (id, content) => set((state) => ({
    drafts: { ...state.drafts, [id]: content }
  })),
}));
```

---

## 🚀 Development Workflow

### 1. Start with Protobuf Schema
```bash
# Define API in proto/adr.proto
protoc --rust_out=. --ts_out=frontend/lib/grpc proto/adr.proto
```

### 2. Implement Domain & SDK
```bash
cd adr-domain
cargo test  # Pure domain logic, fast tests
```

### 3. Implement Filesystem Adapter
```bash
cd adr-adapters
cargo test --features filesystem
```

### 4. Build CLI
```bash
cd adr-cli
cargo run -- create --title "Test ADR"
```

### 5. Build Service
```bash
cd adr-service
cargo run  # Starts on localhost:50051
```

### 6. Build Frontend
```bash
cd frontend
npm run dev  # Next.js on localhost:3000
```

---

## ✅ Implementation Checklist

### Phase 1: Core (Week 1-2)
- [ ] Define protobuf schema (extend existing adr.proto)
- [ ] Build adr-domain crate (pure entities)
- [ ] Build adr-sdk crate (ports + use cases)
- [ ] Build filesystem adapter
- [ ] Write comprehensive tests

### Phase 2: CLI (Week 2-3)
- [ ] Build CLI with clap
- [ ] Wire filesystem adapter
- [ ] Implement CRUD commands
- [ ] Add output formatting (JSON, YAML, table)

### Phase 3: Service (Week 3-4)
- [ ] Build gRPC server with tonic
- [ ] Wire filesystem adapter (start simple)
- [ ] Add configuration system
- [ ] Deploy container

### Phase 4: Frontend (Week 4-6)
- [ ] Set up Next.js App Router
- [ ] Generate gRPC client (or REST gateway)
- [ ] Build view components (Server Components)
- [ ] Build editor components (Client Components)
- [ ] Integrate Zustand + React Query
- [ ] Add forms with validation

### Phase 5: Database Adapters (Week 6+)
- [ ] Postgres adapter
- [ ] Schema migrations
- [ ] DynamoDB adapter (if needed)
- [ ] Multi-tenancy support

---

## 📊 Success Metrics

- **Code Reuse**: 80%+ of business logic shared between CLI and service
- **Test Coverage**: 90%+ on domain and SDK
- **Build Time**: < 2 minutes full workspace build
- **Adapter Addition**: < 1 day for new storage backend
- **API Type Safety**: 100% (generated from protobuf)
- **Bundle Size**: Frontend < 200KB initial load

---

## 🔗 Key Resources

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [tonic gRPC Guide](https://github.com/hyperium/tonic)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Zustand](https://github.com/pmndrs/zustand)
- [TanStack Query](https://tanstack.com/query/latest)

---

*This architecture supports: CLI, service, web UI, multiple storage backends, and future extensibility!*
