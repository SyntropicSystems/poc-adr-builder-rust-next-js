# Development Workflow

**ADR Editor PoC** - Day-to-Day Development Commands

---

## 🎯 Primary Tool: Cargo

**Remember**: Cargo is the primary development tool. Use it for 90% of your work.

---

## 🦀 Rust Development (Primary)

### Building

```bash
# Build everything
cargo build

# Build specific crate
cargo build -p adr-domain
cargo build -p adr-sdk
cargo build -p adr-cli

# Build in release mode
cargo build --release
```

### Testing

```bash
# Test everything
cargo test

# Test specific crate
cargo test -p adr-domain
cargo test -p adr-sdk

# Test with output
cargo test -- --nocapture

# Test specific function
cargo test test_create_adr
```

### Running

```bash
# Run CLI
cargo run -p adr-cli -- --help
cargo run -p adr-cli create --title "My ADR"

# Run service
cargo run -p adr-service

# Run with environment variables
ADR_SERVICE_PORT=8080 cargo run -p adr-service
```

### Code Quality

```bash
# Check without building
cargo check

# Format code
cargo fmt

# Lint
cargo clippy

# Fix lints automatically
cargo clippy --fix
```

---

## 🌐 Frontend Development (When Needed)

### Development Server

```bash
# From root
pnpm web:dev

# Or from app directory
cd apps/adr-web
pnpm dev
```

### Building

```bash
# From root
pnpm web:build

# Or from app directory
cd apps/adr-web
pnpm build
```

### Testing

```bash
pnpm web:test
pnpm web:lint
```

---

## 🐍 Utility Scripts (Occasional)

```bash
# Validate documentation
pnpm docs:validate

# Generate API docs
pnpm docs:generate
```

---

## 🔄 Full System Development

### Run Everything

**Terminal 1** (Backend):
```bash
cargo run -p adr-service
```

**Terminal 2** (Frontend):
```bash
pnpm web:dev
```

**Terminal 3** (Development):
```bash
# Make changes, test, etc.
cargo test
```

---

## 🧪 Testing Workflow

### Unit Tests (Fast)

```bash
# Test domain logic
cargo test -p adr-domain

# Test use cases
cargo test -p adr-sdk
```

### Integration Tests

```bash
# Test with filesystem adapter
cargo test -p adr-adapters --features filesystem

# Test CLI end-to-end
cargo run -p adr-cli create --title "Test"
```

### Frontend Tests

```bash
cd apps/adr-web
pnpm test
```

---

## 🔍 Debugging

### Rust

```bash
# Run with debug logging
RUST_LOG=debug cargo run -p adr-service

# Run with specific module logging
RUST_LOG=adr_sdk=trace cargo run -p adr-cli
```

### Frontend

```bash
# Next.js debug mode
NODE_OPTIONS='--inspect' pnpm web:dev
```

### gRPC

```bash
# Test service with grpcurl
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 adr.v1.ADRService/ListADRs
```

---

## 📦 Dependency Management

### Add Rust Dependency

```bash
# Add to specific crate
cd crates/adr-domain
cargo add serde --features derive

# Or edit Cargo.toml manually and run
cargo build
```

### Add Frontend Dependency

```bash
cd apps/adr-web
pnpm add <package>
pnpm add -D <dev-package>
```

---

## 🔄 Common Workflows

### Adding a New Use Case

1. Define in `adr-sdk/src/use_cases/`
2. Add tests
3. Wire into service and/or CLI
4. Test end-to-end

```bash
# Create file
touch crates/adr-sdk/src/use_cases/update_adr.rs

# Edit, then test
cargo test -p adr-sdk
```

### Adding a New Adapter

1. Create module in `adr-adapters/src/`
2. Implement `ADRRepository` trait
3. Add feature flag in `Cargo.toml`
4. Test

```bash
# Edit crates/adr-adapters/src/postgres.rs
# Then build with feature
cargo build -p adr-adapters --features postgres
cargo test -p adr-adapters --features postgres
```

### Adding Frontend Component

1. Create in `apps/adr-web/components/`
2. Add to page
3. Test in browser

```bash
cd apps/adr-web
pnpm dev
# Open http://localhost:3000
```

---

## 🚀 Pre-Commit Checklist

```bash
# Format
cargo fmt

# Lint
cargo clippy

# Test
cargo test

# Check docs
python3 scripts/validate_docs.py

# Build
cargo build
```

Or use the convenience command:
```bash
pnpm validate
```

---

## 🔗 Related

- **Setup Guide**: [SETUP.md](./SETUP.md)
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Architecture**: [../architecture/OVERVIEW.md](../architecture/OVERVIEW.md)

---

**Remember**: Cargo is your primary tool. pnpm only for frontend. Python only for scripts.
