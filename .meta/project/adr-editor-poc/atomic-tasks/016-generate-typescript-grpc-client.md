# Task 016: Generate TypeScript gRPC Client from Protobuf

**Phase**: Phase 4 - Next.js Frontend
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 002: Protobuf schema exists
- Task 015: Next.js app exists

**Blocks**:
- Task 019: List page (needs client to fetch data)
- Task 020-022: Other frontend features

**Value Delivered**:
Type-safe TypeScript client for gRPC API! Frontend can now communicate with backend with full type safety. Proves protobuf-first API design works across languages.

**Architectural Validation**:
✅ Validates protobuf generates types for multiple languages
✅ Type safety across frontend/backend boundary

---

## 📝 Description

Generate TypeScript types and gRPC client from `proto/adr/v1/adr.proto`:
- Use grpc-web or Connect-Web for browser compatibility
- Generate TypeScript interfaces for messages
- Generate client stubs for RPCs
- Configure code generation as npm script

---

## ✅ Acceptance Criteria

- [ ] Code generation tooling configured
- [ ] TypeScript types generated from protobuf
- [ ] gRPC client stubs generated
- [ ] Types available in `apps/adr-web/src/generated/` or similar
- [ ] Can import and use types in TypeScript code
- [ ] npm script for regeneration: `pnpm gen:proto`
- [ ] Client can connect to gRPC service at localhost:50051
- [ ] Types match Rust backend (verified manually)

---

## 🧪 Verification

```bash
cd apps/adr-web
pnpm gen:proto

# Check generated files exist
ls src/generated/

# Try importing in a test file
# import { ADR, ADRStatus } from '@/generated/adr/v1/adr'
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
