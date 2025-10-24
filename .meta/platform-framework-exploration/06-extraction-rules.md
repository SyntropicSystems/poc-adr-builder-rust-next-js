# Extraction Rules: When and How to Share Code

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Rule of two/three philosophy
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What's foundational (extract immediately)
- ← [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What's emergent (rule of two/three)
- ← [04-repository-strategy.md](./04-repository-strategy.md) - Where extracted code goes
- ← [05-technology-integration.md](./05-technology-integration.md) - Technology-specific extraction

---

## Context

### The Extraction Problem

Code sharing is a double-edged sword:

**Extract Too Early** (premature abstraction):
- ❌ Wrong abstractions that don't fit real usage
- ❌ Over-engineered for theoretical cases
- ❌ Coordination overhead for every change
- ❌ Wasted effort on unused features
- ❌ Hard to change once shared

**Extract Too Late** (duplication debt):
- ❌ Copy-paste errors and inconsistencies
- ❌ Bug fixes need to happen in multiple places
- ❌ Hard to extract after 5+ uses (too much duplication)
- ❌ Missed opportunity for reuse
- ❌ Technical debt accumulates

**What We Need**:
- Clear rules for WHEN to extract
- Clear rules for WHAT to extract
- Clear rules for HOW to extract
- Evidence-based decisions (not guesses)
- Process that's easy to follow

### Key Constraints

**Known From Experience**:
1. First use: Don't know if pattern will be reused
2. Second use: Can see variations, but maybe coincidence
3. Third use: Pattern is proven, worth extracting
4. Fourth+ use: Too late, too much duplication

**Exceptions**:
- Foundational infrastructure: Extract immediately (100% certainty needed)
- UI components: Never extract (too project-specific)
- Rapidly changing code: Wait longer (not stable yet)

---

## Key Insights

### Insight 1: The Rule of Two/Three

**The Rule**:

```
┌──────────────────────────────────────────────┐
│  1st Use: Keep in Project                   │
│  - Tag as "candidate for sharing"           │
│  - Document use case                        │
│  - Don't abstract yet                       │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  2nd Use: Copy with Intention               │
│  - Copy to 2nd project                      │
│  - Notice variations                        │
│  - Start designing interface                │
│  - Still don't extract                      │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  3rd Use: MUST Extract                      │
│  - Extract to shared repo                   │
│  - Unify the three implementations          │
│  - Version and document                     │
│  - Update all three projects to use it     │
└──────────────────────────────────────────────┘
```

**Why These Numbers**:

**1 use**:
- Only one data point
- Don't know if pattern is general
- Could be project-specific
- Abstraction would be premature

**2 uses**:
- See how pattern varies
- Understand what's common vs different
- Can design better abstraction
- Still not confident enough to extract

**3 uses**:
- Pattern proven across multiple contexts
- Variations are understood
- Abstraction will be correct
- Cost of extraction is worth it

**4+ uses**:
- TOO LATE! Should have extracted at 3
- Now have duplication debt
- Extraction is harder
- More places to update

**Example Timeline**:
```
Month 1: Project A implements ADR creation
         → Tag as "candidate: adr-domain"

Month 2: Project B needs ADR creation
         → Copy from A, notice variations
         → Document differences
         → Still no extraction

Month 3: Project C needs ADR creation
         → This is the 3rd use!
         → Extract to capabilities/adr-domain
         → Update A, B, C to use shared repo
```

### Insight 2: Foundational Exception

**Rule DOES NOT Apply** to foundational infrastructure:

```
Foundational Infrastructure → Extract IMMEDIATELY
         ↓
  Contracts, Gateway, AI SDK, etc.
         ↓
  100% certainty all projects need it
         ↓
  High cost to retrofit if done wrong
         ↓
  EXTRACT ON 1ST USE (in Week 1-2)
```

**Why Exception Makes Sense**:
- We KNOW all projects will need API gateway
- We KNOW all projects will need frontend foundation
- We KNOW all projects will need observability
- We KNOW all projects will need contracts
- No risk of premature abstraction (these are universal)

**How to Identify Foundational**:
- ✅ 100% certainty: Can confidently say "every project needs this"
- ✅ Cross-cutting: Affects all layers and projects
- ✅ High retrofit cost: Painful to change after projects built
- ✅ Technology/architecture: About HOW to build, not WHAT to build

**Examples**:
- ✅ Foundational: API gateway pattern (every project has APIs)
- ❌ Not foundational: ADR domain logic (only ADR projects need it)

### Insight 3: Five-Question Test

**Before extracting, ask these 5 questions**:

**Question 1: Is it reusable?**
```
Does this code solve a general problem,
or is it specific to this project's unique needs?

✅ Extract: "User authentication with JWT"
❌ Don't: "ADR approval workflow for our org structure"
```

**Question 2: Is it domain-agnostic OR proven in domain?**
```
Is this infrastructure (any domain can use),
OR has it been used in 3+ projects (proven domain capability)?

✅ Extract: "Rate limiting middleware" (any domain)
✅ Extract: "ADR management" (used in 3+ projects)
❌ Don't: "ADR management" (only 1 project)
```

**Question 3: What drives changes?**
```
What causes this code to change?

✅ Extract: Changes for technical reasons (bugs, performance)
❌ Don't: Changes for business reasons (requirements change)
```

**Question 4: Can it be tested independently?**
```
Can you write tests without project context?

✅ Extract: Can test with mock inputs/outputs
❌ Don't: Needs project-specific setup to test
```

**Question 5: Is ownership clear?**
```
Who should own this code?

✅ Extract: Platform team owns (not project team)
❌ Don't: Product/business team owns (project-specific)
```

**Scoring**:
- 5/5 yes: Definitely extract
- 3-4/5 yes: Probably extract (use judgment)
- 0-2/5 yes: Don't extract (keep in project)

### Insight 4: Decision Tree

```
┌─────────────────────────────────────┐
│  Is it foundational infrastructure? │
│  (Contracts, Gateway, AI, etc.)     │
└────────┬────────────┬───────────────┘
         │ Yes        │ No
         ↓            ↓
    ┌─────────┐   ┌──────────────────┐
    │ EXTRACT │   │ How many uses?   │
    │ NOW     │   └───┬──────────────┘
    └─────────┘       │
                      ↓
         ┌────────────┼────────────┐
         │            │            │
     1st use      2nd use      3rd use
         │            │            │
         ↓            ↓            ↓
    ┌────────┐  ┌─────────┐  ┌────────┐
    │ Tag as │  │ Copy    │  │ EXTRACT│
    │ candidate│ │ with   │  │ to     │
    │ KEEP   │  │ intention│ │ shared │
    │ in     │  │ KEEP   │  │        │
    │ project│  │ in     │  └────────┘
    └────────┘  │ project│
                └─────────┘
```

**Additional Checks** (can override):

```
┌────────────────────────────────────┐
│  Is it UI component?               │
│  (React, Vue, Svelte components)   │
└────────┬───────────────────────────┘
         │ Yes
         ↓
    ┌──────────┐
    │ NEVER    │
    │ EXTRACT  │
    └──────────┘
         ↑
         │ Yes
┌────────┴───────────────────────────┐
│  Is it rapidly changing?           │
│  (Requirements change weekly)      │
└────────────────────────────────────┘
```

### Insight 5: What NOT to Extract

**Never Extract** (even with 3+ uses):

**Category 1: Project-Specific Business Logic**
```rust
// ❌ Don't extract
// Reason: Specific to organization's ADR approval process
pub fn requires_architecture_review(adr: &ADR) -> bool {
    adr.impacts_security || adr.cost > 100_000
}
```

**Category 2: UI Components**
```typescript
// ❌ Don't extract
// Reason: UI is project-specific (branding, layout, behavior)
export function ADRCard({ adr }: { adr: ADR }) {
  return (
    <div className="custom-card">
      {/* project-specific UI */}
    </div>
  );
}
```

**Category 3: Configuration**
```rust
// ❌ Don't extract
// Reason: Configuration is environment-specific
pub struct Config {
    database_url: String,
    api_key: String,
}
```

**Category 4: Rapidly Changing Code**
```python
# ❌ Don't extract (yet)
# Reason: Requirements change weekly, wait until stable
def experimental_ml_workflow(input: str) -> str:
    # This changes every sprint based on feedback
    ...
```

**Category 5: Integration Glue**
```rust
// ❌ Don't extract
// Reason: Bridges project-specific concerns
pub fn initialize_app(config: Config) -> App {
    // Wires together project's specific dependencies
}
```

**Why Not Extract**:
- Business logic: Changes driven by product, not reusable
- UI components: Too project-specific (branding, UX)
- Config: Every project has different config
- Rapidly changing: Not stable enough to share
- Integration glue: Specific to project's architecture

**Gray Areas** (use five-question test):
- Validation rules: Extract if domain-agnostic, keep if business-specific
- Helper functions: Extract if truly general, keep if context-specific
- Data transformers: Extract if protocol conversion, keep if business mapping

### Insight 6: Extraction Process

**Step-by-Step Process** (when 3rd use appears):

**Step 1: Preparation**
```bash
# Identify the code to extract
# Example: ADR domain logic

# Check: Does it pass five-question test?
# Check: Is it on 3rd use (or foundational)?
# Check: Is it NOT in the "never extract" list?
```

**Step 2: Create Shared Repo**
```bash
# In shared/ (foundational) or capabilities/ (emergent)
mkdir capabilities/adr-domain
cd capabilities/adr-domain

# Initialize as new repo
git init
git remote add origin https://github.com/org/capability-adr-domain

# Create structure
mkdir -p src tests docs
cargo init --lib  # or appropriate for language
```

**Step 3: Copy Code with History** (optional but nice)
```bash
# Use git filter-branch to preserve history
# (If not important, just copy files)

cd projects/project-a
git subtree split -P crates/adr-domain -b adr-domain-history

cd capabilities/adr-domain
git pull ../projects/project-a adr-domain-history
```

**Step 4: Unify Implementations**
```rust
// Review three implementations
// - projects/project-a/crates/adr-domain
// - projects/project-b/crates/adr-domain
// - projects/project-c/crates/adr-domain

// Identify:
// - What's common (extract as-is)
// - What varies (make configurable)
// - What's project-specific (don't extract)

// Create unified version
pub struct ADR {
    // Common fields from all three
}

pub trait ADRRepository {
    // Common interface from all three
}
```

**Step 5: Add Documentation**
```markdown
# capabilities/adr-domain/README.md

# ADR Domain

Domain logic for Architecture Decision Records.

## Usage

```rust
use adr_domain::{ADR, ADRStatus};

let adr = ADR::new("Use Rust", "...");
```

## History

Extracted from:
- Project A (2025-10-15)
- Project B (2025-10-20)
- Project C (2025-10-24) ← 3rd use triggered extraction
```

**Step 6: Version and Publish**
```toml
# Cargo.toml
[package]
name = "adr-domain"
version = "0.1.0"  # First version
```

```bash
# Tag release
git tag v0.1.0
git push origin v0.1.0
```

**Step 7: Update Consumers**
```toml
# projects/project-a/Cargo.toml
[dependencies]
adr-domain = { git = "https://github.com/org/capability-adr-domain", tag = "v0.1.0" }

# Remove old local crate
# rm -rf crates/adr-domain
```

**Step 8: Update Manifest** (if using Google Repo)
```xml
<!-- .repo/manifest.xml -->
<project name="capabilities/adr-domain" path="capabilities/adr-domain" />
```

**Step 9: Verify**
```bash
# In each project
cargo clean
cargo build
cargo test

# Verify all three projects build and tests pass
```

**Step 10: Document Extraction**
```markdown
# Update 03-emergent-capabilities.md

## ADR Domain Capability

**Status**: EXTRACTED
**Version**: 0.1.0
**Repo**: capabilities/adr-domain

**Usage History**:
- 1st use: Project A (2025-10-15)
- 2nd use: Project B (2025-10-20)
- 3rd use: Project C (2025-10-24) → Extracted
```

---

## Open Questions

### Questions for Next Stage

**Process**:
- [ ] Who approves extraction? (Platform team? Tech lead?)
- [ ] How often to review for extraction candidates? (Weekly? Per sprint?)
- [ ] What's the SLA for extraction? (Must extract within 1 sprint of 3rd use?)
- [ ] How to handle disagreements? (Force extract at 3? Allow exceptions?)

**Mechanics**:
- [ ] Preserve git history or fresh start? (Trade-off: history vs clean slate)
- [ ] Keep copy in project during transition? (Safety vs duplication)
- [ ] How to handle breaking changes after extraction? (Semver + coordination)
- [ ] Monorepo for capabilities or separate repos? (Coordination vs independence)

**Exceptions**:
- [ ] Can we delay extraction past 3rd use? (If yes, what's criteria?)
- [ ] Can we extract before 3rd use? (If yes, what's criteria?)
- [ ] Who decides exceptions? (Need clear authority)

**Measurement**:
- [ ] How to track "uses" across projects? (Tagging in code? Tracking doc?)
- [ ] How to measure extraction success? (Adoption? Satisfaction? Velocity?)
- [ ] When to revisit extracted code? (Annual? When issues arise?)

### Deferred Questions (Not Now)

- Automated extraction tools (future tooling)
- Multi-language extraction (handle Rust + Python + TS together)
- Deprecation process for old shared code (not needed yet)
- Forking vs updating shared code (cross that bridge later)

---

## Related Concepts

### Connection to Other Documents

**Strategic Context** ([01-strategic-context.md](./01-strategic-context.md)):
- Rule of two/three is core philosophy
- Foundational exception is key insight
- Emergence over architecture drives extraction timing

**Foundational Infrastructure** ([02-foundational-infrastructure.md](./02-foundational-infrastructure.md)):
- Extract immediately (1st use)
- All 7 pieces created in Week 1-2
- No rule of two/three needed

**Emergent Capabilities** ([03-emergent-capabilities.md](./03-emergent-capabilities.md)):
- Follow rule of two/three
- Track uses across projects
- Extract on 3rd use

**Repository Strategy** ([04-repository-strategy.md](./04-repository-strategy.md)):
- Extracted code goes to shared/ or capabilities/
- Each extracted piece becomes separate repo
- Google Repo tool helps coordinate

**Technology Integration** ([05-technology-integration.md](./05-technology-integration.md)):
- Extraction rules apply per language
- Rust code extracts to Rust crate
- Python code extracts to Python package
- Protobuf contracts extract immediately

### Extraction Examples

**Example 1: Contracts (Foundational)**
```
Week 1: Create shared/contracts repo
      → Extract immediately (foundational)
      → All projects use from day one
```

**Example 2: ADR Domain (Emergent)**
```
Month 1: Project A implements ADR logic
       → Tag as "candidate: adr-domain"

Month 2: Project B needs similar logic
       → Copy from A, notice variations
       → Tag both as "adr-domain: 2nd use"

Month 3: Project C needs similar logic
       → This is 3rd use!
       → Extract to capabilities/adr-domain
       → Update A, B, C to use shared repo
```

**Example 3: Custom Approval Workflow (Never Extract)**
```
Month 1: Project A has org-specific approval flow
       → Keep in project (business logic)

Month 2: Project B has DIFFERENT approval flow
       → Keep in project (variations are business-driven)

Month 3: Project C has YET ANOTHER flow
       → Still keep in projects
       → These are NOT the same pattern
       → Variations are product decisions, not technical
```

### Decision Matrix

| Code Type | Uses | Foundational? | Extract? | Where? |
|-----------|------|---------------|----------|--------|
| Contracts | 1st | Yes | ✅ Immediately | shared/contracts |
| API Gateway | 1st | Yes | ✅ Immediately | shared/api-gateway |
| ADR Domain | 1st | No | ❌ Tag candidate | projects/a |
| ADR Domain | 2nd | No | ❌ Copy with intention | projects/b |
| ADR Domain | 3rd | No | ✅ Extract now | capabilities/adr |
| UI Component | 3+ | No | ❌ Never | projects/* |
| Business Logic | 3+ | No | ❌ Never | projects/* |

---

## Next Steps

### For This Document

- [ ] Validate five-question test with team
- [ ] Answer process questions (who approves, SLA, etc.)
- [ ] Create extraction checklist (step-by-step guide)
- [ ] Add more examples (real code from ADR PoC)
- [ ] Mark as STABLE when rules are validated

### For Implementation

**Week 1-2** (Foundational Extraction):
1. Create repos for 7 foundational pieces
2. Follow extraction process for each
3. Document learnings and adjust process

**Month 2-3** (Tagging Phase):
1. Review code in projects monthly
2. Tag candidates for sharing
3. Track use counts in [03-emergent-capabilities.md](./03-emergent-capabilities.md)
4. Document variations between uses

**Month 4** (First Emergent Extraction):
1. When 3rd use appears, extract immediately
2. Follow extraction process step-by-step
3. Document what went well/poorly
4. Adjust process based on learnings

**Ongoing**:
1. Weekly extraction review meetings
2. Track extraction candidates
3. Measure extraction success
4. Evolve rules based on evidence

---

## Success Criteria

These extraction rules are successful when:

**Clarity**:
- ✅ Engineers know when to extract (clear decision tree)
- ✅ Five-question test is easy to apply
- ✅ Exceptions are well understood
- ✅ Process is documented and followed

**Timing**:
- ✅ No premature abstractions (nothing extracted before 3rd use, except foundational)
- ✅ No excessive duplication (3rd use triggers extraction within 1 sprint)
- ✅ Foundational infrastructure extracted in Week 1-2
- ✅ Emergent capabilities appear naturally (not forced)

**Quality**:
- ✅ Extracted code is truly reusable (all consumers use it)
- ✅ No false starts (extracted code doesn't get abandoned)
- ✅ Abstractions fit real usage (not theoretical)
- ✅ Breaking changes are rare (<1 major version bump per 6 months)

**Process**:
- ✅ Extraction takes <1 week (from decision to completion)
- ✅ Clear ownership of shared code
- ✅ Review process is lightweight
- ✅ Extraction doesn't block project work

**Evidence-Based**:
- ✅ Decisions based on real usage (not speculation)
- ✅ Can measure extraction success (adoption, satisfaction)
- ✅ Can adjust rules based on learnings
- ✅ Regular retrospectives on extractions

---

## References

**Internal**:
- ADR PoC: [../../README.md](../../README.md) - Reference implementation
- Emergent Capabilities: [03-emergent-capabilities.md](./03-emergent-capabilities.md) - Tracking template

**External Philosophy**:
- Rule of Three (Martin Fowler): https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)
- Sandi Metz on Duplication: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- YAGNI (You Aren't Gonna Need It): https://martinfowler.com/bliki/Yagni.html

**Anti-Patterns**:
- Premature Abstraction: https://wiki.c2.com/?PrematureGeneralization
- Golden Hammer: https://en.wikipedia.org/wiki/Law_of_the_instrument
- Not Invented Here: https://en.wikipedia.org/wiki/Not_invented_here

**Best Practices**:
- DRY (Don't Repeat Yourself) - but not too early
- WET (Write Everything Twice) - before abstracting
- AHA (Avoid Hasty Abstractions) - wait for evidence

---

**Status Notes**:
- **EXPLORING**: Rules documented, need validation in practice
- **Next**: Apply rules to ADR PoC and first extraction
- **After**: Refine rules based on real extraction experience
