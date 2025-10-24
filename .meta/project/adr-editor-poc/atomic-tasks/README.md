# Atomic Tasks

**Purpose**: Incremental, value-driven task breakdown for ADR Editor PoC implementation

**Status**: Active
**Created**: 2025-10-24
**Last Updated**: 2025-10-24

---

## 🎯 Purpose

This folder contains **atomic tasks** that build the ADR Editor PoC incrementally from zero to a complete system. Each task:

- **Delivers atomic value** - Produces a working, testable increment
- **Has clear boundaries** - Single responsibility, well-defined scope
- **Builds on previous tasks** - Sequential dependencies, no circular deps
- **Is independently verifiable** - Has acceptance criteria and tests

**Goal**: Enable both humans and LLMs to understand, track, and execute implementation with full context.

---

## 📂 Structure

```
atomic-tasks/
├── README.md              # This file - Purpose and rules
├── INDEX.md               # Navigation hub + status dashboard
├── 001-*.md              # Phase 1: Foundation (Tasks 1-5)
├── 002-*.md
├── ...
├── 010-*.md              # Phase 3: gRPC Service (Tasks 10-14)
├── ...
└── 030-*.md              # Phase 7: Final validation
```

### File Naming Convention

```
<TASK_ID>-<slug-name>.md

Examples:
- 001-create-cargo-workspace.md
- 015-create-nextjs-app.md
- 030-validate-end-to-end.md
```

**Rules**:
- Task ID: 3-digit zero-padded (001-030)
- Slug: Kebab-case, descriptive, max 5 words
- Extension: Always `.md`

---

## 📋 Task File Format

Each task file MUST follow this structure:

```markdown
# Task XXX: [Title]

**Phase**: [Phase Name]
**Status**: [pending|in-progress|completed|blocked]
**Estimated Time**: X EU
**Actual Time**: X EU (when completed)

---

## 📍 Context

**Dependencies**:
- Task XXX: [Dependency name]
- Task XXX: [Another dependency]

**Blocks**:
- Task XXX: [Tasks waiting on this]

**Value Delivered**:
[Clear statement of what working capability this task enables]

---

## 📝 Description

[Detailed description of what needs to be done]

---

## ✅ Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## 🔧 Implementation Notes

[Technical details, decisions, approaches]

---

## 🧪 Verification

**How to test**:
```bash
# Commands to verify task completion
```

**Expected outcome**:
[What should happen when tests pass]

---

## 📚 Resources

- [Link to relevant docs]
- [Related ADRs]
- [External references]

---

## 📝 Completion Notes

**Date Completed**: YYYY-MM-DD
**Completed By**: [Name/AI Agent]

**Learnings**:
- [Key insights from implementation]

**Deviations**:
- [Any changes from original plan]
```

---

## 🔄 Workflow Rules

### For Humans

**Starting a task**:
1. Check `INDEX.md` for current status
2. Open task file (e.g., `001-create-cargo-workspace.md`)
3. Read dependencies - ensure they're completed
4. Update status to `in-progress` in task file AND `INDEX.md`
5. Implement according to acceptance criteria
6. Run verification commands
7. Update status to `completed` with completion notes
8. Update `INDEX.md` status

**Creating new tasks** (if needed):
1. Use next available task ID
2. Follow file format exactly
3. Add to `INDEX.md` in appropriate phase
4. Update dependency chains

### For LLMs

**Context Loading**:
1. **Always read** `INDEX.md` first for overview
2. Read current task file for details
3. Check dependencies - read completed task files if needed
4. Load relevant docs from `docs/` directory

**Executing a task**:
1. Read task file completely
2. Verify dependencies are completed
3. Create implementation plan
4. Update task status to `in-progress`
5. Implement (create files, write code, tests)
6. Run verification commands
7. Mark acceptance criteria as completed
8. Update status to `completed` with notes
9. Update `INDEX.md`

**Status updates**:
- Update task file status field
- Update `INDEX.md` matching entry
- Keep both in sync (CRITICAL)

---

## 📊 Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `pending` | Not started | Can start if dependencies done |
| `in-progress` | Currently being worked on | Complete implementation |
| `completed` | Done and verified | Move to next task |
| `blocked` | Waiting on external factor | Resolve blocker |

