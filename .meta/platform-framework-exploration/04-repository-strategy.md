# Repository Strategy: Multi-Repo Topology

**Status**: EXPLORING
**Last Updated**: 2025-10-24
**Related Documents**:
- ← [01-strategic-context.md](./01-strategic-context.md) - Strategic context for repository choices
- ← [02-foundational-infrastructure.md](./02-foundational-infrastructure.md) - What goes in shared/
- ← [03-emergent-capabilities.md](./03-emergent-capabilities.md) - What goes in capabilities/
- → [05-technology-integration.md](./05-technology-integration.md) - How technologies integrate across repos
- → [06-extraction-rules.md](./06-extraction-rules.md) - When and how to extract code to shared repos

---

## Context

### The Repository Topology Problem

When building multiple projects that share code, we face a fundamental tension:

**Monorepo Approach**:
- ✅ Easy code sharing
- ✅ Atomic changes across projects
- ✅ Single build system
- ❌ Everything coupled together
- ❌ Can't reuse externally
- ❌ Scales poorly over time
- ❌ Hard to version independently

**Many Tiny Repos**:
- ✅ Independent versioning
- ✅ Can reuse externally
- ✅ Clear ownership
- ❌ Coordination nightmare
- ❌ Version conflict hell
- ❌ Hard to make cross-cutting changes
- ❌ Build system duplication

**What We Need**:
- Projects that iterate quickly (monorepo benefits)
- Shared code that's reusable (independent versioning)
- Optional coordination when needed (not mandatory)
- Clear boundaries between shared and project-specific
- Easy to extract patterns when they emerge

### Key Constraints

