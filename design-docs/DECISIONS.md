# CLI Tools Architecture - Problem-Solution Decision Document

## Document Structure
Each problem follows this format:
- **Problem Statement**: What are we solving?
- **Problem Stack**: Where does this sit in the hierarchy?
- **Why This Is A Problem**: Impact and risks
- **Options**: Research and trade-offs
- **Decision**: What we're doing
- **Success Criteria**: How we know it works
- **Metrics**: What to measure
- **Triggers to Revisit**: Evidence-based indicators (not time-based)
- **Risks of Decision**: What could go wrong
- **Migration Cost**: Cost to rollback or change

---

## Problem Stack Overview

```
P1. Multi-Tool System Architecture (STRATEGIC)
    ├── P1.1. Tool Composition Model
    │   ├── P1.1.1. Dependency Management
    │   └── P1.1.2. Plugin Architecture
    ├── P1.2. Code Organization
    │   ├── P1.2.1. Workspace Structure
    │   └── P1.2.2. Shared Framework Design
    └── P1.3. Build & Distribution
        ├── P1.3.1. Binary Distribution Strategy
        └── P1.3.2. Versioning Strategy

P2. Single Source of Truth (ARCHITECTURAL)
    ├── P2.1. Command Definition Location
    ├── P2.2. Documentation Generation
    │   ├── P2.2.1. Doc Format & Location
    │   └── P2.2.2. Doc Generation Timing
    └── P2.3. Example Management
        ├── P2.3.1. Example Definition Format
        └── P2.3.2. Example Validation

P3. Testing Strategy (QUALITY)
    ├── P3.1. Test Co-location vs Centralization
    ├── P3.2. Test-Doc Integration
    │   ├── P3.2.1. Example-as-Test Pattern
    │   └── P3.2.2. Snapshot Testing
    ├── P3.3. Contract Testing
    └── P3.4. Integration Testing

P4. Developer Experience (OPERATIONAL)
    ├── P4.1. Command Development Workflow
    ├── P4.2. Tool Addition/Removal Process
    └── P4.3. Debugging & Introspection
```

---

# P1. Multi-Tool System Architecture

## P1.1. Tool Composition Model

### Problem Statement
How do we structure multiple CLI tools so they can work both independently and as a unified system, without creating tight coupling or unnecessary complexity?

### Problem Stack
- **Parent**: P1 (Multi-Tool System Architecture)
- **Children**: P1.1.1 (Dependency Management), P1.1.2 (Plugin Architecture)
- **Level**: Strategic

### Why This Is A Problem
**Impact:**
- Determines how easily tools can be added, removed, or maintained
- Affects code reuse and duplication
- Influences testing complexity
- Impacts user experience (standalone vs unified)

**Risks of Not Solving:**
- Tools become tightly coupled, can't be released independently
- Duplication across tools increases maintenance burden
- Hard to onboard new tools or deprecate old ones
- Inconsistent user experience across tools

### Options

#### Option A: Monolithic Single Binary
**Description**: One large binary with all tools compiled in, no separation.

**Pros**:
- Simple build process
- No distribution complexity
- Shared code is easy

**Cons**:
- Can't use tools independently
- Binary size bloat (user gets all tools even if they need one)
- Tight coupling makes changes risky
- Can't version tools independently
- Testing is all-or-nothing

**Trade-offs**: Simplicity vs flexibility

#### Option B: Separate Binaries Only (No Unified CLI)
**Description**: Each tool is completely independent, no composition layer.

**Pros**:
- Maximum independence
- Clear boundaries
- Simple mental model per tool
- Easy to version independently

**Cons**:
- No shared patterns enforced
- Users need to install multiple binaries
- Hard to discover related tools
- Potential for inconsistent UX
- Code duplication without framework

**Trade-offs**: Independence vs consistency

#### Option C: Cargo Workspace + Library Pattern + Optional Unified Binary ⭐ CHOSEN
**Description**: Each tool is a library that can be compiled standalone or imported by unified CLI.

**Pros**:
- Tools work independently (cargo build -p tool-a)
- Tools work unified (unified-cli delegates to libraries)
- Hermetic - each tool owns its context
- Shared patterns via framework dependency
- Can version independently
- Users choose standalone or unified
- Low coupling, high cohesion

**Cons**:
- Slightly more complex setup
- Need to maintain both library and binary interfaces
- Workspace coordination needed

**Trade-offs**: Some complexity for maximum flexibility

**Research References**:
- Cargo workspaces: https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
- Library + binary pattern: Common in Rust ecosystem (ripgrep, bat, etc.)
- Plugin architectures: tower (trait-based), mdBook (static plugins)

### Decision
**Chosen**: Option C - Cargo Workspace + Library Pattern + Optional Unified Binary

**Rationale**:
- Maximizes flexibility: tools can be used standalone or unified
- Enables hermetic development: each tool is self-contained
- Supports independent versioning and releases
- Framework dependency provides consistency without coupling
- Industry-standard pattern in Rust ecosystem
- Low migration cost if we need to change approach

### Success Criteria
1. ✅ Can build any tool independently: `cargo build -p tool-a`
2. ✅ Can use any tool standalone: `tool-a --help`
3. ✅ Can use unified CLI: `unified --help`
4. ✅ Adding a tool requires changes only in: new tool crate + unified-cli registration (2 files)
5. ✅ Removing a tool requires changes only in: unified-cli registration (1 file)
6. ✅ Changing a tool doesn't require rebuilding other tools
7. ✅ Shared patterns available via cli-framework dependency

