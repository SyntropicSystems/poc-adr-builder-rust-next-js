# Emergent Capabilities: Domain Patterns That Emerge

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Rule of two/three
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - Contrast with foundational
- → [06-extraction-rules.md](./06-extraction-rules.md) - When to extract

---

## Context

### What Makes Something "Emergent"

**Criteria for emergent capabilities**:
1. ✅ **Domain-specific** (not infrastructure)
2. ✅ **Usage pattern not proven** (need real usage to understand)
3. ✅ **Low retrofit cost** (easy to extract later)
4. ✅ **Business logic** (not technology choice)

**Examples**:
- Emergent: ADR Domain (business logic, usage pattern needs proving)
- NOT Emergent: API Gateway (infrastructure, proven pattern)

**Rule**: Emergent capabilities follow **rule of two/three** before extraction

---

## Key Insights

### The 5 Likely Emergent Capabilities

Based on project needs, these will likely emerge:

```
1. ADR Domain            ← Decision record management (1st use: ADR PoC)
2. Workflow Engine       ← Process orchestration (0 uses yet)
3. Notification SDK      ← Notification delivery (0 uses yet)
4. Search Primitives     ← Search infrastructure (TBD)
5. Document Ingestion    ← Document processing (TBD)
```

**Note**: These are **predictions**, not certainties. Rule of two/three will validate.

---

## 1. ADR Domain (1st Use: ADR PoC)

### Current Status
- **Uses**: 1 (ADR PoC project)
- **Next**: Wait for 2nd project to need ADRs
- **Extraction**: At 3rd use

### What It Is
Domain model for Architecture Decision Records:
- ADR entity (id, title, context, decision, consequences, status)
- Status enum (draft, proposed, accepted, rejected, deprecated)
- Validation rules (title length, status transitions)
- Pure domain logic (no infrastructure)

### Hexagonal Structure (When Extracted)
```
capabilities/adr-domain/      # Pure domain
capabilities/adr-sdk/         # Ports + use cases
capabilities/adr-adapters/    # Implementations
```

### Current Home
`poc-adr-builder-rust-next-js/crates/adr-domain/`

