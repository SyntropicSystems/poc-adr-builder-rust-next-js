# Documentation Guide

**Purpose**: How to maintain documentation that stays in sync with code while minimizing duplication and maintenance burden.

---

## 🎯 Core Philosophy

### The Golden Rule

**CODE IS TRUTH**

When documentation and code conflict, the code is correct. Documentation should be updated to match the code, never the other way around based on stale docs.

### Documentation Hierarchy

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

3. WRITTEN DOCUMENTATION (LOWEST AUTHORITY)
   ├─ Architecture decisions (docs/adr/)
   ├─ System overview (docs/architecture/)
   └─ Development guides (docs/development/)
```

**Critical Rule**: If level 1 and level 3 conflict, update level 3 to match level 1.

---

## ✅ What to Document

### DO Document (High Value)

#### 1. Architecture & Decisions (`docs/adr/`, `docs/architecture/`)
**Why**: Code shows WHAT, docs explain WHY
- ✅ Why we chose this architecture (not obvious from code)
- ✅ Trade-offs and alternatives considered
- ✅ Integration patterns between components
- ✅ Migration strategies
- ✅ Constraints and assumptions

**Example**: 
```markdown
<!-- Good: Documents WHY -->
We chose hexagonal architecture to enable testing business logic 
without infrastructure, and to support multiple storage backends 
without changing core logic.

<!-- Bad: Documents WHAT -->
The adr-sdk crate contains the ADRRepository trait and use cases.
```

#### 2. API Contracts (`docs/api/`)
**Why**: Public interfaces need external documentation
- ✅ gRPC service contracts (but: generated from `.proto`)
- ✅ Authentication/authorization patterns
- ✅ Error handling conventions
- ✅ Breaking change policies
- ✅ Versioning strategy

**Note**: Prefer generation over manual docs.

#### 3. Development Workflow (`docs/development/`)
**Why**: Can't be inferred from reading code
- ✅ How to set up environment
- ✅ How to run tests
- ✅ How to add new features
- ✅ Where to find things (navigation)
- ✅ Build and deployment processes

### DON'T Document (Low Value)

#### 1. Implementation Details
**Why**: Code is self-documenting with good names
- ❌ How a function works (use clear function names + inline comments)
- ❌ What parameters do (use descriptive types + names)
- ❌ Internal algorithms (code should be self-explanatory)
- ❌ Data structures (Rust types are self-documenting)

**Instead**: Write clear code
```rust
// DON'T write docs for this
/// Calculates the total
fn calc(x: i32, y: i32) -> i32 { x + y }

// DO write clear code
fn calculate_total_price(base_price: i32, tax: i32) -> i32 {
    base_price + tax
}
```

#### 2. API Definitions
**Why**: Should be generated from source of truth
- ❌ gRPC endpoints (generate from `.proto`)
- ❌ Request/response types (generate from `.proto`)
- ❌ CLI commands (generate from `clap` definitions)

**Instead**: Use generation
```bash
# Generate API docs from protobuf
pnpm docs:generate-api

# CLI help generated automatically
cargo run -p adr-cli -- --help
```

---

## 🔄 Keeping Docs in Sync

### Strategy 1: Generate from Code

**Principle**: Single source of truth in code, docs are byproduct

#### Protobuf → API Documentation

```bash
# When .proto files change, regenerate docs
pnpm docs:generate-api

# This generates:
# - docs/api/GRPC.md (human-readable API docs)
# - Rust types (via tonic-build)
# - TypeScript types (via protoc-gen-ts)
```

**Automation**: 
- CI checks that generated files are up-to-date
- Pre-commit hook can auto-generate
- Tests fail if generation needed

#### CLI → Help Text

```rust
// Command definitions in code using clap
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "adr-cli")]
#[command(about = "ADR Editor CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

// Help text auto-generated!
// No separate CLI docs needed.
```

#### Tests → Examples

```rust
// Example constants defined in code
pub const BASIC_EXAMPLE: Example = Example {
    name: "basic",
    description: "Create a simple ADR",
    command: "adr-cli create --title 'Use REST API'",
    expected_output: Some("Created ADR-001"),
};

// Tests import and execute examples
#[test]
fn test_basic_example() {
    let result = execute(BASIC_EXAMPLE.command);
    assert!(result.is_ok());
}