### Metrics
**Quantitative**:
- Time to add new tool: < 30 minutes
- Lines of code in unified-cli: < 100 (mostly registration)
- Build time impact: new tool adds < 5s to workspace build
- Coupling metric: tools have 0 cross-dependencies (only framework)

**Qualitative**:
- Developer feedback: "Easy to add new tools"
- User feedback: "Can use just the tools I need"
- Code review: "Changes are localized to relevant tool"

### Triggers to Revisit

**Evidence that this solution isn't working**:

1. **Coupling Creep Indicator**
   - Any tool starts depending on another tool (not framework)
   - Unified-cli has business logic (not just registration)
   - Changes to one tool frequently break others

2. **Complexity Indicator**
   - Time to add new tool exceeds 2 hours
   - Developers report confusion about where code goes
   - PR reviews frequently ask for restructuring

3. **Performance Indicator**
   - Workspace build time exceeds 2 minutes for clean builds
   - Incremental builds of one tool trigger rebuilds of others
   - Binary sizes indicate unnecessary bloat

4. **User Feedback Indicator**
   - Users consistently choose only unified OR only standalone (never both)
   - Multiple requests to separate tools into different repos
   - Complaints about installation complexity

5. **Maintenance Indicator**
   - More than 20% of changes touch multiple unrelated tools
   - Difficult to track which tool owns which functionality
   - Version conflicts between tool releases become common

### Risks of Decision

1. **Workspace Complexity**
   - Risk: Developers unfamiliar with workspaces may struggle
   - Mitigation: Comprehensive docs + Makefile shortcuts
   - Severity: Low (one-time learning curve)

2. **Library API Surface**
   - Risk: Need to maintain stable library APIs for unified-cli
   - Mitigation: Semantic versioning + CliTool trait contract
   - Severity: Medium (ongoing maintenance)

3. **Build System Coordination**
   - Risk: Workspace dependencies can create version conflicts
   - Mitigation: Workspace-level dependency management
   - Severity: Low (tooling handles this well)

4. **Binary Duplication**
   - Risk: Each tool compiled standalone duplicates framework code
   - Mitigation: Dynamic linking (future), thin binaries
   - Severity: Low (disk space is cheap)

### Migration Cost

**To Monolithic (Option A)**:
- Cost: Medium
- Steps:
  1. Merge all tool crates into one
  2. Remove library boundaries
  3. Update build scripts
- Time: ~1 week
- Risk: Lose independence, hard to reverse

**To Separate Repos (Option B)**:
- Cost: Low
- Steps:
  1. Move each tool to its own repo
  2. Publish cli-framework as separate crate
  3. Remove unified-cli or make it depend on published crates
- Time: ~2 days
- Risk: Lose unified experience, but tools still work

**Rollback Cost**: Low - each tool is already independent, just need to change distribution

---

## P1.1.1. Dependency Management

### Problem Statement
How do we manage shared dependencies across multiple tool crates while avoiding version conflicts and keeping builds fast?

### Problem Stack
- **Parent**: P1.1 (Tool Composition Model)
- **Siblings**: P1.1.2 (Plugin Architecture)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Version conflicts can break builds or cause subtle bugs
- Inconsistent versions lead to increased binary size
- Dependency updates become risky without centralized control
- Security updates need to propagate to all tools

**Risks of Not Solving:**
- Build failures due to dependency conflicts
- Security vulnerabilities in outdated dependencies
- Wasted time debugging version mismatches
- Bloated binaries from duplicate dependencies

### Options

#### Option A: Each Tool Manages Own Dependencies
**Description**: Each tool's Cargo.toml independently specifies all dependencies.

**Pros**:
- Maximum flexibility per tool
- No coordination needed
- Tools truly independent

**Cons**:
- Version drift inevitable
- Manual work to keep aligned
- Multiple versions of same crate in build
- Security updates require touching every tool

**Trade-offs**: Independence vs consistency

#### Option B: Workspace-Level Dependency Management ⭐ CHOSEN
**Description**: Use `[workspace.dependencies]` to define versions once, tools reference without version.

**Pros**:
- Single source of truth for versions
- Guaranteed consistency
- Security updates in one place
- Cargo deduplicates automatically
- Still allows tool-specific overrides if needed

**Cons**:
- Requires Cargo 1.64+ (2022 edition)
- All tools must use same major versions

**Trade-offs**: Minor version flexibility for guaranteed consistency

**Research References**:
- RFC 2906: https://github.com/rust-lang/rfcs/blob/master/text/2906-cargo-workspace-deduplicate.md
- Cargo book: https://doc.rust-lang.org/cargo/reference/workspaces.html#the-dependencies-table

### Decision
**Chosen**: Option B - Workspace-Level Dependency Management

**Rationale**:
- Prevents version conflicts automatically
- Makes security updates simple (one file)
- Reduces binary size through deduplication
- Industry best practice for workspaces
- Still allows per-tool overrides when needed

### Success Criteria
1. ✅ All common dependencies defined in workspace Cargo.toml
2. ✅ No version conflicts in `cargo tree` output
3. ✅ Tools can use dependencies without specifying versions
4. ✅ Updating dependency version requires changing one file

### Metrics
**Quantitative**:
- Number of version conflicts: 0
- Time to update common dependency: < 5 minutes
- Binary size reduction: ~10-30% from deduplication

**Qualitative**:
- Zero "dependency hell" incidents
- Smooth dependency updates

### Triggers to Revisit

**Evidence-based triggers**:

1. **Version Conflict Indicator**
   - Frequent cargo version resolution failures
   - Multiple versions of same crate appearing in builds
   - Developers needing to override workspace versions regularly

2. **Flexibility Indicator**
   - More than 2 tools need different major versions of a core dependency
   - Workspace version constraints blocking tool development
   - Requests to split workspace due to dependency incompatibility

3. **Update Friction Indicator**
   - Dependency updates regularly break multiple tools
   - Security updates take > 1 day to propagate
   - Cargo.lock conflicts in multiple PRs

### Risks of Decision

1. **Version Lock-in**
   - Risk: All tools must use compatible versions
   - Mitigation: Choose stable, compatible dependencies
   - Severity: Low

2. **Breaking Change Propagation**
   - Risk: Major version update affects all tools at once
   - Mitigation: Feature flags, gradual migration
   - Severity: Medium

### Migration Cost
**Rollback to Option A**: Very low (~1 hour to add versions to each Cargo.toml)

---

## P1.2. Code Organization

### Problem Statement
How do we structure code within the workspace to maximize clarity, maintainability, and discoverability while minimizing coupling?

### Problem Stack
- **Parent**: P1 (Multi-Tool System Architecture)
- **Children**: P1.2.1 (Workspace Structure), P1.2.2 (Shared Framework Design)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Affects onboarding time for new developers
- Determines how easy it is to find and modify code
- Influences testing and build patterns
- Impacts refactoring and evolution

**Risks of Not Solving:**
- Code scattered with no clear organization
- Difficult to understand ownership
- Duplication due to inability to find existing code
- Merge conflicts from poor separation

### Options

#### Option A: Flat Structure
```
crates/
├── tool-a/
├── tool-b/
├── tool-c/
├── cli-framework/
└── unified-cli/
```

**Pros**:
- Simple, flat hierarchy
- Easy to list all tools
- No nesting to navigate

**Cons**:
- No grouping of related concerns
- Framework not visually distinct from tools
- Scales poorly (50 tools = 50 directories at same level)

#### Option B: Categorized Structure
```
crates/
├── framework/
│   └── cli-framework/
├── tools/
│   ├── tool-a/
│   ├── tool-b/
│   └── tool-c/
└── unified/
    └── unified-cli/
```

**Pros**:
- Clear grouping by purpose
- Scales to many tools
- Visually distinct layers

**Cons**:
- More nesting
- Paths become longer
- Migration needed if structure changes

#### Option C: Hybrid (Flat for Now, Migrate When > 10 Tools) ⭐ CHOSEN
**Description**: Start flat, add structure when needed.

**Pros**:
- Start simple (YAGNI principle)
- Easy to refactor when needed (Cargo supports path changes)
- No premature optimization
- Clear migration trigger

**Cons**:
- Will need migration eventually
- Could argue for structure from the start

**Research**:
- YAGNI principle: Don't add structure until it's needed
- Cargo workspace refactoring is safe (just path changes)
- Examples: ripgrep (flat), bat (flat), many Rust projects start flat

### Decision
**Chosen**: Option C - Hybrid (Start Flat, Migrate When Needed)

**Rationale**:
- Simplicity for early stage (<10 tools)
- Easy migration path (just Cargo.toml paths)
- No functional impact (just organization)
- Common Rust pattern

**Structure**:
```
crates/
├── cli-framework/        # Foundation
├── tool-a/              # Tools (flat for now)
├── tool-b/
├── tool-c/
└── unified-cli/         # Composition
```

### Success Criteria
1. ✅ Any developer can find a tool in < 10 seconds
2. ✅ Clear distinction between framework, tools, unified
3. ✅ Flat structure works well for current number of tools

### Metrics
**Quantitative**:
- Number of tools in workspace: < 10 = flat structure
- Time to locate code: < 30 seconds

**Qualitative**:
- Developer feedback: "Easy to navigate"
- No complaints about structure

### Triggers to Revisit

**Evidence-based triggers**:

1. **Scale Indicator**
   - Number of tool crates exceeds 10
   - Difficulty finding specific tool among many
   - Requests to group related tools

2. **Confusion Indicator**
   - New developers ask "where should new tool go?"
   - Frequent questions about what's a tool vs framework
   - Discussion about adding subdirectories

3. **Maintenance Indicator**
   - Desire to separate internal vs public tools
   - Need for different release cadences by category
   - Multiple "types" of tools emerging

### Risks of Decision

1. **Migration Needed Later**
   - Risk: Will need to restructure eventually
   - Mitigation: Cargo makes this easy (just path updates)
   - Severity: Very Low

2. **Temporary Clutter**
   - Risk: Directory listing gets long with 10 tools
   - Mitigation: Trigger set at 10 tools
   - Severity: Very Low

### Migration Cost
**To Categorized (Option B)**:
- Cost: Very Low
- Steps: Move directories, update paths in Cargo.toml
- Time: 30 minutes
- Risk: None (Cargo will catch broken paths)

---

## P2. Single Source of Truth

### Problem Statement
How do we ensure command definitions, documentation, tests, and examples never drift apart, while maintaining DRY principles?

### Problem Stack
- **Parent**: Root (Architecture)
- **Children**: P2.1 (Command Definition), P2.2 (Documentation), P2.3 (Examples)
- **Level**: Architectural

### Why This Is A Problem
**Impact:**
- Documentation drift from code is extremely common
- Out-of-date examples break user trust
- Tests that don't match actual CLI behavior give false confidence
- Maintenance burden multiplies with duplication

