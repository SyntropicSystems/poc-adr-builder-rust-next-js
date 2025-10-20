# ADR 0004: Repository Pattern for Storage

**Status**: ✅ Accepted  
**Date**: 2025-10-20  
**Validated**: PoC Phase 2-3

---

## Context

Need storage abstraction that:
- Supports multiple backends (filesystem, Postgres, DynamoDB)
- Allows swapping without changing business logic
- Enables testing without real storage
- Works with async Rust

## Decision

Use **Repository Pattern** with trait-based ports:

```rust
#[async_trait]
pub trait ADRRepository: Send + Sync {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError>;
    async fn list_all(&self) -> Result<Vec<ADR>, ADRError>;
    // ...
}
```

Implementations as adapters with feature flags.

## Alternatives Considered

| Alternative | Why Not |
|------------|---------|
| Direct database access | Tight coupling, can't swap |
| Generic storage trait | Too abstract, lose domain semantics |
| DAO pattern | Java-centric, not idiomatic Rust |

## Consequences

### Positive
- ✅ Swappable: Change one line in config
- ✅ Testable: Use mock repository
- ✅ Type-safe: Compiler enforces contract
- ✅ Async-native: Works with tokio

### Negative
- ⚠️ Trait object overhead (minimal)
- ⚠️ Each adapter needs full implementation

## Validation

- ✅ **Phase 2**: FilesystemAdapter implements trait
- ✅ **Metric**: Swapping adapter = 1 line change
- ✅ **Metric**: Tests use MockRepository (no I/O)

## Related

- [Hexagonal Architecture](./0001-use-hexagonal-architecture.md)
- [Workspace Structure](./0003-cargo-workspace-structure.md)

---

**Status**: Pattern validated with filesystem adapter.
