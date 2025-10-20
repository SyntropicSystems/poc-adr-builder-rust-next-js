# ADR Editor PoC - LLM Context Guide

**Last Updated**: 2025-10-20  
**Version**: 0.1.0  
**Status**: Documentation phase - Implementation starting

---

## 🎯 Quick Overview

**What**: ADR Editor Proof of Concept  
**Why**: Validate architectural decisions (hexagonal architecture, gRPC, multi-language) before monorepo migration  
**Goal**: Build a system that can be lifted into monorepo with minimal refactoring  
**Time Budget**: 16-24 Engineering Units (EU)

**Current Phase**: Documentation & Foundation Setup

---

## 📂 Documentation Map

### For Quick Context
- **This File**: Navigation and quick reference
- **README.md**: User-facing quick start and overview
- **Current Plan**: `.meta/task-service/project-management/IMPLEMENTATION_PLAN.md`

### Architecture (Source of Truth)
- **Overview**: `docs/architecture/OVERVIEW.md` - System architecture, components, diagrams
- **Tech Stack**: `docs/architecture/TECHNOLOGY_STACK.md` - Technology choices with rationale
- **Migration**: `docs/architecture/MIGRATION.md` - Monorepo migration strategy
- **Hexagonal Pattern**: `docs/architecture/HEXAGONAL.md` - Ports & Adapters implementation

### Architecture Decision Records (ADRs)
- **Index**: `docs/adr/README.md` - List of all finalized decisions
- **ADR 0001**: `docs/adr/0001-use-hexagonal-architecture.md` - Core architectural pattern
- **In Progress**: `.meta/task-service/design-docs/DECISIONS.md` - Problem-solution analysis (WIP)

### API & Protocols
- **gRPC**: `docs/api/GRPC.md` - Service contracts (generated from `.proto`)
- **Protobuf**: `proto/adr/v1/adr.proto` - **SOURCE OF TRUTH** for API

### Development
- **Setup**: `docs/development/SETUP.md` - Environment setup instructions
- **Workflow**: `docs/development/WORKFLOW.md` - Development process and commands
- **Contributing**: `docs/development/CONTRIBUTING.md` - How to contribute, PR checklist
- **Documentation**: `docs/development/DOCUMENTATION_GUIDE.md` - **How to keep docs in sync**

### Ephemeral (Work in Progress)
- **Design Docs**: `.meta/task-service/design-docs/` - Design explorations (not finalized)
- **Project Management**: `.meta/task-service/project-management/` - Current plans, sprint notes

---

## 🏗️ Project Structure

```
adr-editor-poc/
├── crates/              # Rust workspace (Hexagonal architecture)
│   ├── adr-domain/      # Pure domain entities (no infrastructure deps)
│   ├── adr-sdk/         # Ports + use cases (repository trait)
│   ├── adr-adapters/    # Storage implementations (filesystem, etc.)
│   ├── adr-service/     # gRPC service (uses SDK)
│   └── adr-cli/         # CLI tool (uses SDK - shared with service!)
│
├── apps/
│   └── adr-web/         # Next.js App Router frontend
│
├── proto/
│   └── adr/v1/          # Protobuf schemas (SOURCE OF TRUTH for API)
│
├── docs/                # Living documentation (source of truth)
│   ├── architecture/    # System architecture
│   ├── adr/            # Finalized architecture decisions
│   ├── development/    # Development guides
│   └── api/            # API documentation
│
├── .meta/              # Ephemeral working documents
│   └── task-service/
│       ├── design-docs/         # Design explorations
│       └── project-management/  # Current plans
│
└── scripts/            # Automation scripts
    ├── validate-docs.sh
    └── generate-api-docs.sh
```

---

## 🎨 Technology Stack

### Backend (Rust)
- **gRPC**: `tonic` + `prost` (Protocol Buffers)
- **Async**: `tokio`
- **CLI**: `clap`
- **Storage**: Repository pattern with adapters (starting with filesystem)

### Frontend (Next.js)
- **Framework**: Next.js 14+ with App Router
- **State**: `zustand` (global UI) + `@tanstack/react-query` (server state)
- **gRPC Client**: Generated from protobuf
- **Package Manager**: **pnpm** (not npm/yarn)
- **Node Version**: **v24** (see `.nvmrc`)

### Build System
- **Primary Development**: Cargo (Rust) + pnpm (Node.js)
- **Learning/Validation**: Bazel (minimal, for monorepo preparation)

---

## 📋 Current State

### Completed
- ✅ Documentation architecture defined
- ✅ Project configuration (pnpm, Node v24, Bazel workspace)
- ✅ llm.md created (this file)

### In Progress
- 🔄 Creating documentation files
- 🔄 Setting up repository structure

### Not Started
- ⏳ Phase 1: Foundation (Cargo workspace, protobuf, domain/SDK)
- ⏳ Phase 2: CLI Tool
- ⏳ Phase 3: gRPC Service
- ⏳ Phase 4: Next.js Frontend
- ⏳ Phase 5: Integration & Documentation

---

## 🧭 Documentation Principles for AI Agents

### Golden Rules

1. **Code is Truth** - When docs and code conflict, CODE WINS
2. **Read Code First** - Check actual implementation before consulting docs
3. **Minimize Documentation** - Only document what code can't express
4. **Validate Before Claiming Done** - Run tests to verify docs match code

### Source of Truth Hierarchy

