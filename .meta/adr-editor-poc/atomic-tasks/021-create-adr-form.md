# Task 021: Create ADR Creation Form with Validation

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 012: gRPC CreateADR endpoint
- Task 016: TypeScript client
- Task 018: React Query (for mutations)

**Blocks**:
- None

**Value Delivered**:
Users can create ADRs from web UI! Form validation matches domain rules. Optimistic updates for responsive UX. Full CRUD from frontend.

---

## 📝 Description

Create `/adrs/new` route with form for creating ADRs:
- Fields: title, context, decision, consequences
- Client-side validation (matches domain rules)
- React Query mutation for CreateADR
- Optimistic update (instant feedback)
- Redirect to new ADR detail page on success
- Error handling

---

## ✅ Acceptance Criteria

- [ ] Route `/adrs/new` works
- [ ] Form with all required fields
- [ ] Client-side validation
- [ ] Submit button disabled during submission
- [ ] Success: redirect to new ADR detail page
- [ ] Error: show error message, keep form data
- [ ] ADR list auto-refreshes (React Query invalidation)
- [ ] Validation errors match backend (title length, etc.)

---

## 🧪 Verification

```bash
# Visit http://localhost:3000/adrs/new
# Fill form and submit
# Should redirect to /adrs/0001 (or next number)
# New ADR should appear in list
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
