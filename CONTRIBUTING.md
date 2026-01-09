# Contributing

This repository is **auto-generated** from the Immich OpenAPI specification.

## Pull requests

Pull requests are welcome! However, **modifications to auto-generated code will be rejected**.

### PR checklist

Before submitting a pull request, please ensure:

1. Install [mise](https://mise.jdx.dev) if you haven't already
2. Run `mise run ci:check` to verify all checks pass
3. To see all available tasks, run `mise tasks ls`

### Auto-generated code restrictions

The following directories contain auto-generated code and **must not be modified**:

- `immich/client/` - All files in this directory are auto-generated from the Immich OpenAPI specification
- Any other auto-generated files

The generated client is updated by automation:

- Generate client from the upstream Immich release
- Commit to `main` via an automation PR
- Tag + release to PyPI

### What can be contributed

You can contribute to:

- Custom wrapper functions in `immich/client_wrapper/`
- Utility functions in `immich/utils.py`
- SDK-level code in `immich/sdk.py`
- Tests in `tests/`
- Documentation improvements
- Build and development tooling

## Where to report issues

- **Immich API/spec problems** (missing/incorrect endpoints, schema issues, breaking API changes): open an issue in the upstream Immich repository.
- **Generation issues** (bad codegen output, typing problems introduced by generation, workflow automation problems): open an issue here.

When reporting, include:

- The `IMMICH-VERSION` from this repo
- The Immich server version you are running
- A minimal reproduction (request/response or endpoint + payload)


