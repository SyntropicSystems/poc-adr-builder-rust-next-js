# Task 022: Add Status Update Functionality to UI

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 014: gRPC UpdateADRStatus endpoint
- Task 020: Detail page (where status is updated)

**Blocks**:
- None

**Value Delivered**:
Complete frontend CRUD! Users can update ADR status from web UI. Full application flow works end-to-end: create, list, view, update. PoC frontend is DONE.

---

## 📝 Description

Add status update feature to ADR detail page:
- Dropdown or button group for status selection
- React Query mutation for UpdateADRStatus
- Optimistic update (instant UI feedback)
- Domain validation errors shown to user
- Auto-refresh detail page and list

---

## ✅ Acceptance Criteria

- [ ] Status selector on detail page
- [ ] All status values available: draft, proposed, accepted, rejected, deprecated, superseded
- [ ] Submit button or auto-submit on change
- [ ] Optimistic update (UI changes immediately)
- [ ] Domain validation errors displayed
- [ ] Success: UI shows new status
- [ ] React Query invalidates queries (list refreshes)

---

## 🧪 Verification

```bash
# Visit ADR detail page
# Change status to "accepted"
# Should update immediately
# Check list page - status updated there too
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
