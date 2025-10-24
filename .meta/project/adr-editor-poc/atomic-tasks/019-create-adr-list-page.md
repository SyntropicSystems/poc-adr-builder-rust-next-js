# Task 019: Create ADR List Page with React Query Integration

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 011: gRPC ListADRs endpoint (backend must work)
- Task 016: TypeScript gRPC client
- Task 018: React Query configured

**Blocks**:
- Task 025: E2E tests (needs working pages)

**Value Delivered**:
FIRST WORKING WEB PAGE! Users can see ADRs in browser. Full-stack working: Rust gRPC service → TypeScript client → React Query → Next.js page. This is a major milestone!

**Architectural Validation**:
✅ Full-stack integration works (Rust ↔ TypeScript)
✅ gRPC over network validated
✅ React Query + gRPC pattern proven

---

## 📝 Description

Create `/adrs` route that:
- Fetches ADRs using React Query + gRPC client
- Displays list with number, title, status
- Shows loading state
- Shows error state
- Links to detail pages
- Responsive design

---

## ✅ Acceptance Criteria

- [ ] Route `/adrs` works
- [ ] Displays all ADRs from gRPC service
- [ ] Shows: number, title, status for each ADR
- [ ] Loading spinner while fetching
- [ ] Error message if fetch fails
- [ ] Empty state ("No ADRs yet")
- [ ] Click ADR → navigate to detail page
- [ ] Data automatically refetches on focus/reconnect
- [ ] Styled with Tailwind CSS

---

## 🧪 Verification

```bash
# Start backend
cargo run -p adr-service &

# Start frontend
cd apps/adr-web && pnpm dev

# Visit http://localhost:3000/adrs
# Should show ADR list
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
