# Technology Stack

**ADR Editor PoC** - Technology Choices and Rationale

---

## 🎯 Overview

This document explains our technology choices, alternatives considered, and the reasoning behind each decision.

**Key Principle**: Choose proven, stable technologies that support our validation goals without over-engineering.

---

## 🦀 Backend: Rust

### Choice: Rust 1.75+

**Why Rust**:
- ✅ **Type Safety**: Compiler prevents entire classes of bugs
- ✅ **Performance**: Zero-cost abstractions, no GC pauses
- ✅ **Async/Await**: First-class async support via Tokio
- ✅ **Ecosystem**: Mature crates for gRPC, serialization, CLI
- ✅ **Learning Goal**: Team wants Rust experience
- ✅ **Monorepo Fit**: Bazel has excellent Rust support

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **Go** | Simple, fast compilation | Less type safety, GC pauses | Rust better for learning & safety |
| **TypeScript/Node** | Unified language with frontend | Runtime errors, memory usage | Need strong typing for backend |
| **Python** | Fast development | Slow, not suitable for services | Great for scripts, not services |

**Trade-offs Accepted**:
- ⚠️ Longer compilation times (mitigated by incremental builds)
- ⚠️ Steeper learning curve (acceptable - learning goal)
- ⚠️ Smaller talent pool (acceptable for PoC)

---

## 🌐 Frontend: Next.js 14+

### Choice: Next.js with App Router

**Why Next.js**:
- ✅ **Server Components**: Fetch from gRPC in RSC (zero client JS)
- ✅ **Client Components**: Interactive UI when needed
- ✅ **File-based Routing**: Simple, intuitive structure
- ✅ **TypeScript**: Type-safe frontend to match Rust backend
- ✅ **Production Ready**: Vercel's backing, active ecosystem
- ✅ **Hybrid Rendering**: SSR + CSR flexibility

**Why App Router** (over Pages Router):
- ✅ Modern React (React 18+ features)
- ✅ Streaming and suspense built-in
- ✅ Better data fetching patterns
- ✅ Layouts and nested routes
- ✅ Future-proof (Pages Router in maintenance mode)

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **Remix** | Great data loading, progressiv

e | Less mature than Next.js | Next.js more established |
| **SvelteKit** | Simpler, less boilerplate | Smaller ecosystem | Team knows React better |
| **Vanilla React** | Maximum control | Need to build SSR ourselves | Next.js saves time |

**Trade-offs Accepted**:
- ⚠️ Opinionated framework (mitigated by clear patterns)
- ⚠️ Vercel-centric (acceptable - not vendor locked)

---

## 🔌 API: gRPC + Protocol Buffers

### Choice: gRPC with tonic (Rust) + grpc-web (Browser)

**Why gRPC**:
- ✅ **Type Safety**: Single source of truth (.proto files)
- ✅ **Code Generation**: Types for Rust AND TypeScript
- ✅ **Efficiency**: Binary protocol, smaller payloads
- ✅ **Streaming**: Built-in support (future use)
- ✅ **Multi-Language**: Proven in polyglot systems
- ✅ **Validation Goal**: Want to prove cross-language RPC

**Why Protocol Buffers**:
- ✅ Language-agnostic schema
- ✅ Backward compatibility built-in
- ✅ Faster than JSON
- ✅ Industry standard (Google, Netflix, etc.)

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **REST + JSON** | Ubiquitous, simple | Manual typing, versioning hard | Lose type safety |
| **GraphQL** | Flexible queries, single endpoint | Complex, overkill for CRUD | Too heavy for PoC |
| **tRPC** | TypeScript-first, simple | Requires Node backend | We use Rust |

**Trade-offs Accepted**:
- ⚠️ Browser needs grpc-web proxy (mitigated by tonic-web)
- ⚠️ Tooling less mature than REST (acceptable - learning goal)
- ⚠️ Debugging harder than JSON (mitigated by grpcurl)

---

## 📦 Package Management

### Primary: Cargo (Rust)

**Why Cargo**:
- ✅ Built into Rust ecosystem
- ✅ Excellent dependency management
- ✅ Workspaces support
- ✅ Fast incremental builds
- ✅ Integrated testing

**No Alternatives**: Cargo is the only real option for Rust.

### Secondary: pnpm (Node.js)

**Why pnpm**:
- ✅ **Disk Efficient**: Content-addressed storage (saves GBs)
- ✅ **Fast**: Faster than npm/yarn
- ✅ **Strict**: No phantom dependencies
- ✅ **Workspace Support**: Monorepo-ready
- ✅ **Modern**: Active development, v9+ stable

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **npm** | Default, universal | Slow, wastes disk space | pnpm strictly better |
| **yarn** | Workspaces, deterministic | Slower than pnpm | pnpm more efficient |
| **bun** | Extremely fast | Too new, unstable | Not mature enough |

**Trade-offs Accepted**:
- ⚠️ Less universal than npm (mitigated by wide adoption)
- ⚠️ Team needs to install pnpm (one-time setup)

---

## 🛠️ Build System: Cargo + Bazel (Learning)

### Primary: Cargo

**Why Cargo**: See above - it's the Rust build tool.

### Learning: Bazel

**Why Bazel**:
- ✅ **Monorepo Focus**: Designed for large, multi-language repos
- ✅ **Caching**: Incremental builds, remote caching
- ✅ **Reproducibility**: Hermetic builds
- ✅ **Multi-Language**: Rust + TypeScript + Python + more
- ✅ **Learning Goal**: Will use in monorepo

