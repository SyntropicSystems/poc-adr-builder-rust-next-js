# ADR Editor PoC

> **Proof of Concept**: Validating hexagonal architecture with Rust + Next.js + gRPC before monorepo migration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node](https://img.shields.io/badge/node-24.x-brightgreen.svg)](https://nodejs.org/)
[![Rust](https://img.shields.io/badge/rust-1.75+-orange.svg)](https://www.rust-lang.org/)

---

## 🎯 What is This?

This is a **proof of concept** to validate architectural decisions for an ADR (Architecture Decision Record) editor before building it in a production monorepo. We're validating:

- ✅ **Hexagonal Architecture** (Ports & Adapters pattern)
- ✅ **gRPC Communication** (Rust backend ↔ Next.js frontend)
- ✅ **Storage Abstraction** (Repository pattern with swappable adapters)
- ✅ **Modern Frontend** (Next.js App Router + Zustand + React Query)
- ✅ **Build Patterns** (Cargo workspace + Bazel learning)

**Goal**: Build a system that can be lifted into a monorepo with minimal refactoring (< 4 EU migration time).

---

## 🚀 Quick Start

### Prerequisites

- **Rust 1.75+** - [Install](https://rustup.rs/)
- **Node v24** - [Install](https://nodejs.org/) or use `.nvmrc`
- **pnpm 9.0+** - `npm install -g pnpm`
- **Bazel** (optional) - For build validation

### Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd adr-editor-poc

# 2. Use correct Node version
nvm use  # or install node v24

# 3. Install Node dependencies
pnpm install

# 4. Build Rust workspace
cargo build

# 5. Run tests
cargo test
pnpm test
```

### Running the System

**CLI Tool** (when implemented):
```bash
cargo run -p adr-cli -- --help
cargo run -p adr-cli create --title "My First ADR"
cargo run -p adr-cli list
```

**gRPC Service** (when implemented):
```bash
cargo run -p adr-service
# Service runs on localhost:50051
```

**Frontend** (when implemented):
```bash
cd apps/adr-web
pnpm dev
# Open http://localhost:3000
```

---

## 📐 Architecture

### Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────┐
│          User Interfaces                 │
├──────────────┬──────────────────────────┤
│              │                           │
│  Next.js     │         CLI Tool          │
│  Frontend    │      (Rust Binary)        │
│              │                           │
└──────┬───────┴────────┬─────────────────┘
       │ gRPC           │ Direct
       │                │
┌──────▼────────────────▼─────────────────┐
│         Rust Service                     │
│    ┌─────────────────────────┐          │
│    │   API Layer (gRPC)      │          │
│    └──────────┬──────────────┘          │
│               │                          │
│    ┌──────────▼──────────────┐          │
│    │   DOMAIN CORE (SDK)     │          │
│    │  ┌──────────────────┐   │          │
│    │  │  adr-domain      │   │          │
│    │  │  (pure entities) │   │          │
│    │  └────────┬─────────┘   │          │
│    │  ┌────────▼─────────┐   │          │
│    │  │  adr-sdk         │   │          │
│    │  │  (ports + use    │   │          │
│    │  │   cases)         │   │          │
│    │  └────────┬─────────┘   │          │
│    └───────────┼──────────────┘          │
│                │                          │
│    ┌───────────▼──────────────┐          │
│    │  adr-adapters            │          │
│    │  (filesystem, etc.)      │          │
│    └───────────┬──────────────┘          │
└────────────────┼───────────────────────────┘
                 │
          ┌──────▼──────┐
          │  Storage    │
          └─────────────┘
```

**Key Insight**: CLI and Service share the SAME SDK code, validating the architecture works in practice.

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 + App Router | Modern React with SSR |
| | Zustand | Global UI state |
| | React Query | Server state & caching |
| **Backend** | Rust + Tokio | High-performance async |
| | tonic + prost | gRPC server + Protocol Buffers |
| | clap | CLI parsing |
| **Storage** | Repository pattern | Swappable adapters (filesystem, etc.) |
| **Build** | Cargo + pnpm | Primary development |
| | Bazel | Learning for monorepo |

---

## 📂 Project Structure

```
adr-editor-poc/
├── crates/              # Rust workspace (Hexagonal layers)
│   ├── adr-domain/      # Pure domain (no infrastructure)
│   ├── adr-sdk/         # Ports + use cases
│   ├── adr-adapters/    # Storage implementations
│   ├── adr-service/     # gRPC service
│   └── adr-cli/         # CLI tool
│
├── apps/
│   └── adr-web/         # Next.js frontend
│
├── proto/
│   └── adr/v1/          # Protobuf schemas (API source of truth)
│
├── docs/                # Living documentation
│   ├── architecture/    # System architecture
│   ├── adr/            # Architecture Decision Records
│   ├── development/    # Development guides
│   └── api/            # API documentation
│
├── .meta/              # Ephemeral working documents
│   └── task-service/
│       ├── design-docs/
│       └── project-management/
│
└── scripts/            # Automation scripts
```

---

## 🔧 Development

### Workspace Commands

**Rust**:
```bash
cargo build                 # Build all crates
cargo test                  # Run all tests
cargo run -p adr-cli        # Run CLI
cargo run -p adr-service    # Run gRPC service
```

**Node.js**:
```bash
pnpm install                # Install dependencies
pnpm dev                    # Start Next.js dev server
pnpm build                  # Build for production
pnpm test                   # Run tests
```

**Bazel** (optional validation):
```bash
bazel build //crates/...    # Build all Rust crates
bazel build //apps/adr-web  # Build Next.js app
bazel test //...            # Run all tests
```

### Documentation

**Generate API docs** (from protobuf):
```bash
pnpm docs:generate-api
```

**Validate docs are current**:
```bash
pnpm docs:validate
```

---

## 📖 Documentation

- **[llm.md](./llm.md)** - Start here! LLM context guide with complete navigation
- **[Architecture Overview](./docs/architecture/OVERVIEW.md)** - System architecture details
- **[ADRs](./docs/adr/)** - Architecture Decision Records
- **[Development Guide](./docs/development/SETUP.md)** - Setup and workflow
- **[API Documentation](./docs/api/GRPC.md)** - gRPC API reference

---

## 🎯 Current Status

**Phase**: Documentation & Foundation Setup

**Completed**:
- ✅ Documentation architecture
- ✅ Project configuration (pnpm, Node v24, Bazel)
- ✅ LLM context guide

**Next**:
- 🔄 Complete documentation files
- ⏳ Phase 1: Foundation (Cargo workspace, protobuf, domain/SDK)
- ⏳ Phase 2: CLI Tool
- ⏳ Phase 3: gRPC Service
- ⏳ Phase 4: Next.js Frontend

See [Implementation Plan](./.meta/task-service/project-management/IMPLEMENTATION_PLAN.md) for details.

---

## 🔄 Migration to Monorepo

This PoC is designed for easy migration:

1. **Copy directories** - `crates/`, `apps/`, `proto/` lift directly
2. **Update workspace files** - Add to monorepo configs
3. **Zero refactoring** - Import paths stay the same
4. **Time estimate**: < 4 EU

See [Migration Guide](./docs/architecture/MIGRATION.md) for full process.

---

## 🤝 Contributing

1. Read [llm.md](./llm.md) for context
2. Check [Contributing Guide](./docs/development/CONTRIBUTING.md)
3. Follow [Development Workflow](./docs/development/WORKFLOW.md)
4. Keep [Docs in Sync](./docs/development/DOCUMENTATION_GUIDE.md)

---

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🔗 Related Documents

- **Design Decisions**: [.meta/task-service/design-docs/DECISIONS.md](./.meta/task-service/design-docs/DECISIONS.md)
- **Implementation Plan**: [.meta/task-service/project-management/IMPLEMENTATION_PLAN.md](./.meta/task-service/project-management/IMPLEMENTATION_PLAN.md)
- **Original Methodology**: [System of Work](https://github.com/SyntropicSystems/methodology-task-orchestration-system-of-work)

---

**Remember**: This is a PoC to validate architecture, not build a production system. Focus on proving patterns work!
