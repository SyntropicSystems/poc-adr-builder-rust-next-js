# Task Index - ADR Editor PoC

**Last Updated**: 2025-10-24
**Total Tasks**: 30
**Completed**: 0
**In Progress**: 0
**Pending**: 30
**Blocked**: 0

**Current Phase**: Phase 1 - Foundation
**Next Task**: [001-create-cargo-workspace.md](./001-create-cargo-workspace.md)

---

## 📊 Progress Dashboard

```
Phase 1: Foundation        [░░░░░] 0/5   (0%)
Phase 2: CLI Tool          [░░░░]  0/4   (0%)
Phase 3: gRPC Service      [░░░░░] 0/5   (0%)
Phase 4: Next.js Frontend  [░░░░░░░░] 0/8 (0%)
Phase 5: Testing           [░░░]   0/3   (0%)
Phase 6: Build System      [░░]    0/2   (0%)
Phase 7: Documentation     [░░░]   0/3   (0%)
─────────────────────────────────────────
Overall Progress           [░░░░░░░░░░] 0/30 (0%)
```

---

## 🎯 Quick Navigation

### By Status
- **Next to work on**: [001-create-cargo-workspace.md](./001-create-cargo-workspace.md)
- **In progress**: None
- **Blocked**: None
- **Recently completed**: None

