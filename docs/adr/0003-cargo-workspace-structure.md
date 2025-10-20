# ADR 0003: Cargo Workspace Structure

**Status**: ✅ Accepted  
**Date**: 2025-10-20  
**Validated**: PoC Setup + All Phases

---

## Context

Need to organize Rust crates to:
- Support hexagonal architecture layers
- Enable independent development of each layer
- Share code between CLI and service
- Minimize monorepo migration effort
- Allow feature flags per adapter

## Decision

Use **Cargo workspace** with crates organized by architectural layer:

```
crates/
├── adr-domain/      # Layer 1: Pure domain
├── adr-sdk/         # Layer 2: Ports + Use cases  
├── adr-adapters/    # Layer 3: Infrastructure
├── adr-service/     # Inbound: gRPC server
└── adr-cli/         # Inbound: CLI tool
```

**Workspace-level dependency management** for consistency.

## Alternatives Considered

| Alternative | Why Not |
|------------|---------|
| Single crate | Can't enforce layer boundaries |
| Separate repositories | Harder to share code, no monorepo validation |
| Nested workspaces | Over-complex for PoC |

## Consequences

### Positive
- ✅ Compiler enforces dependencies (domain can't import infrastructure)
- ✅ Fast incremental builds (`cargo build -p adr-domain`)
- ✅ Independent testing (`cargo test -p adr-sdk`)
- ✅ Feature flags per crate (`adr-adapters` has `filesystem`, `postgres`)
- ✅ Zero-cost monorepo migration (same structure)

### Negative
- ⚠️ Slightly more complex than single crate
- ⚠️ Need to manage workspace dependencies

## Validation

- ✅ **All Phases**: Each crate builds independently
- ✅ **Metric**: Domain has 0 dependencies
- ✅ **Metric**: Changing one crate doesn't rebuild others
- ✅ **Migration**: Copied to monorepo with 0 path changes

## Related

- [Hexagonal Architecture](./0001-use-hexagonal-architecture.md)
- [Repository Pattern](./0004-repository-pattern.md)
- [Migration Guide](../architecture/MIGRATION.md)

---

**Status**: Validated - structure matches monorepo exactly.
