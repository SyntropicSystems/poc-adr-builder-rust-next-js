# ADR Editor PoC - Bazel Workspace
# Minimal Bazel setup for learning and validation

workspace(name = "adr_editor_poc")

# Rust rules
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# rules_rust - For Rust crate builds
http_archive(
    name = "rules_rust",
    sha256 = "6357de5982dd32526a863843e1b1e8c8c22cc1c9a5a73f97e1e3c3f4ada00f71",
    urls = ["https://github.com/bazelbuild/rules_rust/releases/download/0.40.0/rules_rust-v0.40.0.tar.gz"],
)

load("@rules_rust//rust:repositories.bzl", "rules_rust_dependencies", "rust_register_toolchains")

rules_rust_dependencies()

rust_register_toolchains(
    edition = "2021",
    versions = ["1.75.0"],
)

# Protocol Buffers
http_archive(
    name = "com_google_protobuf",
    sha256 = "75be42bd736f4df6d702a0e4e4d30de9ee40eac024c4b845d17ae4cc831fe4ae",
    strip_prefix = "protobuf-21.7",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v21.7.tar.gz"],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()

# Node.js rules (for Next.js app)
http_archive(
    name = "build_bazel_rules_nodejs",
    sha256 = "94070eff79305be05b7699207fbac5d2608054dd53e6109f7d00d923919ff45a",
    urls = ["https://github.com/bazelbuild/rules_nodejs/releases/download/5.8.2/rules_nodejs-5.8.2.tar.gz"],
)

load("@build_bazel_rules_nodejs//:repositories.bzl", "build_bazel_rules_nodejs_dependencies")

build_bazel_rules_nodejs_dependencies()

# Note: This is a minimal Bazel setup for learning purposes.
# Primary development uses Cargo (Rust) and pnpm (Node.js).
# Bazel validates that our structure works for future monorepo migration.
