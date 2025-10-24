# Task 015: Create Next.js App with App Router Setup

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Package.json already configured (from docs phase)
- Node v24 via .nvmrc

**Blocks**:
- All subsequent frontend tasks (016-022)

**Value Delivered**:
Frontend foundation established. Next.js app configured with App Router, TypeScript, and basic project structure. Ready for feature implementation.

---

## 📝 Description

Create Next.js application in `apps/adr-web/` using:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS for styling
- pnpm as package manager
- Basic routing structure

Directory: `apps/adr-web/`

---

## ✅ Acceptance Criteria

- [ ] `apps/adr-web/` directory created
- [ ] Next.js 14+ installed with App Router
- [ ] TypeScript configured
- [ ] Tailwind CSS set up
- [ ] Basic layout component
- [ ] Home page (root route) works
- [ ] `pnpm dev` starts dev server on localhost:3000
- [ ] No console errors on page load
- [ ] Hot reload works

---

## 🧪 Verification

```bash
cd apps/adr-web
pnpm install
pnpm dev

# Visit http://localhost:3000
# Should show homepage
```

---

## 📚 Resources

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- `docs/architecture/TECHNOLOGY_STACK.md`

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
