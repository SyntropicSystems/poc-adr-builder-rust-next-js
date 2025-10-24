# Task 004: Create adr-sdk Crate with Repository Trait

**Phase**: Phase 1 - Foundation
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001: Create Cargo workspace
- Task 003: Create adr-domain crate (SDK uses domain types)

**Blocks**:
- Task 005: Create adr-adapters crate (implements SDK traits)
- Task 006: Create adr-cli crate (uses SDK)
- Task 010: Create adr-service crate (uses SDK)

**Value Delivered**:
Defines the **ports** (interfaces) of hexagonal architecture. This is the contract that adapters must implement and applications will use. The repository trait enables swappable storage implementations without changing business logic.

---

## 📝 Description

Create the `adr-sdk` crate containing:
1. **ADRRepository trait** - Port for storage operations (CRUD)
2. **Use cases** - Business operations (CreateADR, ListADRs, GetADR, UpdateStatus)
3. **SDK errors** - Application-level errors
4. **Repository mock** - For testing (using mockall)

This is the **core of hexagonal architecture**:
- **Port**: `ADRRepository` trait defines what we need from storage
- **Use cases**: Application logic that uses the port
- **Adapters**: Will implement the trait (filesystem, database, etc.)

---

## ✅ Acceptance Criteria

- [ ] `crates/adr-sdk/Cargo.toml` created with dependency on `adr-domain`
- [ ] `ADRRepository` trait defined with async methods
- [ ] Use cases implemented: `create_adr`, `list_adrs`, `get_adr`, `update_adr_status`
- [ ] SDK errors defined (NotFound, ValidationError, StorageError)
- [ ] Mock repository for testing (using mockall)
- [ ] Unit tests for use cases using mocked repository
- [ ] Documentation on trait methods
- [ ] `cargo test -p adr-sdk` passes
- [ ] Async/await support with tokio

---

## 🔧 Implementation Notes

**Crate Structure**:
```
crates/adr-sdk/
├── Cargo.toml
└── src/
    ├── lib.rs              # Module exports
    ├── repository.rs       # ADRRepository trait
    ├── use_cases.rs        # Business operations
    └── errors.rs           # SDK errors
```

**Repository Trait**:
```rust
use async_trait::async_trait;
use adr_domain::{ADR, ADRId, ADRNumber};

#[async_trait]
pub trait ADRRepository: Send + Sync {
    /// Save a new or existing ADR
    async fn save(&self, adr: &ADR) -> Result<(), RepositoryError>;

    /// Find ADR by ID (UUID)
    async fn find_by_id(&self, id: &ADRId) -> Result<Option<ADR>, RepositoryError>;

    /// Find ADR by sequential number (e.g., 0001)
    async fn find_by_number(&self, number: ADRNumber) -> Result<Option<ADR>, RepositoryError>;

    /// List all ADRs
    async fn list_all(&self) -> Result<Vec<ADR>, RepositoryError>;

    /// Get next sequential number
    async fn next_number(&self) -> Result<ADRNumber, RepositoryError>;
}
```

**Use Case Example**:
```rust
pub struct ADRService<R: ADRRepository> {
    repository: Arc<R>,
}

impl<R: ADRRepository> ADRService<R> {
    pub fn new(repository: Arc<R>) -> Self {
        Self { repository }
    }

    pub async fn create_adr(
        &self,
        title: String,
        context: String,
        decision: String,
        consequences: String,
    ) -> Result<ADR, SDKError> {
        // 1. Create domain entity (validates)
        let mut adr = ADR::new(title, context, decision, consequences)?;

        // 2. Assign sequential number
        let number = self.repository.next_number().await?;
        adr.set_number(number);

        // 3. Persist
        self.repository.save(&adr).await?;

        Ok(adr)
    }

    pub async fn list_adrs(&self) -> Result<Vec<ADR>, SDKError> {
        self.repository.list_all().await
            .map_err(SDKError::from)
    }

    pub async fn get_adr(&self, id_or_number: String) -> Result<ADR, SDKError> {
        // Try parsing as number first (e.g., "0001")
        if let Ok(num) = id_or_number.parse::<i32>() {
            if let Some(adr) = self.repository.find_by_number(ADRNumber::new(num)).await? {
                return Ok(adr);
            }
        }

        // Try as UUID
        if let Ok(uuid) = Uuid::parse_str(&id_or_number) {
            if let Some(adr) = self.repository.find_by_id(&ADRId::from(uuid)).await? {
                return Ok(adr);
            }
        }

        Err(SDKError::NotFound(id_or_number))
    }

    pub async fn update_adr_status(
        &self,
        id: &ADRId,
        new_status: ADRStatus,
    ) -> Result<ADR, SDKError> {
        let mut adr = self.repository.find_by_id(id).await?
            .ok_or_else(|| SDKError::NotFound(id.to_string()))?;

        adr.update_status(new_status)?;
        self.repository.save(&adr).await?;

        Ok(adr)
    }
}
```

**Key Decisions**:
- Use `async_trait` for async trait methods
- Return `Result<Option<T>>` for find operations (None = not found, Ok)
- Accept both UUID and sequential number for lookups
- Use Arc for shared repository references

---

## 🧪 Verification

**How to test**:
```bash
# 1. Build the crate
cargo build -p adr-sdk

# 2. Run unit tests with mocked repository
cargo test -p adr-sdk

# 3. Check for warnings
cargo clippy -p adr-sdk -- -D warnings

# 4. Verify documentation
cargo doc -p adr-sdk --open
```

**Expected outcome**:
- Tests pass using mocked repository
- Use cases work correctly
- Repository trait is well-documented
- Ready to be implemented by adapters

---

## 📚 Resources

- [Async Trait](https://docs.rs/async-trait/)
- [Mockall for Testing](https://docs.rs/mockall/)
- ADR 0001: Use Hexagonal Architecture (`docs/adr/0001-use-hexagonal-architecture.md`)
- ADR 0004: Repository Pattern (`docs/adr/0004-repository-pattern.md`)

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