**Rule**: Only ONE task should be `in-progress` at a time (focus!)

---

## 🎯 Phases Overview

| Phase | Tasks | Goal | Value Checkpoint |
|-------|-------|------|------------------|
| **1: Foundation** | 001-005 | Build infrastructure | Can compile & test domain |
| **2: CLI Tool** | 006-009 | Working CLI | Usable ADR management tool |
| **3: gRPC Service** | 010-014 | Network API | Remote ADR operations |
| **4: Next.js Frontend** | 015-022 | Web UI | Full-stack application |
| **5: Testing** | 023-025 | Reliability | Regression protection |
| **6: Build System** | 026-027 | Monorepo ready | Migration validated |
| **7: Documentation** | 028-030 | Complete PoC | Handoff ready |

---

## 🚨 Critical Rules

### DO

✅ **Keep status in sync** - Task file AND INDEX.md
✅ **Update completion notes** - Document learnings
✅ **Follow dependencies** - Don't skip ahead
✅ **Run verification** - Always test before marking complete
✅ **Document deviations** - Note any changes from plan

### DON'T

❌ **Skip dependencies** - Will break incremental value
❌ **Work on multiple tasks** - Focus on one at a time
❌ **Mark complete without testing** - Must verify
❌ **Change format** - Consistency critical for parsing
❌ **Delete completed tasks** - Keep for historical context

---

## 🔍 Finding Information

| Need | Check |
|------|-------|
| Current status | `INDEX.md` - Status Dashboard |
| Next task to work on | `INDEX.md` - First `pending` with dependencies done |
| Task details | Individual task file (e.g., `015-*.md`) |
| Dependencies | Task file → Dependencies section |
| Blocked tasks | Task file → Blocks section |
| Progress by phase | `INDEX.md` - Phase sections |
| Historical context | Completed task files → Completion Notes |

---

## 📏 Quality Standards

**Before marking a task complete**:
1. ✅ All acceptance criteria checked
2. ✅ Verification commands run successfully
3. ✅ Tests pass (if applicable)
4. ✅ Code committed to git
5. ✅ Documentation updated (if required)
6. ✅ Completion notes filled in
7. ✅ INDEX.md status updated

**Incomplete work**:
- Keep status as `in-progress`
- Add notes about what's done
- Document what remains
- Don't lie about completion (integrity!)

---

## 🔄 Maintenance

**Weekly**:
- Review `INDEX.md` for accuracy
- Update time estimates based on actuals
- Document patterns/learnings

**Per Task**:
- Update status immediately when changed
- Fill completion notes within 1 hour of finishing
- Update any blocked tasks if you unblock them

**End of Phase**:
- Review all completed tasks
- Document phase-level learnings
- Update estimates for remaining phases

---

## 🤖 LLM Integration Notes

**For AI agents working with this system**:

1. **Session start**: Read `INDEX.md` first (context anchor)
2. **Before any task**: Verify dependencies complete
3. **During task**: Keep notes in task file as you work
4. **After task**: Always update both task file AND INDEX.md
5. **Blockers**: Document clearly - humans may need to resolve

**Context Windows**:
- INDEX.md: ~500 tokens (always load)
- Task file: ~300-500 tokens (load current + dependencies)
- Total context: Keep under 5K tokens for task context

**Parallel work**:
- Multiple agents: Coordinate via INDEX.md status
- Lock mechanism: Update status to `in-progress` atomically
- Conflicts: Last write wins - check before updating

---

## 📞 Support

**Questions?**
- Architecture: See `docs/architecture/`
- Development: See `docs/development/`
- Decisions: See `docs/adr/`
- Context: See `llm.md` (root)

**Issues with tasks?**
- Unclear acceptance criteria: Update task file + note reason
- Blocked: Mark as `blocked` + document blocker
- Dependency missing: Add task + update dependencies

---

## 📈 Success Metrics

**Task quality**:
- All acceptance criteria met
- Verification passes
- No rework needed on dependencies

**Process quality**:
- Status always accurate
- Dependencies followed in order
- Completion notes provide value

**Outcome quality**:
- Each task delivers stated value
- Incremental builds work at each step
- PoC goals validated by end

---

**Remember**: These tasks are designed for **incremental value delivery**. Each completed task should leave the system in a working, testable state. Never move forward with broken foundations!
