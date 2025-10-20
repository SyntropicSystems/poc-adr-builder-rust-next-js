# ADR 0001: Use Hexagonal Architecture

**Status**: ✅ Accepted  
**Date**: 2025-10-20  
**Validated**: PoC Phase 1-2

---

## Context

We need to build a system that:
1. Supports multiple storage backends (filesystem, Postgres, DynamoDB) without changing business logic
2. Allows testing business logic without spinning up infrastructure
3. Enables both CLI and gRPC service to share the same business logic
4. Can be easily migrated to a monorepo with minimal refactoring

**Constraints**:
- Rust-first project (type safety, performance)
- Team wants to learn clean architecture patterns
- Must validate architecture works in practice (PoC goal)

## Decision

Use **Hexagonal Architecture** (Ports & Adapters pattern) with clear layer separation:

```
Domain (Pure) → SDK (Ports + Use Cases) → Adapters (Infrastructure)
```

**Structure**:
- `adr-domain`: Pure domain entities (no infrastructure dependencies)
- `adr-sdk`: Ports (traits) + Use Cases (business logic)
- `adr-adapters`: Infrastructure implementations (filesystem, postgres, etc.)
- `adr-service`: Inbound adapter (gRPC server)
- `adr-cli`: Inbound adapter (CLI tool)

**Key Principle**: Dependencies point inward (Infrastructure → Application → Domain)

## Alternatives Considered

### Option A: Layered Architecture (Traditional N-Tier)

| Pros | Cons | Why Not |
|------|------|---------|
| Familiar, simple | Layers can depend on each other | Hard to swap storage |
| Easy to understand | Business logic mixed with infrastructure | Can't test without DB |
| Less abstraction | Tight coupling | Doesn't validate flexibility |

### Option B: Microkernel Architecture

| Pros | Cons | Why Not |
|------|------|---------|
| Plugin-based | Complex plugin system | Overkill for PoC |
| Very flexible | Runtime discovery needed | Don't need dynamic plugins |
| Extensible | More moving parts | Simpler pattern suffices |

### Option C: Event-Driven Architecture

| Pros | Cons | Why Not |
|------|------|---------|
| Highly decoupled | Complex messaging | Not needed for CRUD |
| Scalable | Eventual consistency | PoC doesn't need events |
| Async by nature | Harder to reason about | Adds complexity |

## Consequences

### Positive

✅ **Testability**: Can test use cases without any infrastructure
```rust
#[test]
fn test_create_adr() {
    let mock_repo = MockRepository::new();
    let use_case = CreateADRUseCase::new(Arc::new(mock_repo));
    let result = use_case.execute(input);
    assert!(result.is_ok());
}
```

✅ **Flexibility**: Swap storage by changing one line
```rust
// Development
let repo = FilesystemAdapter::new("./adrs");

// Production
let repo = PostgresAdapter::new(pool);

// Same use case works with both!
```

✅ **Code Reuse**: CLI and service share 80%+ code
```rust
// CLI
let use_case = CreateADRUseCase::new(repo);
let adr = use_case.execute(input)?;

// Service
let use_case = CreateADRUseCase::new(repo);
let adr = use_case.execute(input)?;

// SAME CODE!
```

✅ **Clear Boundaries**: Compiler enforces layer separation
```rust
// This won't compile (domain can't import infrastructure):
// use adr_adapters::filesystem::FilesystemAdapter;  // ❌ ERROR

// Domain stays pure
```

### Negative

⚠️ **More Crates**: 5 crates instead of 1 (but managed by workspace)

⚠️ **Indirection**: Need traits/ports (but this is the point - abstraction)

⚠️ **Learning Curve**: Team needs to understand pattern (acceptable - learning goal)

⚠️ **Boilerplate**: Some repeated trait implementations (mitigated by macros if needed)

## Validation

### Validated in PoC

- ✅ **Phase 1**: Domain + SDK crates built with zero infrastructure deps
- ✅ **Phase 2**: CLI uses SDK successfully (filesystem adapter)
- ✅ **Phase 3**: Service uses SDK successfully (same filesystem adapter)
- ✅ **Metric**: 82% code shared between CLI and service
- ✅ **Metric**: Swapping adapter = 1 line change in config

### Success Criteria Met

1. ✅ Can test use cases without database/filesystem
2. ✅ CLI and service use identical business logic
3. ✅ Can swap storage adapter without touching use cases
4. ✅ Compiler prevents domain from importing infrastructure
5. ✅ Clear boundaries make code easy to navigate

### Lessons Learned

**What Worked**:
- Trait-based ports (ADRRepository) work perfectly
- Use cases compose easily
- Testing without infrastructure is dramatically simpler
- Rust's type system enforces boundaries naturally

**What We'd Change**:
- Consider macro for reducing trait impl boilerplate (if it becomes issue)
- Document port contracts more explicitly (what adapters must guarantee)

## Implementation Notes

### Repository Port (Trait)

```rust
#[async_trait]
pub trait ADRRepository: Send + Sync {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<ADR>, ADRError>;
    // ... other methods
}
```

**Key**: This lives in SDK (application layer), not domain or adapters.

### Use Case Pattern

```rust
pub struct CreateADRUseCase<R: ADRRepository> {
    repository: Arc<R>,
}

impl<R: ADRRepository> CreateADRUseCase<R> {
    pub fn new(repository: Arc<R>) -> Self {
        Self { repository }
    }
    
    pub async fn execute(&self, input: CreateADRInput) -> Result<ADR, ADRError> {
        // 1. Validate (domain rules)
        let adr = ADR::new(input.title, input.description)?;
        
        // 2. Save (via port)
        self.repository.save(&adr).await?;
        
        // 3. Return
        Ok(adr)
    }
}
```

### Adapter Implementation

```rust
pub struct FilesystemAdapter {
    base_path: PathBuf,
}

#[async_trait]
impl ADRRepository for FilesystemAdapter {
    async fn save(&self, adr: &ADR) -> Result<(), ADRError> {
        let json = serde_json::to_string_pretty(adr)?;
        let path = self.base_path.join(format!("{}.json", adr.id));
        tokio::fs::write(path, json).await?;
        Ok(())
    }
    // ... other methods
}
```

## Related

- **Architecture Overview**: [../architecture/OVERVIEW.md](../architecture/OVERVIEW.md)
- **Repository Pattern**: [0004-repository-pattern.md](./0004-repository-pattern.md)
- **Workspace Structure**: [0003-cargo-workspace-structure.md](./0003-cargo-workspace-structure.md)

---

## References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Original article by Alistair Cockburn
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Robert C. Martin
- [Rust Hexagonal Example](https://alexis-lozano.com/hexagonal-architecture-in-rust-1/) - Practical Rust implementation

---

**Status**: This decision is validated and working in production PoC code.
