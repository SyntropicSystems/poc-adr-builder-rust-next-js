#!/usr/bin/env python3
"""
Generate API documentation from protobuf files.

This script:
1. Reads .proto files
2. Generates markdown documentation
3. Updates docs/api/GRPC.md with generated content
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Main generation function."""
    print("📝 Generating API documentation...")
    
    # Check if proto files exist
    proto_dir = Path("proto/adr/v1")
    if not proto_dir.exists():
        print("⚠️  Proto directory doesn't exist yet (Phase 1 pending)")
        print("   Create proto/adr/v1/adr.proto first")
        return 1
    
    proto_files = list(proto_dir.glob("*.proto"))
    if not proto_files:
        print("⚠️  No .proto files found")
        return 1
    
    # Generate documentation
    docs = generate_docs(proto_files)
    
    # Write to docs/api/GRPC.md
    output_file = Path("docs/api/GRPC.md")
    output_file.write_text(docs)
    
    print(f"✅ Generated {output_file}")
    print("   Remember to also generate Rust and TypeScript types:")
    print("   - Rust: cargo build (build.rs handles it)")
    print("   - TypeScript: cd apps/adr-web && pnpm proto:generate")
    
    return 0


def generate_docs(proto_files):
    """Generate markdown documentation from proto files."""
    proto_hash = calculate_file_hash(proto_files)
    timestamp = datetime.now().isoformat()
    
    # Read proto content
    content = []
    for proto_file in proto_files:
        content.append(proto_file.read_text())
    
    proto_content = "\n\n".join(content)
    
    # Generate markdown
    docs = f"""# gRPC API Reference

**Status**: ✅ Generated from `.proto` files

**Last Generated**: {timestamp}  
**Proto Hash**: `{proto_hash[:16]}...`

---

## 📝 Source

Generated from: `{', '.join(str(f) for f in proto_files)}`

---

## 🎯 Protocol Buffer Schema

```protobuf
{proto_content}
```

---

## 🔧 Usage Examples

### Rust (tonic)

```rust
use adr_service::{{
    adr_service_server::{{AdrService, AdrServiceServer}},
    CreateAdrRequest, Adr,
}};

#[tonic::async_trait]
impl AdrService for ADRServiceImpl {{
    async fn create_adr(
        &self,
        request: Request<CreateAdrRequest>,
    ) -> Result<Response<Adr>, Status> {{
        // Implementation
    }}
}}
```

### TypeScript (grpc-web)

```typescript
import {{ ADRServiceClient }} from './generated/adr_pb_service';

const client = new ADRServiceClient('http://localhost:50051');

const response = await client.createADR({{
  title: 'My ADR',
  description: 'Description here'
}});
```

### grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Call method
grpcurl -plaintext -d '{{"title":"Test"}}' \\
  localhost:50051 adr.v1.ADRService/CreateADR
```

---

## 🔄 Regeneration

To regenerate this file:

```bash
pnpm docs:generate
```

**Remember**: This is a generated file. Don't edit manually!

---

**Metadata**:
- Generated: {timestamp}
- Proto Hash: {proto_hash}
"""
    
    return docs


def calculate_file_hash(files):
    """Calculate combined hash of multiple files."""
    hasher = hashlib.sha256()
    for file_path in sorted(files):
        content = Path(file_path).read_bytes()
        hasher.update(content)
    return hasher.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