**Known From Experience**:
1. Need to support both rapid prototyping (PoC) and production platforms
2. Multiple projects will share foundational infrastructure
3. Some domain capabilities will emerge over time (rule of two/three)
4. Need external reusability (can't lock everything in one monorepo)
5. Want fast iteration within projects (monorepo style)

**Unknown Factors**:
- Exactly how many shared repos we'll end up with
- How frequently breaking changes will occur
- Whether Google Repo tool will be sufficient or need custom tooling
- How to handle version conflicts when they arise

---

## Key Insights

### Insight 1: Hybrid Topology

Not monorepo OR multi-repo, but **both where each excels**:

```
┌─────────────────────────────────────────────┐
│  SHARED REPOS (versioned, external reuse)   │
│  - Foundational infrastructure              │
│  - Extracted capabilities                   │
│  - Published as versioned crates/packages   │
│  - Independent release cycles               │
└─────────────────────────────────────────────┘
                    ↑ uses
┌─────────────────────────────────────────────┐
│  PROJECT MONOREPOS (fast iteration)         │
│  - Project-specific code                    │
│  - Multiple crates/packages within          │
│  - Rapid iteration without versioning       │
│  - Can depend on shared repos               │
└─────────────────────────────────────────────┘
```

**Benefits**:
- Shared code versioned and reusable → foundational infrastructure stable
- Projects iterate quickly → no versioning overhead during development
- Can coordinate when needed → Google Repo tool for multi-repo workflows
- Clear extraction path → proven patterns move from project → shared

### Insight 2: Google Repo Tool for Coordination

**Not**: Mandatory monorepo tooling (like Bazel workspace or Git submodules)

**But**: Optional coordination when you need to work across repos

**What is Google Repo**:
- Manifest-based multi-repo coordination
- Developed for Android (manages 1000+ Git repos)
- Simple XML manifest describes repo layout
- Commands: `repo sync`, `repo start`, `repo upload`
- Each repo is still independent Git repo

**When to use it**:
- Working on feature that spans shared + project
- Making breaking change across multiple repos
- Onboarding new developer (one command to clone everything)
- Running integration tests across repos

**When NOT to use it**:
- Day-to-day work within single project
- Working on isolated feature
- Just using shared repos as dependencies

**Example Manifest** (`.repo/manifest.xml`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <!-- Shared foundational infrastructure -->
  <project name="shared/contracts" path="shared/contracts" />
  <project name="shared/api-gateway-core" path="shared/api-gateway-core" />
  <project name="shared/ai-gateway-sdk" path="shared/ai-gateway-sdk" />

  <!-- Emergent capabilities (as they're extracted) -->
  <project name="capabilities/adr-domain" path="capabilities/adr-domain" />

  <!-- Projects -->
  <project name="projects/adr-platform" path="projects/adr-platform" />
  <project name="projects/second-platform" path="projects/second-platform" />
</manifest>
```

**Workflow**:
```bash
# Setup (one time)
repo init -u https://github.com/org/manifests
repo sync

# Daily work
cd projects/adr-platform/
# ... normal git operations

# Cross-repo feature
repo start feature-name --all
# ... work across multiple repos
repo upload
```

### Insight 3: Three-Layer Structure

```
workspace/
├── shared/              # Tier 1: Foundational Infrastructure
│   ├── contracts/       # Proto schemas (all projects need)
│   ├── api-gateway-core/
│   ├── ai-gateway-sdk/
│   ├── frontend-foundation/
│   ├── observability-sdk/
│   ├── cli-framework/
│   └── storage-patterns/
│
├── capabilities/        # Tier 2: Emergent Capabilities
│   ├── adr-domain/      # Extracted after 3rd use
│   ├── workflow-engine/ # (when it emerges)
│   └── notification-sdk/# (when it emerges)
│
└── projects/            # Project Monorepos
    ├── adr-platform/    # First project (Cargo workspace)
    │   ├── crates/
    │   ├── frontend/
    │   └── workers/
    └── second-platform/ # Second project (future)
```

**Why This Structure**:
- **shared/**: 100% certainty needed, extract immediately, versioned
- **capabilities/**: Proven by usage (rule of two/three), versioned when extracted
- **projects/**: Fast iteration, no versioning needed, monorepo style

**Repository Boundaries**:
- Each folder in `shared/` = separate Git repo
- Each folder in `capabilities/` = separate Git repo
- Each folder in `projects/` = separate Git repo (but internally a monorepo)

### Insight 4: Versioning Strategy

**Shared Repos** (foundational infrastructure):
```toml
# Cargo.toml in shared/contracts
[package]
name = "contracts"
version = "0.1.0"  # Semantic versioning
```

**Project Consumption**:
```toml
# projects/adr-platform/Cargo.toml
[dependencies]
contracts = { git = "https://github.com/org/contracts", tag = "v0.1.0" }
```

**When to bump versions**:
- **Patch** (0.1.0 → 0.1.1): Bug fixes, no API changes
- **Minor** (0.1.0 → 0.2.0): New features, backward compatible
- **Major** (0.1.0 → 1.0.0): Breaking changes

**Breaking Change Process**:
1. Create feature branch in shared repo
2. Use `repo` manifest to test across projects
3. Update all consumers to new API
4. Merge and tag new major version
5. Projects update dependency version

**Capabilities Repos** (emergent):
- No versioning until 3rd use (when extracted)
- First version is 0.1.0 (not 1.0.0, signals early stage)
- Expect iteration and changes initially

**Project Repos**:
- No versioning of internal crates
- Fast iteration without semver overhead
- Can tag releases if deploying to production

### Insight 5: Extraction Process

**When Code Lives in Project** (before extraction):
```
projects/adr-platform/
└── crates/
    └── adr-domain/      # Not yet extracted
        ├── src/
        └── Cargo.toml
```

**After Extraction to Shared**:
```
capabilities/adr-domain/  # New repo
├── src/
├── Cargo.toml
├── README.md
└── .github/workflows/

projects/adr-platform/
└── Cargo.toml           # Now depends on capabilities/adr-domain
```

**Steps**:
1. **Identify extraction candidate** (3rd use, or foundational)
2. **Create new repo** in appropriate location (shared/ or capabilities/)
3. **Copy code** with git history (`git filter-branch` or `git subtree`)
4. **Add versioning** (Cargo.toml version field)
5. **Add README and docs**
6. **Update project** to depend on new repo
7. **Add to repo manifest** (if using Google Repo)
8. **Document** in capability tracking or foundational docs

### Insight 6: Dependency Flow

**Allowed Dependencies**:
```
Projects → Capabilities → Shared → External
  ↓           ↓             ↓
  ✓           ✓             ✓
```

**NOT Allowed**:
- ❌ Shared → Capabilities (foundational can't depend on emergent)
- ❌ Shared → Projects (foundational can't depend on projects)
- ❌ Capabilities → Projects (emergent can't depend on projects)

**Why This Matters**:
- Prevents circular dependencies
- Keeps shared code truly reusable
- Makes extraction order clear
- Foundational infrastructure stays pure

**Example Valid Dependency**:
```toml
# projects/adr-platform/crates/api-service/Cargo.toml
[dependencies]
# ✅ Can depend on capabilities
adr-domain = { git = "...", tag = "v0.2.0" }

# ✅ Can depend on shared
api-gateway-core = { git = "...", tag = "v0.1.0" }
contracts = { git = "...", tag = "v0.1.0" }
```

**Example Invalid Dependency**:
```toml
# shared/api-gateway-core/Cargo.toml
[dependencies]
# ❌ CANNOT depend on capabilities
adr-domain = { git = "...", tag = "v0.2.0" }  # WRONG!
```

---

## Open Questions

### Questions for Next Stage

**Repository Hosting**:
- [ ] GitHub organization structure? (e.g., `org/shared-contracts`, `org/capability-adr`)
- [ ] Naming conventions for repos? (prefix vs folder structure in name)
- [ ] Public vs private repos? (can foundational infra be open source?)
- [ ] Who has write access to shared vs capabilities repos?

**Google Repo Tool**:
- [ ] Where to host manifest repo?
- [ ] How often to update manifest? (every shared repo release?)
- [ ] Should manifest track specific versions or branches?
- [ ] Alternative to Repo tool if we outgrow it?

**Versioning**:
- [ ] Pre-1.0 versioning strategy? (how long in 0.x?)
- [ ] How to communicate breaking changes?
- [ ] Process for coordinating multi-repo breaking changes?
- [ ] Automated version bumping? (conventional commits?)

**Build System**:
- [ ] Bazel workspace vs Cargo workspace for projects?
- [ ] How to handle shared build configuration?
- [ ] CI/CD per repo or centralized?
- [ ] Cross-repo integration tests?

**Extraction Mechanics**:
- [ ] Who approves extraction to shared repos?
- [ ] Code review process for shared vs project code?
- [ ] How to preserve git history during extraction?
- [ ] Deprecation process for code being extracted?

### Deferred Questions (Not Now)

- Monorepo tools like Nx or Turborepo (premature)
- Dependency graph visualization (nice to have, later)
- Automated dependency updates (Dependabot, Renovate)
- Multi-language package management (poetry, npm, cargo together)

---

## Related Concepts

### Connection to Other Documents

**Foundational Infrastructure** ([02-foundational-infrastructure.md](./02-foundational-infrastructure.md)):
- Each of the 7 foundational pieces → separate repo in `shared/`
- Repos created in Week 1-2 of roadmap
- All projects depend on these from day one

**Emergent Capabilities** ([03-emergent-capabilities.md](./03-emergent-capabilities.md)):
- Live in project repos initially
- Move to `capabilities/` on 3rd use
- Each capability → separate versioned repo
- Track usage across projects before extracting

**Extraction Rules** ([06-extraction-rules.md](./06-extraction-rules.md)):
- Decision tree determines shared/ vs capabilities/ vs stay in project
- Process documented for how to move code between repos
- Clear criteria for when to create new repo

**Technology Integration** ([05-technology-integration.md](./05-technology-integration.md)):
- Shared repos can contain Rust, Python, or TypeScript
- Protobuf contracts span all languages
- Each language follows its own package management within repos

### Repository Lifecycle

```
1. Code written in project repo (fast iteration)
      ↓
2. Tagged as "candidate for sharing" (1st use)
      ↓
3. Used in 2nd project (copied with intention)
      ↓
4. Used in 3rd project → EXTRACT to capabilities/
      ↓
5. Versioned, independent releases
      ↓
6. (Optional) Promoted to shared/ if becomes foundational
```

### Coordination Patterns

**Pattern 1: Independent Project Work**
- Developer works in single project repo
- Depends on versioned shared/capabilities repos
- No coordination needed
- Standard Git workflow

**Pattern 2: Cross-Repo Feature**
- Use `repo` manifest to checkout all repos
- Branch in multiple repos simultaneously
- Test changes together locally
- PR to each repo individually
- Coordinate merge timing

**Pattern 3: Breaking Change**
- Create feature branch in shared repo
- Update manifest to point to feature branch
- Update all consuming projects
- Verify everything works together
- Merge shared repo, tag new version
- Update projects to use new version
- Update manifest to stable versions

---

## Next Steps

### For This Document

- [ ] Validate repo topology with team
- [ ] Answer repository hosting questions
- [ ] Decide on Repo tool or alternative
- [ ] Create repo naming conventions
- [ ] Mark as STABLE when structure is agreed

### For Implementation

**Week 1-2** (Foundational Repos):
1. Create GitHub organization (or equivalent)
2. Create repos for 7 foundational pieces
3. Set up initial directory structure
4. Create initial repo manifest
5. Document repo creation process

**Week 3-4** (First Projects):
1. Create first two project repos
2. Set up as Cargo/npm workspaces internally
3. Add dependencies on shared repos
4. Test repo coordination workflow
5. Document learnings

**Month 2-3** (Usage Tracking):
1. Tag potential shared code in projects
2. Track usage across projects
3. Weekly extraction review meetings
4. Update manifest as repos are added

**Month 4+** (Extractions):
1. Extract capabilities on 3rd use
2. Set up versioning for each capability
3. Update consuming projects
4. Refine extraction process based on learnings

---

## Success Criteria

This repository strategy is successful when:

**Structure**:
- ✅ Clear distinction between shared/, capabilities/, projects/
- ✅ Each repo has clear purpose and boundaries
- ✅ Dependency flow is one-directional
- ✅ Can work in single repo without coordination overhead

**Process**:
- ✅ Extraction process is documented and practiced
- ✅ Can extract code to new repo in < 1 day
- ✅ Projects can depend on shared code easily
- ✅ Breaking changes have clear process

**Developer Experience**:
- ✅ New developer can clone and build single project quickly
- ✅ Can optionally use coordination tool for cross-repo work
- ✅ Clear where new code should live (shared vs project)
- ✅ Version conflicts are rare and resolvable

**Coordination**:
- ✅ Google Repo manifest (or alternative) works well
- ✅ Cross-repo changes are manageable
- ✅ CI/CD per repo works correctly
- ✅ Integration testing across repos is possible

**Evolution**:
- ✅ Can add new shared repos easily
- ✅ Can add new projects easily
- ✅ Extraction doesn't disrupt project work
- ✅ Structure scales to 10+ projects

---

## References

**Internal**:
- ADR PoC: [../../README.md](../../README.md) - Current single-repo structure
- Atomic Tasks: [../atomic-tasks/](../atomic-tasks/) - Task breakdown for single project

**External Patterns**:
- Google Repo tool: https://gerrit.googlesource.com/git-repo/
- Android multi-repo structure
- Chromium depot_tools approach
- Cargo workspace docs: https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html

**Philosophy**:
- Hybrid topology: Get benefits of both monorepo and multi-repo
- Optional coordination: Use coordination tool when needed, not mandatory
- Clear boundaries: Foundational vs emergent vs project-specific
- Gradual extraction: Prove patterns before sharing

---

**Status Notes**:
- **EXPLORING**: Structure documented, need validation
- **Next**: Team review, answer open questions about hosting and naming
- **After**: Create first repos, test coordination tool
