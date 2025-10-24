# Task 008: Add Show Command to adr-cli

**Phase**: Phase 2 - CLI Tool
**Status**: pending
**Estimated Time**: 0.5 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 006: adr-cli crate exists

**Blocks**:
- None (parallel with other commands)

**Value Delivered**:
Users can view full ADR details by ID or number. Validates retrieval logic works correctly, including lookup by both UUID and sequential number.

---

## 📝 Description

Add `adr show` command that displays full ADR content including all fields: title, context, decision, consequences, status, timestamps.

Should accept either:
- Sequential number: `adr show 0001`
- UUID: `adr show <uuid>`

---

## ✅ Acceptance Criteria

- [ ] Command works: `adr show <id-or-number>`
- [ ] Displays all ADR fields in readable format
- [ ] Works with sequential number (e.g., `0001`, `1`)
- [ ] Works with UUID
- [ ] Shows "ADR not found" for invalid ID
- [ ] Help text: `adr show --help`
- [ ] Output is well-formatted and easy to read

---

## 🧪 Verification

```bash
# Show by number
cargo run -p adr-cli -- show 0001

# Show by UUID (if you know it)
cargo run -p adr-cli -- show <uuid>

# Test not found
cargo run -p adr-cli -- show 9999  # Should error gracefully
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