**Risks of Not Solving:**
- Users follow outdated docs, get frustrated
- Tests pass but CLI is broken
- Examples don't work, damaging credibility
- Time wasted synchronizing multiple sources
- Bugs from inconsistency

### Options

#### Option A: Manual Synchronization
**Description**: Write command definitions, docs, tests, examples separately. Keep them in sync manually.

**Pros**:
- Most flexible (each artifact optimized independently)
- No tooling complexity
- Common pattern (most projects)

**Cons**:
- WILL drift (not if, but when)
- Manual work to synchronize
- Easy to forget to update all places
- No guarantee of consistency
- High maintenance burden

**Trade-offs**: Flexibility vs guaranteed consistency

#### Option B: Generate Everything from Separate Schema
**Description**: Define commands in YAML/JSON/DSL, generate code, docs, tests from schema.

**Pros**:
- True single source of truth
- Can't drift (everything generated)
- Tooling enforces consistency

**Cons**:
- Complex tooling needed
- Less idiomatic (not standard Rust)
- Harder to customize
- Debugging generated code is difficult
- Schema becomes a bottleneck

**Trade-offs**: Guaranteed consistency vs development complexity

#### Option C: Code as Schema + Strategic Generation ⭐ CHOSEN
**Description**: Command definitions in code (clap), examples in code (structs), everything else derives from these.