// Docs generation uses same examples
// Can't drift - single source of truth!
```

### Strategy 2: Validation Tests

**Principle**: Tests enforce documentation correctness

#### Test: Protobuf Docs Current

```rust
#[test]
fn proto_docs_are_current() {
    let proto_hash = hash_proto_files("proto/");
    let doc_metadata = read_doc_metadata("docs/api/GRPC.md");
    
    assert_eq!(proto_hash, doc_metadata.source_hash,
        "API docs out of date! Run: pnpm docs:generate-api");
}
```

#### Test: Architecture Matches Code

```rust
#[test]
fn architecture_diagram_matches_code() {
    // Parse actual crate dependencies from Cargo.toml
    let actual_deps = parse_workspace_dependencies();
    
    // Parse architecture doc for described dependencies
    let documented_deps = parse_architecture_doc("docs/architecture/OVERVIEW.md");
    
    assert_eq!(actual_deps, documented_deps,
        "Architecture docs don't match code structure!");
}
```

#### Test: Examples Work

```rust
#[test]
fn all_documented_examples_execute() {
    // Extract code examples from markdown docs
    let examples = extract_examples_from_docs("docs/api/");
    
    for example in examples {
        let result = execute_command(&example.command);
        assert!(result.is_ok(),
            "Example in {} doesn't work: {}",
            example.file, example.command);
    }
}
```

### Strategy 3: Update Triggers

**Principle**: Clear rules on when documentation needs updating

#### Update Matrix

| Change Type | Update Required? | Location | How |
|-------------|------------------|----------|-----|
| **Add/modify `.proto`** | ✅ Auto-generate | `docs/api/GRPC.md` | `pnpm docs:generate-api` |
| **Change architecture** | ✅ Manual | `docs/adr/`, `docs/architecture/` | Edit files |
| **Add CLI command** | ❌ Auto-generated | N/A | `clap` handles it |
| **Add use case** | ❌ Self-documenting | N/A | Good names suffice |
| **Add crate** | ✅ Manual | `docs/architecture/OVERVIEW.md` | Update diagram |
| **Change workflow** | ✅ Manual | `docs/development/WORKFLOW.md` | Edit file |
| **Add dependency** | ✅ Manual | `docs/architecture/TECHNOLOGY_STACK.md` | Edit file |
| **Refactor internals** | ❌ No docs change | N/A | Code is docs |

#### PR Checklist Template

Add to `.github/pull_request_template.md`:

```markdown
## Documentation Checklist

- [ ] If `.proto` changed: Ran `pnpm docs:generate-api`
- [ ] If architecture changed: Updated `docs/adr/` and `docs/architecture/`
- [ ] If workflow changed: Updated `docs/development/WORKFLOW.md`
- [ ] If new crate added: Updated `docs/architecture/OVERVIEW.md`
- [ ] Ran doc validation: `pnpm docs:validate`
- [ ] All tests pass: `cargo test && pnpm test`
```

---

## 🤖 Guidelines for AI Agents

### Always Do This

1. **Check code first, then docs**
   - Read the actual implementation
   - Only consult docs for WHY, not WHAT

2. **Prefer generation over manual docs**
   - Can it be generated? → Generate it
   - Can code be clearer? → Improve code, not add docs

3. **Update docs only when required**
   - Check update matrix above
   - Don't document what's self-evident

4. **Validate before claiming done**
   ```bash
   # Run these before saying "docs updated"
   cargo test doc_validation
   pnpm docs:validate
   ```

### Never Do This

1. **Don't trust stale docs**
   - Docs may be outdated
   - Code is always current

2. **Don't duplicate code in docs**
   - Code changes → docs drift
   - Reference code, don't copy it

3. **Don't document implementation**
   - "How" belongs in code
   - Docs explain "why"

4. **Don't claim sync without validation**
   - Run tests
   - Check that examples execute

### Decision Tree

```
Need to document something?
│
├─ Can it be generated from code?
│  └─ YES → Set up generation, don't write manually
│
├─ Can code be clearer instead?
│  └─ YES → Improve code (better names, types, structure)
│
├─ Is it explaining WHY (decisions, trade-offs)?
│  └─ YES → Document it (architecture, ADR)
│
├─ Is it explaining HOW (workflow, setup)?
│  └─ YES → Document it (development guides)
│
└─ Is it explaining WHAT (implementation details)?
   └─ NO → Don't document, improve code clarity
```

---

## 📝 Documentation Patterns

### Good Documentation

#### Architecture Decision Record

```markdown
# ADR 0001: Use Hexagonal Architecture

## Status
Accepted

## Context
We need to build a system that can support multiple storage backends
(filesystem, Postgres, DynamoDB) without changing business logic, and
that allows testing business logic without spinning up infrastructure.

## Decision
Use hexagonal architecture (Ports & Adapters) with:
- Pure domain in `adr-domain` (no infrastructure deps)
- Port interfaces in `adr-sdk` (traits like `ADRRepository`)
- Adapter implementations in `adr-adapters` (filesystem, postgres, etc.)

## Consequences

**Pros**:
- Can swap storage without touching business logic
- Can test use cases without infrastructure
- Clear boundaries enforced by compiler

**Cons**:
- More crates to manage
- Need dependency injection
- Slight complexity overhead

## Validation
- ✅ Validated in PoC Phase 1-2
- ✅ CLI and service both use same SDK successfully
```

#### Development Guide

```markdown
# Adding a New Storage Adapter

