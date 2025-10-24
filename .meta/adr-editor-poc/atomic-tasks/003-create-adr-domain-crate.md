# Task 003: Create adr-domain Crate with ADR Entity

**Phase**: Phase 1 - Foundation
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001: Create Cargo workspace (workspace must exist)

**Blocks**:
- Task 004: Create adr-sdk crate (SDK depends on domain types)
- Task 005: Create adr-adapters crate (adapters use domain types)

**Value Delivered**:
Pure domain logic with NO infrastructure dependencies. This is the heart of hexagonal architecture - business rules that are completely independent of storage, APIs, or frameworks. Can be tested in complete isolation.

---

## 📝 Description

Create the `adr-domain` crate containing:
1. **ADR entity** - Core business object with validation
2. **Value objects** - ADRId, ADRNumber, ADRStatus, Timestamps
3. **Domain validation** - Business rules (e.g., title length, status transitions)
4. **No external dependencies** - Only standard library + serde for serialization

This crate should be:
- **Pure** - No I/O, no database, no network
- **Testable** - All logic unit testable
- **Type-safe** - Use newtype pattern for IDs, numbers, etc.

---

## ✅ Acceptance Criteria

- [ ] `crates/adr-domain/Cargo.toml` created
- [ ] `crates/adr-domain/src/lib.rs` with module structure
- [ ] ADR struct with all fields (id, number, title, context, decision, status, consequences, timestamps)
- [ ] Value objects: ADRId (UUID wrapper), ADRNumber (i32 wrapper), ADRStatus enum
- [ ] Domain validation methods (e.g., `validate_title`, status transition rules)
- [ ] Builder pattern for ADR construction
- [ ] Comprehensive unit tests (>80% coverage)
- [ ] Documentation comments on public API
- [ ] `cargo test -p adr-domain` passes
- [ ] Zero infrastructure dependencies (only serde, chrono, uuid)

---

## 🔧 Implementation Notes

**Crate Structure**:
```
crates/adr-domain/
├── Cargo.toml
└── src/
    ├── lib.rs           # Module exports
    ├── adr.rs           # ADR entity
    ├── value_objects.rs # ADRId, ADRNumber, etc.
    └── errors.rs        # Domain errors
```

**Example ADR Entity**:
```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ADR {
    id: ADRId,
    number: ADRNumber,
    title: String,
    context: String,
    decision: String,
    status: ADRStatus,
    consequences: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl ADR {
    pub fn new(title: String, context: String, decision: String, consequences: String) -> Result<Self, DomainError> {
        Self::validate_title(&title)?;

        Ok(Self {
            id: ADRId::generate(),
            number: ADRNumber::new(0), // Will be assigned by repository
            title,
            context,
            decision,
            status: ADRStatus::Draft,
            consequences,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    pub fn update_status(&mut self, new_status: ADRStatus) -> Result<(), DomainError> {
        self.validate_status_transition(self.status, new_status)?;
        self.status = new_status;
        self.updated_at = Utc::now();
        Ok(())
    }

    fn validate_title(title: &str) -> Result<(), DomainError> {
        if title.is_empty() {
            return Err(DomainError::InvalidTitle("Title cannot be empty".into()));
        }
        if title.len() > 200 {
            return Err(DomainError::InvalidTitle("Title too long (max 200 chars)".into()));
        }
        Ok(())
    }

    fn validate_status_transition(&self, from: ADRStatus, to: ADRStatus) -> Result<(), DomainError> {
        // Business rule: Can't go from ACCEPTED to DRAFT
        match (from, to) {
            (ADRStatus::Accepted, ADRStatus::Draft) => {
                Err(DomainError::InvalidStatusTransition(from, to))
            }
            _ => Ok(())
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum ADRStatus {
    Draft,
    Proposed,
    Accepted,
    Rejected,
    Deprecated,
    Superseded,
}
```

**Key Decisions**:
- Use `chrono` for timestamps (standard in Rust)
- Use `uuid` crate for ADRId
- Keep validation logic in domain (not in SDK or adapters)
- Immutable by default, explicit mutation methods

---

## 🧪 Verification

**How to test**:
```bash
# 1. Build the crate
cargo build -p adr-domain

# 2. Run unit tests
cargo test -p adr-domain

# 3. Check test coverage (if using tarpaulin)
cargo tarpaulin -p adr-domain

# 4. Run clippy for linting
cargo clippy -p adr-domain -- -D warnings

# 5. Check documentation
cargo doc -p adr-domain --open
```

**Expected outcome**:
- All tests pass
- No clippy warnings
- Documentation is clear and complete
- Can create ADR instances with validation
- Status transitions follow business rules

---

## 📚 Resources

- [Domain-Driven Design in Rust](https://doc.rust-lang.org/book/ch17-00-oop.html)
- [Newtype Pattern](https://doc.rust-lang.org/rust-by-example/generics/new_types.html)
- ADR 0001: Use Hexagonal Architecture (`docs/adr/0001-use-hexagonal-architecture.md`)

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
