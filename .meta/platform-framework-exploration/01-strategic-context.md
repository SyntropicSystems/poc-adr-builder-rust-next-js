# Strategic Context: Platform Framework Strategy

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- → [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What to build now
- → [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What to build later
- → [06-extraction-rules.md](./06-extraction-rules.md) - When to extract

---

## Context

### The Core Problem

We're building **multiple projects in parallel** (from PoC to platform) while simultaneously developing a **reusable platform framework**. The challenge:

**Traditional Approaches Fail**:
- ❌ **Framework-first**: 6-12 months building "the perfect framework" with no business value
- ❌ **Per-project**: Each project builds from scratch, massive duplication
- ❌ **Waterfall planning**: Create the perfect architecture upfront that doesn't scale
- ❌ **Pure ad-hoc**: No patterns emerge, chaos and inconsistency

**What We Need**:
- ✅ Build real projects that deliver value immediately
- ✅ Identify and extract reusable patterns as they emerge
- ✅ Enable rapid experimentation while growing the framework
- ✅ Support both atomic PoCs and production platforms
- ✅ Scale patterns from 1 project → 2 projects → N projects

### Key Constraints

**Known Requirements** (stated explicitly):
1. Multiple projects will need **Next.js frontend**
2. Multiple projects will need **API Gateway**
3. Multiple projects will need **AI integration**
4. Multiple projects will need **CLI tools**
5. Technologies: **Rust** (sync tier), **Python** (async tier), **TypeScript** (frontend)

**Unknown Requirements** (will discover):
- Exactly which domain capabilities will be reused
- How workflows will be structured
- What notification patterns emerge
- Which search patterns work
- Specific business logic patterns

---

## Key Insights

### Insight 1: Two-Tier Architecture Pattern

Not all code is created equal. We discovered a **fundamental distinction**:

```
┌─────────────────────────────────────────────┐
│  TIER 1: FOUNDATIONAL INFRASTRUCTURE        │
│  - 100% certainty all projects need it      │
│  - High cost to retrofit if done wrong      │
│  - Technology/architecture decisions        │
│  - Extract IMMEDIATELY                      │
│  Examples: Contracts, Gateway, AI, Frontend │
└─────────────────────────────────────────────┘
                    ↓ uses
┌─────────────────────────────────────────────┐
│  TIER 2: EMERGENT CAPABILITIES              │
│  - Domain-specific patterns                 │
│  - Usage not yet proven                     │
│  - Low cost to extract later                │
│  - Extract after RULE OF TWO/THREE          │
│  Examples: ADR, Workflow, Notifications     │
└─────────────────────────────────────────────┘
```

**Why this matters**:
- Foundation enables rapid project development
- Domain capabilities emerge from real usage
- No premature abstraction
- No wasted effort on unused framework features

### Insight 2: Emergence Over Architecture

**The Emergence Philosophy**:
```
Real Projects → Real Patterns → Extract → Framework Emerges
     ↑                                            │
     └────────────── Feedback Loop ───────────────┘
```

Not:
```
Perfect Architecture → Build Projects to Fit Architecture
```

**Why this works**:
- Patterns proven in real usage (not theoretical)
- Framework solves actual problems (not imagined ones)
- Can course-correct quickly (only 3-4 months invested)
- Team learns what actually works (not guesses)

### Insight 3: Rule of Two/Three

**The Rule**:
- **1st use** (one project): Keep in project, tag "Candidate for sharing"
- **2nd use** (different project): Copy with intention, start designing interface
- **3rd use**: MUST extract to shared repo

**Why this specific number**:
- 1 use: Don't know if pattern is general
- 2 uses: See variations, can design abstraction
- 3 uses: Confident pattern works, worth extracting
- 4+ uses: Too late, too much duplication

**Exception**: Foundational infrastructure (known to be needed) extracts immediately

### Insight 4: Contracts-First, Everything Else Emerges

**Why Protobuf contracts are special**:
- Zero downside (just types, no implementation)
- High value (type safety across all languages)
- No premature abstraction (types are concrete)
- Enables rapid development (generate code)
- Forces clear boundaries (schema design)

**Start with**:
```
shared/contracts/proto/
├── common/v1/          # User, Org, Error (foundational)
├── ai/v1/              # Chat, Completion (foundational)
└── [domain]/v1/        # Domain-specific (emergent)
```

### Insight 5: Technology as Solution, Not Problem

**Not "two-language problem"** (prototype in Python, rewrite in Rust)

**But "two-language solution"**:
- **Rust**: Synchronous, user-facing, real-time (where it excels)
- **Python**: Asynchronous, ML workflows, complex orchestration (where it excels)
- **TypeScript**: Browser, SSR, type-safe UI (where it excels)
- **Boundary**: Kafka event bus (clean architectural separation)

**Pattern from ADR Platform Architecture**:
```
Browser (TS)
    ↓ gRPC-Web
Rust Services (sync tier)
    ↓ Kafka
Python Workers (async tier)
    ↓
Postgres
```

### Insight 6: Repository Topology Matters

**Not**:
- ❌ Giant monorepo (everything coupled, can't reuse externally)
- ❌ Many tiny repos (coordination hell, version chaos)

**But**:
- ✅ **Hybrid**: Shared repos (versioned) + Project monorepos (fast iteration)
- ✅ **Google Repo tool**: Optional coordination (use when needed)
- ✅ **Clear boundaries**: Shared vs project-specific

**Structure**:
```
shared/              # Foundational infrastructure (versioned)
capabilities/        # Emergent capabilities (versioned)
projects/            # Project monorepos (independent)
```

---

## Open Questions

### Questions to Answer in Next Stage

**Architecture**:
- [ ] Which specific provider SDKs to use? (Anthropic SDK, OpenAI SDK)
- [ ] Envoy vs custom gateway layer?
- [ ] Postgres pgvector vs dedicated vector DB (Qdrant)?
- [ ] Managed Kafka vs Redpanda vs NATS JetStream?

**Organization**:
- [ ] Naming conventions for shared repos?
- [ ] How to handle breaking changes in shared repos?
- [ ] Who owns what? (platform team vs project teams)

**Process**:
- [ ] How often to review for extraction?
- [ ] What's the approval process for new shared repos?
- [ ] How to handle version conflicts?

**Scope**:
- [ ] Which projects will be the first two?
- [ ] What features will they build?
- [ ] Which patterns will likely be shared?

### Deferred Questions (Not Now)

- Detailed API designs (too early)
- Specific library versions (will evolve)
- Performance optimization (premature)
- Multi-region deployment (future)
- Advanced Bazel usage (later)

---

## Related Concepts

### Foundation for Understanding

Before reading other documents, understand these core concepts:

**Foundational vs Emergent**:
- See [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) for what's foundational
- See [03-emergent-capabilities.md](./03-emergent-capabilities.md) for what's emergent
- Rule: Known infrastructure → foundational, Domain logic → emergent

**Rule of Two/Three**:
- See [06-extraction-rules.md](./06-extraction-rules.md) for detailed rules
- Applied to emergent capabilities only
- Foundational infrastructure exempt (extracted immediately)

**Emergence Philosophy**:
- See [07-implementation-roadmap.md](./07-implementation-roadmap.md) for how it plays out
- Build real projects first, extract patterns second
- Framework emerges from battle-tested code

### Key Design Patterns

**From Reference Projects** (see [10-reference-projects.md](./10-reference-projects.md)):

1. **FlowOS Pattern**: Contracts → Engines → Apps
   - Contracts = Protobuf schemas (single source of truth)
   - Engines = Reusable capabilities (shared repos)
   - Apps = Projects using capabilities (project monorepos)

2. **Hexagonal Architecture** (Ports & Adapters):
   - Domain = Pure business logic (no infrastructure)
   - Ports = Interfaces/traits (abstraction)
   - Adapters = Implementations (swappable)

3. **Event-Driven Boundary**:
   - Synchronous = gRPC (Rust services)
   - Asynchronous = Kafka (Python workers)
   - Clean separation, independent scaling

### Connecting to Other Documents

**If you want to know WHAT to build**:
- → [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - 7 foundational pieces
- → [03-emergent-capabilities.md](./03-emergent-capabilities.md) - Domain capabilities

**If you want to know HOW to organize**:
- → [04-repository-strategy.md](./04-repository-strategy.md) - Repo topology
- → [05-technology-integration.md](./05-technology-integration.md) - Language integration

**If you want to know WHEN to extract**:
- → [06-extraction-rules.md](./06-extraction-rules.md) - Rules and decision tree
- → [08-decision-framework.md](./08-decision-framework.md) - Decision tools

**If you want to know execution plan**:
- → [07-implementation-roadmap.md](./07-implementation-roadmap.md) - 90-day roadmap

---

## Next Steps

### For This Document

- [ ] Validate core insights with team
- [ ] Answer open questions (move to design docs)
- [ ] Identify two real projects to start with
- [ ] Mark as STABLE when insights are validated

### For Overall Strategy

1. **Week 1-2**: Design foundational infrastructure
   - Detail out the 7 foundational pieces
   - Create initial protobuf contracts
   - Document patterns from ADR PoC

2. **Week 3-4**: Set up project structure
   - Choose two real projects
   - Create project templates
   - Establish build/CI patterns

3. **Month 2-3**: Build and learn
   - Projects ship features
   - Tag potential shared code
   - Weekly extraction reviews

4. **Month 4+**: Extract and scale
   - Extract when 3rd use appears
   - Refine shared repos
   - Onboard more projects

---

## Success Criteria

This strategic context is successful when:

**Understanding**:
- ✅ Team understands foundational vs emergent distinction
- ✅ Team understands rule of two/three
- ✅ Team understands emergence philosophy
- ✅ Clear why not building framework first

**Alignment**:
- ✅ Agreement on two-tier approach
- ✅ Agreement on extraction rules
- ✅ Agreement on repository strategy
- ✅ Agreement on technology choices

**Readiness**:
- ✅ Can confidently design foundational infrastructure
- ✅ Can identify what's foundational vs emergent
- ✅ Can make extraction decisions
- ✅ Ready to start building

**Evolution**:
- ✅ Core insights captured in ADRs
- ✅ Strategy document evolves into architecture docs
- ✅ Decision framework becomes operational
- ✅ Success metrics are trackable

---

## References

**Internal**:
- ADR PoC: [../../README.md](../../README.md) - Reference implementation
- Atomic Tasks: [../atomic-tasks/](../atomic-tasks/) - ADR PoC task breakdown

**External Patterns**:
- FlowOS: Contracts → Engines → Apps layering
- Multi-Repo Strategy: Google Repo tool approach
- ADR Platform: Rust + Python + TypeScript integration
- CLI Tools: Command patterns and testing

**Philosophy**:
- YAGNI: You Aren't Gonna Need It (don't build what you don't need)
- Rule of Three: Don't abstract until 3rd use (Sandi Metz, Martin Fowler)
- Emergence: Patterns emerge from real usage (not planned upfront)

---

**Status Notes**:
- **EXPLORING**: Core insights documented, need validation
- **Next**: Team review and alignment
- **After**: Convert stable insights to ADRs
