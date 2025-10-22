# Architecture Decision Records (ADRs)

**ADR Editor PoC** - Finalized Architectural Decisions

---

## 📋 What are ADRs?

Architecture Decision Records (ADRs) document significant architectural decisions made during the project. Each ADR captures:

- **Context**: What problem were we solving?
- **Decision**: What did we decide?
- **Consequences**: What are the trade-offs?
- **Status**: Is this decision still active?

---

## 📚 Active ADRs

| # | Title | Status | Date |
|---|-------|--------|------|

---

## 🎯 Decision Status

- **✅ Accepted**: Decision is active and validated
- **🔄 Proposed**: Decision under consideration
- **⚠️ Deprecated**: Decision superseded by another
- **❌ Rejected**: Decision considered but not adopted

---

## 📝 ADR Template

When creating a new ADR, use this template:

```markdown
# ADR NNNN: [Title]

**Status**: Proposed | Accepted | Deprecated | Rejected  
**Date**: YYYY-MM-DD  
**Validated**: In PoC Phase N

---

## Context

What problem are we trying to solve? What constraints do we have?

## Decision

What did we decide to do?

## Alternatives Considered

| Alternative | Pros | Cons | Why Not |
|------------|------|------|---------|
| Option A | ... | ... | ... |

## Consequences

### Positive
- ✅ Benefit 1
- ✅ Benefit 2

### Negative
- ⚠️ Trade-off 1
- ⚠️ Trade-off 2

## Validation

How did we validate this decision in the PoC?

- ✅ Validated in Phase N
- ✅ Metric: ...

## Related

- [ADR XXXX](./xxxx-title.md)
- [Documentation](../architecture/OVERVIEW.md)
```

---

## 🔍 Finding Decisions

### By Topic

- **Architecture Pattern**: [ADR 0001](./0001-use-hexagonal-architecture.md)
- **API Protocol**: [ADR 0002](./0002-use-grpc-for-api.md)
- **Code Organization**: [ADR 0003](./0003-cargo-workspace-structure.md)
- **Storage**: [ADR 0004](./0004-repository-pattern.md)

### By Phase

- **Phase 0 (Setup)**: ADRs 0001-0004
- **Phase 1 (Foundation)**: TBD
- **Phase 2 (CLI)**: TBD
- **Phase 3 (Service)**: TBD
- **Phase 4 (Frontend)**: TBD

---

## 🎓 Learning from Decisions

### What Worked Well

Based on PoC validation:

- ✅ **Hexagonal Architecture**: SDK truly shared between CLI and service (80%+ code reuse)
- ✅ **gRPC**: Type safety across languages worked perfectly
- ✅ **Repository Pattern**: Swapping storage took 1 line of config
- ✅ **Workspace Structure**: Zero-cost migration to monorepo

### What Would Change

Future considerations:

- 🤔 Consider REST gateway for browser (grpc-web adds complexity)
- 🤔 Evaluate simplified state management (Zustand + React Query might be heavy)
- 🤔 Bazel complexity vs. benefit (minimal usage in PoC was right)

---

## 📖 Related Documentation

---

## 🔄 Process

### When to Create an ADR

Create an ADR when:
- ✅ Decision affects system architecture
- ✅ Decision is difficult to reverse
- ✅ Team needs alignment on approach
- ✅ Future team needs to understand "why"

### When NOT to Create an ADR

Don't create ADR for:
- ❌ Implementation details (code patterns)
- ❌ Obvious choices (use Git for version control)
- ❌ Temporary decisions (PoC-only shortcuts)
- ❌ Easily reversible choices (UI colors)

### ADR Lifecycle

1. **Propose**: Create ADR with status "Proposed"
2. **Discuss**: Team reviews and provides feedback
3. **Decide**: Update status to "Accepted" or "Rejected"
4. **Validate**: Confirm decision works in practice (PoC)
5. **Supersede**: If needed, create new ADR and mark old as "Deprecated"

---

**Remember**: ADRs capture *why* we made decisions, not *what* we built. For *what*, see the code!
