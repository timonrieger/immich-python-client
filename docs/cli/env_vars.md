# Environment Variables

The Immich CLI supports several environment variables that can be used to configure the CLI behavior. These environment variables can be used as an alternative to command-line flags or profile settings.

## Configuration Priority

Environment variables have the following priority in the configuration hierarchy (highest to lowest):

1. Command-line flags (`--api-key`, `--base-url`, etc.)
2. **Environment variables** (this page)
3. Profile settings (from `immich setup`)

## Available Environment Variables

### `IMMICH_API_URL`

The URL of your Immich server API endpoint.

**Type**: String
**Example**: `https://demo.immich.app/api`
**Command-line equivalent**: `--base-url`
**Default**: None (must be set via environment variable, profile, or command-line flag)

**Usage**:
```bash
export IMMICH_API_URL="https://demo.immich.app/api"
immich assets list
```

---

### `IMMICH_API_KEY`

Your Immich API key for authentication. You can get an API key from your [Immich account settings](https://my.immich.app/user-settings?isOpen=api-keys).

**Type**: String
**Example**: `your-api-key-here`
**Command-line equivalent**: `--api-key`
**Default**: None

**Usage**:
```bash
export IMMICH_API_KEY="your-api-key-here"
immich assets list
```

!!! warning "Security"
    API keys are sensitive credentials. Never commit them to version control or share them publicly.

---

### `IMMICH_ACCESS_TOKEN`

An access token for authentication. This is an alternative to using an API key.

**Type**: String
**Example**: `your-access-token-here`
**Command-line equivalent**: `--access-token`
**Default**: None

**Usage**:
```bash
export IMMICH_ACCESS_TOKEN="your-access-token-here"
immich assets list
```

!!! note "API Key vs Access Token"
    You can use either `IMMICH_API_KEY` or `IMMICH_ACCESS_TOKEN` for authentication, but not both. If both are provided, the API key takes precedence.

!!! warning "Security"
    Access tokens are sensitive credentials. Never commit them to version control or share them publicly.

---

### `IMMICH_PROFILE`

The profile name to use for CLI configuration. Profiles are created using `immich setup --profile <name>`.

**Type**: String
**Example**: `demo`, `production`, `default`
**Command-line equivalent**: `--profile` or `-p`
**Default**: `default`

**Usage**:
```bash
export IMMICH_PROFILE="demo"
immich assets list
```

---

### `IMMICH_FORMAT`

The output format for CLI commands.

**Type**: String
**Valid values**: `pretty`, `json`, `table`
**Command-line equivalent**: `--format`
**Default**: `pretty`

**Usage**:
```bash
export IMMICH_FORMAT="json"
immich assets list
```

**Format descriptions**:
- `pretty`: Human-readable formatted output (default)
- `json`: JSON output, useful for scripting and automation
- `table`: Tabular output format

---

## Examples

### Using environment variables instead of profiles

Instead of creating a profile, you can set all required environment variables:

```bash
export IMMICH_API_URL="https://demo.immich.app/api"
export IMMICH_API_KEY="your-api-key-here"
export IMMICH_FORMAT="json"
immich assets list
```

### Temporary override

You can temporarily override profile settings using environment variables:

```bash
# Use a different server for this command only
IMMICH_API_URL="https://staging.immich.app/api" immich assets list
```

### Using in scripts

Environment variables are particularly useful in scripts and automation:

```bash
#!/bin/bash
export IMMICH_API_URL="https://demo.immich.app/api"
export IMMICH_API_KEY="${IMMICH_API_KEY}"
export IMMICH_FORMAT="json"

immich assets list --limit 10
```

### Using with `.env` files

You can use a `.env` file with tools like `direnv` or by sourcing it manually:

```bash
# .env file
IMMICH_API_URL=https://demo.immich.app/api
IMMICH_API_KEY=your-api-key-here
IMMICH_FORMAT=json
```

```bash
# Load and use
source .env
immich assets list
```

---

## See Also

- [Getting Started](./getting-started.md) - Learn how to set up the CLI
- [Reference](./reference.md) - Complete CLI command reference