```
1. CODE (HIGHEST AUTHORITY)
   ├─ Protobuf schemas (.proto files)
   ├─ Rust type definitions
   ├─ CLI command definitions (clap)
   └─ Test specifications

2. GENERATED DOCUMENTATION
   ├─ From protobuf → TypeScript + Rust types
   ├─ From clap → CLI help text
   └─ From tests → Examples in docs

3. WRITTEN DOCUMENTATION
   ├─ Architecture decisions (docs/adr/)
   ├─ System overview (docs/architecture/)
   └─ Development guides (docs/development/)
```

**Rule**: If (1) and (3) conflict, update (3) to match (1)

### When to Update Documentation

**✅ Always Update**:
- Changed `.proto` files → Run `pnpm docs:generate-api`
- Changed architecture → Update `docs/adr/` + `docs/architecture/`
- Changed development workflow → Update `docs/development/WORKFLOW.md`
- Added new ADR → Create file in `docs/adr/` + update index

**❌ Never Update** (Self-Documenting):
- Added function → Clear name + types are enough
- Modified use case → Code should be self-explanatory
- Added CLI command → `clap` auto-generates help
- Changed implementation → Good names + comments suffice

**Before Claiming "Documentation Updated"**:
1. Run `cargo test doc_validation` (when tests exist)
2. Run `pnpm docs:validate` (validates docs are current)
3. Check that examples in docs actually execute
4. Verify architecture diagrams match current structure

### Finding Information

| Need to Know | Check First | Then Check |
|--------------|-------------|------------|
| Architecture decisions | Code structure | `docs/adr/` |
| API contracts | `.proto` files | `docs/api/` |
| Development workflow | Run actual commands | `docs/development/` |
| Implementation details | **READ THE CODE** | Don't rely on docs |
| Current phase/status | `.meta/task-service/project-management/` | This file |

---

## 🚀 Quick Start Commands

### Development
```bash
# Rust crates (when implemented)
cargo build                 # Build all crates
cargo test                  # Run all tests
cargo run -p adr-cli        # Run CLI

# Frontend (when implemented)
pnpm install                # Install dependencies
pnpm dev                    # Start Next.js dev server
pnpm build                  # Build for production

# Bazel (validation)
bazel build //crates/...    # Build Rust crates
bazel build //apps/adr-web  # Build Next.js app
```

### Documentation
```bash
# Generate API docs from protobuf
pnpm docs:generate-api

# Validate docs are current
pnpm docs:validate
```

---

## 🎯 PoC Validation Goals

### Must Validate (High Risk)
- ✅ **Hexagonal Architecture**: SDK shared between CLI and service
- ✅ **gRPC Integration**: Rust ↔ Next.js communication works
- ✅ **Storage Abstraction**: Repository pattern with swappable adapters
- ✅ **Next.js Patterns**: App Router + Zustand + React Query integration
- ✅ **Build Patterns**: Cargo workspace + minimal Bazel learning

### Can Skip (Defer to Monorepo)
- ❌ Multiple storage backends (filesystem only proves pattern)
- ❌ Multi-language clients (protobuf already validates)
- ❌ Production operations (K8s, monitoring, etc.)
- ❌ Advanced Bazel features (basic learning only)

---

## 📦 Key Architectural Patterns

### Hexagonal Architecture (Ports & Adapters)
```
adr-domain  ← Pure domain (no infrastructure)
    ↑
adr-sdk     ← Ports (traits) + Use Cases
    ↑
adr-adapters ← Implementations (filesystem, postgres, etc.)
    ↑
    ├─ adr-service ← gRPC server (uses SDK)
    └─ adr-cli     ← CLI tool (uses SDK - SHARED!)
```

**Key Insight**: CLI and service use SAME SDK code. This validates the architecture works.

### Repository Pattern
```rust
// Port (trait in adr-sdk)
trait ADRRepository {
    async fn save(&self, adr: &ADR) -> Result<()>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>>;
    // ...
}

// Adapter (implementation in adr-adapters)
struct FilesystemAdapter { /* ... */ }
impl ADRRepository for FilesystemAdapter { /* ... */ }
```

**Key Insight**: Swap storage by changing one line of configuration.

---

## 🔄 Migration to Monorepo

### Strategy
1. **Copy directories** - `crates/`, `apps/`, `proto/` lift directly
2. **Update workspace files** - Add to monorepo's `Cargo.toml`, `package.json`
3. **Zero refactoring** - Import paths stay the same
4. **Time budget**: < 4 EU

### What Transfers
- ✅ All Rust crates (same structure)
- ✅ Next.js app (same structure)
- ✅ Protobuf schemas (same location)
- ✅ Documentation (copy `docs/` directory)
- ✅ Bazel BUILD files (already compatible)

See `docs/architecture/MIGRATION.md` for detailed process.

---

## 💡 For New Contributors

1. **Read this file first** (you're doing it!)
2. **Check current phase**: `.meta/task-service/project-management/IMPLEMENTATION_PLAN.md`
3. **Understand architecture**: `docs/architecture/OVERVIEW.md`
4. **Follow workflow**: `docs/development/WORKFLOW.md`
5. **Keep docs in sync**: `docs/development/DOCUMENTATION_GUIDE.md`

---

## 📞 Getting Help

- **Architecture questions**: See `docs/architecture/`
- **Development questions**: See `docs/development/`
- **Decision rationale**: See `docs/adr/` or `.meta/task-service/design-docs/DECISIONS.md`
- **Current status**: See `.meta/task-service/project-management/`

---

**Remember**: This is a PoC to validate architecture, not build a production system. Focus on proving patterns work, not on feature completeness.
