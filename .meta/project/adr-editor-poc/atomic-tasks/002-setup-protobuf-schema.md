# Task 002: Set up proto/ Directory with adr.proto Schema

**Phase**: Phase 1 - Foundation
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- None (can run in parallel with Task 001)

**Blocks**:
- Task 010: Create adr-service crate (needs proto definitions)
- Task 011-014: Implement gRPC endpoints (need service definitions)
- Task 016: Generate TypeScript gRPC client (needs proto files)

**Value Delivered**:
Establishes the API contract as the source of truth. Protobuf definitions will generate both Rust and TypeScript types, ensuring type safety across frontend and backend.

---

## 📝 Description

Create the protobuf schema that defines:
1. **ADR message types** - The core data structure
2. **ADRService gRPC interface** - Service methods (CRUD operations)
3. **Request/Response messages** - For each RPC method

This becomes the **source of truth** for the API. Both Rust backend and TypeScript frontend will generate code from these definitions.

Directory structure:
```
proto/
└── adr/
    └── v1/
        └── adr.proto
```

---

## ✅ Acceptance Criteria

- [ ] `proto/adr/v1/adr.proto` file created
- [ ] ADR message defined with fields: id, number, title, context, decision, status, consequences, created_at, updated_at
- [ ] Status enum defined: DRAFT, PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED
- [ ] ADRService service defined with RPCs: CreateADR, GetADR, ListADRs, UpdateADRStatus
- [ ] Request/Response messages defined for each RPC
- [ ] Proper protobuf syntax (proto3)
- [ ] Package name: `adr.v1`
- [ ] File compiles with protoc

---

## 🔧 Implementation Notes

**Protobuf Schema Example**:
```protobuf
syntax = "proto3";

package adr.v1;

// ADR Status
enum ADRStatus {
  DRAFT = 0;
  PROPOSED = 1;
  ACCEPTED = 2;
  REJECTED = 3;
  DEPRECATED = 4;
  SUPERSEDED = 5;
}

// Core ADR entity
message ADR {
  string id = 1;              // UUID
  int32 number = 2;           // Sequential number (0001, 0002, etc.)
  string title = 3;
  string context = 4;
  string decision = 5;
  ADRStatus status = 6;
  string consequences = 7;
  string created_at = 8;      // ISO8601 timestamp
  string updated_at = 9;      // ISO8601 timestamp
}

// Request/Response messages
message CreateADRRequest {
  string title = 1;
  string context = 2;
  string decision = 3;
  string consequences = 4;
}

message CreateADRResponse {
  ADR adr = 1;
}

message GetADRRequest {
  string id = 1;  // Can be UUID or number (e.g., "0001")
}

message GetADRResponse {
  ADR adr = 1;
}

message ListADRsRequest {
  // Future: add pagination, filters
}

message ListADRsResponse {
  repeated ADR adrs = 1;
}

message UpdateADRStatusRequest {
  string id = 1;
  ADRStatus status = 2;
}

message UpdateADRStatusResponse {
  ADR adr = 1;
}

// gRPC Service
service ADRService {
  rpc CreateADR(CreateADRRequest) returns (CreateADRResponse);
  rpc GetADR(GetADRRequest) returns (GetADRResponse);
  rpc ListADRs(ListADRsRequest) returns (ListADRsResponse);
  rpc UpdateADRStatus(UpdateADRStatusRequest) returns (UpdateADRStatusResponse);
}
```

**Key Decisions**:
- Use `proto3` syntax (latest, simpler)
- Package version `v1` for future evolution
- String timestamps (ISO8601) for simplicity in PoC
- Sequential numbers start at 1 (like real ADRs)

---

## 🧪 Verification

**How to test**:
```bash
# 1. Validate protobuf syntax (requires protoc installed)
protoc --proto_path=proto --descriptor_set_out=/dev/null proto/adr/v1/adr.proto

# 2. Check file structure
ls -la proto/adr/v1/adr.proto

# 3. View the schema
cat proto/adr/v1/adr.proto
```

**Expected outcome**:
- `protoc` compiles without errors
- File is readable and well-structured
- Schema matches acceptance criteria

---

## 📚 Resources

- [Protocol Buffers v3 Guide](https://protobuf.dev/programming-guides/proto3/)
- [gRPC Basics](https://grpc.io/docs/what-is-grpc/core-concepts/)
- ADR 0002: Use gRPC for API (`docs/adr/0002-use-grpc-for-api.md`)
- API Docs: `docs/api/GRPC.md`

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
