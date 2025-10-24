# Task 009: Add Update Status Command to adr-cli

**Phase**: Phase 2 - CLI Tool
**Status**: pending
**Estimated Time**: 0.5 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 006: adr-cli crate exists

**Blocks**:
- None

**Value Delivered**:
Completes CLI CRUD operations. Users can now change ADR status (draft → proposed → accepted, etc.). Validates status transition rules in domain layer work correctly.

---

## 📝 Description

Add `adr update-status` command that changes ADR status. Should enforce domain validation rules (e.g., can't go from accepted back to draft).

---

## ✅ Acceptance Criteria

- [ ] Command works: `adr update-status <id> <new-status>`
- [ ] Accepts status values: draft, proposed, accepted, rejected, deprecated, superseded
- [ ] Domain validation enforced (invalid transitions rejected)
- [ ] Success message confirms change
- [ ] Updated status visible in `adr list` and `adr show`
- [ ] Help text available

---

## 🧪 Verification

```bash
# Update status
cargo run -p adr-cli -- update-status 0001 accepted

# Verify in list
cargo run -p adr-cli -- list  # Should show "accepted"

# Test invalid transition (if domain rules prevent it)
cargo run -p adr-cli -- update-status 0001 draft  # May error
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
