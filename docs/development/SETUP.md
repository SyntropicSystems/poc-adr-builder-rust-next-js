# Development Setup

**ADR Editor PoC** - Environment Setup Guide

---

## 🎯 Prerequisites

### Required Tools

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| **Rust** | 1.75+ | Backend development | [rustup.rs](https://rustup.rs/) |
| **Node.js** | v24 | Frontend development | [nodejs.org](https://nodejs.org/) or `nvm` |
| **pnpm** | 9.0+ | Package management | `npm install -g pnpm` |
| **Python** | 3.14+ | Utility scripts | [python.org](https://python.org/) |

### Optional Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **Bazel** | Build validation | [bazel.build](https://bazel.build/) |
| **protoc** | Protobuf compiler | `brew install protobuf` |
| **grpcurl** | gRPC testing | `brew install grpcurl` |

---

## 🚀 Quick Setup

### 1. Clone Repository

```bash
git clone <repo-url>
cd adr-editor-poc
```

### 2. Set Node Version

```bash
# If using nvm
nvm use

# Verify
node --version  # Should be v24.x
```

### 3. Install Rust Dependencies

```bash
# Already have Rust? Skip to next step
# Otherwise:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify
rustc --version  # Should be 1.75+
cargo --version
```

### 4. Build Rust Workspace

```bash
# Build all crates
cargo build

# Run tests
cargo test
```

### 5. Install Frontend Dependencies (when ready)

```bash
# When apps/adr-web exists
cd apps/adr-web
pnpm install
```

### 6. Verify Setup

```bash
# Check Rust
cargo check

# Check Python
python3 --version  # Should be 3.14+

# Check pnpm
pnpm --version  # Should be 9.0+
```

---

## 🔧 IDE Setup

### VS Code (Recommended)

**Required Extensions**:
- `rust-analyzer` - Rust language support
- `Even Better TOML` - TOML syntax
- `Error Lens` - Inline errors

**Recommended Extensions**:
- `crates` - Cargo.toml management
- `ES

Lint` - TypeScript linting
- `Prettier` - Code formatting

**Settings** (`.vscode/settings.json`):
```json
{
  "rust-analyzer.cargo.features": "all",
  "editor.formatOnSave": true,
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  }
}
```

### RustRover / IntelliJ

- Import as Cargo project
- Enable Rust plugin
- Set Rust toolchain to stable

---

## 🐛 Troubleshooting

### Cargo Build Fails

```bash
# Update Rust
rustup update

# Clean build artifacts
cargo clean
cargo build
```

### Node Version Wrong

```bash
# Install correct version
nvm install 24
nvm use 24
```

### pnpm Not Found

```bash
# Install globally
npm install -g pnpm

# Or use corepack
corepack enable
corepack prepare pnpm@9.0.0 --activate
```

### Python Script Errors

```bash
# Ensure Python 3.14+
python3 --version

# May need to install via pyenv
pyenv install 3.14.0
pyenv global 3.14.0
```

---

## 🎓 Learning Resources

- **Rust**: [The Rust Book](https://doc.rust-lang.org/book/)
- **Cargo**: [Cargo Book](https://doc.rust-lang.org/cargo/)
- **Next.js**: [Next.js Docs](https://nextjs.org/docs)
- **gRPC**: [gRPC Basics](https://grpc.io/docs/what-is-grpc/introduction/)

---

## ✅ Verification Checklist

- [ ] Rust 1.75+ installed
- [ ] Node v24 installed
- [ ] pnpm 9.0+ installed
- [ ] Python 3.14+ installed
- [ ] `cargo build` succeeds
- [ ] `cargo test` passes
- [ ] IDE configured with rust-analyzer

---

**Next**: See [WORKFLOW.md](./WORKFLOW.md) for day-to-day development commands.
