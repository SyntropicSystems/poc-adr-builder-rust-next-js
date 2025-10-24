# Task 018: Set up React Query for Server State Management

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 015: Next.js app exists
- Task 016: TypeScript gRPC client generated

**Blocks**:
- Task 019-022: Pages that fetch/mutate server data

**Value Delivered**:
Server state management with caching, invalidation, and optimistic updates. Makes frontend responsive and efficient. Handles all server communication patterns.

**Architectural Validation**:
✅ Validates modern React patterns (React Query + gRPC)

---

## 📝 Description

Configure React Query (TanStack Query):
- Install @tanstack/react-query
- Set up QueryClientProvider
- Configure default options (staleTime, cacheTime, etc.)
- Integrate with gRPC client
- Create example query hook (e.g., useADRs)

---

## ✅ Acceptance Criteria

- [ ] React Query installed and configured
- [ ] QueryClientProvider wraps app
- [ ] Dev tools enabled in development
- [ ] Default query options configured
- [ ] Example query hook works (can be minimal)
- [ ] Error and loading states handled
- [ ] Integrates with gRPC client from Task 016

---

## 🧪 Verification

```bash
pnpm dev
# Check React Query devtools appear
# Test query hook in a page
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
