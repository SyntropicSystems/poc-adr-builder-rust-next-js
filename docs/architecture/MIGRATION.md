# Migration to Monorepo

**ADR Editor PoC** - Monorepo Migration Strategy

---

## 🎯 Goal

Migrate this PoC into the production monorepo with **minimal refactoring** (< 4 Engineering Units).

**Key Principle**: The PoC structure mirrors the monorepo structure, so migration should be mostly copy-paste.

---

## 📋 Migration Checklist

### Pre-Migration Validation

- [ ] All PoC phases complete
- [ ] Architecture validated (hexagonal, gRPC, storage)
- [ ] Tests passing (`cargo test` + `pnpm test`)
- [ ] Documentation complete and current
- [ ] No known critical issues

### Migration Steps

**Time Estimate**: 3-4 EU total

#### Step 1: Copy Directories (0.5 EU)

```bash
# From PoC repository
cd /path/to/adr-editor-poc

# To monorepo
MONOREPO=/path/to/platform-monorepo

# Copy Rust crates
cp -r crates/* $MONOREPO/crates/

# Copy Next.js app
cp -r apps/adr-web $MONOREPO/apps/

# Copy protobuf schemas
cp -r proto/adr $MONOREPO/proto/

# Copy documentation
cp -r docs/* $MONOREPO/docs/
```

**What Gets Copied**:
- ✅ `crates/` → All Rust crates
- ✅ `apps/adr-web/` → Next.js application
- ✅ `proto/adr/` → Protobuf schemas
- ✅ `docs/` → Living documentation
- ✅ `scripts/` → Automation scripts (if monorepo needs them)

**What Stays in PoC**:
- ❌ `.meta/` - Ephemeral working documents
- ❌ Root config files (.nvmrc, package.json) - Monorepo has its own
- ❌ PoC-specific README
- ❌ WORKSPACE (Bazel) - Monorepo has its own

#### Step 2: Update Workspace Configuration (1 EU)

**Cargo.toml** (Monorepo Root):

```toml
# Before (PoC)
[workspace]
members = [
    "crates/adr-domain",
    "crates/adr-sdk",
    "crates/adr-adapters",
    "crates/adr-service",
    "crates/adr-cli",
]

# After (Monorepo - add our crates)
[workspace]
members = [
    # Existing crates...
    "crates/existing-service",
    
    # NEW: ADR Editor crates
    "crates/adr-domain",
    "crates/adr-sdk",
    "crates/adr-adapters",
    "crates/adr-service",
    "crates/adr-cli",
]
```

**package.json** (Monorepo Root):

```json
{
  "workspaces": [
    "apps/*",
    // Our app is now included automatically
  ]
}
```

**WORKSPACE** (Bazel - if using):

```python
# Just works - our BUILD files already compatible
```

#### Step 3: Verify Build (0.5 EU)

```bash
cd $MONOREPO

# Verify Rust builds
cargo build -p adr-domain
cargo build -p adr-sdk
cargo build -p adr-adapters
cargo build -p adr-service
cargo build -p adr-cli

# Verify tests pass
cargo test -p adr-domain
cargo test -p adr-sdk

# Verify frontend builds
cd apps/adr-web
pnpm install
pnpm build

# Verify Bazel (optional)
bazel build //crates/adr-domain
bazel build //apps/adr-web
```

**Expected Result**: Everything builds without changes.

#### Step 4: Update Import Paths (0.5 EU)

**Should Be Zero Changes** because:
- ✅ Crate names stay same (`adr_domain`, `adr_sdk`, etc.)
- ✅ File paths relative to crate root
- ✅ No absolute paths used

**If Monorepo Uses Different Conventions**:

```rust
// PoC might have
use adr_sdk::repository::ADRRepository;

// Monorepo might require
use platform_adr_sdk::repository::ADRRepository;

// Fix with find-replace (rare)
```

**Check These Files**:
- [ ] `crates/*/Cargo.toml` - Dependency paths
- [ ] `crates/*/src/*.rs` - Import statements
- [ ] `apps/adr-web/package.json` - Workspace dependencies

#### Step 5: Update Documentation Links (0.5 EU)

Update docs to reflect monorepo paths:

```markdown
<!-- Before (PoC) -->
See [Architecture](./docs/architecture/OVERVIEW.md)

<!-- After (Monorepo) -->
See [Architecture](../../docs/adr-editor/architecture/OVERVIEW.md)

<!-- Or monorepo-specific format -->
```

**Files to Update**:
- [ ] `docs/` - Update internal links
- [ ] `README.md` - Point to monorepo structure
- [ ] `llm.md` - Update context for monorepo

#### Step 6: Integration Testing (1 EU)

Test the complete system in monorepo:

```bash
# Test CLI
cargo run -p adr-cli -- --help
cargo run -p adr-cli create --title "Test in Monorepo"

# Test Service
cargo run -p adr-service &
# Verify service starts on expected port

# Test Frontend
cd apps/adr-web
pnpm dev
# Verify connects to service
```

**Integration Points to Verify**:
- [ ] CLI creates ADRs
- [ ] Service responds to gRPC requests
- [ ] Frontend connects to service
- [ ] Storage adapter works
- [ ] Protobuf types generated correctly

#### Step 7: CI/CD Integration (0.5 EU)

Add ADR Editor to monorepo CI:

```yaml
# .github/workflows/adr-editor.yml
name: ADR Editor

on:
  pull_request:
    paths:
      - 'crates/adr-*/**'
      - 'apps/adr-web/**'
      - 'proto/adr/**'

jobs:
  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rust-lang/setup-rust-toolchain@v1
      - run: cargo test -p adr-domain
      - run: cargo test -p adr-sdk
      - run: cargo test -p adr-adapters

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '24'
      - run: cd apps/adr-web && pnpm install
      - run: cd apps/adr-web && pnpm test
```

---

## 🗺️ Directory Mapping

### PoC → Monorepo

| PoC Location | Monorepo Location | Notes |
|--------------|-------------------|-------|
| `crates/adr-domain/` | `crates/adr-domain/` | ✅ Same |
| `crates/adr-sdk/` | `crates/adr-sdk/` | ✅ Same |
| `crates/adr-adapters/` | `crates/adr-adapters/` | ✅ Same |
| `crates/adr-service/` | `crates/adr-service/` | ✅ Same |
| `crates/adr-cli/` | `crates/adr-cli/` | ✅ Same |
| `apps/adr-web/` | `apps/adr-web/` | ✅ Same |
| `proto/adr/v1/` | `proto/adr/v1/` | ✅ Same |
| `docs/` | `docs/adr-editor/` | ⚠️ Organized by project |
| `.meta/` | N/A | ❌ Not migrated |

---

## 🔍 Import Path Verification

### Rust Crates

**Should Not Change**:

```rust
// In adr-sdk/src/lib.rs
use adr_domain::ADR;  // ✅ Works in PoC and monorepo

// In adr-service/src/main.rs
use adr_sdk::repository::ADRRepository;  // ✅ Works in both

// In adr-cli/src/main.rs
use adr_adapters::filesystem::FilesystemAdapter;  // ✅ Works in both
```

**Verify Command**:

```bash
# Check no absolute paths
grep -r "^use crate::" crates/
# Should be empty (all use relative or crate names)

# Check all imports resolve
cargo check
```

### TypeScript/Next.js

**Should Not Change**:

```typescript
// In apps/adr-web/lib/grpc/client.ts
import { ADRServiceClient } from './generated/adr_pb_service';  // ✅ Relative

// In apps/adr-web/components/ADRList.tsx
import { useADRStore } from '@/lib/state/adr-store';  // ✅ Uses @/ alias
```

**Verify Command**:

```bash
cd apps/adr-web
pnpm build
# Should build without errors
```

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Workspace Dependency Conflicts

**Problem**: Monorepo has different version of dependency

