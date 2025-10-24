# Task 020: Create ADR Detail Page

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 013: gRPC GetADR endpoint
- Task 016: TypeScript client
- Task 018: React Query
- Task 019: List page (for navigation)

**Blocks**:
- None

**Value Delivered**:
Users can view full ADR details in browser. Navigation works (list → detail). Shows all ADR fields in readable format.

---

## 📝 Description

Create `/adrs/[id]` dynamic route that:
- Accepts ADR number or UUID in URL
- Fetches single ADR via GetADR gRPC call
- Displays all fields: title, context, decision, consequences, status, timestamps
- Link back to list
- Edit/update status button (for Task 022)

---

## ✅ Acceptance Criteria

- [ ] Route `/adrs/[id]` works
- [ ] Fetches ADR by ID/number
- [ ] Displays all ADR fields
- [ ] Loading state
- [ ] 404 page for invalid ID
- [ ] Back to list navigation
- [ ] Responsive layout
- [ ] Timestamps formatted nicely

---

## 🧪 Verification

```bash
# Visit http://localhost:3000/adrs/0001
# Should show full ADR details
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