**Why Minimal Bazel in PoC**:
- ⚠️ Complex setup (don't want to slow down PoC)
- ⚠️ Cargo sufficient for development
- ✅ Just validate structure works with Bazel
- ✅ Learn basics, not advanced features

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **Buck2** | Fast, modern | Less mature, Facebook-centric | Bazel more established |
| **Pants** | Python-friendly | Smaller community | Bazel more universal |
| **Just Cargo** | Simple, no learning curve | Can't test monorepo patterns | Need Bazel learning |

**Trade-offs Accepted**:
- ⚠️ Maintain two build systems temporarily (acceptable for learning)
- ⚠️ Bazel complexity (mitigated by minimal usage)

---

## 🗃️ Storage: Repository Pattern with Adapters

### PoC: Filesystem

**Why Filesystem for PoC**:
- ✅ Zero setup required
- ✅ Easy to inspect (just JSON files)
- ✅ Sufficient to validate architecture
- ✅ Fast development

**Future: Multiple Backends**

| Backend | Use Case | Status |
|---------|----------|--------|
| **Filesystem** | Development, demos | ✅ PoC |
| **PostgreSQL** | Production, relational data | 🔄 Future |
| **DynamoDB** | Serverless, high scale | 🔄 Future |

**Why Repository Pattern**:
- ✅ Swappable implementations
- ✅ Testable (mock repository)
- ✅ Clean architecture boundary
- ✅ Validates hexagonal pattern

---

## 🎨 State Management: Zustand + React Query

### Choice: Zustand (Global) + React Query (Server)

**Why Zustand**:
- ✅ **Tiny**: ~1KB, minimal overhead
- ✅ **Simple**: No boilerplate, just hooks
- ✅ **Flexible**: Use as much or little as needed
- ✅ **TypeScript**: Excellent TS support
- ✅ **DevTools**: Redux DevTools integration

**Why React Query** (TanStack Query):
- ✅ **Server State**: Purpose-built for server data
- ✅ **Caching**: Intelligent cache management
- ✅ **Mutations**: Optimistic updates, rollback
- ✅ **DevTools**: Built-in inspector
- ✅ **Suspense**: Works with React Suspense

**State Division**:
```
Global UI State → Zustand
(theme, modals, navigation)

Server State → React Query
(ADRs, API data, mutations)
```

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **Redux Toolkit** | Powerful, established | Heavy, boilerplate | Overkill for PoC |
| **Jotai/Recoil** | Atomic state | More complex than Zustand | Zustand simpler |
| **Just useState** | Simple | Prop drilling, no caching | Need better solution |

**Trade-offs Accepted**:
- ⚠️ Two state libraries (mitigated by clear separation)
- ⚠️ Learning curve (minimal - both are simple)

---

## 🐍 Utilities: Python 3.14

### Choice: Python for Automation Scripts

**Why Python**:
- ✅ **Scripting**: Excellent for one-off scripts
- ✅ **Libraries**: Rich ecosystem (toml, markdown, etc.)
- ✅ **Readability**: Easy to understand and maintain
- ✅ **Cross-Platform**: Works everywhere
- ✅ **Version 3.14**: Latest stable features

**Use Cases**:
- Documentation validation
- Protobuf → Markdown generation
- Build automation helpers
- NOT part of core system

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| **Bash** | Universal | Hard to maintain, error-prone | Python more robust |
| **Node.js** | Already have Node | Would confuse role of Node | Keep Node for frontend only |
| **Rust** | Type-safe scripts | Overkill for simple scripts | Too heavy |

---

## 🧪 Testing Strategy

### Rust: Built-in + Tokio Test

**Why Built-in**:
- ✅ No additional dependencies
- ✅ Fast execution
- ✅ Integrated with Cargo
- ✅ `#[tokio::test]` for async

### TypeScript: Vitest

**Why Vitest** (when we add tests):
- ✅ Fast (Vite-powered)
- ✅ Jest-compatible API
- ✅ ES modules native
- ✅ TypeScript out-of-box

### Integration: Manual (PoC)

**Why Manual**:
- ✅ Simple for PoC
- ✅ No complex test infrastructure
- ✅ Can add proper E2E later (Playwright, Cypress)

---

## 🔧 Development Tools

### Required

| Tool | Version | Purpose |
|------|---------|---------|
| **Rust** | 1.75+ | Backend/CLI development |
| **Node** | v24 | Frontend development |
| **pnpm** | 9.0+ | Frontend package management |
| **Python** | 3.14+ | Utility scripts |

### Optional

| Tool | Purpose |
|------|---------|
| **Bazel** | Build validation |
| **grpcurl** | gRPC testing |
| **protoc** | Protobuf compilation |

### IDE Recommendations

| IDE | Rust | TypeScript | Both |
|-----|------|------------|------|
| **VS Code** | ✅ rust-analyzer | ✅ Built-in | ✅ Best choice |
| **RustRover** | ✅ Native | ⚠️ Basic | Good for Rust-first |
| **WebStorm** | ⚠️ Basic | ✅ Excellent | Good for TS-first |

---

## 📊 Technology Decision Matrix

### Must Validate in PoC

| Technology | Reason | Status |
|-----------|--------|--------|
| **Hexagonal Arch** | Core pattern | 🎯 Validating |
| **Rust + Next.js** | Language choices | 🎯 Validating |
| **gRPC Cross-Lang** | API integration | 🎯 Validating |
| **Repository Pattern** | Storage abstraction | 🎯 Validating |
| **App Router** | Modern React patterns | 🎯 Validating |

### Can Defer to Production

| Technology | Reason | When |
|-----------|--------|------|
| **PostgreSQL** | Database choice | After PoC proves pattern |
| **Redis** | Caching | If needed in production |
| **Kubernetes** | Orchestration | Production deployment |
| **Observability** | Monitoring | Production operations |

---

## 🎯 Success Criteria

This technology stack succeeds if:

✅ **Rust ↔ TypeScript** communication works (gRPC)
✅ **SDK reusability** validated (CLI + service share code)
✅ **Repository pattern** proves swappable
✅ **App Router** integrates cleanly with gRPC
✅ **Bazel structure** validates (even if unused daily)
✅ **Migration to monorepo** remains low-cost

---

## 🔗 Related Documentation

- **Why Hexagonal**: [ADR 0001](../adr/0001-use-hexagonal-architecture.md)
- **Why gRPC**: [ADR 0002](../adr/0002-use-grpc-for-api.md)
- **Architecture Overview**: [OVERVIEW.md](./OVERVIEW.md)
- **Migration Strategy**: [MIGRATION.md](./MIGRATION.md)

---

**Remember**: We chose these technologies to validate architecture, not to build a production system. Focus on proving patterns work!
