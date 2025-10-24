# ADR Editor PoC - Meta Workspace

**Purpose**: Ephemeral working documents and project management for ADR Editor PoC

---

## 📂 Structure

```
.meta/adr-editor-poc/
├── README.md                    # This file
├── implementation-plan/         # Current phase planning
│   └── CURRENT_PHASE.md        # What we're working on now
└── retrospective/               # Learnings and reflections
    └── SETUP_LEARNINGS.md      # What we learned during setup
```

---

## 🎯 Purpose of This Workspace

This workspace contains **ephemeral** documents that support development but are NOT part of the final system.

**Ephemeral means**:
- Work-in-progress plans
- Sprint notes
- Design explorations
- Retrospectives
- Temporary analysis

**NOT for**:
- Finalized decisions → `docs/adr/`
- Architecture docs → `docs/architecture/`
- Development guides → `docs/development/`
- Code → `crates/`, `apps/`

---

## 🔄 Relationship to docs/

### When to Use .meta/ vs docs/

| Content | Location | Why |
|---------|----------|-----|
| **Finalized decisions** | `docs/adr/` | Single source of truth |
| **Exploring options** | `.meta/` | Work in progress |
| **Architecture overview** | `docs/architecture/` | Living documentation |
| **Design draft** | `.meta/` | Not final yet |
| **Development workflow** | `docs/development/` | How to work |
| **Sprint plan** | `.meta/` | Temporary planning |

### Migration Path

```
Design exploration (.meta/)
    ↓
Decision made
    ↓
Create ADR (docs/adr/)
    ↓
Referenced by architecture docs (docs/architecture/)
```

---

## 📋 Current Phase

See [implementation-plan/CURRENT_PHASE.md](./implementation-plan/CURRENT_PHASE.md)

---

## 🎓 Learnings

See [retrospective/](./retrospective/) for what we've learned.

---

## 🗑️ Cleanup

After PoC completion or repo rename:
- Archive useful learnings to docs/
- Delete .meta/ or specific project workspace
- Keep .meta/ README.md for future projects
