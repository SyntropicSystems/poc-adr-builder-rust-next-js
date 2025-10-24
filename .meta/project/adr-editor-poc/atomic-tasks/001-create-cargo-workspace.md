# Task 001: Create Cargo Workspace Root Configuration

**Phase**: Phase 1 - Foundation
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- None (starting task)

**Blocks**:
- Task 003: Create adr-domain crate
- Task 004: Create adr-sdk crate
- Task 005: Create adr-adapters crate
- Task 006: Create adr-cli crate
- Task 010: Create adr-service crate

**Value Delivered**:
Establishes Rust workspace structure that allows multiple crates to share dependencies and build together. This is the foundation of the hexagonal architecture where crates represent different layers.

---

## 📝 Description

Create the root `Cargo.toml` workspace file that will coordinate all Rust crates in the project. This workspace will contain 5 crates organized by hexagonal architecture layers:
- Domain layer (adr-domain)
- Port/use case layer (adr-sdk)
- Adapter layer (adr-adapters)
- Application layers (adr-cli, adr-service)

The workspace configuration should:
- Define member crates in `crates/` directory
- Set up shared dependencies (workspace dependencies feature)
- Configure workspace-level settings (edition, version, authors)
- Set up common dev dependencies (testing, etc.)

---

## ✅ Acceptance Criteria

- [ ] Root `Cargo.toml` file created with `[workspace]` section
- [ ] Workspace members list includes: `crates/adr-domain`, `crates/adr-sdk`, `crates/adr-adapters`, `crates/adr-cli`, `crates/adr-service`
- [ ] Workspace dependencies defined for common crates (tokio, serde, etc.)
- [ ] Rust edition set to 2021
- [ ] `crates/` directory created
- [ ] `cargo build` runs successfully (even with empty crates initially)
- [ ] `.gitignore` includes `target/`, `Cargo.lock` for library crates

---

## 🔧 Implementation Notes

**Workspace Structure**:
```toml
[workspace]
members = [
    "crates/adr-domain",
    "crates/adr-sdk",
    "crates/adr-adapters",
    "crates/adr-cli",
    "crates/adr-service",
]
resolver = "2"

[workspace.package]
version = "0.1.0"
edition = "2021"
authors = ["Your Team"]
license = "MIT"

[workspace.dependencies]
# Async runtime
tokio = { version = "1.35", features = ["full"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Date/time
chrono = { version = "0.4", features = ["serde"] }

# Error handling
anyhow = "1.0"
thiserror = "1.0"

# Testing
mockall = "0.12"
```

**Key Decisions**:
- Use workspace dependencies to centralize version management
- Resolver "2" for better dependency resolution
- Edition 2021 for latest Rust features

---

## 🧪 Verification

**How to test**:
```bash
# 1. Verify workspace structure
cargo metadata --format-version 1 | jq '.workspace_members'

# 2. Try to build (should succeed even with no crates yet)
cargo build --workspace

# 3. Check workspace is recognized
cargo tree
```

**Expected outcome**:
- `cargo build` completes without errors (may warn about no crates)
- Workspace shows 5 members when queried
- Directory structure is clean and organized

---

## 📚 Resources

- [Cargo Workspaces](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html)
- [Workspace Dependencies](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- ADR 0003: Cargo Workspace Structure (`docs/adr/0003-cargo-workspace-structure.md`)

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
