# Platform Framework Exploration - Navigation Index

**Last Updated**: 2025-10-24
**Status**: Active Exploration
**Documents**: 10 core documents + supporting materials

---

## 🗺️ Knowledge Graph Map

```
                    ┌─────────────────────┐
                    │  Strategic Context  │
                    │  (Start Here)       │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ↓              ↓              ↓
    ┌───────────────┐  ┌─────────────┐  ┌──────────────┐
    │ Foundational  │  │  Emergent   │  │  Repository  │
    │Infrastructure │  │ Capabilities│  │   Strategy   │
    └───────┬───────┘  └──────┬──────┘  └──────┬───────┘
            │                 │                 │
            └────────┬────────┴────────┬────────┘
                     │                 │
                     ↓                 ↓
            ┌──────────────┐   ┌──────────────┐
            │  Technology  │   │  Extraction  │
            │ Integration  │   │    Rules     │
            └──────┬───────┘   └──────┬───────┘
                   │                  │
                   └────────┬─────────┘
                            │
                            ↓
                ┌───────────────────────┐
                │  Implementation       │
                │  Roadmap              │
                └───────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ↓               ↓               ↓
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Decision   │ │   Success   │ │  Reference  │
    │  Framework  │ │   Metrics   │ │  Projects   │
    └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 📖 Core Documents (Read in Order)

### 1. Strategic Context
**File**: [01-strategic-context.md](./01-strategic-context.md)
**Status**: EXPLORING
**Purpose**: The big picture - what we're building and why

**Key Topics**:
- The core problem: Building multiple projects while growing a platform framework
- Two-tier approach: Foundational vs Emergent
- Rule of two/three: When to extract shared code
- Emergence over architecture philosophy

**Read this first**: Provides context for all other documents

**Related Documents**:
- → [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What to build now
- → [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What to build later
- → [06-extraction-rules.md](./06-extraction-rules.md) - When to extract

---

### 2. Foundational Infrastructure
**File**: [02-foundational-infrastructure.md](./02-foundational-infrastructure.md)
**Status**: EXPLORING
**Purpose**: The 7 core pieces to build immediately

**Key Topics**:
- Contracts (Proto Schemas) - Type safety foundation
- API Gateway Core - Gateway patterns and Envoy config
- AI Gateway SDK - AI provider abstraction and streaming
- Frontend Foundation - Next.js + Connect patterns
- Observability SDK - Tracing, metrics, logs
- CLI Framework - CLI tool patterns
- Storage Patterns - Database, RLS, repository

**Why foundational**: 100% certainty all projects need these, high retrofit cost

**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Why these are foundational
- → [05-technology-integration.md](./05-technology-integration.md) - How they work together
- → [07-implementation-roadmap.md](./07-implementation-roadmap.md) - How to build them

---

### 3. Emergent Capabilities
**File**: [03-emergent-capabilities.md](./03-emergent-capabilities.md)
**Status**: EXPLORING
**Purpose**: Domain capabilities that emerge from real usage

**Key Topics**:
- ADR Domain - Decision record management (1st use in ADR PoC)
- Workflow Engine - Process orchestration (0 uses yet)
- Notification SDK - Notification delivery (0 uses yet)
- Search Primitives - Search infrastructure (TBD)
- Document Ingestion - Document processing (TBD)

**Why emergent**: Usage patterns not proven, low retrofit cost, follow rule of two/three

**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Rule of two/three philosophy
- → [06-extraction-rules.md](./06-extraction-rules.md) - When to extract these
- → [08-decision-framework.md](./08-decision-framework.md) - How to decide

---

### 4. Repository Strategy
**File**: [04-repository-strategy.md](./04-repository-strategy.md)
**Status**: EXPLORING
**Purpose**: Multi-repo topology and coordination with Google Repo tool

**Key Topics**:
- Hybrid approach: Shared repos + Project monorepos
- Google Repo tool for coordination
- Repository structure and naming
- Versioning and dependency management
- Extraction process

**Key Decisions**:
- Shared capabilities in versioned repos
- Projects as monorepos (fast iteration)
- Repo tool optional (use when needed)

**Related Documents**:
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What goes in shared/
- ← [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What goes in capabilities/
- → [06-extraction-rules.md](./06-extraction-rules.md) - How to extract

---

### 5. Technology Integration
**File**: [05-technology-integration.md](./05-technology-integration.md)
**Status**: EXPLORING
**Purpose**: How Rust, Python, and TypeScript work together

**Key Topics**:
- Language usage matrix (what language for what)
- Communication patterns (gRPC, Kafka, Connect)
- Synchronous tier (Rust) - User-facing, real-time
- Asynchronous tier (Python) - Background workflows, ML
- Frontend tier (TypeScript) - Browser, SSR
- Protobuf as glue (generates types for all)

**Key Insight**: Not "two-language problem", but "two-language solution"

**Related Documents**:
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - Foundation for all languages
- → [ADR Platform doc](../../../docs/architecture/brief.md) - Full architecture

---

### 6. Extraction Rules
**File**: [06-extraction-rules.md](./06-extraction-rules.md)
**Status**: EXPLORING
**Purpose**: Clear rules for when and how to extract shared code

**Key Topics**:
- Rule of two/three: 1st use, 2nd use, 3rd use
- Foundational vs emergent criteria
- Extraction decision tree
- Extraction process (step-by-step)
- What NOT to extract

**Critical Rules**:
- Foundational: Extract immediately (contracts, gateway, AI, etc.)
- Domain: Extract on 3rd use (ADR, workflow, etc.)
- Never extract: Project-specific, rapidly changing, UI components

**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Philosophy behind rules
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What's foundational
- ← [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What's emergent
- → [08-decision-framework.md](./08-decision-framework.md) - How to apply rules

---

### 7. Implementation Roadmap
**File**: [07-implementation-roadmap.md](./07-implementation-roadmap.md)
**Status**: EXPLORING
**Purpose**: Concrete steps for the next 90 days

**Key Topics**:
- Week 1-2: Build foundational infrastructure
- Week 3-4: Set up two projects
- Month 2-3: Build features, tag duplication
- Month 4+: Extract capabilities as they emerge
- Success metrics per phase

**Timeline**:
- Month 1: Foundation complete, projects starting
- Month 2-3: Projects shipping features
- Month 4: First capability extractions
- Month 6: Framework emerges

**Related Documents**:
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What to build in weeks 1-2
- ← [06-extraction-rules.md](./06-extraction-rules.md) - When to extract in month 4+
- → [09-success-metrics.md](./09-success-metrics.md) - How to measure progress

---

## 🎯 Supporting Documents

### 8. Decision Framework
**File**: [08-decision-framework.md](./08-decision-framework.md)
**Status**: EXPLORING
**Purpose**: Tools and frameworks for making extraction decisions

**Key Topics**:
- 5-question test (reusability, domain, change drivers, testing, ownership)
- Decision tree (is it foundational? is it domain-specific?)
- Examples of each category
- When to break the rules
- Exception handling

**Use this when**: Unsure if code should be shared or stay in project

**Related Documents**:
- ← [06-extraction-rules.md](./06-extraction-rules.md) - The rules to apply
- → [10-reference-projects.md](./10-reference-projects.md) - Real examples

---

### 9. Success Metrics
**File**: [09-success-metrics.md](./09-success-metrics.md)
**Status**: EXPLORING
**Purpose**: How to measure if the strategy is working

**Key Topics**:
- Foundational infrastructure metrics (time to start project, reuse, breaking changes)
- Emergent capability metrics (extraction timing, premature extractions)
- Developer experience metrics (onboarding, setup, autonomy)
- Triggers to revisit decisions
- Evidence-based indicators

**Use this for**: Tracking progress and detecting problems early

**Related Documents**:
- ← [07-implementation-roadmap.md](./07-implementation-roadmap.md) - When to measure
- ← [06-extraction-rules.md](./06-extraction-rules.md) - Rules to validate

---

### 10. Reference Projects
**File**: [10-reference-projects.md](./10-reference-projects.md)
**Status**: EXPLORING
**Purpose**: Real-world examples and patterns to learn from

**Key Topics**:
- ADR PoC (current) - Reference implementation
- FlowOS pattern - Contracts → Engines → Apps
- Multi-Repo Strategy - Google Repo approach
- ADR Platform Architecture - Rust + Python + TS integration
- CLI Tools Architecture - Command patterns

**Use this for**: Concrete examples and proven patterns

**Related Documents**:
- → All core documents reference these examples

---

## 🔍 Quick Reference

### By Use Case

**I want to...**

| Goal | Read This |
|------|-----------|
| Understand the overall strategy | [01-strategic-context.md](./01-strategic-context.md) |
| Know what to build first | [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) |
| Know what to build later | [03-emergent-capabilities.md](./03-emergent-capabilities.md) |
| Understand the repo structure | [04-repository-strategy.md](./04-repository-strategy.md) |
| Understand how languages work together | [05-technology-integration.md](./05-technology-integration.md) |
| Decide if code should be extracted | [06-extraction-rules.md](./06-extraction-rules.md) + [08-decision-framework.md](./08-decision-framework.md) |
| Know what to do next | [07-implementation-roadmap.md](./07-implementation-roadmap.md) |
| Check if we're on track | [09-success-metrics.md](./09-success-metrics.md) |
| See real examples | [10-reference-projects.md](./10-reference-projects.md) |

### By Topic

| Topic | Relevant Documents |
|-------|-------------------|
| **Philosophy** | [01-strategic-context.md](./01-strategic-context.md) |
| **What to Build** | [02-foundational-infrastructure.md](./02-foundational-infrastructure.md), [03-emergent-capabilities.md](./03-emergent-capabilities.md) |
| **How to Organize** | [04-repository-strategy.md](./04-repository-strategy.md) |
| **Technology Choices** | [05-technology-integration.md](./05-technology-integration.md) |
| **Decision Making** | [06-extraction-rules.md](./06-extraction-rules.md), [08-decision-framework.md](./08-decision-framework.md) |
| **Execution** | [07-implementation-roadmap.md](./07-implementation-roadmap.md) |
| **Measurement** | [09-success-metrics.md](./09-success-metrics.md) |
| **Examples** | [10-reference-projects.md](./10-reference-projects.md) |

### By Exploration Status

| Status | Documents |
|--------|-----------|
| **EXPLORING** | All documents currently (2025-10-24) |
| **MATURING** | None yet |
| **STABLE** | None yet |
| **EVOLVED** | None yet |

*Will update as documents mature*

---

## 🔄 Document Relationships

### Foundation Layer
```
Strategic Context (01)
    ↓
