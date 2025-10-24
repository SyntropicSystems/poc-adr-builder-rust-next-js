# Task 010: Create adr-service Crate with gRPC Server Setup

**Phase**: Phase 3 - gRPC Service
**Status**: pending
**Estimated Time**: 2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001: Cargo workspace
- Task 002: Protobuf schema (generates Rust gRPC code)
- Task 003-005: Domain, SDK, Adapters (service uses SDK)

**Blocks**:
- Task 011-014: gRPC endpoints (need server infrastructure)
- Task 016: TypeScript client (needs running server)

**Value Delivered**:
Network-accessible API! This is the CRITICAL validation point - the service uses the SAME SDK as the CLI, proving hexagonal architecture works. Same business logic, different interface.

**Architectural Validation**:
✅ Proves hexagonal architecture - Service is another "driver" adapter using SDK
✅ Validates gRPC integration works with Rust

---

## 📝 Description

Create gRPC service crate using `tonic` that:
- Generates Rust code from `proto/adr/v1/adr.proto`
- Sets up gRPC server infrastructure
- Uses filesystem adapter for storage (same as CLI)
- Implements basic health check endpoint
- Runs on localhost:50051

This proves the SDK can be consumed by multiple applications (CLI and Service share code).

---

## ✅ Acceptance Criteria

- [ ] `crates/adr-service/` directory created
- [ ] Protobuf code generation configured in build.rs
- [ ] Rust gRPC stubs generated from proto files
- [ ] gRPC server starts successfully on port 50051
- [ ] Basic health check or ping endpoint works
- [ ] Server uses SDK with filesystem adapter
- [ ] Can run: `cargo run -p adr-service`
- [ ] Server logs startup message
- [ ] Graceful shutdown on Ctrl+C

---

## 🧪 Verification

```bash
# Start server
cargo run -p adr-service

# In another terminal, test connection (using grpcurl or similar)
grpcurl -plaintext localhost:50051 list

# Check it's running
ps aux | grep adr-service
```

**Expected**:
- Server starts without errors
- Listens on port 50051
- Can list available services

---

## 📚 Resources

- [Tonic gRPC](https://github.com/hyperium/tonic)
- ADR 0002: Use gRPC for API
- `docs/api/GRPC.md`

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