**Pros**:
- Code is the single source of truth
- Type-safe (Rust compiler enforces)
- Idiomatic Rust (using clap)
- Can extract metadata for docs/tests
- No complex code generation
- Easy to debug (it's just code)

**Cons**:
- Some generation needed (docs from clap)
- Need helpers for test-example integration

**Trade-offs**: Some tooling for massive consistency gains

**Research**:
- Clap design philosophy: code as schema
- Similar patterns: structopt, argh
- Industry: Click (Python), Commander (Node) use similar approaches

### Decision
**Chosen**: Option C - Code as Schema + Strategic Generation

**Rationale**:
- Leverages Rust's type system for safety
- Uses industry-standard tools (clap)
- Minimal custom tooling needed
- Easy to understand and debug
- Proven pattern in Rust ecosystem

**Implementation**:
```
Code (commands/mod.rs)
  ├─→ definitions (clap Command)    ← Single source of truth
  ├─→ examples (const structs)      ← Single source of truth
  └─→ handlers (execution logic)
      ↓
  ┌───┴────┬──────────┬───────────┐
  │        │          │           │
CLI    Tests      Docs      Validation
(clap)  (import)  (extract)  (compile-time)
```

### Success Criteria
1. ✅ Command definition exists in exactly one place
2. ✅ Changing command structure breaks tests if examples invalid
3. ✅ Documentation reflects actual CLI behavior (generated)
4. ✅ Examples are executable and tested
5. ✅ No manual synchronization needed

### Metrics
**Quantitative**:
- Number of places command structure defined: 1 (commands/mod.rs)
- Documentation coverage: 100% of commands documented
- Example coverage: 100% of examples tested
- Drift incidents: 0 (impossible due to architecture)

**Qualitative**:
- Developer feedback: "Easy to keep in sync"
- User feedback: "Examples actually work"
- Zero "docs are outdated" complaints

### Triggers to Revisit

**Evidence-based triggers**:

1. **Drift Detection**
   - Any instance of docs/tests/examples out of sync
   - Manual synchronization work happening
   - Bugs from inconsistency

2. **Complexity Indicator**
   - Clap becomes limiting (can't express what we need)
   - Custom macro/proc-macro needed just for definitions
   - Developers avoiding command changes due to complexity

3. **Maintenance Burden**
   - Time to add new command > 30 minutes (due to duplication)
   - Regular issues with sync between artifacts
   - Requests for "better tooling" to keep things in sync

4. **Scale Indicator**
   - Hundreds of commands (tooling may need to improve)
   - Multi-language support needed (may need schema)
   - External integrations need machine-readable definitions

### Risks of Decision

1. **Clap Limitations**
   - Risk: Clap may not support all use cases
   - Mitigation: Clap is very mature, handles 99% of CLI patterns
   - Severity: Low

2. **Doc Generation Quality**
   - Risk: Generated docs may not be as good as hand-written
   - Mitigation: Supplement with manual docs where needed
   - Severity: Low

3. **Learning Curve**
   - Risk: Team needs to learn "code as schema" pattern
   - Mitigation: Good documentation, examples
   - Severity: Low

### Migration Cost

**To Manual Sync (Option A)**: Very Low (~1 day to separate)
**To Schema-Based (Option B)**: High (~2 weeks to build tooling)

**Rollback**: Low - just stop generating, write manually

---

## P2.1. Command Definition Location

### Problem Statement
Where exactly within each tool crate should command definitions live to maximize discoverability, testability, and reusability?

### Problem Stack
- **Parent**: P2 (Single Source of Truth)
- **Siblings**: P2.2 (Documentation Generation), P2.3 (Example Management)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Determines how easy it is to find and modify commands
- Affects test imports and reusability
- Influences separation of concerns
- Impacts build/compile times

**Risks of Not Solving:**
- Definitions scattered across multiple files
- Hard to import for tests
- Business logic mixed with CLI parsing
- Difficult to generate docs

### Options

#### Option A: Inline in main.rs/lib.rs
```rust
// src/lib.rs
pub fn run() {
    let matches = Command::new("tool")
        .arg(...)  // Definitions inline
        .get_matches();
    execute(matches);
}
```

**Pros**:
- Simple for small tools
- Everything in one place
- No extra files

**Cons**:
- Hard to test definitions separately
- Can't reuse definitions
- File becomes large
- Mixed concerns (definition + execution)

#### Option B: Separate commands.rs Module
```rust
// src/commands.rs
pub fn build_cli() -> Command { ... }
```

**Pros**:
- Separated from execution
- Can import for tests
- Single file for all commands

**Cons**:
- Gets large with many commands
- All subcommands in one file
- Hard to organize complex CLIs

#### Option C: Structured commands/ Module ⭐ CHOSEN
```rust
// src/commands/mod.rs
pub mod definitions { ... }
pub mod examples { ... }
pub mod handlers { ... }
```

**Pros**:
- Clear separation of concerns
- Easy to import specific pieces
- Scales well (can split by subcommand)
- Organized by purpose
- Testable in isolation

**Cons**:
- More files/structure
- Slight overkill for tiny tools

### Decision
**Chosen**: Option C - Structured commands/ Module

**Rationale**:
- Clear organization: definitions, examples, handlers separate
- Easy to import: `use crate::commands::definitions`
- Scales: can split into multiple files if needed
- Testable: each module independently testable
- Consistent: same structure across all tools

**Structure**:
```rust
src/
└── commands/
    └── mod.rs
        ├── pub mod definitions   // clap Command builders
        ├── pub mod examples      // Example const structs
        └── pub mod handlers      // Execution logic
```

### Success Criteria
1. ✅ Tests can import: `use tool::commands::definitions`
2. ✅ Clear what file to edit for: new command, new example, fix bug
3. ✅ Definitions have zero execution logic
4. ✅ Can build Command without executing anything

### Metrics
**Quantitative**:
- Time to find command definition: < 10 seconds
- Lines per file: < 500 (split if larger)

**Qualitative**:
- Developer feedback: "Easy to find what I need"
- No confusion about where to add commands

### Triggers to Revisit

1. **Scale Indicator**
   - commands/mod.rs exceeds 500 lines
   - More than 10 subcommands
   - Difficulty navigating single file

2. **Confusion Indicator**
   - Questions about where to add commands
   - Code in wrong modules

3. **Flexibility Indicator**
   - Need to share command definitions across tools
   - Complex command hierarchies

### Risks of Decision

1. **Over-engineering for Simple Tools**
   - Risk: Extra structure for 3-command tool
   - Mitigation: Consistent pattern worth it
   - Severity: Very Low

### Migration Cost
**To Option A or B**: Very Low (30 minutes to consolidate files)

---

## P2.2. Documentation Generation

### Problem Statement
When and how should documentation be generated from command definitions to ensure it's always up-to-date without creating friction in the development workflow?

### Problem Stack
- **Parent**: P2 (Single Source of Truth)
- **Children**: P2.2.1 (Doc Format), P2.2.2 (Doc Generation Timing)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Determines if docs are actually kept in sync
- Affects developer workflow friction
- Influences doc quality and discoverability
- Impacts CI/CD complexity

**Risks of Not Solving:**
- Documentation becomes outdated
- Manual doc generation forgotten
- Docs out of sync with code
- Users trust docs that are wrong

### Options

#### Option A: Manual Generation (On-Demand)
**Description**: Developers run `cargo run --example gen-docs` when they remember.

**Pros**:
- Simple - no automation needed
- No build-time overhead
- Developer controls when

**Cons**:
- WILL be forgotten
- No enforcement
- Easy to commit outdated docs
- Requires discipline

#### Option B: Build-Time Generation (build.rs)
**Description**: build.rs generates docs every build.

**Pros**:
- Always up-to-date
- Automatic, no thinking
- Can't forget

**Cons**:
- Slower builds (runs every time)
- Build.rs complexity
- Hard to debug
- Generated files in source tree (gitignore or commit?)

#### Option C: CI-Time Generation (On PR)
**Description**: CI generates docs, commits them or checks if they match.

**Pros**:
- No developer friction
- Enforced by CI
- Fast local builds

**Cons**:
- CI complexity
- Extra commits or failed checks
- Delay in feedback

#### Option D: Hybrid (Test + CI) ⭐ CHOSEN
**Description**:
- `cargo test generate_docs` - test that generates docs
- CI checks docs are up-to-date
- Developers run tests before committing (normal workflow)

**Pros**:
- No special commands to remember
- Normal test workflow
- CI enforces
- No build-time overhead
- Can review doc changes in PR

**Cons**:
- Need to remember to commit generated docs
- Slightly larger test suite

### Decision
**Chosen**: Option D - Hybrid (Test + CI)

**Rationale**:
- Fits existing workflow (developers run tests)
- No new commands to learn
- CI provides safety net
- Generated docs are reviewable in PRs
- No build-time penalty

**Implementation**:
```rust
#[test]
fn generate_docs() {
    let output_dir = PathBuf::from("docs/generated");
    docs::generate_all(&output_dir).unwrap();
}

#[test]
fn docs_are_up_to_date() {
    // Generate to temp dir
    // Compare with committed docs
    // Fail if different
}
```

### Success Criteria
1. ✅ Docs generated as part of normal test run
2. ✅ CI fails if docs out of date
3. ✅ Generated docs committed and reviewable
4. ✅ No extra commands to remember

### Metrics
**Quantitative**:
- Docs update time: < 1 second (during test run)
- CI check time: < 30 seconds
- Doc drift incidents: 0 (caught by CI)

**Qualitative**:
- Developer feedback: "Just works"
- No forgotten doc updates

### Triggers to Revisit

1. **Friction Indicator**
   - Developers complaining about test slowdown
   - Skipping doc tests regularly
   - CI failures frustrating developers

2. **Quality Indicator**
   - Generated docs consistently need manual fixes
   - Docs not actually useful
   - Users ignoring docs

3. **Scale Indicator**
   - Doc generation takes > 5 seconds
   - Many tools = slow test suite

### Risks of Decision

1. **Test Suite Slowdown**
   - Risk: Doc generation slows tests
   - Mitigation: Make generation fast, can be separate test
   - Severity: Low

2. **Git History Noise**
   - Risk: Generated docs clutter commits
   - Mitigation: Worth it for safety, can squash
   - Severity: Very Low

### Migration Cost
**To Build-Time**: Medium (need to write build.rs)
**To Manual**: Low (just remove test)

---

## P2.3. Example Management

### Problem Statement
How do we define, store, and validate examples so they serve as both documentation and executable tests?

### Problem Stack
- **Parent**: P2 (Single Source of Truth)
- **Children**: P2.3.1 (Example Format), P2.3.2 (Example Validation)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Examples are critical for user onboarding
- Broken examples damage credibility
- Duplication between test code and docs
- Hard to keep examples current

**Risks of Not Solving:**
- Examples break and no one notices
- Test commands != doc commands
- Users copy-paste broken examples
- Maintenance burden

### Options

#### Option A: Examples as Strings in Tests
```rust
#[test]
fn test_example() {
    let output = run_command("tool-a --input hello");
    assert_eq!(output, "expected");
}
```

**Pros**:
- Simple
- Standard test pattern

**Cons**:
- Can't reuse in docs
- No metadata (description, tags)
- Hard to generate docs from

#### Option B: Examples as External Files
```
examples/
├── basic.sh
├── advanced.sh
└── README.md
```

**Pros**:
- Separated from code
- Easy to run manually
- Can be complex scripts

**Cons**:
- Not validated automatically
- Hard to test programmatically
- Drift from tests

#### Option C: Examples as Typed Structs ⭐ CHOSEN
```rust
pub const BASIC_EXAMPLE: Example = Example {
    name: "basic",
    description: "Process a simple input",
    command: "tool-a process --input hello",
    expected_output: Some("Processed: hello"),
    tags: &["basic", "process"],
};
```

**Pros**:
- Type-safe, compile-time checked
- Can import in tests AND docs
- Rich metadata available
- Single source of truth
- Can validate command syntax at compile time

**Cons**:
- Slightly verbose
- All examples in code (not separate files)

### Decision
**Chosen**: Option C - Examples as Typed Structs

**Rationale**:
- Examples become testable data
- Can't drift (imported by tests and docs)
- Rich metadata for organization
- Type safety ensures validity
- Co-located with command definitions

**Structure**:
```rust
// commands/mod.rs
pub mod examples {
    #[derive(Debug, Clone)]
    pub struct Example {
        pub name: &'static str,
        pub description: &'static str,
        pub command: &'static str,
        pub expected_output: Option<&'static str>,
        pub tags: &'static [&'static str],
    }
    
    pub const BASIC: Example = Example { ... };
    pub const ADVANCED: Example = Example { ... };
    
    pub fn all() -> Vec<Example> {
        vec![BASIC, ADVANCED]
    }
    
    pub fn by_tag(tag: &str) -> Vec<Example> {
        all().into_iter()
            .filter(|e| e.tags.contains(&tag))
            .collect()
    }
}
```

### Success Criteria
1. ✅ Examples defined once, used in tests and docs
2. ✅ All examples are executable
3. ✅ Adding example adds it to tests and docs automatically
4. ✅ Can filter/organize examples by tags

### Metrics
**Quantitative**:
- Example coverage: 100% tested
- Example breakage: 0 (tests catch)
- Time to add example: < 2 minutes

**Qualitative**:
- User feedback: "Examples work!"
- No drift incidents

### Triggers to Revisit

1. **Complexity Indicator**
   - Examples need complex setup (can't be one command string)
   - Need multi-step examples
   - Examples require external state/files

2. **Scale Indicator**
   - Hundreds of examples (code file too large)
   - Need different example formats
   - Interactive examples needed

3. **Flexibility Indicator**
   - Need examples that can't be represented as strings
   - Platform-specific examples
   - Examples with variable outputs

### Risks of Decision

1. **Limited to Simple Examples**
   - Risk: Complex examples hard to represent
   - Mitigation: Can extend struct or add external examples
   - Severity: Low

2. **Code Bloat**
   - Risk: Many examples = large const definitions
   - Mitigation: Can split into separate files
   - Severity: Very Low

### Migration Cost
**To External Files**: Low (1-2 hours to script conversion)
**To Test-Only**: Very Low (just remove struct wrapper)

---

## P3. Testing Strategy

### Problem Statement
How do we structure tests across the workspace to ensure quality, avoid duplication, enable fast feedback, and support both isolated and integrated testing?

### Problem Stack
- **Parent**: Root (Architecture)
- **Children**: P3.1 (Co-location), P3.2 (Test-Doc Integration), P3.3 (Contract Testing), P3.4 (Integration Testing)
- **Level**: Quality

### Why This Is A Problem
**Impact:**
- Determines confidence in changes
- Affects development velocity (slow tests = slow feedback)
- Influences refactoring safety
- Impacts bug detection rate

**Risks of Not Solving:**
- Bugs reach production
- Changes break things unpredictably
- Slow test suite blocks development
- Test duplication wastes time

### Options

#### Option A: Centralized E2E Tests Only
**Description**: All tests in workspace-level `tests/` directory.

**Pros**:
- Single place to find all tests
- Easy to test interactions
- Shared fixtures

**Cons**:
- Not hermetic (changes affect all tests)
- Slow (can't isolate)
- Hard to determine what tests belong to what
- Tool changes require running entire suite

#### Option B: Fully Hermetic (Each Crate Tests Itself) ⭐ CHOSEN
**Description**: Each tool has its own tests/, unified-cli only tests composition.

**Pros**:
- Fast (`cargo test -p tool-a`)
- Hermetic (tool changes only run its tests)
- Clear ownership
- Parallel testing

**Cons**:
- Test utility duplication (mitigated by framework)
- Harder to test cross-tool interactions (but we don't need this)

### Decision
**Chosen**: Option B - Fully Hermetic Testing

**Rationale**:
- Tools are independent, tests should be too
- Fast feedback (test only what changed)
- Clear ownership (test lives with code)
- Parallel CI (test each tool independently)
- Framework provides shared test utilities

### Success Criteria
1. ✅ Each tool's tests run in < 10 seconds
2. ✅ Changing tool-a doesn't require testing tool-b
3. ✅ Can run `cargo test -p tool-a` in isolation
4. ✅ Test utilities shared via cli-framework

### Metrics
**Quantitative**:
- Average test time per tool: < 10s
- Test isolation: 100% (no cross-dependencies)
- Test coverage: > 80% per tool

**Qualitative**:
- Fast feedback loop
- Developer satisfaction with test speed

### Triggers to Revisit

1. **Tool Interaction Indicator**
   - Tools start depending on each other
   - Need to test cross-tool workflows
   - Unified CLI becomes more than registry

2. **Duplication Indicator**
   - Significant test utility duplication
   - Copy-pasting test code between tools
   - Framework not providing needed utilities

3. **Performance Indicator**
   - Individual tool tests exceed 30s
   - Test suite too slow for CI
   - Developers skip tests due to speed

### Risks of Decision

1. **Missed Integration Bugs**
   - Risk: Won't catch issues in tool composition
   - Mitigation: Unified-cli has its own tests
   - Severity: Low (tools are independent)

2. **Framework Dependency**
   - Risk: All tools depend on test framework
   - Mitigation: Framework is well-designed
   - Severity: Very Low

### Migration Cost
**To Centralized**: Medium (2-3 days to consolidate)
**Rollback**: Low (tests stay where they are)

---

## P3.2.1. Example-as-Test Pattern

### Problem Statement
How do we ensure every example in documentation is actually tested and works?

### Problem Stack
- **Parent**: P3.2 (Test-Doc Integration)
- **Siblings**: P3.2.2 (Snapshot Testing)
- **Level**: Tactical

### Why This Is A Problem
**Impact:**
- Broken examples destroy user trust
- Manual testing of examples is error-prone
- Example code drift from actual functionality
- No validation that documented commands work

**Risks of Not Solving:**
- Users copy broken examples
- Lose credibility
- Time wasted debugging "examples"
- Documentation becomes unreliable

### Options

#### Option A: Separate Tests and Examples
**Description**: Write tests, write examples independently.

**Pros**:
- Flexibility in each

**Cons**:
- WILL drift
- Double maintenance
- No guarantee examples work

#### Option B: Examples Generate Tests
**Description**: Parse example commands in docs, generate tests.

**Pros**:
- Can't forget to test examples

**Cons**:
- Complex parsing
- Limited to simple examples
- Fragile

#### Option C: Examples ARE Tests ⭐ CHOSEN
**Description**: Example structs imported and executed by tests.

```rust
#[test]
fn test_basic_example() {
    let ex = examples::BASIC;
    let result = execute(ex.command);
    assert!(result.is_ok());
}

#[test]
fn all_examples_work() {
    for ex in examples::all() {
        assert!(execute(ex.command).is_ok());
    }
}
```

**Pros**:
- Can't drift (same data)
- Examples guaranteed tested
- Simple implementation
- No duplication

**Cons**:
- Examples must be executable (not pseudo-code)

### Decision
**Chosen**: Option C - Examples ARE Tests

**Rationale**:
- Impossible for examples to drift
- Every example automatically tested
- Simple: just import and run
- Examples become executable specification

### Success Criteria
1. ✅ Every example has corresponding test
2. ✅ Test suite catches broken examples
3. ✅ Adding example automatically tests it
4. ✅ No separate test command strings

### Metrics
**Quantitative**:
- Example test coverage: 100%
- Broken examples caught: 100%

**Qualitative**:
- User feedback: "Examples work"
- Zero "example doesn't work" issues

### Triggers to Revisit

1. **Complexity Indicator**
   - Need pseudo-code examples (not executable)
   - Examples require extensive setup
   - Platform-specific examples

2. **Performance Indicator**
   - Too many examples slow down tests
   - Examples take long to execute

### Risks of Decision

1. **Example Simplicity Constraint**
   - Risk: Can only show executable examples
   - Mitigation: Most examples should be executable anyway
   - Severity: Low

### Migration Cost
**Rollback**: Very Low (just remove test imports)

---

## P4. Developer Experience

### Problem Statement
How do we minimize friction and cognitive load for developers working on CLI tools while maintaining quality and consistency?

### Problem Stack
- **Parent**: Root (Architecture)
- **Children**: P4.1 (Command Development), P4.2 (Tool Addition), P4.3 (Debugging)
- **Level**: Operational

### Why This Is A Problem
**Impact:**
- Determines development velocity
- Affects developer satisfaction and retention
- Influences code quality
- Impacts onboarding time

**Risks of Not Solving:**
- Developers avoid adding features (too complex)
- High onboarding time (weeks instead of hours)
- Inconsistency due to confusion
- Mistakes due to complexity

### Options

#### Option A: No Conventions (Figure It Out)
**Description**: No standards, everyone does it their way.

**Pros**:
- Maximum flexibility
- No upfront investment

**Cons**:
- Chaos
- Inconsistency
- High cognitive load
- Hard to review

#### Option B: Heavy Tooling (Scaffolding/Generators)
**Description**: CLI tools to generate everything: `cli-tool new my-tool`.

**Pros**:
- Very low friction
- Consistency enforced
- Fast to start

**Cons**:
- Tooling maintenance burden
- Less flexible
- Can be opaque

#### Option C: Documentation + Examples + Makefile ⭐ CHOSEN
**Description**: Clear docs, example tool, Makefile shortcuts.

**Pros**:
- Transparency (just code)
- Flexible (modify as needed)
- Low maintenance
- Easy to understand

**Cons**:
- Requires reading docs
- Manual setup

### Decision
**Chosen**: Option C - Documentation + Examples + Makefile

**Rationale**:
- No magic, just patterns
- Easy to customize
- Low maintenance burden
- Developers understand what's happening
- Can evolve to Option B if needed

**Implementation**:
```makefile
# Makefile
.PHONY: test
test:
    cargo test --workspace

.PHONY: test-tool
test-tool:
    cargo test -p $(tool)

.PHONY: add-tool
add-tool:
    @echo "Creating new tool: $(name)"
    @mkdir -p crates/$(name)/src/{bin,commands}
    @mkdir -p crates/$(name)/tests
    @echo "See docs/NEW_TOOL.md for next steps"
```

### Success Criteria
1. ✅ Onboarding doc exists and is followed
2. ✅ Can add new tool in < 30 minutes
3. ✅ Common tasks have Makefile shortcuts
4. ✅ Example tool demonstrates all patterns

### Metrics
**Quantitative**:
- Time to onboard new developer: < 4 hours
- Time to add new tool: < 30 minutes
- Time to add new command: < 15 minutes

**Qualitative**:
- Developer feedback: "Easy to get started"
- Code review: "Follows patterns"

### Triggers to Revisit

1. **Complexity Indicator**
   - Onboarding time exceeds 1 day
   - Frequent questions about "how do I..."
   - Developers avoid adding features

2. **Consistency Indicator**
   - Code reviews frequently request restructuring
   - Tools diverge significantly in structure
   - Many "wrong way" implementations

3. **Scale Indicator**
   - Adding new tool takes > 2 hours
   - Makefile becomes unwieldy
   - Need for more automation

### Risks of Decision

1. **Documentation Drift**
   - Risk: Docs become outdated
   - Mitigation: Docs are code-adjacent, reviewed
   - Severity: Low

2. **Flexibility Excess**
   - Risk: Too much freedom leads to inconsistency
   - Mitigation: Code reviews enforce patterns
   - Severity: Medium

### Migration Cost
**To Heavy Tooling**: Medium (2-3 weeks to build)
**Rollback**: Zero (docs stay useful)

---

## Summary: Decision Registry

| ID | Problem | Decision | Status | Revisit Trigger |
|---|---|---|---|---|
| P1.1 | Tool Composition | Cargo Workspace + Library Pattern | ✅ Active | Tool coupling detected |
| P1.1.1 | Dependencies | Workspace-level management | ✅ Active | Version conflicts increase |
| P1.2 | Code Organization | Flat structure until > 10 tools | ✅ Active | > 10 tools |
| P2 | Single Source of Truth | Code as schema + generation | ✅ Active | Drift detected |
| P2.1 | Command Location | Structured commands/ module | ✅ Active | Files exceed 500 lines |
| P2.2 | Doc Generation | Hybrid (test + CI) | ✅ Active | Developer friction |
| P2.3 | Example Management | Typed structs | ✅ Active | Complex examples needed |
| P3 | Testing Strategy | Hermetic per-tool | ✅ Active | Tool interaction needed |
| P3.2.1 | Example Testing | Examples ARE tests | ✅ Active | Non-executable examples |
| P4 | Developer Experience | Docs + Examples + Makefile | ✅ Active | Onboarding > 1 day |

---

## Metrics Dashboard

Track these metrics to monitor decision health:

### Architecture Health
- **Tool Independence**: 0 cross-dependencies (framework only)
- **Coupling Score**: Lines in unified-cli < 100
- **Build Time**: Per-tool build < 30s

### Quality Metrics
- **Test Coverage**: > 80% per tool
- **Example Coverage**: 100% tested
- **Documentation Coverage**: 100% of commands
- **Drift Incidents**: 0 (architectural guarantee)

### Developer Experience
- **Onboarding Time**: < 4 hours
- **Time to Add Tool**: < 30 minutes
- **Time to Add Command**: < 15 minutes
- **Time to Update Dependency**: < 5 minutes

### User Experience
- **Example Success Rate**: 100% (tested)
- **Documentation Accuracy**: 100% (generated)
- **Standalone Usage**: All tools work standalone
- **Unified Usage**: All tools work in unified-cli

---

*This document should be updated when any decision is revisited or changed.*