### Related Docs
- Reference: ADR PoC README.md
- Hexagonal: [10-reference-projects.md](./10-reference-projects.md#hexagonal-architecture)

---

## 2. Workflow Engine (0 Uses Yet)

### Current Status
- **Uses**: 0
- **Predicted**: 2+ projects will need workflows
- **Don't extract yet**: Wait for 1st use

### What It Might Be
Process orchestration and state management:
- Workflow definition (steps, transitions, conditions)
- State machine execution
- Event handling
- Task scheduling

### Why Emergent
- Don't know exact requirements yet
- Workflow patterns will emerge from real usage
- Premature to build before 1st use

### When to Extract
1st use: Keep in project, learn patterns
2nd use: Design shared interface
3rd use: Extract to `capabilities/workflow-engine/`

---

## 3. Notification SDK (0 Uses Yet)

### Current Status
- **Uses**: 0
- **Predicted**: 2+ projects will send notifications
- **Don't extract yet**: Wait for 1st use

### What It Might Be
Notification delivery abstraction:
- Multiple channels (email, SMS, push, webhook)
- Template management
- Delivery tracking
- Retry logic

### Why Emergent
- Don't know which channels are needed
- Template patterns will emerge from usage
- Delivery requirements project-specific initially

### When to Extract
Follow rule of two/three as projects need notifications

---

## 4. Search Primitives (TBD)

### Current Status
- **Uses**: 0
- **Predicted**: May or may not be needed
- **Don't extract yet**: Wait to see if pattern emerges

### What It Might Be
Search infrastructure abstraction:
- Full-text search (Postgres tsvector)
- Vector search (pgvector)
- Hybrid search (combine both)
- Faceting and filters

### Why Emergent
- Unclear if all projects need search
- Search patterns may be project-specific
- May not be a shared capability at all

### When to Extract
Only if 3 projects implement similar search patterns

---

## 5. Document Ingestion (TBD)

### Current Status
- **Uses**: 0
- **Predicted**: May be needed for content-heavy projects
- **Don't extract yet**: Wait to see if pattern emerges

### What It Might Be
Document processing pipeline:
- File upload handling
- Format parsing (PDF, DOCX, HTML)
- Text extraction
- Chunking strategies
- Metadata extraction

### Why Emergent
- Unclear which projects need document processing
- Format support project-specific
- Processing patterns may vary significantly

### When to Extract
Only if multiple projects need similar document workflows

---

## Extraction Process (Rule of Two/Three)

### Stage 1: First Use (Keep in Project)
```rust
// project-a/crates/adr-management/src/domain.rs
// Tag: Candidate for extraction (1st use)

pub struct ADR {
    pub id: Uuid,
    pub title: String,
    // ...
}
```

**Actions**:
- Tag code with "Candidate for extraction"
- Document what it does and why it exists
- Note design decisions

### Stage 2: Second Use (Design Interface)
```rust
// project-b/crates/decision-tracking/src/adr.rs
// Tag: TODO: Extract on 3rd use (2nd use)

// Copy from project-a
// Note differences in usage
// Start ADR for shared interface
```

**Actions**:
- Compare implementations
- Identify common patterns vs variations
- Write ADR proposing shared interface
- Don't extract yet (wait for 3rd use)

### Stage 3: Third Use (Extract)
```bash
# Create capability
mkdir -p capabilities/adr-domain
mkdir -p capabilities/adr-sdk  
mkdir -p capabilities/adr-adapters

# Extract pattern
# Generalize
# Version v0.1.0
# Projects depend on it
```

**Actions**:
- Extract to `capabilities/`
- Remove project-specific code
- Add tests
- Document
- Projects update dependencies

---

## Open Questions

### Capability Predictions

**ADR Domain**:
- [ ] Will 2nd project actually need ADRs?
- [ ] If yes, what variations from ADR PoC?
- [ ] Should we extract domain only, or domain + SDK together?

**Workflow Engine**:
- [ ] Which projects will need workflows?
- [ ] What level of complexity (simple state machine vs full BPMN)?
- [ ] Event-driven vs polling?

**Notification SDK**:
- [ ] Which notification channels are common?
- [ ] Template system needed?
- [ ] Sync vs async delivery?

**Other Capabilities**:
- [ ] What capabilities did we miss?
- [ ] What will emerge that we didn't predict?
- [ ] How to handle unexpected patterns?

### Process Questions

**Extraction Timing**:
- [ ] Exactly how to identify 2nd/3rd use?
- [ ] What if 2nd use is very different from 1st?
- [ ] Can we extract before 3rd use if confident?

**Capability Boundaries**:
- [ ] How granular should capabilities be?
- [ ] When to combine related capabilities?
- [ ] When to split large capabilities?

---

## Related Concepts

### Contrast with Foundational

| Aspect | Foundational | Emergent |
|--------|-------------|----------|
| **Certainty** | 100% will be used | May or may not be used |
| **Retrofit Cost** | High | Low |
| **Type** | Infrastructure | Domain logic |
| **Extraction** | Immediately | After 3rd use |
| **Location** | `shared/` | `capabilities/` |

### Rule of Two/Three in Practice

**Tracking Template**:
```markdown
## ADR Domain Capability

**1st Use**: Project A (ADR PoC) - 2025-10-24
- Implementation: `project-a/crates/adr-domain`
- Notes: Pure domain logic, status enum, validation

**2nd Use**: Project B (TBD) - Not yet
- Expected: Q1 2026?
- Action when happens: Design shared interface

**3rd Use**: Project C or Project B (2nd context) - Not yet
- Action when happens: Extract to `capabilities/adr-domain`
```

### Weekly Extraction Review

**Agenda**:
1. Review all tagged code ("Candidate for extraction")
2. Count uses per potential capability
3. Compare implementations (if 2+ uses)
4. Decide: Extract now, design interface, or wait
5. Update tracking documents

**See**: [07-implementation-roadmap.md](./07-implementation-roadmap.md#month-2-3-weekly-reviews)

---

## Next Steps

### For This Document

- [ ] Validate predictions (are these the right 5?)
- [ ] Define tracking mechanism
- [ ] Create extraction ADR template
- [ ] Document when to make exceptions

### For Implementation

**Month 1**: Projects start (no emergent capabilities yet)
- Tag potential shared code
- Document design decisions
- Note what might be reusable

**Month 2-3**: Pattern recognition
- Weekly review of tagged code
- Compare implementations
- Track use counts

**Month 4+**: Extraction
- Extract when 3rd use appears
- Follow extraction process
- Update this document with learnings

---

## Success Criteria

This approach is successful when:

**Discovery**:
- ✅ Emergent capabilities are discovered (not forced)
- ✅ Real usage patterns inform extraction
- ✅ No premature abstraction

**Timing**:
- ✅ No extraction before 2nd use
- ✅ Extraction happens at 3rd use
- ✅ Rare exceptions documented

**Quality**:
- ✅ Extracted capabilities solve real problems
- ✅ Abstractions fit multiple use cases
- ✅ Low refactoring needed after extraction
- ✅ Projects adopt extracted capabilities

**Learning**:
- ✅ Unexpected capabilities are discovered
- ✅ Predicted capabilities may not emerge (that's OK!)
- ✅ Learnings feed back into process

---

**Status Notes**:
- **EXPLORING**: Predictions made, waiting for real usage
- **Next**: Start projects, begin tagging code
- **After**: Weekly reviews, pattern recognition
