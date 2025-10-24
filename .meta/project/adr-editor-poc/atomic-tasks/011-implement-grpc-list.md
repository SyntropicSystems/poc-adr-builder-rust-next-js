# Task 011: Implement gRPC ListADRs Endpoint

**Phase**: Phase 3 - gRPC Service
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 010: gRPC server infrastructure exists

**Blocks**:
- Task 019: Next.js list page (frontend needs this endpoint)

**Value Delivered**:
First network-accessible ADR operation! Can retrieve ADR list over gRPC. Service uses SDK's list use case - proving code reuse works.

---

## 📝 Description

Implement the `ListADRs` RPC method defined in protobuf. Should:
- Accept `ListADRsRequest` (empty for now)
- Call SDK's `list_adrs()` use case
- Convert domain ADRs to protobuf ADR messages
- Return `ListADRsResponse` with ADR array

---

## ✅ Acceptance Criteria

- [ ] `ListADRs` RPC handler implemented
- [ ] Uses SDK service to fetch ADRs
- [ ] Converts domain types to protobuf messages
- [ ] Returns all ADRs in response
- [ ] Works with empty list (no ADRs)
- [ ] Can test with grpcurl or Postman
- [ ] Proper error handling (returns gRPC status codes)

---

## 🧪 Verification

```bash
# Start service
cargo run -p adr-service &

# Test with grpcurl
grpcurl -plaintext \
  -d '{}' \
  localhost:50051 \
  adr.v1.ADRService/ListADRs
```

**Expected**: Returns JSON list of ADRs

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
