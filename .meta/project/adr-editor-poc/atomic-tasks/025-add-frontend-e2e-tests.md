# Task 025: Add E2E Tests for Next.js Frontend

**Phase**: Phase 5 - Testing & Validation
**Status**: pending
**Estimated Time**: 2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 015-022: All frontend features implemented

**Blocks**:
- None

**Value Delivered**:
User journey validation! E2E tests verify complete workflows work from user perspective. Tests real browser interactions. Protects against UI regressions.

---

## 📝 Description

Add E2E tests using Playwright or Cypress:
- Test user workflows: create ADR, view list, view details, update status
- Test against running backend
- Verify UI interactions work
- Test error states

---

## ✅ Acceptance Criteria

- [ ] E2E test framework configured (Playwright or Cypress)
- [ ] Tests cover: list page, detail page, create form, status update
- [ ] Tests start backend service automatically
- [ ] Success paths tested
- [ ] Error states tested (network errors, validation)
- [ ] Tests run with: `pnpm test:e2e`
- [ ] All tests pass
- [ ] Tests run in CI-friendly headless mode

---

## 🧪 Verification

```bash
cd apps/adr-web
pnpm test:e2e
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
