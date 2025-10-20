# API Documentation

**ADR Editor PoC** - API Reference

---

## 📡 API Protocol

This system uses **gRPC** with **Protocol Buffers** for the API.

**Key Documents**:
- [gRPC Details](./GRPC.md) - Generated API reference
- [ADR 0002](../adr/0002-use-grpc-for-api.md) - Why gRPC

---

## 🎯 Quick Reference

### Endpoints

| RPC | Purpose | Request | Response |
|-----|---------|---------|----------|
| `CreateADR` | Create new ADR | `CreateADRRequest` | `ADR` |
| `GetADR` | Get ADR by ID | `GetADRRequest` | `ADR` |
| `ListADRs` | List all ADRs | `ListADRsRequest` | `ListADRsResponse` |
| `UpdateADR` | Update existing ADR | `UpdateADRRequest` | `ADR` |
| `DeleteADR` | Delete ADR | `DeleteADRRequest` | `Empty` |

---

## 🔧 Testing the API

### Using grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# List ADRs
grpcurl -plaintext localhost:50051 adr.v1.ADRService/ListADRs

# Create ADR
grpcurl -plaintext -d '{"title":"Test ADR","description":"Testing"}' \
  localhost:50051 adr.v1.ADRService/CreateADR
```

### Using TypeScript Client

```typescript
import { ADRServiceClient } from './generated/adr_pb_service';

const client = new ADRServiceClient('http://localhost:50051');

// Create ADR
const response = await client.createADR({
  title: 'My ADR',
  description: 'Description here'
});
```

---

## 📝 Schema

**Source of Truth**: `proto/adr/v1/adr.proto`

This is the single source of truth. All types are generated from this schema.

---

## 🔄 Generating Documentation

API documentation is generated from `.proto` files:

```bash
# Generate docs
pnpm docs:generate

# This creates:
# - docs/api/GRPC.md (human-readable reference)
# - Rust types (via tonic-build)
# - TypeScript types (via protoc-gen-ts)
```

---

## 🔗 Related

- **Technology Stack**: [../architecture/TECHNOLOGY_STACK.md](../architecture/TECHNOLOGY_STACK.md)
- **Why gRPC**: [../adr/0002-use-grpc-for-api.md](../adr/0002-use-grpc-for-api.md)