┌───────────────────────────────────┐
│                                   │
Foundational Infrastructure (02)   Emergent Capabilities (03)
    ↓                                   ↓
Repository Strategy (04) ←──────────────┘
```

### Integration Layer
```
Technology Integration (05)
    ↑
    │ (uses)
    │
Foundation + Emergent
```

### Decision Layer
```
Extraction Rules (06)
    ↓
Decision Framework (08)
    ↓
Success Metrics (09)
```

### Execution Layer
```
Implementation Roadmap (07)
    ↑
    │ (informed by)
    │
All Core Documents
```

### Reference Layer
```
Reference Projects (10)
    ↓ (examples for)
    │
All Documents
```

---

## 📊 Exploration Progress

### Current Status (2025-10-24)

**Phase**: Initial Discovery
**Completed**: Strategic thinking and option exploration
**In Progress**: Document creation and knowledge capture
**Next**: Document refinement and team alignment

### Documents by Status

| Status | Count | Documents |
|--------|-------|-----------|
| EXPLORING | 10 | All core documents |
| MATURING | 0 | None yet |
| STABLE | 0 | None yet |
| EVOLVED | 0 | None yet |

### Readiness for Design Phase

| Criteria | Status | Notes |
|----------|--------|-------|
| Core strategy clear | 🟡 In progress | Being documented |
| Foundational vs emergent defined | ✅ Yes | Clear distinction |
| Extraction rules concrete | ✅ Yes | Rule of two/three |
| Technology integration documented | ✅ Yes | Rust/Python/TS patterns |
| Implementation roadmap clear | 🟡 In progress | Timeline exists |
| Team alignment | ⏳ Pending | Needs review |

---

## 🎯 Next Actions

### Immediate (This Week)
1. Complete all 10 core documents
2. Review and refine cross-references
3. Validate examples and patterns
4. Update statuses as documents stabilize

### Short-term (Next 2 Weeks)
1. Team review of exploration documents
2. Address open questions
3. Mark stable documents as STABLE
4. Begin converting to ADRs where appropriate

### Medium-term (Next Month)
1. Start building foundational infrastructure
2. Create project templates
3. Document learnings back into exploration
4. Evolve exploration docs into design docs

---

## 📞 Getting Help

**Navigation Questions**:
- Start at [README.md](./README.md) for folder purpose
- Use this INDEX for document map
- Follow "Related Documents" links in each document

**Content Questions**:
- Check "Open Questions" sections in documents
- Look at "Related Concepts" for connections
- Review [10-reference-projects.md](./10-reference-projects.md) for examples

**Process Questions**:
- See [README.md](./README.md) "How to Use This Folder"
- Check document lifecycle section
- Review exploration stages

---

**Remember**: This is a **knowledge graph**, not a linear document. Explore in any order that makes sense for your questions!
