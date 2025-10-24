# Task 027: Set up Bazel BUILD File for Next.js App

**Phase**: Phase 6 - Build System Validation
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 015-022: Next.js app complete
- WORKSPACE file configured

**Blocks**:
- None

**Value Delivered**:
Complete Bazel validation! Both Rust and Next.js build with Bazel. Fully validates monorepo-ready structure. PoC proves architecture works with target build system.

**Architectural Validation**:
✅ Validates entire project structure for monorepo migration

---

## 📝 Description

Add BUILD.bazel for Next.js app:
- apps/adr-web/BUILD.bazel
- Configure Node.js rules
- Build Next.js app with Bazel
- Keep pnpm as primary (Bazel for validation only)

---

## ✅ Acceptance Criteria

- [ ] BUILD.bazel in apps/adr-web/
- [ ] `bazel build //apps/adr-web:adr-web` works
- [ ] Output is functional Next.js build
- [ ] pnpm commands still work (coexistence)
- [ ] Documentation on Bazel build for frontend

---

## 🧪 Verification

```bash
# Build with Bazel
bazel build //apps/adr-web:adr-web

# Verify pnpm still works
cd apps/adr-web
pnpm build
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