### By Phase
- [Phase 1: Foundation](#phase-1-foundation-tasks-001-005) (0/5)
- [Phase 2: CLI Tool](#phase-2-cli-tool-tasks-006-009) (0/4)
- [Phase 3: gRPC Service](#phase-3-grpc-service-tasks-010-014) (0/5)
- [Phase 4: Next.js Frontend](#phase-4-nextjs-frontend-tasks-015-022) (0/8)
- [Phase 5: Testing & Validation](#phase-5-testing--validation-tasks-023-025) (0/3)
- [Phase 6: Build System Validation](#phase-6-build-system-validation-tasks-026-027) (0/2)
- [Phase 7: Documentation & Finalization](#phase-7-documentation--finalization-tasks-028-030) (0/3)

---

## Phase 1: Foundation (Tasks 001-005)

**Goal**: Establish build infrastructure and core domain logic
**Value Checkpoint**: Can compile and test domain entities
**Status**: 0/5 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 001 | Create Cargo workspace root configuration | `pending` | 1 EU | [001-create-cargo-workspace.md](./001-create-cargo-workspace.md) |
| 002 | Set up proto/ directory with adr.proto schema | `pending` | 1 EU | [002-setup-protobuf-schema.md](./002-setup-protobuf-schema.md) |
| 003 | Create adr-domain crate with ADR entity | `pending` | 1-2 EU | [003-create-adr-domain-crate.md](./003-create-adr-domain-crate.md) |
| 004 | Create adr-sdk crate with repository trait | `pending` | 1-2 EU | [004-create-adr-sdk-crate.md](./004-create-adr-sdk-crate.md) |
| 005 | Create adr-adapters crate with filesystem adapter | `pending` | 1-2 EU | [005-create-adr-adapters-crate.md](./005-create-adr-adapters-crate.md) |

**Dependencies**: None (starting point)
**Value Delivered**: Core hexagonal architecture established, domain logic testable

---

## Phase 2: CLI Tool (Tasks 006-009)

**Goal**: Working CLI that validates SDK architecture
**Value Checkpoint**: Usable tool for managing ADRs via command line
**Status**: 0/4 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 006 | Create adr-cli crate with list command | `pending` | 1 EU | [006-create-adr-cli-list.md](./006-create-adr-cli-list.md) |
| 007 | Add create command to adr-cli | `pending` | 1 EU | [007-add-cli-create-command.md](./007-add-cli-create-command.md) |
| 008 | Add show command to adr-cli | `pending` | 0.5 EU | [008-add-cli-show-command.md](./008-add-cli-show-command.md) |
| 009 | Add update status command to adr-cli | `pending` | 0.5 EU | [009-add-cli-update-status.md](./009-add-cli-update-status.md) |

**Dependencies**: Phase 1 (Tasks 001-005)
**Value Delivered**: First working interface proves hexagonal architecture works

---

## Phase 3: gRPC Service (Tasks 010-014)

**Goal**: Network API that reuses SDK (validates shared architecture)
**Value Checkpoint**: Remote ADR operations via gRPC
**Status**: 0/5 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 010 | Create adr-service crate with gRPC server setup | `pending` | 2 EU | [010-create-grpc-service.md](./010-create-grpc-service.md) |
| 011 | Implement gRPC ListADRs endpoint | `pending` | 1 EU | [011-implement-grpc-list.md](./011-implement-grpc-list.md) |
| 012 | Implement gRPC CreateADR endpoint | `pending` | 1 EU | [012-implement-grpc-create.md](./012-implement-grpc-create.md) |
| 013 | Implement gRPC GetADR endpoint | `pending` | 0.5 EU | [013-implement-grpc-get.md](./013-implement-grpc-get.md) |
| 014 | Implement gRPC UpdateADRStatus endpoint | `pending` | 0.5 EU | [014-implement-grpc-update-status.md](./014-implement-grpc-update-status.md) |

**Dependencies**: Phase 1 (Tasks 001-005), Task 002 (protobuf)
**Value Delivered**: CLI and Service share SDK - hexagonal architecture VALIDATED

---

## Phase 4: Next.js Frontend (Tasks 015-022)

**Goal**: Modern web UI consuming gRPC API
**Value Checkpoint**: Full-stack application with UI
**Status**: 0/8 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 015 | Create Next.js app with App Router setup | `pending` | 2 EU | [015-create-nextjs-app.md](./015-create-nextjs-app.md) |
| 016 | Generate TypeScript gRPC client from protobuf | `pending` | 1 EU | [016-generate-typescript-grpc-client.md](./016-generate-typescript-grpc-client.md) |
| 017 | Set up Zustand store for UI state | `pending` | 1 EU | [017-setup-zustand-store.md](./017-setup-zustand-store.md) |
| 018 | Set up React Query for server state | `pending` | 1 EU | [018-setup-react-query.md](./018-setup-react-query.md) |
| 019 | Create ADR list page with React Query | `pending` | 1-2 EU | [019-create-adr-list-page.md](./019-create-adr-list-page.md) |
| 020 | Create ADR detail page | `pending` | 1 EU | [020-create-adr-detail-page.md](./020-create-adr-detail-page.md) |
| 021 | Create ADR creation form with validation | `pending` | 1-2 EU | [021-create-adr-form.md](./021-create-adr-form.md) |
| 022 | Add status update functionality to UI | `pending` | 1 EU | [022-add-status-update-ui.md](./022-add-status-update-ui.md) |

**Dependencies**: Phase 3 (gRPC service must be working)
**Value Delivered**: Complete full-stack application, gRPC integration validated

---

## Phase 5: Testing & Validation (Tasks 023-025)

**Goal**: Prove system reliability and correctness
**Value Checkpoint**: Regression protection and quality confidence
**Status**: 0/3 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 023 | Add integration tests for CLI commands | `pending` | 1-2 EU | [023-add-cli-integration-tests.md](./023-add-cli-integration-tests.md) |
| 024 | Add integration tests for gRPC service | `pending` | 1-2 EU | [024-add-grpc-integration-tests.md](./024-add-grpc-integration-tests.md) |
| 025 | Add E2E tests for Next.js frontend | `pending` | 2 EU | [025-add-frontend-e2e-tests.md](./025-add-frontend-e2e-tests.md) |

**Dependencies**: Phases 2-4 (features must exist to test)
**Value Delivered**: Confidence in architecture, catch regressions early

---

## Phase 6: Build System Validation (Tasks 026-027)

**Goal**: Validate monorepo-ready structure with Bazel
**Value Checkpoint**: Migration confidence, build system proven
**Status**: 0/2 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 026 | Set up minimal Bazel BUILD files for Rust crates | `pending` | 2 EU | [026-setup-bazel-rust-builds.md](./026-setup-bazel-rust-builds.md) |
| 027 | Set up Bazel BUILD file for Next.js app | `pending` | 1-2 EU | [027-setup-bazel-nextjs-build.md](./027-setup-bazel-nextjs-build.md) |

**Dependencies**: Phases 1-4 (code must exist to build)
**Value Delivered**: Monorepo migration de-risked, Bazel patterns learned

---

## Phase 7: Documentation & Finalization (Tasks 028-030)

**Goal**: Complete PoC deliverable with documentation
**Value Checkpoint**: Handoff-ready package
**Status**: 0/3 completed

| ID | Task | Status | Est. Time | File |
|----|------|--------|-----------|------|
| 028 | Generate API documentation from protobuf schemas | `pending` | 0.5 EU | [028-generate-api-documentation.md](./028-generate-api-documentation.md) |
| 029 | Update README with final usage examples | `pending` | 1 EU | [029-update-readme-final.md](./029-update-readme-final.md) |
| 030 | Validate all tests pass end-to-end | `pending` | 0.5 EU | [030-validate-end-to-end.md](./030-validate-end-to-end.md) |

**Dependencies**: All previous phases
**Value Delivered**: Complete, documented, validated PoC ready for handoff

---

## 🔗 Dependency Graph

```
Foundation (001-005)
    ├─→ CLI Tool (006-009)
    └─→ gRPC Service (010-014)
            └─→ Next.js Frontend (015-022)
                    ├─→ Testing (023-025)
                    └─→ Build System (026-027)
                            └─→ Documentation (028-030)
```

**Critical Path**: 001 → 002 → 003 → 004 → 005 → 010 → 015 → 030

---

## 📈 Time Tracking

| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 4-6 EU | - | - |
| Phase 2 | 3 EU | - | - |
| Phase 3 | 5 EU | - | - |
| Phase 4 | 8-10 EU | - | - |
| Phase 5 | 4-6 EU | - | - |
| Phase 6 | 3-4 EU | - | - |
| Phase 7 | 2 EU | - | - |
| **Total** | **29-37 EU** | **0 EU** | **-** |

---

## 🚧 Current Blockers

None - ready to start implementation

---

## 📝 Recent Updates

### 2025-10-24
- Created atomic task breakdown
- Established folder structure and documentation
- All 30 tasks defined and ready to start

---

## 🎯 Architectural Validation Tracking

| Validation Goal | Tasks | Status |
|----------------|--------|--------|
| Hexagonal Architecture | 003-006 (CLI uses SDK) | Not started |
| gRPC Integration | 010-014, 016, 019-022 | Not started |
| Storage Abstraction | 004-005 (Repository pattern) | Not started |
| Next.js Patterns | 017-018 (Zustand + React Query) | Not started |
| Build Patterns | 026-027 (Bazel) | Not started |
| Monorepo Ready | 001, 026-027 | Not started |

---

## 📋 Quick Reference

**File Locations**:
- Task files: `.meta/adr-editor-poc/atomic-tasks/`
- Documentation: `docs/`
- Implementation: `crates/`, `apps/`, `proto/`

**Key Commands**:
```bash
# Check current status
cat .meta/adr-editor-poc/atomic-tasks/INDEX.md

# View specific task
cat .meta/adr-editor-poc/atomic-tasks/001-create-cargo-workspace.md

# Run tests (when implemented)
cargo test
pnpm test

# Build everything
cargo build
pnpm build
```

**Navigation**:
- Overview: [README.md](./README.md)
- This file: `INDEX.md`
- Individual tasks: `NNN-task-name.md`
- Project root: [../../../README.md](../../../README.md)
- LLM context: [../../../llm.md](../../../llm.md)

---

**Next Step**: Start with [001-create-cargo-workspace.md](./001-create-cargo-workspace.md) to begin Phase 1!
