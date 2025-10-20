# ADR Editor PoC - Repository Structure

## Document Purpose
This document defines how to structure the ADR Editor PoC repository to validate architectural decisions while minimizing migration costs when moving to the final monorepo.

---

## Core Problem

### Problem Statement
How do we structure the ADR Editor PoC repository so that:
1. It validates our architectural decisions (hexagonal, gRPC, multi-language)
2. Components can be lifted into monorepo with minimal changes
3. We learn Bazel patterns that will apply to monorepo
4. Directory structure mirrors final monorepo structure

### Why This Is A Problem
**Impact:**
- Poor PoC structure means high migration cost (defeats PoC purpose)
- Different structure = need to restructure when moving to monorepo
- Can't validate real architectural patterns
- Wasted effort if PoC doesn't translate to production

**Risks of Not Solving:**
- PoC becomes throwaway code
- Migration to monorepo takes weeks instead of hours
- Can't validate real build/deploy patterns
- Learn wrong patterns that don't apply to monorepo

---

## Problem Stack

```
P.PoC.1. Repository Structure (STRATEGIC)
    ├── P.PoC.1.1. Directory Layout
    ├── P.PoC.1.2. Crate/Package Organization
    └── P.PoC.1.3. Migration Strategy

P.PoC.2. Build System Integration (ARCHITECTURAL)
    ├── P.PoC.2.1. Bazel Adoption Level
    ├── P.PoC.2.2. Cargo vs Bazel
    └── P.PoC.2.3. Build File Organization

P.PoC.3. Validation Strategy (TACTICAL)
    ├── P.PoC.3.1. What to Validate
    ├── P.PoC.3.2. What to Skip
    └── P.PoC.3.3. Success Metrics

P.PoC.4. Migration Path (OPERATIONAL)
    ├── P.PoC.4.1. Lift-and-Shift Process
    ├── P.PoC.4.2. Integration Points
    └── P.PoC.4.3. Cleanup Strategy
```

---

# P.PoC.1. Repository Structure

## P.PoC.1.1. Directory Layout

### Problem Statement
What directory structure should the PoC use to mirror the eventual monorepo while remaining simple for rapid development?

### Problem Stack
- **Parent**: P.PoC.1 (Repository Structure)
- **Siblings**: P.PoC.1.2 (Crate Organization), P.PoC.1.3 (Migration)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Directory structure determines migration difficulty
- Different structure = move files + update paths everywhere
- Want to validate real patterns, not PoC-specific hacks
- Structure affects Bazel usage and learning

**Risks of Not Solving:**
- PoC in flat structure, monorepo nested = major refactor
- Import paths change completely during migration
- Bazel patterns don't transfer
- High migration cost (days/weeks of work)

### Options

#### Option A: Flat PoC Structure
```
adr-editor-poc/
├── rust/           # All Rust code here
├── frontend/       # Next.js here
├── proto/          # Protobufs
└── README.md
```

**Pros**:
- Very simple
- Fast to navigate
- No nesting

**Cons**:
- Doesn't match monorepo structure
- High migration cost (restructure everything)
- Can't validate real patterns
- Import paths all wrong

**Trade-offs**: PoC speed vs migration cost

#### Option B: Mirror Monorepo Exactly
```
adr-editor-poc/
├── services/
│   └── adr-service/
├── crates/
│   ├── adr-domain/
│   ├── adr-sdk/
│   └── adr-adapters/
├── apps/
│   ├── adr-cli/
│   └── adr-web/
├── proto/
└── ...
```

**Pros**:
- Exact match to monorepo
- Zero restructuring during migration
- Validates real structure

**Cons**:
- Heavy for PoC (many directories)
- Over-engineering for single project

**Trade-offs**: Perfect migration vs PoC simplicity

