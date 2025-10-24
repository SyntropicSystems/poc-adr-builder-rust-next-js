# Task 007: Add Create Command to adr-cli

**Phase**: Phase 2 - CLI Tool
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 006: adr-cli crate with list command (CLI infrastructure exists)

**Blocks**:
- Task 023: CLI integration tests (needs create command)

**Value Delivered**:
Users can now CREATE ADRs via CLI! This completes the write-path validation - we can create new records, assign sequential numbers, and persist to storage. Combined with list command, this proves the full CRUD foundation works.

---

## 📝 Description

Add `adr create` command that:
- Accepts title, context, decision, consequences as arguments or prompts
- Calls SDK's `create_adr` use case
- Assigns next sequential number
- Persists to filesystem
- Returns success message with ADR number

Validates:
- Domain validation works (title length, etc.)
- Sequential numbering works correctly
- Repository save operation works
- User feedback is clear and helpful

---

## ✅ Acceptance Criteria

- [ ] Command `adr create` works with flags: `--title`, `--context`, `--decision`, `--consequences`
- [ ] Creates ADR with auto-assigned sequential number (0001, 0002, etc.)
- [ ] Success message shows: "Created ADR 0001: [title]"
- [ ] File saved to `.adr/adrs/NNNN-slug.json`
- [ ] Validation errors show helpful messages (e.g., title too long)
- [ ] Help text available: `adr create --help`
- [ ] Works with multiline input (for context, decision, consequences)
- [ ] Created ADR appears in `adr list` output

---

## 🧪 Verification

**How to verify**:
```bash
# Create ADR with all fields
cargo run -p adr-cli -- create \
  --title "Use Hexagonal Architecture" \
  --context "Need clean separation" \
  --decision "Use ports and adapters" \
  --consequences "Better testability"

# Verify it was created
cargo run -p adr-cli -- list

# Check file exists
ls .adr/adrs/0001-*.json

# Test validation
cargo run -p adr-cli -- create --title ""  # Should fail with error
```

**Expected outcome**:
- ADR created successfully
- File exists with correct format
- Appears in list output
- Validation prevents invalid data

---

## 📚 Resources

- ADR 0001: Hexagonal Architecture
- `docs/development/WORKFLOW.md`

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
