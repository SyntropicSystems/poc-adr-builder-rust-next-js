# Task 013: Implement gRPC GetADR Endpoint

**Phase**: Phase 3 - gRPC Service
**Status**: pending
**Estimated Time**: 0.5 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 010: gRPC server infrastructure

**Blocks**:
- Task 020: Next.js detail page

**Value Delivered**:
Can retrieve single ADR details over network. Frontend can show full ADR content.

---

## 📝 Description

Implement `GetADR` RPC that retrieves single ADR by ID or number.

---

## ✅ Acceptance Criteria

- [ ] `GetADR` RPC handler implemented
- [ ] Accepts ID (UUID or number string)
- [ ] Returns full ADR details
- [ ] Returns NOT_FOUND gRPC status for invalid ID
- [ ] Works with both UUID and number lookup

---

## 🧪 Verification

```bash
grpcurl -plaintext \
  -d '{"id": "0001"}' \
  localhost:50051 \
  adr.v1.ADRService/GetADR
```

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
