# Getting Started

## Set up your Immich server

1. Have your Immich server running or use the [demo server](https://demo.immich.app)
2. Get an API key from your [Immich account settings](https://my.immich.app/user-settings?isOpen=api-keys)

## Create a profile

Using profiles allows you to use the CLI with different servers and reuse configurations easily.

<div class="termy">

```console
$ immich setup

# Enter your server URL: $ https://demo.immich.app/api
# Enter your API key: $ ********

Profile 'default' created successfully!
```
</div>

!!! note "Validation"
    The server is validated when you run `immich setup`. The CLI will fail if the server is not reachable.

See [`immich setup`](./reference.md#immich-setup) for the full command reference.

## First commands

That's it! You can now run interact with the Immich server using the CLI.

<div class="termy">

```console
$ immich server get-about-info

{
  "build": "20375083601",
  "version": "v2.4.1",
}
```
</div>

You can also get the information in a different format, e.g. as a table:

<div class="termy">

```console
$ immich --format table server get-about-info

┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Key      ┃ Value          ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ build    │ 20375083601    │
│ version  │ v2.4.1         │
└──────────┴────────────────┘
```

</div>

To see all available commands, run `immich --help` or see the [reference](./reference.md).

## Configuration Priority

Priority order (highest to lowest):

1. Command-line flags (`--api-key`, `--base-url`)
2. Environment variables
3. Profile settings (from `immich setup`)

This lets you switch between servers or override settings when needed. If you are unsure which configuration is used, run `immich --verbose <command>` to see the configuration in use.

## Boolean Options

- Flags like `--verbose`, `--dry-run` are simple toggles: present = true, absent = false.
- Optional flags like `--albums` let you pass true, false, or omit them — omission lets the server apply its default.