**Solution**:
```toml
# Monorepo Cargo.toml has
[workspace.dependencies]
tokio = "1.35"

# Our crates expect
tokio = "1.40"

# Fix: Accept monorepo version (usually backwards compatible)
# Or: Request monorepo upgrade if breaking changes needed
```

### Issue 2: Bazel Build Configurations

**Problem**: Our BUILD files don't match monorepo conventions

**Solution**:
```python
# Update BUILD.bazel files to match monorepo patterns
# Usually just different naming conventions
```

### Issue 3: Port Conflicts

**Problem**: Service port (50051) conflicts with existing service

**Solution**:
```rust
// Make port configurable
let port = env::var("ADR_SERVICE_PORT").unwrap_or("50051".to_string());
```

### Issue 4: Proto Path Issues

**Problem**: Protobuf import paths don't resolve

**Solution**:
```protobuf
// Use monorepo-relative imports
import "proto/common/types.proto";  // ✅ From monorepo root
```

---

## 🧪 Testing Migration

### Pre-Migration Tests (in PoC)

```bash
# Ensure everything works in PoC first
cargo test --workspace
cd apps/adr-web && pnpm test
python3 scripts/validate_docs.py
```

### Post-Migration Tests (in Monorepo)

```bash
# Same tests, different location
cd $MONOREPO
cargo test -p adr-domain -p adr-sdk -p adr-adapters
cd apps/adr-web && pnpm test
```

### Integration Tests

**Manual Testing**:
1. Create ADR via CLI
2. Start service
3. Open frontend
4. Verify ADR appears
5. Create ADR via UI
6. Verify CLI sees it

**Automated Testing** (add to monorepo):
```rust
#[tokio::test]
async fn end_to_end_test() {
    // 1. Start service
    // 2. Create ADR via gRPC
    // 3. Verify storage
    // 4. Query via gRPC
    // 5. Verify response
}
```

---

## 📊 Migration Risk Assessment

### Low Risk (High Confidence)

| Item | Risk | Mitigation |
|------|------|------------|
| **Rust crates** | Very Low | Same structure, tested in PoC |
| **Import paths** | Very Low | Relative paths, crate names same |
| **Protobuf** | Low | Schema is schema |
| **Frontend** | Low | Self-contained app |

### Medium Risk (Manageable)

| Item | Risk | Mitigation |
|------|------|------------|
| **Dependency versions** | Medium | Accept monorepo versions |
| **Bazel configs** | Medium | Update BUILD files as needed |
| **CI/CD** | Medium | Copy patterns from existing services |

### Watch For

- ⚠️ Port conflicts (make configurable)
- ⚠️ Path conventions (update if different)
- ⚠️ Monorepo-specific tooling (adapt as needed)

---

## 🎯 Success Criteria

Migration is successful when:

- ✅ All crates compile in monorepo
- ✅ All tests pass
- ✅ CLI runs and creates ADRs
- ✅ Service starts and responds to gRPC
- ✅ Frontend connects to service
- ✅ No import errors
- ✅ CI/CD includes ADR Editor
- ✅ Documentation updated for monorepo

**Time to Success**: < 4 EU (as designed)

---

## 🔄 Rollback Plan

If migration fails, rollback is easy:

1. **Remove copied directories**
   ```bash
   rm -rf $MONOREPO/crates/adr-*
   rm -rf $MONOREPO/apps/adr-web
   rm -rf $MONOREPO/proto/adr
   ```

2. **Revert workspace configs**
   ```bash
   git checkout Cargo.toml package.json WORKSPACE
   ```

3. **Continue development in PoC**
   ```bash
   cd /path/to/adr-editor-poc
   # Fix issues, try again later
   ```

**Cost**: < 1 EU to rollback

---

## 🔗 Related Documentation

- **Architecture**: [OVERVIEW.md](./OVERVIEW.md)
- **Technology Stack**: [TECHNOLOGY_STACK.md](./TECHNOLOGY_STACK.md)
- **Why This Structure**: [ADR 0003](../adr/0003-cargo-workspace-structure.md)

---

**Remember**: This migration should be boring. If it's exciting, we structured the PoC wrong!
