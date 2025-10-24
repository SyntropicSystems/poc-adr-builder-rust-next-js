# Task 026: Set up Minimal Bazel BUILD Files for Rust Crates

**Phase**: Phase 6 - Build System Validation
**Status**: pending
**Estimated Time**: 2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001-014: All Rust crates exist
- WORKSPACE file already configured

**Blocks**:
- None

**Value Delivered**:
Bazel build working for Rust! Validates project structure works with Bazel. De-risks monorepo migration. Proves we can build with both Cargo AND Bazel.

**Architectural Validation**:
✅ Validates structure works for monorepo build system

---

## 📝 Description

Add minimal BUILD.bazel files for each Rust crate:
- crates/adr-domain/BUILD.bazel
- crates/adr-sdk/BUILD.bazel
- crates/adr-adapters/BUILD.bazel
- crates/adr-cli/BUILD.bazel
- crates/adr-service/BUILD.bazel

Goal: Learn Bazel patterns, prove structure works. Not for production use (Cargo remains primary).

---

## ✅ Acceptance Criteria

- [ ] BUILD.bazel file in each crate directory
- [ ] `bazel build //crates/adr-domain:adr-domain` works
- [ ] `bazel build //crates/...` builds all crates
- [ ] `bazel test //crates/...` runs tests
- [ ] Dependencies between crates configured
- [ ] No Cargo.toml changes needed (both systems coexist)
- [ ] Documentation: how to use Bazel builds

---

## 🧪 Verification

```bash
# Build all Rust crates with Bazel
bazel build //crates/...

# Run tests
bazel test //crates/...

# Verify Cargo still works
cargo build
cargo test
```

---

## 📚 Resources

- [rules_rust](https://github.com/bazelbuild/rules_rust)
- `WORKSPACE` file

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:

**Deviations**:
