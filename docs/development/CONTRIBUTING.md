# Contributing Guide

**ADR Editor PoC** - How to Contribute

---

## 🎯 Getting Started

1. Read [SETUP.md](./SETUP.md) - Set up your environment
2. Read [WORKFLOW.md](./WORKFLOW.md) - Learn the commands
3. Read [llm.md](../../llm.md) - Understand the project

---

## 📋 PR Checklist

Before submitting a pull request:

### Code Quality
- [ ] Code follows project conventions
- [ ] `cargo fmt` run (Rust formatting)
- [ ] `cargo clippy` passes (no warnings)
- [ ] `cargo test` passes (all tests green)
- [ ] `pnpm web:lint` passes (if frontend changes)

### Documentation
- [ ] If `.proto` changed: Ran `pnpm docs:generate`
- [ ] If architecture changed: Updated `docs/adr/` and `docs/architecture/`
- [ ] If workflow changed: Updated `docs/development/WORKFLOW.md`
- [ ] If new crate added: Updated `docs/architecture/OVERVIEW.md`
- [ ] Ran `pnpm docs:validate` (docs are current)

### Testing
- [ ] Added tests for new functionality
- [ ] All tests pass locally
- [ ] Tested manually (if applicable)

---

## 🎨 Code Conventions

### Rust

**Naming**:
- `snake_case` for functions, variables
- `PascalCase` for types, traits
- `SCREAMING_SNAKE_CASE` for constants

**Structure**:
```rust
// Good
pub struct CreateADRUseCase<R: ADRRepository> {
    repository: Arc<R>,
}

// Imports at top, organized
use std::sync::Arc;
use crate::repository::ADRRepository;
```

**Error Handling**:
```rust
// Use Result types
pub async fn execute(&self, input: Input) -> Result<ADR, ADRError> {
    // ...
}

// Use ? operator
let adr = self.repository.save(&adr).await?;
```

### TypeScript

**Naming**:
- `camelCase` for functions, variables
- `PascalCase` for components, types
- `SCREAMING_SNAKE_CASE` for constants

**Components**:
```typescript
// Use function components
export function ADRList() {
  // Hooks at top
  const { data } = useQuery(/* ... */);
  
  // Early returns
  if (!data) return <Loading />;
  
  return <div>{/* ... */}</div>;
}
```

---

## 🏗️ Architecture Guidelines

### Adding a New Use Case

1. **Define in SDK** (`crates/adr-sdk/src/use_cases/`)
2. **Add tests** (unit tests in same file)
3. **Wire into service** (`crates/adr-service/`)
4. **Wire into CLI** (`crates/adr-cli/`)
5. **Update docs** if public API changed

### Adding a Storage Adapter

1. **Create module** (`crates/adr-adapters/src/new_adapter.rs`)
2. **Implement trait** (`ADRRepository`)
3. **Add feature flag** (`Cargo.toml`)
4. **Add tests** (integration tests)
5. **Document** in `docs/architecture/TECHNOLOGY_STACK.md`

### Adding Frontend Feature

1. **Create component** (`apps/adr-web/components/`)
2. **Add to page** (`apps/adr-web/app/`)
3. **Add state** if needed (Zustand or React Query)
4. **Test manually** (run `pnpm web:dev`)

---

## 🧪 Testing Guidelines

### What to Test

**Do Test**:
- ✅ Domain logic (all business rules)
- ✅ Use cases (happy path + error cases)
- ✅ Adapters (with real implementations)
- ✅ API endpoints (integration tests)

**Don't Test**:
- ❌ Third-party libraries
- ❌ Generated code (protobuf types)
- ❌ Trivial getters/setters

### Test Structure

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_create_adr_success() {
        // Arrange
        let repo = MockRepository::new();
        let use_case = CreateADRUseCase::new(Arc::new(repo));
        
        // Act
        let result = use_case.execute(input);
        
        // Assert
        assert!(result.is_ok());
    }
}
```

---

## 📝 Commit Messages

### Format

```
type(scope): brief description

Longer explanation if needed.

- Bullet points for details
- Reference issues: Fixes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change (no behavior change)
- `test`: Adding tests
- `chore`: Maintenance (deps, config, etc.)

### Examples

```
feat(sdk): add UpdateADR use case

Implements the UpdateADR use case with validation.

- Validates ADR exists before updating
- Checks title length constraints
- Updates timestamp

Closes #42
```

---

## 🔄 Review Process

### What Reviewers Look For

1. **Correctness**: Does it work?
2. **Tests**: Is it tested?
3. **Documentation**: Is it documented?
4. **Architecture**: Follows hexagonal pattern?
5. **Style**: Matches conventions?

### Addressing Feedback

- Respond to all comments
- Make requested changes
- Push new commits (don't force-push during review)
- Re-request review when ready

---

## ❓ Questions?

- **Architecture questions**: See `docs/architecture/`
- **Decision rationale**: See `docs/adr/`
- **Current status**: See `.meta/adr-editor-poc/implementation-plan/`

---

**Thank you for contributing!** 🎉
