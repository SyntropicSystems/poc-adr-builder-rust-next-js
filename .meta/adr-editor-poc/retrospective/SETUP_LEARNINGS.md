# Setup Phase Learnings

**Date**: 2025-10-20  
**Phase**: Documentation & Foundation Setup

---

## 🎓 What We Learned

### 1. Documentation Architecture

**Insight**: Separation of concerns between `.meta/` and `docs/` is crucial

**What Worked**:
- ✅ `docs/` as single source of truth (finalized, living docs)
- ✅ `.meta/` for ephemeral work (drafts, explorations)
- ✅ `llm.md` as lightweight navigation hub (not content dump)
- ✅ Code-as-truth philosophy prevents drift

**Key Decision**: Don't duplicate - reference the source of truth

### 2. Tool Hierarchy Clarity

**Insight**: Package.json can mislead about primary tools

**What We Fixed**:
- ❌ Initial `package.json` implied pnpm was primary
- ✅ Updated with script prefixes (`web:*`, `docs:*`)
- ✅ Made Cargo's primacy explicit in comments
- ✅ Clarified Python's role (utilities only)

**Learning**: Make tool roles crystal clear upfront

### 3. Multi-Language Project Structure

**Insight**: Three languages need clear boundaries

**Structure That Works**:
```
Rust (Primary)     → Cargo is the main tool
TypeScript (UI)    → pnpm only for apps/adr-web/
Python (Utilities) → Scripts only, not core system
Bazel (Learning)   → Optional validation
```

**Anti-Pattern**: Using package.json as workspace root creates confusion

### 4. Bazel Integration

**Insight**: Bazel for learning, not daily development

**What We Decided**:
- ✅ Minimal WORKSPACE file (learning)
- ✅ Cargo/pnpm for primary development
- ✅ Bazel validates structure works
- ❌ Don't let Bazel slow down PoC

**Learning**: Learn incrementally, don't block on tooling

---

## 🔧 Technical Decisions

### Python 3.14 for Scripts

**Why**: Better than bash scripts
- More robust error handling
- Easier to read and maintain
- Cross-platform compatibility
- Rich library ecosystem

**Use Cases**:
- Documentation validation
- Code generation helpers
- Build automation

**Not For**: Core system logic (that's Rust)

### pnpm vs npm/yarn

**Why pnpm**:
- Disk efficient (content-addressed storage)
- Faster than alternatives
- Strict (no phantom dependencies)
- Monorepo-ready

**Learning**: Worth the small setup cost

---

## 📋 Documentation Principles Validated

### Code is Truth

**Principle**: When docs and code conflict, code wins

**Implementation**:
1. `.proto` files generate docs (not written manually)
2. `clap` definitions generate CLI help
3. Tests validate examples work
4. Compiler enforces architecture

**Result**: Drift is impossible by design

### Strategic Documentation Only

**Document**:
- ✅ WHY decisions were made (ADRs)
- ✅ HOW to work (development guides)
- ✅ WHAT the architecture is (high-level)

**Don't Document**:
- ❌ Implementation details (code is self-documenting)
- ❌ Generated content (use generation)
- ❌ Obvious information

**Result**: Minimal, high-value documentation

---

## 🚀 What's Ready for Phase 1

### Foundation in Place
- ✅ Complete documentation architecture
- ✅ Clear tool hierarchy
- ✅ Validation strategy
- ✅ Migration path defined

### Can Now Create
- Cargo workspace (structure is documented)
- Protobuf schema (patterns are clear)
- Domain crate (architecture is defined)
- SDK crate (ports pattern is documented)

### AI Agent Ready
- Any new agent can read `llm.md`
- Navigate to relevant documentation
- Understand all decisions
- Start contributing immediately

---

## ⚠️ Challenges Encountered

### 1. Naming Confusion

**Issue**: Repo named for "task management" but docs for "ADR editor"

**Resolution**: Building ADR editor, repo will be renamed

**Learning**: Align naming early

### 2. Tool Hierarchy Clarity

**Issue**: Initial package.json made pnpm seem primary

**Resolution**: Added comments, prefixes, clearer structure

**Learning**: Make tool roles explicit

### 3. .meta/ vs docs/ Distinction

**Issue**: When to use which location?

**Resolution**: 
- `.meta/` = ephemeral, work-in-progress
- `docs/` = finalized, source of truth

**Learning**: Clear separation prevents duplication

---

## 💡 Best Practices Established

### 1. Documentation Strategy
- Code first, docs second
- Generate when possible
- Validate automatically
- Keep minimal

### 2. Repository Structure
- Mirror monorepo structure
- Use standard names (`crates/`, `apps/`, `proto/`)
- Flat structure initially (< 10 items)

### 3. Tool Usage
- Cargo for Rust (primary)
- pnpm for frontend (secondary)
- Python for utilities (support)
- Bazel for validation (optional)

### 4. Context Management
- llm.md as entry point
- Documentation map with clear links
- Single source of truth per topic

---

## 📈 Metrics

**Documentation Created**: 22 files
**Time Spent**: ~4 EU
**Tool Clarity**: Achieved (Cargo primary, roles defined)
**Migration Readiness**: High (< 4 EU to migrate)

---

## 🎯 Success Indicators

- ✅ Any AI agent can read llm.md and understand project
- ✅ Documentation is self-contained (no dependencies on .meta/task-service/)
- ✅ Tool hierarchy is clear (Cargo > pnpm > Python > Bazel)
- ✅ Code-as-truth philosophy established
- ✅ Validation strategy in place

---

## 🔄 What Would We Do Differently?

### If Starting Over

1. **Tool hierarchy first**: Clarify Cargo is primary before package.json
2. **Documentation architecture upfront**: Establish .meta/ vs docs/ early
3. **Naming alignment**: Ensure repo name matches domain immediately

### What We Got Right

1. ✅ Comprehensive planning before implementation
2. ✅ Documentation-first approach
3. ✅ Clear separation of concerns
4. ✅ Code-as-truth philosophy
5. ✅ Migration strategy designed upfront

---

**Status**: Documentation phase complete. Ready for Phase 1 implementation.
