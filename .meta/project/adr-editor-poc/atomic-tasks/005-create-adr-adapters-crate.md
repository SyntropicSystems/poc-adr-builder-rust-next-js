# Task 005: Create adr-adapters Crate with Filesystem Adapter

**Phase**: Phase 1 - Foundation
**Status**: pending
**Estimated Time**: 1-2 EU
**Actual Time**: -

---

## 📍 Context

**Dependencies**:
- Task 001: Create Cargo workspace
- Task 003: Create adr-domain crate
- Task 004: Create adr-sdk crate (implements ADRRepository trait)

**Blocks**:
- Task 006: Create adr-cli crate (CLI needs working storage)
- Task 010: Create adr-service crate (service needs working storage)

**Value Delivered**:
First concrete implementation of the repository port. Proves hexagonal architecture works - storage is swappable. Enables actual persistence of ADRs to filesystem, making the system functional.

---

## 📝 Description

Create the `adr-adapters` crate with filesystem storage adapter:
1. **FilesystemAdapter** - Implements `ADRRepository` trait
2. **File operations** - Save/load ADRs as JSON files
3. **Directory management** - Create `.adr/` directory structure
4. **Numbering** - Sequential number assignment logic
5. **Integration tests** - Test actual file I/O

File structure:
```
.adr/
├── adrs/
│   ├── 0001-use-hexagonal-architecture.json
│   ├── 0002-use-grpc-for-api.json
│   └── ...
└── index.json  # Metadata: next_number, etc.
```

---

## ✅ Acceptance Criteria

- [ ] `crates/adr-adapters/Cargo.toml` created with dependencies on `adr-domain` and `adr-sdk`
- [ ] `FilesystemAdapter` struct implementing `ADRRepository` trait
- [ ] Directory creation logic (creates `.adr/adrs/` if not exists)
- [ ] Save ADR to JSON file with format: `NNNN-slug.json`
- [ ] Load ADR from JSON file by ID or number
- [ ] List all ADRs by reading directory
- [ ] Sequential number management (stored in index.json)
- [ ] Proper error handling (file not found, permissions, etc.)
- [ ] Integration tests using temp directories
- [ ] `cargo test -p adr-adapters` passes

---

## 🔧 Implementation Notes

**Crate Structure**:
```
crates/adr-adapters/
├── Cargo.toml
└── src/
    ├── lib.rs                 # Module exports
    ├── filesystem.rs          # FilesystemAdapter implementation
    └── tests/
        └── integration_test.rs
```

**FilesystemAdapter Implementation**:
```rust
use adr_sdk::{ADRRepository, RepositoryError};
use adr_domain::{ADR, ADRId, ADRNumber};
use std::path::PathBuf;
use tokio::fs;

pub struct FilesystemAdapter {
    base_path: PathBuf,
}

impl FilesystemAdapter {
    pub async fn new(base_path: PathBuf) -> Result<Self, RepositoryError> {
        let adrs_path = base_path.join(".adr").join("adrs");
        fs::create_dir_all(&adrs_path).await
            .map_err(|e| RepositoryError::InitializationFailed(e.to_string()))?;

        Ok(Self { base_path })
    }

    fn adr_file_path(&self, adr: &ADR) -> PathBuf {
        let filename = format!("{:04}-{}.json", adr.number().value(), slug::slugify(adr.title()));
        self.base_path.join(".adr").join("adrs").join(filename)
    }

    async fn read_index(&self) -> Result<Index, RepositoryError> {
        let index_path = self.base_path.join(".adr").join("index.json");
        if !index_path.exists() {
            return Ok(Index::default());
        }

        let content = fs::read_to_string(&index_path).await?;
        serde_json::from_str(&content)
            .map_err(|e| RepositoryError::CorruptedData(e.to_string()))
    }

    async fn write_index(&self, index: &Index) -> Result<(), RepositoryError> {
        let index_path = self.base_path.join(".adr").join("index.json");
        let content = serde_json::to_string_pretty(index)?;
        fs::write(&index_path, content).await?;
        Ok(())
    }
}

#[async_trait]
impl ADRRepository for FilesystemAdapter {
    async fn save(&self, adr: &ADR) -> Result<(), RepositoryError> {
        let path = self.adr_file_path(adr);
        let content = serde_json::to_string_pretty(adr)?;
        fs::write(&path, content).await
            .map_err(|e| RepositoryError::SaveFailed(e.to_string()))?;
        Ok(())
    }

    async fn find_by_id(&self, id: &ADRId) -> Result<Option<ADR>, RepositoryError> {
        let adrs = self.list_all().await?;
        Ok(adrs.into_iter().find(|adr| adr.id() == id))
    }

    async fn find_by_number(&self, number: ADRNumber) -> Result<Option<ADR>, RepositoryError> {
        let adrs_dir = self.base_path.join(".adr").join("adrs");
        let pattern = format!("{:04}-*.json", number.value());

        let mut entries = fs::read_dir(&adrs_dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            let filename = entry.file_name().to_string_lossy().to_string();
            if filename.starts_with(&format!("{:04}-", number.value())) {
                let content = fs::read_to_string(entry.path()).await?;
                let adr: ADR = serde_json::from_str(&content)?;
                return Ok(Some(adr));
            }
        }

        Ok(None)
    }

    async fn list_all(&self) -> Result<Vec<ADR>, RepositoryError> {
        let adrs_dir = self.base_path.join(".adr").join("adrs");
        let mut adrs = Vec::new();

        let mut entries = fs::read_dir(&adrs_dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            if entry.path().extension().and_then(|s| s.to_str()) == Some("json") {
                let content = fs::read_to_string(entry.path()).await?;
                let adr: ADR = serde_json::from_str(&content)?;
                adrs.push(adr);
            }
        }

        adrs.sort_by_key(|adr| adr.number().value());
        Ok(adrs)
    }

    async fn next_number(&self) -> Result<ADRNumber, RepositoryError> {
        let mut index = self.read_index().await?;
        index.next_number += 1;
        self.write_index(&index).await?;
        Ok(ADRNumber::new(index.next_number))
    }
}

#[derive(Serialize, Deserialize, Default)]
struct Index {
    next_number: i32,
}
```

**Key Decisions**:
- Store ADRs as individual JSON files (human-readable)
- Use format: `NNNN-slug.json` for easy sorting and reading
- Keep index.json for metadata (next number)
- Use tokio async file I/O

---

## 🧪 Verification

**How to test**:
```bash
# 1. Build the crate
cargo build -p adr-adapters

# 2. Run integration tests
cargo test -p adr-adapters

# 3. Manually test filesystem operations
cargo test -p adr-adapters -- --nocapture --test-threads=1
```

**Expected outcome**:
- Tests create temp directories
- ADRs persist to JSON files correctly
- Can read back saved ADRs
- Sequential numbering works
- Files have correct format and naming

---

## 📚 Resources

- [Tokio Filesystem](https://docs.rs/tokio/latest/tokio/fs/)
- [Serde JSON](https://docs.rs/serde_json/)
- ADR 0004: Repository Pattern (`docs/adr/0004-repository-pattern.md`)

---

## 📝 Completion Notes

**Date Completed**:
**Completed By**:

**Learnings**:
-

**Deviations**:
-
