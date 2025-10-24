# Task 014: Implement gRPC UpdateADRStatus Endpoint

**Phase**: Phase 3 - gRPC Service
**Status**: pending
**Estimated Time**: 0.5 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 010: gRPC server infrastructure

**Blocks**:
- Task 022: Next.js status update UI

**Value Delivered**:
Full CRUD over gRPC complete! Can update ADR status remotely. Service fully functional.

---

## 📝 Description

Implement `UpdateADRStatus` RPC that changes ADR status with domain validation.

---

## ✅ Acceptance Criteria

- [ ] `UpdateADRStatus` RPC handler implemented
- [ ] Accepts ID and new status
- [ ] Domain validation enforced
- [ ] Returns updated ADR
- [ ] Invalid transitions return appropriate gRPC errors

---

## 🧪 Verification

```bash
grpcurl -plaintext \
  -d '{"id": "0001", "status": "ACCEPTED"}' \
  localhost:50051 \
  adr.v1.ADRService/UpdateADRStatus
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