## Overview
Storage adapters implement the `ADRRepository` trait from `adr-sdk`.

## Steps

1. **Create adapter module** in `crates/adr-adapters/src/`:
   ```rust
   // crates/adr-adapters/src/my_adapter.rs
   use adr_sdk::repository::ADRRepository;
   
   pub struct MyAdapter { /* ... */ }
   
   #[async_trait]
   impl ADRRepository for MyAdapter {
       async fn save(&self, adr: &ADR) -> Result<(), ADRError> {
           // Implementation
       }
   }
   ```

2. **Add feature flag** in `crates/adr-adapters/Cargo.toml`:
   ```toml
   [features]
   my_adapter = ["dep:my-adapter-crate"]
   ```

3. **Export adapter** in `crates/adr-adapters/src/lib.rs`:
   ```rust
   #[cfg(feature = "my_adapter")]
   pub mod my_adapter;
   ```

4. **Test adapter**:
   ```rust
   #[cfg(test)]
   mod tests {
       #[tokio::test]
       async fn test_save() {
           let adapter = MyAdapter::new();
           // Test implementation
       }
   }
   ```

See `filesystem.rs` for reference implementation.
```

### Bad Documentation

❌ **Don't do this**:

```markdown
# adr-sdk Module

## Overview
The adr-sdk module contains the core SDK.

## Files
- `lib.rs` - Library entry point
- `repository.rs` - Repository trait
- `use_cases/` - Use case implementations

## Functions

### create_adr
Creates an ADR.

**Parameters**:
- `title: String` - The title
- `description: String` - The description

**Returns**: `Result<ADR, ADRError>`

**Example**:
```rust
let adr = create_adr(title, description)?;
```
```

**Why bad**:
- Documents WHAT (obvious from code)
- Will drift as code changes
- No WHY (why is there a repository trait?)
- Example trivial (just repeats signature)

✅ **Instead, write clear code**:

```rust
// crates/adr-sdk/src/use_cases/create_adr.rs

/// Creates a new ADR with validated inputs.
/// 
/// Business rules enforced:
/// - Title must be non-empty and < 200 chars
/// - Auto-generates ID based on existing ADRs
/// - Sets status to "proposed"
/// - Records creation timestamp
pub async fn create_adr(
    repository: &dyn ADRRepository,
    title: String,
    description: String,
) -> Result<ADR, ADRError> {
    // Implementation with clear variable names
    // and inline comments for complex logic
}
```

---

## 🚀 Automation Scripts

### Generate API Documentation

**File**: `scripts/generate-api-docs.sh`

```bash
#!/bin/bash
set -e

echo "Generating API documentation from protobuf..."

# Generate Rust types
cargo build

# Generate TypeScript types
cd apps/adr-web
pnpm proto:generate

# Generate markdown docs
cd ../..
./scripts/proto-to-markdown.sh proto/ docs/api/GRPC.md

echo "✅ API documentation generated"
echo "📝 Review: docs/api/GRPC.md"
```

### Validate Documentation

**File**: `scripts/validate-docs.sh`

```bash
#!/bin/bash
set -e

echo "Validating documentation..."

# Check protobuf docs are current
echo "→ Checking API docs..."
cargo test proto_docs_are_current

# Check architecture docs match code
echo "→ Checking architecture docs..."
cargo test architecture_diagram_matches_code

# Check examples in docs work
echo "→ Checking documented examples..."
cargo test all_documented_examples_execute

echo "✅ All documentation validated"
```

---

## 📊 Metrics & Monitoring

### How to Measure Doc Health

**Good Metrics**:
- ✅ Documentation validation test pass rate: 100%
- ✅ Generated doc coverage: 80%+ of API surface
- ✅ Time from code change to doc update: < 1 hour
- ✅ Doc-related PR comments: < 2 per PR

**Bad Metrics** (vanity metrics):
- ❌ Total lines of documentation
- ❌ Number of files in docs/
- ❌ Documentation-to-code ratio

### Warning Signs

**Documentation drift detected if**:
- Validation tests failing
- Examples in docs don't execute
- Architecture diagrams don't match code
- Multiple "docs out of date" issues

**Fix**: Run validation, update docs, add tests to prevent recurrence

---

## 🎓 Learning Resources

### Internal
- **llm.md** - Project-specific patterns
- **docs/architecture/** - How our system works
- **docs/adr/** - Why we made decisions

### External
- [Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)

---

## ✅ Summary Checklist

**Before committing**:
- [ ] Code is self-documenting (clear names, types)
- [ ] Generated docs are current (`pnpm docs:generate-api`)
- [ ] Only documented what code can't express
- [ ] Validation tests pass (`pnpm docs:validate`)
- [ ] Architecture docs match actual structure
- [ ] Examples in docs execute successfully

**Remember**: The best documentation is clear, well-structured code. Write docs for the WHY, not the WHAT.