#### Option C: Simplified Monorepo Structure ⭐ CHOSEN
```
adr-editor-poc/
├── crates/              # Rust workspace (matches monorepo)
│   ├── adr-domain/      # Pure domain
│   ├── adr-sdk/         # Ports + use cases
│   ├── adr-adapters/    # Storage implementations
│   ├── adr-service/     # gRPC service
│   └── adr-cli/         # CLI tool
├── apps/                # Frontend apps (matches monorepo)
│   └── adr-web/         # Next.js
├── proto/               # Protobuf schemas
│   └── adr/
│       └── v1/
│           └── adr.proto
├── bazel/               # Bazel config (minimal)
│   └── ...
├── Cargo.toml           # Workspace root
├── package.json         # Workspace root (for apps)
├── WORKSPACE            # Bazel workspace
├── BUILD.bazel          # Root build file
└── README.md
```

**Pros**:
- Mirrors key monorepo structure
- Simple enough for PoC
- Easy to lift into monorepo (copy directories)
- Import paths stay same
- Can validate Cargo workspace + Bazel
- Clear separation (crates/ vs apps/)

**Cons**:
- Slightly more structure than flat
- Need to understand workspace concepts

**Trade-offs**: Minimal additional structure for low migration cost

### Decision
**Chosen**: Option C - Simplified Monorepo Structure

**Rationale**:
- Matches monorepo top-level structure (`crates/`, `apps/`, `proto/`)
- Rust workspace in `crates/` is same pattern as monorepo
- Next.js in `apps/adr-web/` is same as monorepo
- Can literally copy these directories into monorepo
- Import paths don't change (e.g., `use adr_sdk::repository`)
- Validates both Cargo and Bazel workspace patterns
- Minimal overhead vs flat structure

**Key Insight**: This IS the monorepo structure, just without other projects.

### Success Criteria
1. ✅ Directory names match monorepo conventions
2. ✅ Rust crate imports work without path changes
3. ✅ Next.js app can be moved without refactoring
4. ✅ Protobuf files in same location as monorepo
5. ✅ Can copy `crates/` directly into monorepo
6. ✅ Can copy `apps/adr-web/` directly into monorepo

### Metrics
**Quantitative**:
- Time to migrate to monorepo: < 4 hours (should be mostly copy/paste)
- Number of import path changes: < 10 (only for monorepo tooling)
- Number of files to move: 0 (directories lift as-is)

**Qualitative**:
- "Feels like working in the monorepo already"
- "Migration was just copying directories"

### Triggers to Revisit

1. **Structure Mismatch**
   - Monorepo structure decisions change
   - PoC structure doesn't match decisions
   - Import paths need major changes

2. **Complexity Indicator**
   - Structure slowing down PoC development
   - Too many directories for single project
   - Confusion about where things go

### Risks of Decision

1. **Slightly More Complex Than Flat**
   - Risk: More directories to navigate
   - Mitigation: Clear README, only 3 top-level dirs
   - Severity: Very Low

2. **Monorepo Structure Unknown**
   - Risk: Guessing at monorepo structure
   - Mitigation: Based on architecture decisions already made
   - Severity: Low

### Migration Cost
**From Flat**: 8-12 EU (restructure everything)
**To Monorepo**: < 1 EU (copy directories)

---

## P.PoC.1.2. Crate/Package Organization

### Problem Statement
How should we organize the Rust crates and their dependencies to match the hexagonal architecture while staying simple for PoC?

### Problem Stack
- **Parent**: P.PoC.1 (Repository Structure)
- **Siblings**: P.PoC.1.1 (Directory Layout), P.PoC.1.3 (Migration)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Validates our layered architecture (P2.1 decision)
- Tests if SDK can really be shared between CLI and service
- Proves hexagonal pattern works in practice
- Dependency graph must match architecture

**Risks of Not Solving:**
- PoC doesn't validate architecture
- Discover architectural issues late (in production)
- Can't prove SDK reusability
- Coupling creeps into PoC, carries to production

### Options

#### Option A: Single Rust Crate
```
crates/
└── adr-all/        # Everything in one crate
    └── src/
        ├── domain/
        ├── sdk/
        ├── adapters/
        ├── service/
        └── cli/
```

**Pros**:
- Simplest
- Fast compilation (no crate boundaries)
- Easy to refactor

**Cons**:
- Doesn't validate architecture
- Can't test SDK reusability
- Coupling not prevented
- High migration cost (need to split)

**Trade-offs**: Speed vs validation

#### Option B: Full Layered Architecture ⭐ CHOSEN
```
crates/
├── adr-domain/         # Pure domain (P2.1.1)
│   └── Cargo.toml      # No dependencies
├── adr-sdk/            # Ports + use cases (P2.1.1)
│   └── Cargo.toml      # depends: adr-domain
├── adr-adapters/       # Adapters (P2.2.1)
│   └── Cargo.toml      # depends: adr-sdk
│                       # features: filesystem, postgres
├── adr-service/        # gRPC service (P3.1.1)
│   └── Cargo.toml      # depends: adr-sdk, adr-adapters
└── adr-cli/            # CLI tool (P6.1)
    └── Cargo.toml      # depends: adr-sdk, adr-adapters
```

**Pros**:
- Validates full hexagonal architecture
- Proves SDK can be used by both CLI and service
- Tests dependency graph is correct
- Enforces clean boundaries (compiler helps)
- Zero migration cost (same structure in monorepo)
- Validates feature flags (adapters)

**Cons**:
- More crates = slightly slower compilation
- Need to manage workspace dependencies

**Trade-offs**: Slight PoC overhead vs architectural validation

### Decision
**Chosen**: Option B - Full Layered Architecture

**Rationale**:
- **This is the point of the PoC** - validate architecture
- Must prove SDK can be shared (CLI and service)
- Must prove hexagonal pattern works
- Compiler enforces boundaries (domain can't import infrastructure)
- Same crates in monorepo (zero migration)
- Validates all architectural decisions (P2.1, P2.2, P3.1)

**Workspace Structure**:
```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/adr-domain",
    "crates/adr-sdk",
    "crates/adr-adapters",
    "crates/adr-service",
    "crates/adr-cli",
]
resolver = "2"

[workspace.dependencies]
# Shared dependency versions (P1.1.1)
tokio = { version = "1.40", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
# ... etc
```

**Dependency Graph** (validates P2.1):
```
adr-domain  ← (no deps)
    ↑
adr-sdk     ← (depends: adr-domain)
    ↑
adr-adapters ← (depends: adr-sdk, features)
    ↑
    ├─ adr-service ← (depends: adr-sdk, adr-adapters)
    └─ adr-cli     ← (depends: adr-sdk, adr-adapters)
```

### Success Criteria
1. ✅ `adr-domain` has zero infrastructure dependencies
2. ✅ `adr-sdk` compiles without adapters
3. ✅ `adr-service` and `adr-cli` import same SDK
4. ✅ Feature flags work (`cargo build -p adr-cli --features filesystem`)
5. ✅ Changing domain doesn't require rebuilding adapters
6. ✅ Compiler prevents invalid dependencies (domain importing storage)

### Metrics
**Quantitative**:
- Crate dependency violations: 0 (enforced by Cargo)
- Shared code between CLI and service: > 80%
- Compilation time: < 30s (workspace build)

**Qualitative**:
- "SDK really is shared"
- "Hexagonal boundaries enforced"
- "Architecture works as designed"

### Triggers to Revisit

1. **Coupling Detected**
   - Domain crate gaining dependencies
   - Circular dependencies appearing
   - Compiler allowing invalid imports

2. **Compilation Issues**
   - Workspace builds too slow
   - Crate boundaries causing problems
   - Feature flags not working

3. **Architectural Changes**
   - Architecture decisions changed
   - Simpler or more complex structure needed

### Risks of Decision

1. **Compilation Overhead**
   - Risk: Multiple crates slower to compile
   - Mitigation: Incremental compilation, monitor time
   - Severity: Low (worthwhile for validation)

2. **PoC Velocity**
   - Risk: Crate boundaries slow down development
   - Mitigation: Can refactor within crates quickly
   - Severity: Low

### Migration Cost
**To Single Crate**: 5-8 EU (lose architectural validation)
**To Monorepo**: 0 EU (same structure)

---

## P.PoC.2. Build System Integration

## P.PoC.2.1. Bazel Adoption Level

### Problem Statement
How much Bazel should we use in the PoC, given we'll use Bazel in the monorepo but want to keep PoC development fast?

### Problem Stack
- **Parent**: P.PoC.2 (Build System Integration)
- **Siblings**: P.PoC.2.2 (Cargo vs Bazel), P.PoC.2.3 (Build Files)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Bazel learning curve affects PoC velocity
- Want to validate Bazel patterns for monorepo
- But: full Bazel adoption could slow PoC significantly
- Need balance: learn Bazel, but don't block PoC

**Risks of Not Solving:**
- Skip Bazel in PoC → don't learn patterns → monorepo adoption harder
- Full Bazel in PoC → slow development → PoC takes too long
- Learn wrong Bazel patterns → redo in monorepo

### Options

#### Option A: No Bazel in PoC
**Description**: Use Cargo for Rust, npm/pnpm for frontend, ignore Bazel.

**Pros**:
- Maximum PoC velocity
- No Bazel learning curve
- Simple, familiar tools

**Cons**:
- Don't learn Bazel patterns
- Monorepo migration requires Bazel adoption (big jump)
- Can't validate Bazel build patterns
- Different build system = higher migration cost

**Trade-offs**: Speed vs learning

#### Option B: Full Bazel from Day 1
**Description**: Use Bazel for everything, deprecate Cargo/npm.

**Pros**:
- Learn Bazel deeply
- Exactly matches monorepo
- Validates Bazel patterns

**Cons**:
- Huge learning curve
- Slows PoC significantly
- Complex setup (rules_rust, rules_nodejs)
- Debugging Bazel harder than native tools
- Overkill for single project

**Trade-offs**: Perfect preparation vs PoC practicality

#### Option C: Hybrid - Native Tools + Minimal Bazel ⭐ CHOSEN
**Description**: Use Cargo/npm for development, add minimal Bazel to learn patterns.

**Approach**:
1. **Primary development**: Cargo and npm (fast iteration)
2. **Bazel layer**: Add BUILD files to learn structure
3. **Validate**: Ensure Bazel builds work (CI)
4. **Learn**: Bazel patterns without blocking development

**Pros**:
- Fast PoC development (native tools)
- Learn Bazel incrementally
- Validate migration patterns
- CI can use Bazel (practice)
- BUILD files ready for monorepo

**Cons**:
- Maintain two build systems temporarily
- Some duplication (Cargo.toml + BUILD.bazel)

**Trade-offs**: Slight duplication vs balanced learning

### Decision
**Chosen**: Option C - Hybrid (Native Tools + Minimal Bazel)

**Rationale**:
- PoC primary goal: validate architecture, not Bazel mastery
- But: want to learn Bazel patterns for monorepo
- Hybrid lets us develop fast, learn incrementally
- Can compare Cargo vs Bazel (educational)
- BUILD files transfer directly to monorepo
- CI uses Bazel → validates it works

**Implementation Strategy**:

**Development Workflow** (Primary):
```bash
# Fast iteration with Cargo
cd crates/adr-service
cargo build
cargo test

# Fast iteration with npm
cd apps/adr-web
npm run dev
```

**Bazel Layer** (Learning + CI):
```bash
# Bazel builds everything
bazel build //crates/adr-service
bazel test //crates/...
bazel build //apps/adr-web
```

**What to Bazelify**:
- ✅ Rust crates (via rules_rust)
- ✅ Protobuf generation (via rules_proto)
- ✅ Next.js app (via rules_nodejs)
- ✅ Integration tests
- ❌ Skip: complex Bazel features (remote caching, etc.)

**Learning Focus**:
- BUILD file structure
- Dependency declarations
- Target naming conventions
- rules_rust basics
- rules_nodejs basics

### Success Criteria
1. ✅ Can develop with Cargo/npm (primary workflow)
2. ✅ Bazel builds work (CI validation)
3. ✅ BUILD files structured for monorepo
4. ✅ Team learns basic Bazel patterns
5. ✅ Protobuf generation works in both systems
6. ✅ Migration to Bazel-only in monorepo is clear path

### Metrics
**Quantitative**:
- Development primarily uses: Cargo/npm (80%+ of time)
- Bazel build success rate: 100% (in CI)
- Time spent on Bazel issues: < 20% of build work
- BUILD file coverage: 100% of crates/apps

**Qualitative**:
- "Bazel didn't slow us down"
- "Learned enough Bazel for monorepo"
- "BUILD files ready to migrate"

### Triggers to Revisit

1. **Bazel Blocking Development**
   - Bazel taking > 20% of development time
   - Debugging Bazel instead of features
   - Team frustrated with Bazel complexity

2. **Insufficient Learning**
   - Monorepo migration requires Bazel knowledge we don't have
   - BUILD files not structured correctly
   - Need to redo Bazel work in monorepo

3. **Divergence Issues**
   - Cargo and Bazel builds out of sync
   - Maintaining two systems causing bugs
   - One system preferred, other abandoned

### Risks of Decision

1. **Two Build Systems**
   - Risk: Duplication and potential divergence
   - Mitigation: CI validates both, primary is Cargo/npm
   - Severity: Low (temporary)

2. **Incomplete Bazel Learning**
   - Risk: Don't learn enough for monorepo
   - Mitigation: Focus on transferable patterns
   - Severity: Medium (but PoC goal is architecture, not Bazel)

3. **False Confidence**
   - Risk: Think we know Bazel, but only surface level
   - Mitigation: Document what we learned vs didn't
   - Severity: Low (acknowledge learning gaps)

### Migration Cost
**To Bazel-Only**: Low-Medium (2-3 EU, remove Cargo/npm workflows)
**To No Bazel**: Very Low (0.5 EU, remove BUILD files)

---

## P.PoC.3. Validation Strategy

## P.PoC.3.1. What to Validate in PoC

### Problem Statement
Which architectural decisions should the PoC validate, and which can wait for the monorepo?

### Problem Stack
- **Parent**: P.PoC.3 (Validation Strategy)
- **Siblings**: P.PoC.3.2 (What to Skip), P.PoC.3.3 (Success Metrics)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- PoC time is limited (want results quickly)
- Must validate high-risk decisions
- Can skip low-risk or well-understood patterns
- Wrong prioritization = miss critical issues or waste time

**Risks of Not Solving:**
- Validate everything → PoC takes months
- Validate too little → critical issues missed
- Validate wrong things → surprises in production

### Decision: Validation Priorities

**Must Validate (Critical Path)**:

1. **Hexagonal Architecture (P1.1, P2.1)** - 🔴 HIGH RISK
   - ✅ Can SDK be used by both CLI and service?
   - ✅ Do adapter boundaries work?
   - ✅ Is domain truly infrastructure-free?
   - **Why**: Core architectural pattern, high risk if wrong

2. **gRPC + Protobuf (P3.1.1)** - 🔴 HIGH RISK
   - ✅ Does Rust ↔ Next.js gRPC work?
   - ✅ Can we generate TypeScript types?
   - ✅ Is grpc-web or tonic-web viable for browser?
   - **Why**: Novel combination, integration risk

3. **Storage Abstraction (P2.2.1)** - 🟡 MEDIUM RISK
   - ✅ Can we swap storage backends?
   - ✅ Does filesystem adapter work?
   - ✅ Is repository trait practical?
   - **Why**: Core to design, needs validation

4. **Next.js App Router + Zustand + React Query (P4.1.1, P4.2)** - 🟡 MEDIUM RISK
   - ✅ Does App Router work with gRPC?
   - ✅ Do Zustand and React Query integrate well?
   - ✅ Is SSR + client state manageable?
   - **Why**: Newer patterns, less examples

5. **CLI SDK Integration (P6.2)** - 🟢 LOW RISK
   - ✅ Can CLI use SDK easily?
   - ✅ Is clap integration smooth?
   - **Why**: Standard pattern, but good to prove

**Can Skip (Defer to Monorepo)**:

1. **Multiple Storage Backends** - 🟢 LOW RISK
   - ❌ PostgreSQL adapter (do later)
   - ❌ DynamoDB adapter (do later)
   - ✅ Filesystem only (prove pattern works)
   - **Why**: One adapter proves pattern

2. **Multi-Language Integration (P.ML.*)** - 🟢 LOW RISK
   - ❌ Python/Go/Node clients (do later)
   - ❌ Auxiliary services (do later)
   - **Why**: Protobuf already validates pattern

3. **Production Operations** - 🟢 LOW RISK
   - ❌ Kubernetes deployment
   - ❌ Monitoring/observability
   - ❌ High availability
   - **Why**: PoC can run locally/simple deploy

4. **Advanced Bazel** - 🟢 LOW RISK
   - ❌ Remote caching
   - ❌ Remote execution
   - ❌ Complex optimizations
   - ✅ Basic BUILD files only
   - **Why**: Learn basics, advanced for monorepo

5. **Full Feature Set** - 🟢 LOW RISK
   - ❌ All ADR workflow features
   - ✅ CRUD + basic queries (prove architecture)
   - **Why**: Not validating features, validating structure

### Success Criteria

**Architecture Validation**:
1. ✅ CLI and service share SDK (same imports)
2. ✅ Swapping storage backend requires changing 1 line
3. ✅ Next.js can call Rust service via gRPC
4. ✅ TypeScript types generated from protobuf
5. ✅ Domain crate has zero infrastructure deps

**Technical Validation**:
1. ✅ App Router + gRPC integration works
2. ✅ Zustand + React Query work together
3. ✅ Server Components can fetch from gRPC
4. ✅ Client Components can mutate via gRPC

**Build Validation**:
1. ✅ Cargo workspace works as designed
2. ✅ Bazel can build all targets
3. ✅ Protobuf generation in both systems

### Metrics

**Validation Coverage**:
- Critical decisions validated: 100%
- Medium decisions validated: 100%
- Low-risk decisions validated: 20% (prove pattern, not all variations)

**Time Budget**:
- Architecture setup: 4-6 EU
- Feature implementation: 8-12 EU
- Integration work: 4-6 EU
- **Total PoC**: 16-24 EU

**Quality**:
- Architectural issues found: Document for fixing
- Integration issues found: Document and solve
- Migration path clear: Yes/No

### Triggers to Revisit

1. **Validation Failure**
   - Critical decision doesn't work as designed
   - Need to revisit architecture
   - PoC reveals fundamental issue

2. **Scope Creep**
   - PoC growing beyond validation goals
   - Adding features not needed for validation
   - Taking > 24 EU

3. **Insufficient Validation**
   - Monorepo reveals issues PoC didn't catch
   - Should have validated more
   - Surprises in production

### Risks of Decision

1. **Under-Validation**
   - Risk: Skip something critical
   - Mitigation: Focus on high-risk, novel parts
   - Severity: Low (prioritization is thoughtful)

2. **Over-Validation**
   - Risk: PoC becomes full product
   - Mitigation: Clear scope, time box
   - Severity: Medium (scope creep common)

### Migration Cost
N/A (defines what validates before migration)

---

## P.PoC.4. Migration Path

## P.PoC.4.1. Lift-and-Shift Process

### Problem Statement
When PoC succeeds, what's the exact process to move code into the monorepo?

### Problem Stack
- **Parent**: P.PoC.4 (Migration Path)
- **Siblings**: P.PoC.4.2 (Integration Points), P.PoC.4.3 (Cleanup)
- **Level**: Operational

### Why This Is A Problem
**Impact:**
- Determines whether PoC work is reusable
- Affects timeline (hours vs weeks)
- Influences whether to start PoC at all
- High cost = throw away PoC

**Risks of Not Solving:**
- No clear migration path
- End up rewriting everything
- PoC becomes disposable
- Wasted effort

### Decision: Migration Process

**Step-by-Step Migration**:

**Phase 1: Copy Directories** (1 EU)
```bash
# From PoC to Monorepo

# Copy Rust crates
cp -r adr-editor-poc/crates/* platform-monorepo/crates/
# Result: crates/adr-domain, crates/adr-sdk, etc.

# Copy Next.js app
cp -r adr-editor-poc/apps/adr-web platform-monorepo/apps/
# Result: apps/adr-web

# Copy protobufs
cp -r adr-editor-poc/proto/adr platform-monorepo/proto/
# Result: proto/adr/v1/adr.proto
```

**Phase 2: Update Workspace Files** (0.5 EU)
```toml
# platform-monorepo/Cargo.toml
[workspace]
members = [
    # Existing members...
    "crates/adr-domain",
    "crates/adr-sdk",
    "crates/adr-adapters",
    "crates/adr-service",
    "crates/adr-cli",
]
```

```json
// platform-monorepo/package.json
{
  "workspaces": [
    "apps/adr-web",
    "apps/workflow-editor",  // existing
    // ...
  ]
}
```

**Phase 3: Update Bazel** (1 EU)
- Copy BUILD files
- Update WORKSPACE if needed
- Verify targets build

**Phase 4: Integration** (1.5 EU)
- Wire into monorepo CI/CD
- Add to deployment configs
- Update documentation
- Add to shared services (if any)

**Phase 5: Cleanup PoC** (0.5 EU)
- Archive adr-editor-poc repo
- Document what was learned
- Note any deviations from original plan

**Total Migration Time**: ~4 EU

### Success Criteria
1. ✅ All PoC code copied without modification
2. ✅ Import paths work without changes
3. ✅ Tests pass immediately after copy
4. ✅ CI builds successfully
5. ✅ Can deploy from monorepo
6. ✅ Migration takes < 8 EU

### Metrics
**Quantitative**:
- Files changed during migration: < 10
- Import path updates: < 10
- Build errors after copy: 0
- Migration time: < 8 EU

**Qualitative**:
- "Copy, paste, done"
- "No refactoring needed"
- "Works immediately"

### Triggers to Revisit

1. **High Migration Cost**
   - Migration takes > 8 EU
   - Significant refactoring needed
   - PoC structure didn't match

2. **Monorepo Structure Changed**
   - Different organization in monorepo
   - Need to restructure PoC code

### Risks of Decision

1. **Structure Mismatch**
   - Risk: Monorepo structure different than expected
   - Mitigation: Based on architecture decisions
   - Severity: Low

2. **Integration Issues**
   - Risk: PoC doesn't integrate with existing monorepo services
   - Mitigation: Plan integration points upfront
   - Severity: Medium

### Migration Cost
**Rollback**: 0 EU (keep PoC separate)
**To Different Structure**: 8-12 EU (restructure)

---

## Summary: PoC Repository Structure

### Directory Layout
```
adr-editor-poc/
├── crates/                      # Rust workspace
│   ├── adr-domain/              # Pure domain (no deps)
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── adr.rs
│   │   │   └── ...
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   ├── adr-sdk/                 # Ports + use cases
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── repository.rs    # trait ADRRepository
│   │   │   └── use_cases/
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   ├── adr-adapters/            # Storage implementations
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   └── filesystem.rs    # [feature = "filesystem"]
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   ├── adr-service/             # gRPC service
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   └── grpc.rs
│   │   ├── Cargo.toml
│   │   └── BUILD.bazel
│   └── adr-cli/                 # CLI tool
│       ├── src/
│       │   └── main.rs
│       ├── Cargo.toml
│       └── BUILD.bazel
│
├── apps/                        # Frontend applications
│   └── adr-web/                 # Next.js app
│       ├── app/                 # App Router
│       ├── components/
│       ├── lib/
│       │   ├── grpc/           # Generated gRPC client
│       │   └── state/          # Zustand stores
│       ├── package.json
│       └── BUILD.bazel
│
├── proto/                       # Protobuf schemas
│   └── adr/
│       └── v1/
│           ├── adr.proto
│           └── BUILD.bazel
│
├── bazel/                       # Bazel configuration
│   ├── rust.bzl                # Rust macros
│   └── nodejs.bzl              # Node.js macros
│
├── Cargo.toml                   # Workspace root
├── package.json                 # npm workspace root
├── WORKSPACE                    # Bazel workspace
├── BUILD.bazel                  # Root build
├── .bazelrc                     # Bazel config
├── .gitignore
└── README.md
```

### Key Principles

**Structure**:
1. **Mirror monorepo**: Same directory names and organization
2. **Cargo workspace**: Full layered architecture (validates P2.1)
3. **Minimal Bazel**: BUILD files for learning, Cargo for development

**Validation**:
1. **Must validate**: Hexagonal architecture, gRPC, storage abstraction
2. **Can skip**: Multiple backends, multi-language, production ops
3. **Time box**: 16-24 EU total

**Migration**:
1. **Lift-and-shift**: Copy directories directly
2. **Zero refactoring**: Import paths stay same
3. **Quick**: < 4 EU to migrate

### Development Workflow

**Primary (Fast Iteration)**:
```bash
# Rust development
cargo build
cargo test
cargo run -p adr-cli

# Frontend development
cd apps/adr-web
npm run dev
```

**Secondary (Validation)**:
```bash
# Bazel builds (CI)
bazel build //crates/...
bazel test //crates/...
bazel build //apps/adr-web
```

**Protobuf Generation**:
```bash
# Generate for Rust
cargo build  # build.rs handles it

# Generate for TypeScript
npm run proto:gen  # or bazel build //proto/...
```

### Migration Checklist

When PoC succeeds:

**Pre-Migration**:
- [ ] Architecture validated (all critical decisions proven)
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Known issues documented

**Migration**:
- [ ] Copy `crates/*` to monorepo
- [ ] Copy `apps/adr-web` to monorepo
- [ ] Copy `proto/adr` to monorepo
- [ ] Update workspace `Cargo.toml`
- [ ] Update workspace `package.json`
- [ ] Update `WORKSPACE` (Bazel)
- [ ] Run tests in monorepo
- [ ] Update CI/CD configs
- [ ] Deploy from monorepo

**Post-Migration**:
- [ ] Archive PoC repo
- [ ] Document lessons learned
- [ ] Update architecture decisions if needed
- [ ] Celebrate! 🎉

### Validation Success Metrics

**Must Prove**:
- ✅ SDK shared between CLI and service (same imports, no duplication)
- ✅ Hexagonal boundaries enforced (compiler prevents violations)
- ✅ Storage adapter swappable (change one line of config)
- ✅ Next.js ↔ Rust gRPC works (browser can call service)
- ✅ TypeScript types generated from protobuf
- ✅ App Router + Zustand + React Query integrate cleanly

**Migration Success**:
- ✅ Copy-paste migration works
- ✅ < 4 EU migration time
- ✅ No refactoring needed
- ✅ Tests pass immediately

---

## Critical Notes

### What Makes This PoC Valuable

1. **Architectural Validation** - Proves hexagonal architecture works with Rust + Next.js + gRPC
2. **Risk Reduction** - Validates high-risk technical decisions before committing
3. **Learning** - Team learns patterns that transfer to monorepo
4. **Reusable** - Code lifts directly into monorepo (not throwaway)

### What Makes Migration Easy

1. **Same Structure** - Directory layout matches monorepo
2. **Same Tools** - Cargo workspace, npm workspace patterns same
3. **Same Paths** - Import paths don't change
4. **Bazel Ready** - BUILD files already written

### What to Avoid

1. ❌ **Don't add features** not needed for validation (scope creep)
2. ❌ **Don't optimize prematurely** (focus on proving architecture)
3. ❌ **Don't build production features** (this is a PoC)
4. ❌ **Don't over-invest in Bazel** (basic learning only)
5. ❌ **Don't skip validation** of critical decisions

### What to Embrace

1. ✅ **Do validate architecture** thoroughly (the point)
2. ✅ **Do use real patterns** (not PoC shortcuts)
3. ✅ **Do match monorepo structure** (enables migration)
4. ✅ **Do document learnings** (feed back to decisions)
5. ✅ **Do time-box** (16-24 EU, no more)

---

*This PoC structure enables rapid validation of architectural decisions while ensuring code can be lifted directly into the monorepo with minimal migration cost.*
