# Task 012: Implement gRPC CreateADR Endpoint

**Phase**: Phase 3 - gRPC Service
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 010: gRPC server infrastructure

**Blocks**:
- Task 021: Next.js creation form

**Value Delivered**:
Can create ADRs via network API. Write operations work over gRPC. Frontend can now create ADRs remotely.

---

## 📝 Description

Implement `CreateADR` RPC that accepts title, context, decision, consequences and creates new ADR using SDK.

---

## ✅ Acceptance Criteria

- [ ] `CreateADR` RPC handler implemented
- [ ] Accepts `CreateADRRequest` with all fields
- [ ] Calls SDK's `create_adr()` use case
- [ ] Returns created ADR with assigned number
- [ ] Domain validation errors map to gRPC errors
- [ ] Created ADR appears in ListADRs

---

## 🧪 Verification

```bash
grpcurl -plaintext \
  -d '{"title": "Test", "context": "...", "decision": "...", "consequences": "..."}' \
  localhost:50051 \
  adr.v1.ADRService/CreateADR
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
