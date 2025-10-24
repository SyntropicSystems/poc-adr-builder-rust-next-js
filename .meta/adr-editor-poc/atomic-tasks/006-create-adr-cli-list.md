# Task 006: Create adr-cli Crate with List Command

**Phase**: Phase 2 - CLI Tool
**Status**: pending
**Estimated Time**: 1 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001: Cargo workspace must exist
- Task 003: adr-domain crate (CLI uses domain types)
- Task 004: adr-sdk crate (CLI uses SDK for business logic)
- Task 005: adr-adapters crate (CLI needs storage implementation)

**Blocks**:
- Task 007: Add create command (builds on CLI infrastructure)
- Task 008: Add show command
- Task 009: Add update status command

**Value Delivered**:
First working interface to the system! This proves the hexagonal architecture works - the CLI uses the SDK directly, sharing the same business logic that the gRPC service will use later. User can actually list ADRs from command line.

**Architectural Validation**:
✅ Proves hexagonal architecture - CLI is a "driver" adapter using SDK ports

---

## 📝 Description

Create a CLI tool using the `clap` crate that can list ADRs. This is the first application layer that uses the SDK, validating that:
- The repository pattern works
- The SDK use cases are accessible
- The filesystem adapter functions correctly
- The layering is clean (CLI → SDK → Adapter → Storage)

The CLI should:
- Parse command-line arguments
- Initialize the filesystem adapter
- Call SDK's list use case
- Display results in a user-friendly format

---

## ✅ Acceptance Criteria

- [ ] `crates/adr-cli/` directory created
- [ ] CLI binary compiles successfully
- [ ] Command `adr list` displays all ADRs
- [ ] Output shows: number, title, status for each ADR
- [ ] Output is formatted in a readable table or list
- [ ] Returns appropriate exit codes (0 = success, 1 = error)
- [ ] Help text available via `adr --help` and `adr list --help`
- [ ] CLI initializes filesystem adapter correctly
- [ ] Can run: `cargo run -p adr-cli -- list`
- [ ] Works even when `.adr/` directory is empty (shows "No ADRs found")

---

## 🔧 Key Technical Decisions

- Use `clap` with derive macros for argument parsing
- Use filesystem adapter as default storage
- Output formatted with `prettytable-rs` or similar
- Support both `--` flags and subcommands
- SDK integration via Arc-wrapped repository

---

## 🧪 Verification

**How to verify this task is complete**:
```bash
# Build CLI
cargo build -p adr-cli

# Run list command
cargo run -p adr-cli -- list

# Test help
cargo run -p adr-cli -- --help
cargo run -p adr-cli -- list --help

# Test empty state
rm -rf .adr/
cargo run -p adr-cli -- list  # Should show "No ADRs found"
```

**Expected behavior**:
- Clean, readable output
- No panics or crashes
- Helpful error messages
- Works from any directory

---

## 📚 Resources

- [clap Documentation](https://docs.rs/clap/)
- ADR 0001: Hexagonal Architecture
- `docs/development/WORKFLOW.md`

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
